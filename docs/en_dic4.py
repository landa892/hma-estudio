# -*- coding: utf-8 -*-
"""Cuarta capa del diccionario del espejo en ingles.

Junta lo que entro al sitio despues de armar las tres capas anteriores: la
nota del estudio, los sellos de las asociaciones, las cifras de la portada,
los titulares de prensa y los filtros de la grilla de obras.

Tambien corrige el año de fundacion. El sitio decia 2002 y paso a decir
2006; como la clave del diccionario quedo con el año viejo, esas frases
volvian al castellano en el espejo.
"""
import re
import en_dic3
from en_dic import DIC, PASA_EXACTO

# Los medios de prensa se rotulan "Medio — Pais". El pais quedaba en
# castellano, y como el nombre del medio es intraducible la regla generica
# devolvia la cadena entera sin avisar. Con una regla propia, cualquier
# medio que se sume mas adelante ya sale bien.
PAISES = {
    'Reino Unido': 'United Kingdom', 'EE.UU.': 'USA', 'España': 'Spain',
    'México': 'Mexico', 'Italia': 'Italy', 'Alemania': 'Germany',
    'Francia': 'France', 'Países Bajos': 'Netherlands', 'Brasil': 'Brazil',
    'Argentina': 'Argentina', 'India': 'India', 'China': 'China',
    'Emiratos Árabes Unidos': 'United Arab Emirates', 'Chile': 'Chile',
}
PAT_PAIS = re.compile(r'^(.+?) — (%s)$'
                      % '|'.join(re.escape(p) for p in PAISES))

# Nombres propios que viajan igual en los dos idiomas.
PASA_EXACTO.update({
    'IIDA Chicago', 'World Confederation Houston', 'SBID London', 'AACC Miami',
    'Worldcob', 'Manduca Market', 'Antiche Tentazioni', 'Antiche Devoto',
    'Archello', 'ArchDaily', 'Ministerio de Diseño', 'Hausscape, Miami',
    'Archidiaries — India', 'Rethinking the Future — India',
    'Ushuaia', 'Olivos', 'Elyaki', 'Casa Olmo', 'The Birra',
    'Stella Artois Mercat', '7167 Burger',
    'STIR World — India', 'El Cronista — Argentina',
    'World Confederation of Businesses member',
    'Business trust certificate WorldCOB trust seal',
})

