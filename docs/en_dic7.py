# -*- coding: utf-8 -*-
"""Septima capa del diccionario del espejo en ingles.

Cubre el campo Equipo, que entro despues en las 61 fichas y nunca habia
pasado por el traductor, y la obra Ualá II.

Los nombres propios no se traducen, pero el titulo "Arq." si: en una pagina
en ingles queda "Arch.". Como la lista de gente crece con cada obra, va como
regla y no como entrada del diccionario.
"""
import re

import en_dic
import en_dic6
from en_dic import DIC, PASA_EXACTO

# Nombres sueltos de la ficha de Indusparquet y Ualá Gigena: van sin titulo,
# asi que la regla de "Arq." no los alcanza y el traductor los reportaria.
PASA_EXACTO.update({
    'Dolores Gayoso', 'Alfana Nizza', 'Josué Solano', 'Joaquín Medina',
    'Federico Kulekdjian',
    # Nombre de la obra en la barra de premios, desde que el premio del concurso
    # internacional dejo de estar atribuido a Novotel. Es marca, no se traduce.
    'Accor',
    # Los dos premios que se sumaron el 12/08/2026. Son nombres propios.
    'Casa FOA', 'Archello',
    # Los tres Uala quedaron con su nombre definitivo el 19/08/2026: el Word
    # aclara que son obras distintas -las dos de la calle Nicaragua y la del
    # Paseo Gigena-. Son nombres propios, no se traducen.
    'Ualá Gigena', 'Ualá Nicaragua I', 'Ualá Nicaragua II',
    # Obra que se publica el 20/08/2026, desde su carpeta del Drive.
    'Comedor Diario', 'Alfredo Doisenbant', 'Arq. Julieta Setton',
    'Arq. Marcela Bernat',
    # La plataforma italiana y su ciudad, en la fila que se sumo el
    # 19/08/2026. Nombres propios.
    'Archilovers', 'Bari',
})

DIC.update({
    # El cliente usa una misma denominacion bilingue para la seccion en el
    # menu. El ampersand es parte del nombre visible, no una conjuncion a
    # traducir como "and".
    'Prensa & News': 'Press & News',
    'Prensa &amp; News': 'Press &amp; News',

    # --- metadatos SEO de las secciones principales ---
    'Estudio de arquitectura e interiorismo en Buenos Aires | HMA':
        'Architecture and interior design studio in Buenos Aires | HMA',
    'Conocé Hitzig Militello Arquitectos, estudio de arquitectura e interiorismo fundado en Buenos Aires en 2006 por Fernando Hitzig y Leonardo Militello.':
        'Meet Hitzig Militello Architects, an architecture and interior design studio founded in Buenos Aires in 2006 by Fernando Hitzig and Leonardo Militello.',
    'Contacto | Estudio de arquitectura en Buenos Aires | HMA':
        'Contact | Architecture studio in Buenos Aires | HMA',
    'Contactá a Hitzig Militello Arquitectos en Palermo, Buenos Aires, para proyectos de arquitectura, interiorismo, hotelería, gastronomía y oficinas.':
        'Contact Hitzig Militello Architects in Palermo, Buenos Aires, for architecture, interior design, hospitality, restaurant and office projects.',
    'Proyectos de arquitectura e interiorismo | Hitzig Militello':
        'Architecture and interior design projects | Hitzig Militello',
    'Proyectos de arquitectura e interiorismo comercial: hotelería, gastronomía, oficinas y obras residenciales en Argentina y el mundo.':
        'Architecture and commercial interior design projects: hospitality, restaurants, offices and residential work in Argentina and worldwide.',

    # Las dos filas nuevas de la pagina de premios.
    'La cafetería de Osten en la 40ª edición, en Madero Harbour.':
        'The Osten coffee shop at the 40th edition, in Madero Harbour.',
    'Elegida entre lo mejor del año por Archello.':
        'Chosen among the best of the year by Archello.',
    # Ninguno de los dos es un concurso con ganadores: Casa FOA es una muestra y
    # el "Best of" de Archello una seleccion curada. Los rotulos lo dicen asi.
    'Espacio seleccionado': 'Selected space',
    'Seleccionada': 'Selected',
    'Ámsterdam': 'Amsterdam',
    'Restaurante y café de 280 m² sobre la calle Nicaragua, Buenos Aires.':
        'Restaurant and cafe of 280 m² on Nicaragua street, Buenos Aires.',
    'Restaurante y café': 'Restaurant and cafe',
    'Anteproyecto:': 'Schematic design:',
    'Elegida Best Project 2022 por la plataforma italiana.':
        'Chosen as Best Project 2022 by the Italian platform.',
})

