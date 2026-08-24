-- Conserva las direcciones anteriores de una obra cuando cambia su slug y
-- lleva Conferencias y clases al panel de Prensa.
-- Ejecutar despues de 0016_intervencion.sql.

do $guarda$
begin
  if to_regprocedure('public.es_admin_hma()') is null then
    raise exception
      'Falta es_admin_hma(): corre antes 0009_seguridad_panel.sql y despues esta.';
  end if;
end
$guarda$;

create table if not exists obra_aliases (
  id         uuid primary key default gen_random_uuid(),
  obra_id    uuid not null references obras(id) on delete cascade,
  slug       text not null unique,
  created_at timestamptz not null default now()
);

create or replace function guardar_slug_anterior()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  if old.slug is distinct from new.slug then
    insert into obra_aliases (obra_id, slug) values (old.id, old.slug)
      on conflict (slug) do update set obra_id = excluded.obra_id;
  end if;
  return new;
end;
$$;

drop trigger if exists obras_guardan_slug_anterior on obras;
create trigger obras_guardan_slug_anterior
  before update of slug on obras
  for each row execute function guardar_slug_anterior();

-- Las dos obras renombradas antes de que existiera el historial.
insert into obra_aliases (obra_id, slug)
select id, 'cerveceria-austral' from obras where slug = 'estancia-austral'
on conflict (slug) do update set obra_id = excluded.obra_id;

insert into obra_aliases (obra_id, slug)
select id, 'indusparquet' from obras where slug = 'bosque'
on conflict (slug) do update set obra_id = excluded.obra_id;

alter table obra_aliases enable row level security;
drop policy if exists "aliases: lectura publica" on obra_aliases;
drop policy if exists "aliases: solo administrador" on obra_aliases;
create policy "aliases: lectura publica" on obra_aliases for select to anon
  using (exists (select 1 from obras where obras.id = obra_id and obras.publicada));
create policy "aliases: solo administrador" on obra_aliases for all to authenticated
  using (es_admin_hma()) with check (es_admin_hma());

create table if not exists prensa_novedades (
  id         uuid primary key default gen_random_uuid(),
  clave      text not null unique,
  rubro      text not null default 'CONFERENCIA',
  titulo     text not null,
  detalle    text,
  anio       text not null,
  link       text,
  orden      int not null default 0,
  publicada  boolean not null default true,
  eliminada  boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists prensa_novedades_updated_at on prensa_novedades;
create trigger prensa_novedades_updated_at
  before update on prensa_novedades
  for each row execute function tocar_updated_at();

alter table prensa_novedades enable row level security;
drop policy if exists "novedades prensa: lectura publica" on prensa_novedades;
drop policy if exists "novedades prensa: solo administrador" on prensa_novedades;
create policy "novedades prensa: lectura publica" on prensa_novedades for select to anon
  using (publicada and not eliminada);
create policy "novedades prensa: solo administrador" on prensa_novedades for all to authenticated
  using (es_admin_hma()) with check (es_admin_hma());

create or replace function prensa_imagen_marca_publicacion()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'DELETE' then
    update prensa_publicaciones set updated_at = now() where id = old.publicacion_id;
    return old;
  end if;
  update prensa_publicaciones set updated_at = now() where id = new.publicacion_id;
  return new;
end;
$$;

drop trigger if exists prensa_imagenes_marcan_publicacion on prensa_imagenes;
create trigger prensa_imagenes_marcan_publicacion
  after insert or update or delete on prensa_imagenes
  for each row execute function prensa_imagen_marca_publicacion();

comment on table obra_aliases is
  'Direcciones anteriores que siguen llevando a la obra despues de renombrarla.';
comment on table prensa_novedades is
  'Conferencias, clases y docencia de Prensa administrables desde el panel.';
