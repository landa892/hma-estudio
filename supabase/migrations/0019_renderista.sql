-- Suma el credito de quien produjo los renders de una obra o proyecto.
-- Ejecutar despues de 0018_cantidad_fotos_cuerpo.sql.

do $guarda$
begin
  if to_regprocedure('public.es_admin_hma()') is null then
    raise exception
      'Falta es_admin_hma(): corre antes 0009_seguridad_panel.sql y despues esta.';
  end if;
end
$guarda$;

alter table obras add column if not exists renderista text;

comment on column obras.renderista is
  'Credito de quien realizo los renders; se publica cuando tiene contenido.';
