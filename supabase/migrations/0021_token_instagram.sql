-- Guarda el token de Instagram para poder refrescarlo solo.
--
-- El token de Instagram dura 60 dias y no tiene periodo de gracia: si nadie lo
-- refresca antes de vencer, muere y hay que volver a autorizar la app a mano
-- desde Meta for Developers. Eso ya paso una vez y dejo el Inicio mostrando la
-- publicacion de respaldo durante semanas.
--
-- Hasta ahora el token vivia en la variable INSTAGRAM_ACCESS_TOKEN de Vercel, y
-- una variable de entorno no se puede reescribir desde el propio sitio. Por eso
-- va a la base: asi /api/instagram-refresh lo renueva cada noche cuando le
-- queda poco y lo deja guardado, sin que nadie toque nada.
--
-- Ejecutar despues de 0009_seguridad_panel.sql.

do $guarda$
begin
  if to_regprocedure('public.es_admin_hma()') is null then
    raise exception
      'Falta es_admin_hma(): corre antes 0009_seguridad_panel.sql y despues esta.';
  end if;
end
$guarda$;

create table if not exists credenciales (
  clave          text primary key,
  valor          text not null,
  vence_en       timestamptz,
  refrescado_en  timestamptz not null default now(),
  nota           text
);

-- RLS prendido y SIN ninguna policy, a proposito. Esta tabla guarda un token
-- que da acceso de lectura a la cuenta de Instagram del estudio: no la puede
-- ver el navegador ni el panel. Sin policies, ni la clave publicable ni un
-- usuario con sesion llegan a una sola fila; solo entra la clave de servicio,
-- que saltea el RLS y vive unicamente en las variables del servidor.
--
-- Es la diferencia con `textos`, que tiene lectura publica porque su contenido
-- se publica igual en el sitio. Guardar el token ahi lo dejaria a la vista de
-- cualquiera que mire la API.
alter table credenciales enable row level security;

comment on table credenciales is
  'Credenciales que el sitio refresca solo. Sin policies: unicamente service_role.';
comment on column credenciales.vence_en is
  'Cuando deja de servir el valor guardado. Para Instagram, 60 dias desde el ultimo refresco.';
comment on column credenciales.refrescado_en is
  'Ultima vez que se renovo. Instagram exige que el token tenga 24 horas antes de poder refrescarlo.';
