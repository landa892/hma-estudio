-- Esquema del panel de autogestion de HMA.
--
-- El sitio publico es estatico: estas tablas son la fuente de la que despues
-- se generan las paginas. Por eso el esquema no guarda solo lo que se cotizo
-- editar, sino todo lo que la pagina de una obra ya muestra hoy: si un campo
-- no esta aca, al regenerar el sitio ese dato desaparece.
--
-- Se corre con la CLI de Supabase (supabase db push) y no a mano desde el
-- dashboard: el esquema tiene que quedar versionado en el repo para poder
-- rehacerlo en otra cuenta cuando el proyecto se transfiera al estudio.

-- ---------------------------------------------------------------------------
-- Tipos
-- ---------------------------------------------------------------------------

-- Los tres estados que pidio el cliente. Como enum y no como text: asi la
-- base rechaza un valor mal escrito en vez de dejar una obra sin filtrar.
create type obra_estado as enum ('en_proyecto', 'en_progreso', 'concluida');

-- Las seis categorias con las que hoy filtra el listado del sitio. Si se
-- suma una, va aca con "alter type ... add value" en una migracion nueva.
create type obra_categoria as enum (
  'gastronomico', 'hoteleria', 'comercial', 'oficinas', 'residencial', 'cultural'
);


-- ---------------------------------------------------------------------------
-- Obras
-- ---------------------------------------------------------------------------

