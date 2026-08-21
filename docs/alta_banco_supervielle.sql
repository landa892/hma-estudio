-- Alta de Banco Supervielle, la obra 90 del Drive.
--
-- Se corre a mano en el editor SQL porque la clave con la que trabajo es de
-- solo lectura. Es lo unico de esta obra que no puede hacer el build: las
-- fotos, los planos, la caratula y el catalogo ya estan en el repositorio.
--
-- Entra como BORRADOR a proposito. Tiene memoria en los dos idiomas, seis
-- fotos, cuatro planos y la ficha tecnica que el estudio agrego al Drive.
--
-- El anio sale de la carpeta del Drive: 90-Supervielle cuelga de "2026", el
-- mismo criterio con el que se confirmo el 2023 de Roket.
--
-- Va todo en un insert y no en insert + update. El primer intento hacia
-- "insert into obras (slug)" y despues el update, y la base lo rechazo:
-- obras.titulo es not null y no tiene default, asi que la fila con el slug
-- solo no puede existir ni por un instante.
--
-- Correrlo dos veces no duplica ni rompe nada: vuelve a dejar la fila igual.

insert into obras (
  slug,
  titulo,
  anio,
  categoria,
  pais,
  estado,
  bajada,
  superficie,
  ubicacion,
  comitente,
  tipologia,
  equipo,
  destacada,
  publicada,
  memoria,
  memoria_en
) values (
  'banco-supervielle',
  'Banco Supervielle',
  '2026',
  'oficinas',
  'Argentina',
  'en_proyecto',
  'Las nuevas oficinas del banco, en lamas de madera y curvas cálidas.',
  '550 m²',
  'S. Fernández 198 esq. Laprida, San Isidro, Provincia de Buenos Aires',
  null,
  'Banco + workplace',
  array['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
        'Arq. Pilar Velasco', 'Arq. Julieta Leibovich'],
  false,
  false,
  '130 años de solidez traducidos en arquitectura. Las nuevas oficinas de Supervielle equilibran tradición y transformación digital en un lenguaje visual cohesivo.

La madera nobilísima en lamas verticales cubre divisiones interiores y revestimientos, comunicando permanencia y calidez. No es decorativa: estructura el espacio, organiza flujos, genera privacidad visual sin clausurar.

Curvaturas sinuosas en cielo raso expresan modernidad, movimiento, transformación digital. Integran iluminación lineal cálida que orquesta la experiencia del usuario sin fatiga visual.

Paleta identitaria de terra cotta, cuero caramelo y marrones cálidos humaniza cada zona. Sofás en cuero, sillas terra cotta, pantallas digitales integradas en muros de madera. La tecnología nunca domina; siempre está contextualizada.

Espacios diferenciados: salas concentradas, lounges circulares, circulaciones como experiencia. Luz natural + artificial en 3000K generan calidez. Plantas humanizadas. Cada zona respira el mismo idioma arquitectónico: sobriedad elegante.

Resultado: no es showroom de lujo ni austero banco tradicional. Es demostración silenciosa de que solidez y modernidad, tiempo largo y cambio rápido, coexisten naturalmente. Arquitectura de confianza.',
  '130 years of solidity translated into architecture. Supervielle’s new offices balance tradition and digital transformation in a cohesive visual language.

Noble wood in vertical slats covers interior partitions and claddings, conveying permanence and warmth. It is not decorative: it structures the space, organises flows and creates visual privacy without closing it off.

Sinuous curves in the ceiling express modernity, movement and digital transformation. They integrate warm linear lighting that orchestrates the user experience without visual fatigue.

An identity palette of terracotta, caramel leather and warm browns humanises every area. Leather sofas, terracotta chairs, digital screens integrated into wooden walls. Technology never dominates; it is always contextualised.

Differentiated spaces: focused meeting rooms, circular lounges, circulations as experience. Natural and artificial light at 3000K create warmth. Plants humanise. Every area breathes the same architectural language: elegant restraint.

The result is neither a luxury showroom nor an austere traditional bank. It is a quiet demonstration that solidity and modernity, long time and fast change, coexist naturally. Architecture of trust.'
)
on conflict (slug) do update set
  titulo       = excluded.titulo,
  anio         = excluded.anio,
  categoria    = excluded.categoria,
  pais         = excluded.pais,
  estado       = excluded.estado,
  bajada       = excluded.bajada,
  superficie   = excluded.superficie,
  ubicacion    = excluded.ubicacion,
  comitente    = excluded.comitente,
  tipologia    = excluded.tipologia,
  equipo       = excluded.equipo,
  destacada    = excluded.destacada,
  publicada    = excluded.publicada,
  memoria      = excluded.memoria,
  memoria_en   = excluded.memoria_en;

select slug, titulo, anio, categoria, publicada,
       length(memoria) as memoria, length(memoria_en) as memoria_en
  from obras where slug = 'banco-supervielle';
