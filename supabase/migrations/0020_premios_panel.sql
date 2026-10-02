-- Premios independientes administrables desde el panel.
-- Se mantienen separados de obras.premios: ese campo sigue siendo el resumen
-- que aparece dentro de la ficha de cada obra.

do $guarda$
begin
  if to_regprocedure('public.es_admin_hma()') is null then
    raise exception
      'Falta es_admin_hma(): corre antes 0009_seguridad_panel.sql y despues esta.';
  end if;
end
$guarda$;

create table if not exists premios_panel (
  id           uuid primary key default gen_random_uuid(),
  anio         int not null check (anio between 1900 and 2100),
  nombre       text not null check (length(trim(nombre)) between 2 and 180),
  resultado    text,
  ciudad       text,
  descripcion  text,
  enlace       text,
  obra_slug    text,
  logo         text,
  orden        int not null default 0 check (orden between 0 and 9999),
  publicada    boolean not null default false,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

create index if not exists premios_panel_orden
  on premios_panel(anio desc, orden asc, created_at asc);

drop trigger if exists premios_panel_updated_at on premios_panel;
create trigger premios_panel_updated_at
  before update on premios_panel
  for each row execute function tocar_updated_at();

alter table premios_panel enable row level security;
drop policy if exists "premios panel: lectura publica" on premios_panel;
drop policy if exists "premios panel: solo administrador" on premios_panel;
create policy "premios panel: lectura publica" on premios_panel for select to anon
  using (publicada);
create policy "premios panel: solo administrador" on premios_panel for all to authenticated
  using (es_admin_hma()) with check (es_admin_hma());

comment on table premios_panel is
  'Premios nuevos cargados desde el panel; se suman a la pagina general de premios.';
