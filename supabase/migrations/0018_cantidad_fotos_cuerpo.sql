-- Permite elegir desde Obras cuantas fotos acompanan la memoria descriptiva.
-- Ejecutar despues de 0017_aliases_y_novedades_prensa.sql.

do $guarda$
begin
  if to_regprocedure('public.es_admin_hma()') is null then
    raise exception
      'Falta es_admin_hma(): corre antes 0009_seguridad_panel.sql y despues esta.';
  end if;
end
$guarda$;

alter table obras
  add column if not exists fotos_cuerpo_cantidad smallint;

-- Las fichas heredadas mostraban tres. Si el estudio ya habia cargado una
-- seleccion explicita, mostraban la portada mas toda esa seleccion; se guarda
-- ese mismo total para que aplicar la migracion no cambie ninguna pagina.
update obras o
   set fotos_cuerpo_cantidad = least(30, 1 + (
         select count(*) from obra_imagenes i
          where i.obra_id = o.id and i.tipo = 'cuerpo'))
 where fotos_cuerpo_cantidad is null
   and exists (select 1 from obra_imagenes i
                where i.obra_id = o.id and i.tipo = 'cuerpo');

update obras
   set fotos_cuerpo_cantidad = 3
 where fotos_cuerpo_cantidad is null;

alter table obras
  alter column fotos_cuerpo_cantidad set default 3,
  alter column fotos_cuerpo_cantidad set not null;

alter table obras drop constraint if exists obras_fotos_cuerpo_cantidad_check;
alter table obras add constraint obras_fotos_cuerpo_cantidad_check
  check (fotos_cuerpo_cantidad between 0 and 30);

comment on column obras.fotos_cuerpo_cantidad is
  'Cantidad de fotos visibles junto a la memoria; las restantes no se borran.';
