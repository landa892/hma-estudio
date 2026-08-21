-- ANTES QUE NADA: esta migracion necesita es_admin_hma(), que crea la 0009.
-- El 20/08/2026 se corrio aca y fallo con "function es_admin_hma() does not
-- exist": la 0009 nunca se habia aplicado en la base del estudio, aunque la
-- 0010, la 0011 y la 0012 si. Se saltea una y las siguientes no avisan.
--
-- El chequeo esta primero para que el error diga que hacer en vez de nombrar
-- una funcion que nadie recuerda de donde sale.
do $guarda$
begin
  if to_regprocedure('public.es_admin_hma()') is null then
    raise exception
      'Falta es_admin_hma(): corre antes 0009_seguridad_panel.sql y despues esta.';
  end if;
end
$guarda$;


-- Que el panel pueda avisar "esto lo guardaste y todavia no esta en la web".
-- Ejecutar despues de 0009_seguridad_panel.sql y 0012_cupo_de_planos.sql.
--
-- El problema que resuelve: guardar y publicar son dos pasos distintos, y no
-- hay nada que lo recuerde. Alguien edita una bajada un martes, cierra el
-- panel, y el cambio se queda en la base hasta que alguien vuelve a apretar
-- "Publicar cambios". Desde afuera parece que el panel no funciona.
--
-- Para avisarlo hacen falta dos cosas que la base todavia no tenia: saber
-- cuando se reconstruyo el sitio por ultima vez, y saber que se toco desde
-- entonces.

-- ---------------------------------------------------------------------------
-- Cuando se reconstruyo el sitio
-- ---------------------------------------------------------------------------

-- Una fila por build terminado. La escribe el ultimo paso de docs/panel_build.py
-- -no el boton del panel- y esa diferencia importa: si el build falla a la
-- mitad no se anota nada, y el panel sigue avisando que hay cambios sin
-- publicar, que es la verdad. Anotarlo al apretar el boton diria que se
-- publico algo que quizas nunca llego a salir.
create table if not exists publicaciones (
  id           uuid primary key default gen_random_uuid(),
  publicada_en timestamptz not null default now(),
  -- De donde salio el build: 'panel', 'git' o lo que informe Vercel. Sirve
  -- para entender un historial raro, no para decidir nada.
  origen       text
);

create index if not exists publicaciones_fecha_idx
  on publicaciones (publicada_en desc);

alter table publicaciones enable row level security;

-- Nadie sin sesion necesita esto: es informacion del panel.
drop policy if exists "publicaciones: solo administrador" on publicaciones;
create policy "publicaciones: solo administrador" on publicaciones for all to authenticated
  using (es_admin_hma()) with check (es_admin_hma());

-- Punto de partida. Sin esta fila el panel no tendria contra que comparar y
-- listaria las 62 obras como pendientes la primera vez que alguien entre.
insert into publicaciones (origen) values ('migracion 0013');


-- ---------------------------------------------------------------------------
-- Que se toco
-- ---------------------------------------------------------------------------

-- obras.updated_at ya existia y lo mantiene un trigger desde 0001. Lo que
-- falta es poder decirlo en castellano: "updated_at cambio" no le sirve a
-- nadie, "cambiaste la bajada" si. Lo escribe el panel al guardar, con los
-- nombres de los campos que efectivamente cambiaron.
alter table obras add column if not exists ultimo_cambio text;

comment on column obras.ultimo_cambio is
  'Frase corta para el aviso del panel: "la bajada y el año". La escribe el '
  'panel al guardar. Puede quedar en null: el aviso funciona igual, solo que '
  'sin el detalle.';


-- Las fotos y los planos viven en otra tabla, asi que moverlos o cambiar la
-- portada no tocaba obras.updated_at y el aviso no los veria. Este trigger
-- hace que cualquier cambio en la galeria marque a su obra, y de paso deja
-- dicho cual de las dos galerias fue.
--
-- Incluye el borrado, que es el caso que ninguna marca de tiempo propia de la
-- fila podria detectar: la fila ya no esta para tener fecha.
create or replace function marcar_obra_por_imagen()
returns trigger language plpgsql
as $$
declare
  fila     obra_imagenes%rowtype;
  etiqueta text;
begin
  -- En un DELETE la fila viene en old y new esta vacio; al reves en un INSERT.
  if tg_op = 'DELETE' then
    fila := old;
  else
    fila := new;
  end if;
  etiqueta := case when fila.tipo = 'plano' then 'los planos' else 'las fotos' end;

  -- Solo la marca de tiempo y la frase. No se toca ningun otro campo para no
  -- disparar el trigger que limita las destacadas del home.
  update obras
     set updated_at = now(),
         ultimo_cambio = etiqueta
   where id = fila.obra_id;

  return null;   -- after trigger: lo que devuelve no se usa
end;
$$;

drop trigger if exists obra_imagenes_marcan_obra on obra_imagenes;
create trigger obra_imagenes_marcan_obra
  after insert or update or delete on obra_imagenes
  for each row execute function marcar_obra_por_imagen();
