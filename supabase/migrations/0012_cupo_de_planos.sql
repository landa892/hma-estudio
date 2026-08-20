-- Sube el cupo de planos de 15 a 40.
--
-- 0011 le dio a los planos su propio cupo, pero copiando el numero de las
-- fotos. Ese 15 es una decision comercial sobre las fotos: el estudio cotizo
-- quince por obra y seleccion_inicial ya las corta ahi. Los planos no se
-- cotizan ni se suben a mano: salen del Drive, son documentacion tecnica, y
-- son los que son. Tostado tiene 35, la Bienal de Venecia y Osten FOA 21,
-- Hyatt Ziva 18, Accor y Goodsten 17.
--
-- Con el tope en 15 el build se caia al sembrar el plano dieciseis de Tostado,
-- y la alternativa -sembrar solo quince- le habria escondido veinte planos al
-- panel y, en cuanto esa ficha se reescribiera, tambien al sitio.
--
-- Cuarenta deja lugar de sobra sobre las 35 de hoy y sigue siendo un tope: la
-- tabla no queda sin limite. Las fotos no se tocan, siguen en quince.
create or replace function limitar_imagenes_por_obra()
returns trigger
language plpgsql
as $$
declare
  cuantas int;
  tope int;
begin
  tope := case new.tipo when 'plano' then 40 else 15 end;

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