create table obras (
  id          uuid primary key default gen_random_uuid(),

  -- El slug es la url publica de la obra (/proyectos/<slug>/). No se deriva
  -- del titulo en la base a proposito: cambiar un titulo no deberia romper un
  -- link que ya esta compartido o indexado.
  slug        text not null unique,
  titulo      text not null,

  -- --- lo que se cotizo editar ---
  ubicacion   text,
  anio        text,          -- text y no int: hay obras con "2012-2013"
  superficie  text,          -- viene con unidad y a veces con dos medidas
  comitente   text,
  tipologia   text,          -- lo que la ficha muestra como "Tipo"
  memoria     text,
  estado      obra_estado not null default 'en_proyecto',
  destacada   boolean not null default false,
  publicada   boolean not null default false,

  -- --- lo que el sitio ya muestra y no puede perderse ---
  -- Sin categoria los filtros del listado quedan vacios.
  categoria   obra_categoria,
  pais        text,
  -- Frase corta de la tarjeta, distinta de la memoria.
  bajada      text,
  -- Los nombres del equipo, uno por elemento, en el orden de la ficha.
  equipo      text[] not null default '{}',
  -- El estudio escribe la memoria en los dos idiomas y el sitio tiene espejo
  -- completo en ingles. Sin esto, editar en castellano deja la version
  -- inglesa desactualizada sin aviso.
  memoria_en  text,

  -- Orden manual del listado. El sitio ordena por año de forma descendente,
  -- pero hay obras sin año y empates que alguien tiene que desempatar.
  orden       int,

  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

comment on column obras.anio is
  'Texto libre: hay obras con rango ("2012-2013") y alguna todavia sin año.';

create index obras_publicadas_idx on obras (publicada, orden);
create index obras_categoria_idx on obras (categoria);


-- ---------------------------------------------------------------------------
-- Imagenes de cada obra
-- ---------------------------------------------------------------------------

create table obra_imagenes (
  id           uuid primary key default gen_random_uuid(),
  obra_id      uuid not null references obras (id) on delete cascade,

  -- Ruta dentro del bucket, no url completa: si el proyecto se transfiere o
  -- cambia de dominio, las urls se recomponen y las filas siguen sirviendo.
  storage_path text not null,
  alt          text,
  orden        int not null default 0,
  es_portada   boolean not null default false,

  -- Se guardan al subir para poder escribir width y height en el <img>. Sin
  -- eso la pagina salta mientras cargan las fotos.
  ancho        int,
  alto         int,

  created_at   timestamptz not null default now()
);

create index obra_imagenes_obra_idx on obra_imagenes (obra_id, orden);

-- Una sola portada por obra, garantizado por la base y no por la pantalla.
create unique index obra_imagenes_una_portada_idx
  on obra_imagenes (obra_id)
  where es_portada;


-- ---------------------------------------------------------------------------
-- Textos de las secciones fijas
-- ---------------------------------------------------------------------------

-- Home, estudio y contacto. Cada texto se identifica con una clave estable
-- que usa el generador; el panel solo edita el contenido, no crea claves.
create table textos (
  clave      text primary key,
  seccion    text not null,          -- home | estudio | contacto
  rotulo     text not null,          -- como se llama el campo en el panel
  es         text,
  en         text,
  -- Un parrafo y un titular no se editan igual.
  multilinea boolean not null default true,
  orden      int not null default 0,
  updated_at timestamptz not null default now()
);

create index textos_seccion_idx on textos (seccion, orden);


-- ---------------------------------------------------------------------------
-- updated_at
-- ---------------------------------------------------------------------------

create or replace function tocar_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

create trigger obras_updated_at
  before update on obras
  for each row execute function tocar_updated_at();

create trigger textos_updated_at
  before update on textos
  for each row execute function tocar_updated_at();


-- ---------------------------------------------------------------------------
-- Tope de imagenes por obra
-- ---------------------------------------------------------------------------

-- El cliente cotizo hasta 15 imagenes por obra. Se valida tambien aca y no
-- solo en el panel: la pantalla se puede saltear llamando a la API con la
-- clave anon.
--
-- OJO con la importacion de lo que ya existe: 37 de las 61 obras del sitio
-- tienen mas de 15 fotos y Osten Casa FOA tiene 103. Si se importan tal cual,
-- este trigger las rechaza. Hay que decidir antes si la importacion recorta a
-- 15 o si el tope solo corre para las obras nuevas.
create or replace function limitar_imagenes_por_obra()
returns trigger
language plpgsql
as $$
declare
  cuantas int;
begin
  select count(*) into cuantas
    from obra_imagenes
   where obra_id = new.obra_id;

  if cuantas >= 15 then
    raise exception
      'La obra ya tiene 15 imagenes, que es el maximo. Borra una antes de subir otra.';
  end if;

  return new;
end;
$$;

create trigger obra_imagenes_tope
  before insert on obra_imagenes
  for each row execute function limitar_imagenes_por_obra();


-- ---------------------------------------------------------------------------
-- Seguridad
-- ---------------------------------------------------------------------------

-- Sin RLS, cualquiera que abra la consola del navegador puede leer la clave
-- anon del sitio y borrar las obras con ella. Va activado desde el arranque.
alter table obras          enable row level security;
alter table obra_imagenes  enable row level security;
alter table textos         enable row level security;

-- --- lectura publica ---
-- Solo las obras publicadas. Las que estan en borrador no salen ni siquiera
-- consultando la API a mano: es el punto del modo borrador.
create policy "obras publicadas visibles"
  on obras for select
  to anon
  using (publicada);

-- Una imagen se ve si su obra esta publicada.
create policy "imagenes de obras publicadas visibles"
  on obra_imagenes for select
  to anon
  using (exists (
    select 1 from obras
     where obras.id = obra_imagenes.obra_id
       and obras.publicada
  ));

create policy "textos visibles"
  on textos for select
  to anon
  using (true);

-- --- con sesion: todo ---
-- Un solo administrador, asi que alcanza con exigir sesion; no hay roles.
--
-- "for all" incluye el select, y las politicas se suman entre si: por eso el
-- administrador ve tambien sus borradores, que la politica publica esconde.
create policy "obras: todo con sesion"
  on obras for all
  to authenticated
  using (true)
  with check (true);

create policy "imagenes: todo con sesion"
  on obra_imagenes for all
  to authenticated
  using (true)
  with check (true);

create policy "textos: todo con sesion"
  on textos for all
  to authenticated
  using (true)
  with check (true);
