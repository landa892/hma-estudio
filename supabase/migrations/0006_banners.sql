-- El rotulo del banner del home.
--
-- El home cierra con tres banners de obra. Hasta ahora la casilla "destacada"
-- del panel se guardaba y no cambiaba nada: no habia con que llenar el banner.
--
-- Mirando los tres banners que ya estan: el titulo del banner es el titulo de la
-- obra y el parrafo es su bajada, palabra por palabra. Lo unico propio del
-- banner es el rotulo de arriba ("Obra recientemente inaugurada"), que no sale
-- de ningun campo. Es el unico que se agrega.
--
-- Va en ingles tambien porque el home tiene espejo completo y el rotulo es texto
-- visible: sin la version inglesa, el banner de /en/ saldria en castellano.
alter table obras add column if not exists banner_rotulo    text;
alter table obras add column if not exists banner_rotulo_en text;

comment on column obras.banner_rotulo is
  'Rotulo chico sobre el titulo, en el banner del home. Solo se usa si la obra
   esta marcada como destacada.';

-- Las tres que estan hoy en el home, con lo que dicen hoy. Sin esto, la primera
-- publicacion desde el panel dejaria los tres banners sin rotulo.
update obras set destacada = true,
                 banner_rotulo = 'Obra recientemente inaugurada',
                 banner_rotulo_en = 'Recently opened'
 where slug = 'indusparquet';

update obras set destacada = true,
                 banner_rotulo = 'Obra recientemente inaugurada',
                 banner_rotulo_en = 'Recently opened'
 where slug = 'parfumerie';

update obras set destacada = true,
                 banner_rotulo = 'Proyecto en proceso',
                 banner_rotulo_en = 'In progress'
 where slug = 'hyatt-ziva';
