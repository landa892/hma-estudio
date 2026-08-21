-- Alta de Banco Supervielle, la obra 90 del Drive.
--
-- Se corre a mano en el editor SQL porque la clave con la que trabajo es de
-- solo lectura. Es lo unico de esta obra que no puede hacer el build: las
-- fotos, los planos, la caratula y el catalogo ya estan en el repositorio.
--
-- Entra como BORRADOR a proposito. Tiene memoria en los dos idiomas, seis
-- fotos y cuatro planos, pero en el Drive no hay ficha tecnica, asi que
-- superficie, ubicacion, comitente y tipologia van vacias. Cuando el estudio
-- las mande se completan desde el panel y se publica con la casilla, sin SQL.
--
-- El año sale de la carpeta del Drive: 90-Supervielle cuelga de "2026", el
-- mismo criterio con el que se confirmo el 2023 de Roket.

insert into obras (slug)
values ('banco-supervielle')
on conflict (slug) do nothing;

update obras set
  titulo       = 'Banco Supervielle',
  anio         = '2026',
  categoria    = 'oficinas',
  pais         = 'Argentina',
  estado       = 'en_proyecto',
  bajada       = 'Las nuevas oficinas del banco, en lamas de madera y curvas cálidas.',
  superficie   = null,
  ubicacion    = null,
  comitente    = null,
  tipologia    = null,
  equipo       = '{}',
  destacada    = false,
  publicada    = false,
  memoria      = '130 años de solidez traducidos en arquitectura. Las nuevas oficinas de Supervielle equilibran tradición y transformación digital en un lenguaje visual cohesivo.

La madera nobilísima en lamas verticales cubre divisiones interiores y revestimientos, comunicando permanencia y calidez. No es decorativa: estructura el espacio, organiza flujos, genera privacidad visual sin clausurar.

Curvaturas sinuosas en cielo raso expresan modernidad, movimiento, transformación digital. Integran iluminación lineal cálida que orquesta la experiencia del usuario sin fatiga visual.

Paleta identitaria de terra cotta, cuero caramelo y marrones cálidos humaniza cada zona. Sofás en cuero, sillas terra cotta, pantallas digitales integradas en muros de madera. La tecnología nunca domina; siempre está contextualizada.

Espacios diferenciados: salas concentradas, lounges circulares, circulaciones como experiencia. Luz natural + artificial en 3000K generan calidez. Plantas humanizadas. Cada zona respira el mismo idioma arquitectónico: sobriedad elegante.

Resultado: no es showroom de lujo ni austero banco tradicional. Es demostración silenciosa de que solidez y modernidad, tiempo largo y cambio rápido, coexisten naturalmente. Arquitectura de confianza.',
  memoria_en   = '130 years of solidity translated into architecture. Supervielle’s new offices balance tradition and digital transformation in a cohesive visual language.

Noble wood in vertical slats covers interior partitions and claddings, conveying permanence and warmth. It is not decorative: it structures the space, organises flows and creates visual privacy without closing it off.

Sinuous curves in the ceiling express modernity, movement and digital transformation. They integrate warm linear lighting that orchestrates the user experience without visual fatigue.

An identity palette of terracotta, caramel leather and warm browns humanises every area. Leather sofas, terracotta chairs, digital screens integrated into wooden walls. Technology never dominates; it is always contextualised.

Differentiated spaces: focused meeting rooms, circular lounges, circulations as experience. Natural and artificial light at 3000K create warmth. Plants humanise. Every area breathes the same architectural language: elegant restraint.

The result is neither a luxury showroom nor an austere traditional bank. It is a quiet demonstration that solidity and modernity, long time and fast change, coexist naturally. Architecture of trust.'
where slug = 'banco-supervielle';

select slug, titulo, anio, categoria, publicada,
       length(memoria) as memoria, length(memoria_en) as memoria_en
  from obras where slug = 'banco-supervielle';
