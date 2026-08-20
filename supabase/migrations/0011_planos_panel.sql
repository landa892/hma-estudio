-- Suma los planos a obra_imagenes, para que el panel los administre igual que
-- las fotos. Hasta aca vivian aparte: docs/planos.json + assets/planos/,
-- escritos a mano por drive_sync.py e insertados en el HTML por
-- planos_fichas.py. El panel de edicion no los mostraba porque no estaban en
-- la base.
--
-- La portada nunca es un plano: se agrega el check para que quede garantizado
-- por la base y no solo por la pantalla, igual que la unicidad de portada de
-- 0001_esquema.sql.
alter table obra_imagenes
  add column tipo text not null default 'foto' check (tipo in ('foto', 'plano'));

alter table obra_imagenes
  add constraint obra_imagenes_portada_es_foto
  check (not (es_portada and tipo <> 'foto'));

-- El trigger de 0001_esquema.sql contaba las 15 imagenes de la obra sin mirar
-- el tipo: con los planos sumandose a la misma tabla, subir un plano le sacaba
-- lugar a las fotos y viceversa. El cliente cotizo 15 fotos; los planos llevan
-- su propio cupo de 15, separado.
create or replace function limitar_imagenes_por_obra()
returns trigger
language plpgsql
as $$
declare
  cuantas int;
begin
  select count(*) into cuantas
    from obra_imagenes
   where obra_id = new.obra_id
     and tipo = new.tipo;

  if cuantas >= 15 then
    raise exception
      'La obra ya tiene 15 %, que es el maximo. Borra una antes de subir otra.',
      case new.tipo when 'plano' then 'planos' else 'imagenes' end;
  end if;

  return new;
end;
$$;
