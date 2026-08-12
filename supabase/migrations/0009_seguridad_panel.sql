-- Cierra el panel al unico correo administrador y limita el home a 3 obras.
-- Ejecutar despues de 0008_memorias_ingles.sql.

create or replace function es_admin_hma()
returns boolean language sql stable
as $$
  select lower(coalesce(auth.jwt() ->> 'email', '')) = 'hitzig.militello@gmail.com';
$$;

drop policy if exists "obras: todo con sesion" on obras;
drop policy if exists "imagenes: todo con sesion" on obra_imagenes;
drop policy if exists "textos: todo con sesion" on textos;

create policy "obras: solo administrador" on obras for all to authenticated
  using (es_admin_hma()) with check (es_admin_hma());
create policy "imagenes: solo administrador" on obra_imagenes for all to authenticated
  using (es_admin_hma()) with check (es_admin_hma());
create policy "textos: solo administrador" on textos for all to authenticated
  using (es_admin_hma()) with check (es_admin_hma());

drop policy if exists "obras: sube quien tiene sesion" on storage.objects;
drop policy if exists "obras: reemplaza quien tiene sesion" on storage.objects;
drop policy if exists "obras: borra quien tiene sesion" on storage.objects;

create policy "obras: sube solo administrador" on storage.objects for insert to authenticated
  with check (bucket_id = 'obras' and es_admin_hma());
create policy "obras: reemplaza solo administrador" on storage.objects for update to authenticated
  using (bucket_id = 'obras' and es_admin_hma())
  with check (bucket_id = 'obras' and es_admin_hma());
create policy "obras: borra solo administrador" on storage.objects for delete to authenticated
  using (bucket_id = 'obras' and es_admin_hma());

create or replace function limitar_destacadas_home()
returns trigger language plpgsql
as $$
declare cuantas int;
begin
  if new.destacada and new.publicada then
    select count(*) into cuantas from obras
     where destacada and publicada and id <> new.id;
    if cuantas >= 3 then
      raise exception 'El home ya tiene 3 obras destacadas.';
    end if;
  end if;
  return new;
end;
$$;

drop trigger if exists obras_tope_destacadas on obras;
create trigger obras_tope_destacadas
  before insert or update of destacada, publicada on obras
  for each row execute function limitar_destacadas_home();
