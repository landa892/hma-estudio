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