DIC.update({
    # --- ajustes de contenido del 14/08/2026 ---
    'Actualidad en LinkedIn': 'Latest on LinkedIn',
    'Indusparquet en Tietê': 'Indusparquet in Tietê',
    'Una entrevista desde la planta de Indusparquet en el estado de São Paulo, en el marco del proyecto que desarrollamos para su flagship de Núñez. El concepto “El Bosque” define la experiencia y la identidad espacial de la tienda.':
        'An interview from the Indusparquet plant in the state of São Paulo, within the project we developed for its Núñez flagship. The “El Bosque” concept defines the store experience and spatial identity.',
    'Entrevista de Hitzig Militello Arquitectos en la planta de Indusparquet en Tietê, Brasil':
        'Hitzig Militello Architects interview at the Indusparquet plant in Tietê, Brazil',
    'Ver LinkedIn': 'View LinkedIn',
    'Ver las publicaciones de Hitzig Militello Arquitectos en LinkedIn':
        'View Hitzig Militello Architects posts on LinkedIn',
    'Proyectos y procesos': 'Projects and processes',
    'Seguinos en LinkedIn para conocer la evolución de nuestras obras, procesos de diseño y novedades del estudio en Argentina y el exterior.':
        'Follow us on LinkedIn for updates on our projects, design process and studio news from Argentina and abroad.',
    'Proyecto hotelero de Hitzig Militello Arquitectos':
        'Hospitality project by Hitzig Militello Architects',
    'El estudio detrás del Movistar Arena': 'The studio behind Movistar Arena',
    'Leonardo Militello y Fernando Hitzig repasan dos décadas de trayectoria, el método de trabajo del estudio y el proceso creativo del espacio VIP gastronómico del Movistar Arena.':
        "Leonardo Militello and Fernando Hitzig revisit two decades of practice, the studio's working method and the creative process behind Movistar Arena's hospitality VIP lounge.",
    'Leer la última nota compartida por Hitzig Militello Arquitectos en LinkedIn':
        'Read the latest article shared by Hitzig Militello Architects on LinkedIn',
    'VIP Lounge del Movistar Arena, proyecto de Hitzig Militello Arquitectos':
        'Movistar Arena VIP Lounge, a project by Hitzig Militello Architects',
    'Ver publicación': 'View post',
    'Ver publicación ↗': 'View post ↗',
    'Concursos': 'Competitions',
    'Ir a LinkedIn': 'Go to LinkedIn',
    'Proyectos construidos en': 'Projects built in',
    'países, con una práctica local y alcance internacional.':
        'countries, combining local practice with international reach.',
    'Ranking Clarín ARQ — Diseñadores de Interior':
        'Clarín ARQ Ranking — Interior Designers',
    'El estudio obtuvo el 2.º puesto en el ranking argentino de diseño interior de 2024.':
        'The studio ranked second in Argentina’s 2024 interior design ranking.',
    'Ranking · 2.º puesto': 'Ranking · 2nd place',
    'El estudio obtuvo el 4.º puesto entre los 25 mejores estudios de arquitectura de Argentina en el ranking de 2025.':
        'The studio ranked 4th among Argentina’s 25 best architecture firms in the 2025 ranking.',
    'El estudio obtuvo el 4.º puesto entre los 30 mejores estudios de arquitectura de Argentina en el ranking de 2024.':
        'The studio ranked 4th among Argentina’s 30 best architecture firms in the 2024 ranking.',
    'Ranking · 4.º puesto': 'Ranking · 4th place',
    'Conferencia': 'Conference',
    'Ciclo de conferencias presenciales DINA — Auditorio Diego de Torres, UCC Córdoba':
        'DINA in-person conference series — Diego de Torres Auditorium, UCC Córdoba',
    'Leonardo Militello, profesor de Interior Creative Architecture en Haus':
        'Leonardo Militello, professor of Interior Creative Architecture at Haus',
    '10.ª TENDIEZ Experiences, Buenos Aires':
        '10th TENDIEZ Experiences, Buenos Aires',
})

