-- Suma a la ficha la disciplina de la intervencion. Es nullable porque el
-- estudio tiene que elegirla: inferirla por categoria confundiria el uso del
-- edificio con el alcance real del trabajo.

do $guarda$
begin
  if to_regprocedure('public.es_admin_hma()') is null then
    raise exception
      'Falta es_admin_hma(): corre antes 0009_seguridad_panel.sql y despues esta.';
  end if;
end
$guarda$;

alter table obras add column if not exists intervencion text;

alter table obras drop constraint if exists obras_intervencion_check;
alter table obras add constraint obras_intervencion_check
  check (intervencion in ('interiorismo', 'arquitectura', 'ambos'));

comment on column obras.intervencion is
  'Alcance publicado antes del estado: interiorismo, arquitectura o ambos.';
