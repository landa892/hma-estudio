-- Bucket de las fotos de obra.
--
-- Lectura publica porque las imagenes se sirven directo al visitante; escribir
-- solo con sesion. Las politicas de storage viven en storage.objects, aparte
-- de las de las tablas.

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'obras',
  'obras',
  true,
  -- 5 MB. El panel convierte a WebP y redimensiona antes de subir, asi que un
  -- archivo que llegue mas grande que esto es una foto que se salteo ese paso.
  5242880,
  array['image/webp', 'image/jpeg', 'image/png']
)
on conflict (id) do nothing;

create policy "obras: lectura publica"
  on storage.objects for select
  to anon, authenticated
  using (bucket_id = 'obras');

create policy "obras: sube quien tiene sesion"
  on storage.objects for insert
  to authenticated
  with check (bucket_id = 'obras');

create policy "obras: reemplaza quien tiene sesion"
  on storage.objects for update
  to authenticated
  using (bucket_id = 'obras');

-- Borrar el archivo es responsabilidad del panel: el "on delete cascade" de
-- obra_imagenes limpia las filas pero no toca el bucket, asi que sin esto los
-- archivos quedan huerfanos ocupando espacio.
create policy "obras: borra quien tiene sesion"
  on storage.objects for delete
  to authenticated
  using (bucket_id = 'obras');
