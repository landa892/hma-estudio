-- Alta de Comedor Diario.
--
-- La obra estaba completa en el Drive -once fotos, cuatro planos, caratula y
-- ficha tecnica- y no figuraba en el sitio. Las fotos, la portada y los planos
-- ya estan en el repositorio; lo unico que falta es la fila en la base, que es
-- de donde el build saca los datos de cada obra.
--
-- Los datos salen de "Comedor Diario-ficha tecnica.doc", en su carpeta
-- 02 - Textos.
--
-- Va SIN memoria descriptiva: en el Drive no hay. La ficha se publica igual
-- -el sitio contempla una obra sin memoria- pero conviene pedirsela al estudio.
--
-- El orden 38 la deja entre las de 2019; de todos modos el paso obras_orden
-- del build reordena por ano, asi que se acomoda sola.

insert into obras (
  slug, titulo, bajada, categoria, tipologia, estado,
  anio, superficie, ubicacion, pais, equipo, fotografia,
  publicada, destacada, orden
) values (
  'comedor-diario',
  'Comedor Diario',
  'Restaurante y café de 280 m² sobre la calle Nicaragua, Buenos Aires.',
  'gastronomico',
  'Restaurante y café',
  'concluida',
  '2019',
  '280 m²',
  'Nicaragua 6055, Buenos Aires',
  'Argentina',
  array[
    'Arq. Leonardo Militello',
    'Arq. Fernando Hitzig',
    'Anteproyecto:',
    'Alfredo Doisenbant',
    'Documentación de obra:',
    'Arq. Julieta Setton',
    'Dirección de obra:',
    'Arq. Marcela Bernat'
  ],
  'Federico Kulekdjian',
  true,
  false,
  38
);