DIC.update({
    # El titular de la portada lleva un espacio duro dentro, asi que en el HTML
    # nunca aparece como una frase suelta y el diccionario no lo tenia. Se
    # necesita entero para el panel de autogestion.
    'Creando & construyendo ideas': 'Creating & building ideas',

    # --- correcciones de contenido de la pagina Estudio ---
    'En Hitzig Militello arquitectos realizamos proyectos comerciales de forma local y regional tanto en América Latina, como en Europa, Medio Oriente y EEUU, con especial enfoque en la industria de la hospitalidad. Más de dos décadas de trayectoria creado arquitectura e interiorismos de reconocimiento internacional.':
        'At Hitzig Militello Architects, we deliver commercial projects locally and regionally across Latin America, Europe, the Middle East and the United States, with a particular focus on the hospitality industry. For more than two decades, we have created internationally recognised architecture and interior design.',
    'Conceptualizamos ideas.': 'We conceptualise ideas.',
    'Equipo de Hitzig Militello Arquitectos trabajando en el estudio':
        'Hitzig Militello Architects team working in the studio',
    'Generamos la documentación técnica.': 'We produce the technical documentation.',
    'Creamos el producto arquitectónico.': 'We create the architectural product.',
    'Construimos nuestras ideas.': 'We build our ideas.',

    # --- fotos nuevas de la pagina Estudio ---
    # Reemplazan a la del plano y al fotograma del video: el estudio pidio dos
    # fotos propias en buena resolucion.
    'La planta del estudio HMA en Buenos Aires, con el equipo trabajando':
        'The HMA studio floor in Buenos Aires, with the team at work',
    'Los socios y el equipo de HMA revisando un proyecto en pantalla':
        'HMA’s partners and team reviewing a project on screen',

    # --- rotulos de la ficha ---
    'Equipo': 'Team',
    'Fotografía': 'Photography',
    'Dirección de obra:': 'Site management:',
    'Documentación de obra:': 'Construction documentation:',
    'Project manager:': 'Project manager:',
    'Colaboradores:': 'Collaborators:',
    'Renders:': 'Renders:',

    # --- categorias que faltaban ---
    'Comercial': 'Commercial',
    'Hotelería': 'Hospitality',

    # --- Ualá II ---
    'Ualá II': 'Ualá II',
    'Casa Luna': 'Luna House',
    'Diseño interior de oficinas': 'Office interior design',
    'Segundas oficinas de Ualá en Palermo: 757 m² organizados alrededor de un patio central y jardín vertical.':
        "Ualá's second offices in Palermo: 757 m² organised around a central courtyard and a vertical garden.",
    'Dos áreas de trabajo conectadas por un pasillo y un patio central dentro de un antiguo tinglado de Palermo.':
        'Two work areas linked by a corridor and a central courtyard inside an old Palermo shed.',
    'La recepción da paso a un espacio de trabajo en doble altura organizado por islas.':
        'The reception opens onto a double-height workspace organised in islands.',
    'La estructura existente y los nuevos materiales construyen un diálogo claro entre lo antiguo y lo nuevo.':
        'The existing structure and the new materials build a clear dialogue between old and new.',
    'El patio central y el jardín vertical llevan luz natural a las áreas de trabajo.':
        'The central courtyard and the vertical garden bring natural light into the work areas.',
})

# Las etiquetas de la ficha de cada nota de prensa. Son de la pagina nueva
# -una por nota- y todavia no habian pasado por el traductor.
DIC.update({
    'Medio': 'Medium',
    'Link': 'Link',
})

# Textos incorporados por las correcciones finales de agosto. Los nombres de
# premios y organizaciones se conservan: son denominaciones propias.
DIC.update({
    'Buenos Aires · São Paulo · Montevideo · Miami · Madrid':
        'Buenos Aires · São Paulo · Montevideo · Miami · Madrid',
    'Argentina · Brasil · Uruguay · Estados Unidos · España':
        'Argentina · Brazil · Uruguay · United States · Spain',
    'Locales de Tostado Café Club en Buenos Aires, São Paulo, Montevideo, Miami y Madrid.':
        'Tostado Café Club venues in Buenos Aires, São Paulo, Montevideo, Miami and Madrid.',
    '1.470 m² cubiertos': '1,470 m² covered area',
    '300 m² interior': '300 m² interior',
    '310 m² planta baja': '310 m² ground floor',
    '240 m² cubiertos': '240 m² covered area',
    'Comitente': 'Client',
    'Socios fundadores': 'Founding partners',
    'Publicaciones': 'Publications',
    'Videos': 'Videos',
    'Filtrar publicaciones por año': 'Filter publications by year',
    'Bienal Internacional de Arquitectura': 'International Architecture Biennial',
    'St Michael': 'St Michael',
    'BIAR': 'BIAR',
    'GNV Group': 'GNV Group',
    'Bienal SCA-CPAU · Restaurant &amp; Bar Design Awards':
        'Bienal SCA-CPAU · Restaurant &amp; Bar Design Awards',
    'IIDA · Next Landmark Awards': 'IIDA · Next Landmark Awards',
    'SBID · Restaurant &amp; Bar Design Awards':
        'SBID · Restaurant &amp; Bar Design Awards',
    'Architizer A+ · Surface Design · Hospitality Design · ARQ-FADEA':
        'Architizer A+ · Surface Design · Hospitality Design · ARQ-FADEA',
    'Prix Versailles · Surface Design Awards':
        'Prix Versailles · Surface Design Awards',
    'Architizer A+ · LIV Hospitality Design Awards':
        'Architizer A+ · LIV Hospitality Design Awards',
    'Prix Versailles · Restaurant &amp; Bar Design Awards':
        'Prix Versailles · Restaurant &amp; Bar Design Awards',
    'Accor Hotels Design &amp; Technical Summit':
        'Accor Hotels Design &amp; Technical Summit',
    'German Design Awards · SBID · Restaurant &amp; Bar Design Awards':
        'German Design Awards · SBID · Restaurant &amp; Bar Design Awards',
})

