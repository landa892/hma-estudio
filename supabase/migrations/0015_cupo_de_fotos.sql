-- Corrige el cupo real de la galeria de 15 a 30 fotos.
--
-- El panel ya muestra y acepta 30, pero algunas bases conservan la funcion de
-- 0012 porque las migraciones se aplican a mano. En ese caso la foto 16 falla
-- aunque la pantalla anuncie otro limite. Esta migracion es independiente de
-- las tablas editoriales de 0014 para poder corregir ese desfasaje sola.
create or replace function limitar_imagenes_por_obra()
returns trigger
language plpgsql
as $$
declare
  cuantas int;
  tope int;
begin
  -- Las fotos del cuerpo pertenecen al relato y no consumen cupo de galeria.
  if new.tipo = 'cuerpo' then
    return new;
  end if;

  tope := case new.tipo when 'plano' then 40 else 30 end;

  select count(*) into cuantas
    from obra_imagenes
   where obra_id = new.obra_id
     and tipo = new.tipo;

  if cuantas >= tope then
    raise exception
      'La obra ya tiene % %, que es el maximo. Borra una antes de subir otra.',
      tope,
      case new.tipo when 'plano' then 'planos' else 'imagenes' end;
  end if;

  return new;
end;
$$;
