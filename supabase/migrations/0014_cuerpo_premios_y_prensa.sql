-- Amplia el panel editorial: 30 fotos de galeria, fotos de cuerpo sin tope,
-- premios por obra y publicaciones de prensa administrables.
-- Ejecutar despues de 0013_aviso_de_cambios.sql.

do $guarda$
begin
  if to_regprocedure('public.es_admin_hma()') is null then
    raise exception
      'Falta es_admin_hma(): corre antes 0009_seguridad_panel.sql y despues esta.';
  end if;
end
$guarda$;

alter table obras add column if not exists premios text;

alter table obra_imagenes drop constraint if exists obra_imagenes_tipo_check;
alter table obra_imagenes add constraint obra_imagenes_tipo_check
  check (tipo in ('foto', 'cuerpo', 'plano'));

alter table obra_imagenes drop constraint if exists obra_imagenes_portada_es_foto;
alter table obra_imagenes add constraint obra_imagenes_portada_es_foto
  check (not (es_portada and tipo <> 'foto'));

create or replace function limitar_imagenes_por_obra()
returns trigger language plpgsql as $$
declare
  cuantas int;
  tope int;
begin
  -- Las fotos del cuerpo son las que necesita el relato y no llevan cupo.
  if new.tipo = 'cuerpo' then return new; end if;
  tope := case new.tipo when 'plano' then 40 else 30 end;
  select count(*) into cuantas from obra_imagenes
   where obra_id = new.obra_id and tipo = new.tipo;
  if cuantas >= tope then
    raise exception
      'La obra ya tiene % %, que es el maximo. Borra una antes de subir otra.',
      tope, case new.tipo when 'plano' then 'planos' else 'imagenes' end;
  end if;
  return new;
end;
$$;

create table if not exists prensa_publicaciones (
  id           uuid primary key default gen_random_uuid(),
  slug         text not null unique,
  titulo       text not null,
  medio        text not null,
  pais         text,
  fecha        text,
  obra         text,
  link         text,
  storage_path text,
  orden        int not null default 0,
  publicada    boolean not null default true,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

create table if not exists prensa_imagenes (
  id             uuid primary key default gen_random_uuid(),
  publicacion_id uuid not null references prensa_publicaciones(id) on delete cascade,
  storage_path   text not null,
  alt            text,
  orden          int not null default 0,
  ancho          int,
  alto           int,
  created_at     timestamptz not null default now()
);

create index if not exists prensa_imagenes_publicacion_orden
  on prensa_imagenes(publicacion_id, orden);

drop trigger if exists prensa_publicaciones_updated_at on prensa_publicaciones;
create trigger prensa_publicaciones_updated_at
  before update on prensa_publicaciones
  for each row execute function tocar_updated_at();

alter table prensa_publicaciones enable row level security;
alter table prensa_imagenes enable row level security;
drop policy if exists "prensa: lectura publica" on prensa_publicaciones;
drop policy if exists "prensa: solo administrador" on prensa_publicaciones;
create policy "prensa: lectura publica" on prensa_publicaciones for select to anon
  using (publicada);
create policy "prensa: solo administrador" on prensa_publicaciones for all to authenticated
  using (es_admin_hma()) with check (es_admin_hma());

drop policy if exists "prensa imagenes: lectura publica" on prensa_imagenes;
drop policy if exists "prensa imagenes: solo administrador" on prensa_imagenes;
create policy "prensa imagenes: lectura publica" on prensa_imagenes for select to anon
  using (exists (
    select 1 from prensa_publicaciones p
    where p.id = publicacion_id and p.publicada
  ));
create policy "prensa imagenes: solo administrador" on prensa_imagenes for all to authenticated
  using (es_admin_hma()) with check (es_admin_hma());

comment on table prensa_publicaciones is
  'Las nueve publicaciones visuales de /prensa, editables desde el panel.';
comment on table prensa_imagenes is
  'Escaneos y fotos internas de cada publicacion de prensa, en orden editorial.';