# La lupa de Trabajos y del archivo de prensa. El placeholder dice solo
# "Buscar", que ya estaba traducido; estas son las etiquetas que lee un lector
# de pantalla y el aviso de que no hubo resultados.
DIC.update({
    'Buscar un trabajo': 'Search the works',
    u'Buscar una publicaci\u00f3n': 'Search the archive',
    u'No hay trabajos que coincidan con la b\u00fasqueda.':
        'No works match your search.',
})


# "Arq. Fernando Hitzig" -> "Arch. Fernando Hitzig". El nombre se copia tal
# cual: traducirlo seria un error, no una omision.
TITULO = re.compile(r'^Arq(?:\.|ta\.)? (.+)$')
MEDIA = re.compile(r'^(.*?) — (foto|plano|imagen) (\d+)$')

# Lo que aporta la pagina de cada nota de prensa. Los titulares y los nombres
# de las publicaciones se citan como salieron: son la fuente, no texto del
# sitio. Lo que si se traduce es lo que arma el sitio alrededor.
PASA_EXACTO.update({
    'G&amp;G Magazine', 'La Nación', 'Hospitality Design', 'Metalocus',
    u'“Antiche Tentazioni, heladería”',
    u'“Comer solo sin pedir perdón”',
    u'“El nuevo restaurante de Belgrano en un patio lleno de plantas”',
    u'“Entrevista a Hitzig Militello Architects”',
    u'“Fogón, restaurante y bar en Riad, Arabia Saudí”',
    u'“Stella Artois Stand / Hitzig Militello arquitectos”',
    u'“The Nim Bar, fotografía de Federico Kulekdjian”',
    u'“Un lugar para sentarse al aire libre en la normalidad pandémica: Williamsburg”',
    u'“Williamsburg, espacio al aire libre en Buenos Aires”',
})

DIC.update({
    # Las tres notas sin mes: la regla de abajo pide mes, y una regla que
    # aceptara solo el ano se comeria cualquier frase que termine en ", 2019.".
    u'Fogón, restaurante y bar en Riad, Arabia Saudí en Design Boom, 2019.':
        u'Fogón, restaurante y bar en Riad, Arabia Saudí in Design Boom, 2019.',
    u'Stella Artois Stand / Hitzig Militello arquitectos en ArchDaily, 2023.':
        u'Stella Artois Stand / Hitzig Militello arquitectos in ArchDaily, 2023.',
    u'The Nim Bar, fotografía de Federico Kulekdjian en Design Boom, 2018.':
        u'The Nim Bar, fotografía de Federico Kulekdjian in Design Boom, 2018.',
    # Paises del filtro de trabajos que faltaban.
    'EE.UU.': 'USA',
    'Reino Unido': 'United Kingdom',
    u'España': 'Spain',
})

# La descripcion de cada nota de prensa: "<titular> en <medio>, <Mes> <ano>.".
# El titular es de la publicacion y se deja como salio; lo que se traduce es
# el armado -"en" y el mes-. Va como regla porque hay una por nota y crecen.
FICHA_NOTA = re.compile(
    r'^(.+) en (.+?), (%s)( \d{4})?\.$' % '|'.join(en_dic.MESES_LARGOS))


def traducir(t):
    m = FICHA_NOTA.match(t)
    if m:
        return u'%s in %s, %s%s.' % (m.group(1), m.group(2),
                                     en_dic.MESES_LARGOS[m.group(3)],
                                     m.group(4) or '')
    m = MEDIA.match(t)
    if m:
        tipo = {'foto': 'photo', 'plano': 'plan', 'imagen': 'image'}[m.group(2)]
        return '%s — %s %s' % (m.group(1), tipo, m.group(3))
    m = TITULO.match(t)
    if m:
        return 'Arch. %s' % m.group(1).replace('Arq. ', 'Arch. ')
    return en_dic6.traducir(t)