DIC.update({
    # El estudio se fundo en 2006, no en 2002.
    'Desde 2006 — Buenos Aires': 'Since 2006 — Buenos Aires',
    'Desde 2006 — obra construida en': 'Since 2006 — built work in',
    'Desde 2006 diseñamos espacios comerciales y residenciales — hoy con obra construida en':
        'Since 2006 we have designed commercial and residential spaces — today with built work in',
    'Equipo, premios y trayectoria desde 2006.':
        'Team, awards and practice since 2006.',

    # Frases que la regla generica dejaba a medio traducir ("See la prensa").
    # Como esa regla devuelve texto en vez de None, no salian en el reporte
    # de faltantes: hay que cubrirlas enteras.
    'ver la obra': 'see the project',
    'Ver la obra': 'See the project',
    'Ver la prensa': 'See the press',
    'Ver las 11 notas': 'See all 11 articles',
    'Ver menos notas': 'See fewer articles',
    'Desde el 2006, más de': 'Since 2006, more than',

    # bloque de la nota del estudio
    # Ojo: en_gen colapsa los espacios antes de buscar, asi que las claves de
    # frases que en el HTML ocupan varias lineas van en una sola linea.
    'Todo se decide acá: el proyecto se dibuja, se discute y se corrige en la misma mesa donde después se resuelve la obra.':
        'Everything is decided here: the project is drawn, discussed and corrected at the same table where the work is later resolved.',
    'Fernando Hitzig y Leonardo Militello, socios fundadores, en el estudio':
        'Fernando Hitzig and Leonardo Militello, founding partners, at the studio',
    'El equipo trabajando sobre un proyecto en el estudio':
        'The team working on a project at the studio',
    'El equipo de Hitzig Militello trabajando en el estudio':
        'The Hitzig Militello team at work in the studio',

    # sellos de asociaciones
    '04 — Miembros de': '04 — Members of',
    'Miembros de the Commercial Interior Design association (IIDA)':
        'Members of the Commercial Interior Design association (IIDA)',
    'Miembros de the Society of British and International Interior Design (SBID)':
        'Members of the Society of British and International Interior Design (SBID)',
    'Miembros de the Argentine American Chamber of Commerce in Florida':
        'Members of the Argentine American Chamber of Commerce in Florida',

    # cifras y bajadas de portada
    'proyectos construidos y proyectados para la industria de la hospitalidad y residencial.':
        'projects built and designed for the hospitality and residential industry.',
    'años de trayectoria creando espacios experienciales.':
        'years of practice creating experiential spaces.',
    'Somos un equipo de arquitectos que trabaja integrando oficios y disciplinas creativas.':
        'We are a team of architects that works by integrating crafts and creative disciplines.',
    'premios y distinciones nacionales e internacionales desde 2008.':
        'national and international awards and distinctions since 2008.',
    'Dezeen, ArchDaily, Wallpaper* y Architectural Digest: más de dos décadas de prensa internacional.':
        'Dezeen, ArchDaily, Wallpaper* and Architectural Digest: more than two decades of international press.',

    # secciones de prensa
    'El estudio afuera': 'The studio abroad',
    'Novedades': 'News',
    'Charlas, clases y conferencias': 'Talks, classes and lectures',
    'Notas que se pueden leer online': 'Articles you can read online',

    # titulares de prensa
    'El secreto mejor guardado de Buenos Aires: el bar oculto':
        "Buenos Aires' best-kept secret: the hidden bar",
    'Factory Food: 7 restaurantes con estética industrial':
        'Factory Food: 7 restaurants with an industrial aesthetic',
    'Un restaurante dentro de una casa histórica de Buenos Aires':
        'A restaurant inside a historic Buenos Aires house',
    'Una ruina urbana para este restaurante de Buenos Aires':
        'An urban ruin for this Buenos Aires restaurant',
    'Un bar en una casa antigua con la sensación de un lugar demolido':
        'A bar in an old house with the feel of a demolished place',
    'Un bar porteño elegido el mejor de América por su diseño':
        'A Buenos Aires bar named the best in the Americas for its design',
    'A757, condominio flexible en Buenos Aires':
        'A757, a flexible condominium in Buenos Aires',

    # medios con su pais
    'Architizer — EE.UU.': 'Architizer — USA',
    'Dezeen — Reino Unido': 'Dezeen — United Kingdom',
    'SBID — Reino Unido': 'SBID — United Kingdom',
    'Floornature — Italia': 'Floornature — Italy',
    'Revista Plot — Argentina': 'Plot Magazine — Argentina',

    # bajadas que quedaban a medio traducir
    'Templo de 600 m² en Palermo, con una fachada de piezas triangulares que filtra la luz.':
        'A 600 m² temple in Palermo, with a facade of triangular pieces that filters the light.',
    'Edificio del Plata — concurso de interiorismo 2024':
        'Edificio del Plata — 2024 interior design competition',

    # obras enlazadas desde la lista de premios
    'Mercado Manduca': 'Mercado Manduca',
    'Dos casas Conde': 'Dos casas Conde',

    # charlas y conferencias
    'Espacio DAR, masterclass de Arquitectura Interior Experiencial, San Miguel de Tucumán · TENDIEZ LAB — "Arquitectura Gastronómica y Hotelera: Negocio, Diseño, Experiencia", Buenos Aires.':
        'Espacio DAR, masterclass on Experiential Interior Architecture, San Miguel de Tucumán · TENDIEZ LAB — "Gastronomic and Hospitality Architecture: Business, Design, Experience", Buenos Aires.',
    'TENDIEZ LAB Mar del Plata (CAPBA 9) · TENDIEZ LAB, Universidad de Palermo · UADE FADI · Mesa redonda HOTELGA 2024, podcast Cerrame la Ocho.':
        'TENDIEZ LAB Mar del Plata (CAPBA 9) · TENDIEZ LAB, Universidad de Palermo · UADE FADI · HOTELGA 2024 round table, Cerrame la Ocho podcast.',

    # --- obras dadas de alta desde el WordPress viejo ---
    # nombres propios
    'Patio de Comidas Abasto': 'Abasto Food Court',
    'El Clásico de Quilmes': 'El Clásico de Quilmes',
    "Lucciano's Olivos": "Lucciano's Olivos",

    # programa
    'Bar': 'Bar',
    'Patio de comidas': 'Food court',
    'Hamburguesería': 'Burger restaurant',
    'Parrilla y bar': 'Grill and bar',
    'Heladería y cafetería': 'Ice cream and coffee shop',
    'Barra': 'Bar counter',
    'Almacén de bebidas': 'Bottle shop',

    # superficies
    '294 m² (Patio Zorzal)': '294 m² (Patio Zorzal)',
    '294 m² (Patio Zorzal) · 1.300 m² (Patio Central)':
        '294 m² (Patio Zorzal) · 1,300 m² (Patio Central)',
    '75 m² cubiertos': '75 m² covered',
    '60 m² planta baja': '60 m² ground floor',
    '60 m² planta baja · 71 m² subsuelo': '60 m² ground floor · 71 m² basement',
    '90 m² planta baja': '90 m² ground floor',
    '38 m² planta baja': '38 m² ground floor',
    '38 m² planta baja · 53 m² primer piso': '38 m² ground floor · 53 m² first floor',
    'Esmeralda 574 , Buenos Aires': 'Esmeralda 574, Buenos Aires',

    # bajadas
    'Los dos patios de comidas del Abasto Shopping, 1.594 m² de reforma integral en Buenos Aires.':
        'Both food courts at Abasto Shopping — a 1,594 m² full refurbishment in Buenos Aires.',
    'Una hamburguesería de 70 m² en Scalabrini Ortiz, Buenos Aires.':
        'A 70 m² burger restaurant on Scalabrini Ortiz, Buenos Aires.',
    'Un bar de 75 m² con patio en el centro de Ushuaia.':
        'A 75 m² bar with a courtyard in central Ushuaia.',
    'Un bar en dos niveles sobre Esmeralda, en el centro de Buenos Aires.':
        'A two-storey bar on Esmeralda, in central Buenos Aires.',
    'Una parrilla japonesa de 57 m² en Palermo, Buenos Aires.':
        'A 57 m² Japanese grill in Palermo, Buenos Aires.',
    'Una heladería y cafetería de 100 m² sobre Libertador, en Olivos.':
        'A 100 m² ice cream and coffee shop on Libertador, in Olivos.',
    'Un bar con patio en el Paseo de la Buena Vista, sobre Libertador.':
        'A bar with a courtyard at Paseo de la Buena Vista, on Libertador.',
    'Una barra de 15 m² para Stella Artois en el Mercat de Villa Crespo.':
        'A 15 m² Stella Artois bar counter at Mercat, Villa Crespo.',
    'Un almacén de bebidas en dos niveles en el centro de Ushuaia.':
        'A two-storey bottle shop in central Ushuaia.',

    # que se premio en cada distincion
    'Diseño arquitectónico en espacios para eventos.':
        'Architectural design for event spaces.',
    '2do puesto en la categoría diseño interior.':
        '2nd place in the interior design category.',
    'Finalista entre 925 candidaturas.':
        'Finalist among 925 entries.',
    '3er puesto en la etapa regional CABA, categoría obra privada de escala media.':
        '3rd place in the CABA regional stage, mid-scale private work category.',
    'Mención especial en excelencia de arquitectura y diseño interior.':
        'Special mention for excellence in architecture and interior design.',
    'Finalista en la categoría Américas.':
        'Finalist in the Americas category.',
    'Ganadores en edificio comercial interior, estructura temporal y paisaje y espacio público.':
        'Winners in commercial interior building, temporary structure, and landscape and public realm.',
    'Seleccionados en la categoría interiorismo.':
        'Selected in the interior design category.',
    'Mención en la categoría restaurante, premio especial exterior de Centroamérica y Sudamérica.':
        'Mention in the restaurant category, special exterior award for Central and South America.',
    'Mejor firma en la especialidad comercial e industrial de diseño interior.':
        'Best firm in the commercial and industrial interior design specialty.',
    'Primer premio del concurso internacional, entre más de 50 estudios de América Latina.':
        'First prize in the international competition, among more than 50 Latin American studios.',
    'Mención en interiorismo de hotelería y en Landmark of the Year.':
        'Mention in hospitality interior design and in Landmark of the Year.',
    'Mención en Landmark of the Year.': 'Mention in Landmark of the Year.',
    'Preseleccionada como mejor bar de América.':
        'Shortlisted as best bar in the Americas.',

    # portada: mitad de novedades y mitad de premios
    'Distinciones': 'Awards',
    'Mención especial · Nueva York': 'Special mention · New York',
    'Ver todas las novedades': 'See all the news',

    # estado del trabajo: construido o todavia en proceso
    'Estado': 'Status',
    'Obra concluida': 'Completed',
    'Proyecto en proceso': 'In progress',
    'Concluida': 'Completed',
    'En proceso': 'In progress',
    'Sala de concierto, night club y restaurante':
        'Concert hall, night club and restaurant',

    # filtros de la grilla de obras
    'Todas': 'All',
    'Obras': 'Built work',
})

_base = en_dic3.traducir


def traducir(t):
    """Igual que la capa anterior, con el rotulo de medios adelantado.

    La regla del pais tiene que correr antes que pasa(), porque "Medio —
    Pais" cumple el patron de nombre propio y salia intacto.
    """
    if t in DIC:
        return DIC[t]
    m = PAT_PAIS.match(t)
    if m:
        return '%s — %s' % (_base(m.group(1)) or m.group(1), PAISES[m.group(2)])
    return _base(t)
