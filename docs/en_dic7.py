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
    # Los fotografos del renglon que pidio el segundo Word del 21/08. Salen del
    # campo `fotografias_proyecto` del WordPress viejo y son gente: no se
    # traducen. Los dos con coma son obras firmadas por dos.
    'Alejandro Peral', 'Esteban Lobo', u'Andrés Domínguez',
    'Mohammed Shehab Din', 'Paloma Zaldua', u'Simón Laprida', 'Uchimay',
    u'Javier Agustín Rojas',
    u'Federico Kulekdjian, Esteban Lobo',
    u'Andrés Martellini, Daniel Karp',
})

DIC.update({
    "A definir": "To be defined",
    "Architizer A+": "Architizer A+",
    "IIDA": "IIDA",
    "ARQ-FADEA": "ARQ-FADEA",
    "← Anteriores": "← Previous",
    "Siguientes →": "Next →",
    "Páginas de conferencias y clases": "Conference and class pages",
    "Paginas de publicaciones": "Publication pages",
    "Profesor en Taller de Arquitectura Interior Experiencial en Haus.":
        "Professor in the Experiential Interior Architecture Workshop at Haus.",
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
    # Sin estas dos, en_gen no avisa nada -el aria-label no es texto visible- y
    # el punteo ingles quedaba con "Go to miembros de" y "Go to las cifras del
    # estudio", medio traducido, que es justo lo que lee un lector de pantalla.
    u'Ir a miembros de': 'Go to members',
    u'Ir a las cifras del estudio': "Go to the studio's figures",
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
    # Rotulo de accion y nombre accesible del numero confirmado de Miami. Son
    # iguales en los dos idiomas, pero se declaran para que el espejo no los
    # reporte como texto castellano sin traducir.
    'WhatsApp: +1 (305) 851 3565': 'WhatsApp: +1 (305) 851 3565',
    'WhatsApp +1 305 851 3565': 'WhatsApp +1 305 851 3565',

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
    'Fotógrafo': 'Photographer',
    'Dirección de obra:': 'Site management:',
    'Documentación de obra:': 'Construction documentation:',
    'Project manager:': 'Project manager:',
    'Colaboradores:': 'Collaborators:',
    'Renders:': 'Renders:',

    # --- categorias que faltaban ---
    'Comercial': 'Commercial',
    'Hotelería': 'Hospitality',
    'Tipología': 'Typology',
    'Intervención': 'Intervention',
    'Interiorismo': 'Interior design',
    'Arquitectura e interiorismo': 'Architecture and interior design',
    'Enviar un mensaje por WhatsApp al +54 11 4773 8658': 'Send a WhatsApp message to +54 11 4773 8658',
    'Enviar un mensaje por WhatsApp al +1 305 851 3565': 'Send a WhatsApp message to +1 305 851 3565',

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
    'Aire Libre: arquitectura y naturaleza': 'Aire Libre: architecture and nature',
    'Aire Libre, proyecto de Hitzig Militello Arquitectos':
        'Aire Libre, a project by Hitzig Militello Architects',
    'Inspirado en los antiguos invernaderos ingleses, Aire Libre combina recursos industriales, vegetación y coctelería en más de 900 m².':
        'Inspired by historic English greenhouses, Aire Libre combines industrial materials, vegetation and cocktail culture across more than 900 m².',
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

    # Banco Supervielle entra desde la base durante el build: su pagina no
    # existe todavia cuando se genera el espejo local por primera vez.
    'Banco Supervielle': 'Banco Supervielle',
    'Banco y Workplace': 'Banking and Workplace',
    'Provincia de Buenos Aires': 'Buenos Aires Province',
    'Las nuevas oficinas del banco, en lamas de madera y curvas cálidas.':
        "The bank's new offices, shaped by timber slats and warm curves.",
    'S. Fernández 198 esq. Laprida San Isidro, Provincia de Buenos Aires':
        'S. Fernandez 198 at Laprida, San Isidro, Buenos Aires Province',
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
    u'Nuestro proyecto VIP Lounge Movistar Arena fue distinguido con una Mención Especial en la categoría Commercial Interiors de los Architizer A+ Awards 2026.':
        'Our VIP Lounge Movistar Arena project received a Special Mention in the Commercial Interiors category of the 2026 Architizer A+ Awards.',
    u'Leonardo Militello y Fernando Hitzig repasan dos décadas de trayectoria y el proceso creativo del espacio VIP gastronómico del Movistar Arena.':
        'Leonardo Militello and Fernando Hitzig look back on two decades of work and the creative process behind the Movistar Arena VIP hospitality space.',
    u'Leonardo Militello y Fernando Hitzig cuentan cómo diseñan espacios que generan experiencia.':
        'Leonardo Militello and Fernando Hitzig explain how they design experience-led spaces.',
    # Los dos puntos que faltaban en el indice lateral del Inicio. "Miembros"
    # rotula la seccion "Miembros de" -las asociaciones- y "Cifras" la fila de
    # numeros; van cortos porque en el punteo son una etiqueta al lado de un
    # cuadradito, no un titulo.
    u'Miembros': 'Members',
    u'Cifras': 'Figures',
    u'Conferencias y prensa': 'Conferences and press',
    u'Conferencias y clases': 'Conferences and classes',
    u'Novedades': 'News',
    u'Publicación': 'Publication',
    u'Ver publicación': 'View publication',
    u'Buscar una publicación': 'Search a publication',
    u'Buscar una conferencia': 'Search a talk',
    u'Filtrar publicaciones por año': 'Filter publications by year',
    # Los rotulos de la lista de conferencias, que salen del CV.
    u'Conferencia': 'Talk',
    u'Charla': 'Talk',
    u'Docencia': 'Teaching',
    u'Clase magistral': 'Masterclass',
    u'Podcast': 'Podcast',
    u'Exposicion': 'Exhibition',
    u'Exposición': 'Exhibition',
    u'Jurado': 'Jury',
    u'Novedad': 'News',
    # Los paises que trae el archivo de prensa y todavia no estaban.
    u'Corea': 'Korea', u'Corea del Sur': 'South Korea', u'India': 'India',
    u'China': 'China', u'Francia': 'France', u'Alemania': 'Germany',
    u'España': 'Spain', u'Mexico': 'Mexico', u'México': 'Mexico',
    u'Colombia': 'Colombia', u'Peru': 'Peru', u'Perú': 'Peru',
    u'Uruguay': 'Uruguay', u'Japon': 'Japan', u'Japón': 'Japan',
    u'Reino Unido': 'United Kingdom', u'Emiratos Arabes Unidos':
        'United Arab Emirates', u'Rusia': 'Russia', u'Turquia': 'Turkey',
    u'Turquía': 'Turkey', u'Polonia': 'Poland', u'Holanda': 'Netherlands',
    u'Paises Bajos': 'Netherlands', u'Países Bajos': 'Netherlands',
    u'Portugal': 'Portugal', u'Canada': 'Canada', u'Canadá': 'Canada',
    u'Australia': 'Australia', u'Suiza': 'Switzerland', u'Austria': 'Austria',
    u'Belgica': 'Belgium', u'Bélgica': 'Belgium', u'Grecia': 'Greece',
    u'Israel': 'Israel', u'Singapur': 'Singapore', u'Tailandia': 'Thailand',
    u'Indonesia': 'Indonesia', u'Vietnam': 'Vietnam',
    u'Republica Checa': 'Czech Republic', u'República Checa': 'Czech Republic',
    u'argentina': 'Argentina', u'USA': 'USA', u'UK': 'UK', u'EEUU': 'USA',
    u'US': 'US', u'Hungria': 'Hungary', u'Hungría': 'Hungary',
    u'Sudáfrica': 'South Africa', u'Sudafrica': 'South Africa',
})


def _nombres_propios_de_prensa():
    """Los medios y los titulares de las 210 publicaciones, que no se traducen.

    Estan en los datos y no en las plantillas, asi que enumerarlos a mano seria
    una lista que hay que tocar cada vez que el estudio carga una nota. Se leen
    del mismo JSON del que salen las tarjetas: una publicacion nueva entra sola
    y en_gen deja de reportarla como faltante.
    """
    import io
    import json
    import os

    fuera = set()
    aqui = os.path.dirname(os.path.abspath(__file__))

    def sumar(valor):
        valor = (valor or '').strip()
        if not valor:
            return
        # En el HTML el & viaja escapado, asi que "Bosch & Cia" del JSON nunca
        # coincidiria con el "Bosch &amp; Cia" que el traductor esta mirando.
        for texto in (valor, valor.replace('&', '&amp;')):
            fuera.add(texto)
            # En las fichas el titular va entre comillas tipograficas.
            fuera.add(u'“%s”' % texto)

    for archivo, campos in (('prensa_datos.json', ('medio', 'titulo')),
                            ('prensa_novedades.json', ('titulo', 'detalle'))):
        ruta = os.path.join(aqui, archivo)
        if not os.path.isfile(ruta):
            continue
        for fila in json.load(io.open(ruta, encoding='utf-8')):
            for campo in campos:
                sumar(fila.get(campo))
            # El rotulo de la tarjeta es "<medio> — <pais>": el pais si se
            # traduce, pero el par armado tambien aparece entero.
            if fila.get('medio') and fila.get('pais'):
                sumar(u'%s — %s' % (fila['medio'], fila['pais']))
    return fuera


PASA_EXACTO.update(_nombres_propios_de_prensa())

# La descripcion de cada nota de prensa: "<titular> en <medio>, <fecha>.".
# El titular es de la publicacion y se deja como salio; lo que se traduce es
# el armado -"en" y el mes-. Va como regla porque hay una por nota y crecen.
#
# La fecha viene de cinco formas, porque es un campo que el estudio cargo a
# mano durante veinte años: "Mayo 2026", "May 2017", "2013", "21.04.2026". La
# primera version solo aceptaba los meses largos en castellano y dejaba sin
# traducir la descripcion de las ciento veintidos notas restantes.
#
# Y ademas hay rangos: "Feb 2014 - Jul 2014 - May 2017" y "Junio- Agosto 2012".
# Por eso la fecha se acepta como un tramo de meses, años y separadores, y la
# traduccion se hace mes por mes sobre lo que haya.
UN_MES = r'(?:%s)' % '|'.join(en_dic.MESES_LARGOS)
FECHA_NOTA = (r'(?:%s|[A-Za-z]{3,10}|\d{1,4})'
              r'(?:[\s./-]+(?:%s|[A-Za-z]{3,10}|\d{1,4}))*' % (UN_MES, UN_MES))
FICHA_NOTA = re.compile(r'^(.+) en (.+?), (%s)\.$' % FECHA_NOTA)
TITULO_PRENSA_SEO = re.compile(r'^(.*?) \| Prensa HMA$')
FICHA_NOTA_SEO = re.compile(
    r'^(.+) en (.+?)(?:, (%s))?\. Arquitectura e interiorismo de '
    r'Hitzig Militello Arquitectos\.$' % FECHA_NOTA)

_MES_SUELTO = re.compile(r'\b(%s)\b' % UN_MES)


def _fecha_en_ingles(fecha):
    """Traduce los meses que esten en castellano; el resto queda como vino."""
    return _MES_SUELTO.sub(lambda m: en_dic.MESES_LARGOS[m.group(1)], fecha)


def traducir(t):
    # El diccionario le gana a los patrones, igual que en en_dic y en en_dic4.
    # Sin esta linea, FICHA_NOTA -el molde "Obra in Medio, fecha."- se quedaba
    # con frases que cumplen su forma por casualidad y las devolvia con el
    # unico cambio de "en" por "in": las 27 conferencias de la lista de Prensa
    # salian en castellano, con "Profesor de Arquitectura Comercial Interior in
    # la Haus". Estaban cargadas mas abajo y no se usaban nunca, porque el
    # patron contestaba antes de que nadie mirara el diccionario.
    if t in DIC:
        return DIC[t]
    m = TITULO_PRENSA_SEO.match(t)
    if m:
        # El titular y el medio son citas de la publicacion. Solo se traduce
        # el rotulo SEO que agrega el sitio alrededor.
        return u'%s | HMA Press' % m.group(1)
    m = FICHA_NOTA_SEO.match(t)
    if m:
        fecha = (u', %s' % _fecha_en_ingles(m.group(3))) if m.group(3) else ''
        return (u'%s in %s%s. Architecture and interior design by Hitzig '
                u'Militello Architects.' % (m.group(1), m.group(2), fecha))
    m = FICHA_NOTA.match(t)
    if m:
        return u'%s in %s, %s.' % (m.group(1), m.group(2),
                                   _fecha_en_ingles(m.group(3)))
    m = MEDIA.match(t)
    if m:
        tipo = {'foto': 'photo', 'plano': 'plan', 'imagen': 'image'}[m.group(2)]
        return '%s — %s %s' % (m.group(1), tipo, m.group(3))
    m = TITULO.match(t)
    if m:
        return 'Arch. %s' % m.group(1).replace('Arq. ', 'Arch. ')
    return en_dic6.traducir(t)


# Las 27 conferencias y clases de la lista de Prensa. El texto que se ve es
# el detalle completo desde que se corrigio la fila -el titulo del JSON venia
# cortado por el medio-, y ese detalle nunca habia tenido traduccion: el
# espejo ingles mostraba castellano con alguna palabra suelta cambiada,
# "Profesor de Arquitectura Comercial Interior in la Haus", que es peor que
# dejarlo entero. en_gen no lo reportaba porque daba la frase por traducida.
#
# Los nombres propios de las instituciones se dejan como estan: FADU, SCA,
# UADE, Malba y las catedras son como se llaman, no se traducen.
DIC.update({
    "Profesor de Arquitectura Comercial Interior en la Haus: Leonardo Militello. Buenos Aires, Argentina.":
        "Professor of Commercial Interior Architecture at la Haus: Leonardo Militello. Buenos Aires, Argentina.",
    "Ciclo de conferencias 2026: impartido en DINA (Asociación Nacional de Diseñadores). Parte del ”Ciclo de conferencias presenciales 2026” —evento presencial en el Auditorio Diego de Torres, UCC Córdoba, Argentina.":
        "2026 lecture series: delivered at DINA (National Association of Designers). Part of the ”2026 in-person lecture series” —in-person event at the Auditorio Diego de Torres, UCC Córdoba, Argentina.",
    "Conferencia en TENDIEZ LAB: «Arquitectura Gastronómica y Hotelera: Negocio, Diseño, Experiencia». Buenos Aires, Argentina.":
        "Lecture at TENDIEZ LAB: «Gastronomic and Hospitality Architecture: Business, Design, Experience». Buenos Aires, Argentina.",
    "Conferencia TENDIEZ LAB: “Gastronomía: Diseño, Negocio, Experiencia y Patrimonio”. Mar del Plata, Argentina.":
        "TENDIEZ LAB lecture: “Gastronomy: Design, Business, Experience and Heritage”. Mar del Plata, Argentina.",
    "Conferencia: Invitados por la UADE FADI – Clase de la arq. Lucía López. Buenos Aires, Argentina.":
        "Lecture: Invited by UADE FADI – Class of Arch. Lucía López. Buenos Aires, Argentina.",
    "Conferencia: En el marco de la feria HOTELGA 2024, fuimos invitados a participar en una mesa redonda en la primera edición en directo del podcast Cerrame la Ocho ‘Los 1o mandamientos para no fracasar en la Industria Gastronómica’. Buenos Aires, Argentina.":
        "Lecture: As part of the HOTELGA 2024 trade fair, we were invited to join a round table at the first live edition of the podcast Cerrame la Ocho, ‘The 10 commandments for not failing in the gastronomic industry’. Buenos Aires, Argentina.",
    "Profesor de Interior Creative Architecture en Haus: Leonardo Militello Buenos Aires, Argentina.":
        "Professor of Interior Creative Architecture at Haus: Leonardo Militello. Buenos Aires, Argentina.",
    "Conferencia en la UADE – FADI (Facultad de Arquitectura y Diseño – Universidad Argentina de la Empresa). Buenos Aires, Argentina.":
        "Lecture at UADE – FADI (School of Architecture and Design – Universidad Argentina de la Empresa). Buenos Aires, Argentina.",
    "Clase magistral impartida en la FAD - UPC (Facultad de Arte y Diseño – Universidad Provincial de Córdoba). En el marco de la 4th Jornada de Interiorismo del centro del País. Córdoba, Argentina.":
        "Masterclass delivered at FAD - UPC (School of Art and Design – Universidad Provincial de Córdoba), as part of the 4th Interior Design Conference of the central region. Córdoba, Argentina.",
    "Clase magistral impartida en el IED Barcelona (Instituto Europeo de Diseño). En el marco del Master in Interior Design for Commercial Spaces and Retail. Barcelona, España.":
        "Masterclass delivered at IED Barcelona (Istituto Europeo di Design), as part of the Master in Interior Design for Commercial Spaces and Retail. Barcelona, Spain.",
    "Clase magistral impartida en el IED Kunsthal (Instituto Europeo de Diseño). En el marco del Master in interior design for commercial, hotel and work spaces. Bilbao, España.":
        "Masterclass delivered at IED Kunsthal (Istituto Europeo di Design), as part of the Master in interior design for commercial, hotel and work spaces. Bilbao, Spain.",
    "Ciclo de conferencias 10.ª TENDIEZ Experiences: \"Transforming gastronomic architecture from architecture, business and experience\". Evento presencial y virtual el 11 de octubre de 2022 a las 19:00 h en el Auditorio del Malba. Museo. Museo de Arte Latinoamericano de Buenos Aires. Buenos Aires, Argentina.":
        "10th TENDIEZ Experiences lecture series: \"Transforming gastronomic architecture from architecture, business and experience\". In-person and online event on 11 October 2022 at 7 pm at the Malba Auditorium. Museo de Arte Latinoamericano de Buenos Aires. Buenos Aires, Argentina.",
    "Conferencia en FADI – UADE (Universidad Argentina de la Empresa). UADE FADI- Proyecto 6 . Arquitectura y diseño. Buenos Aires, Argentina.":
        "Lecture at FADI – UADE (Universidad Argentina de la Empresa). UADE FADI - Project 6. Architecture and design. Buenos Aires, Argentina.",
    "Conferencia en el seminario web: Invited by BN. Miami: the market everyone is talking about ( BN-Building Network ). Buenos Aires, Argentina.":
        "Webinar lecture: Invited by BN. Miami: the market everyone is talking about (BN-Building Network). Buenos Aires, Argentina.",
    "Conferencia en seminario web: Invited by ESAD University of Moron Escuela Superior de Arquitectura y Diseño. Seminario web sobre su práctica profesional. Buenos Aires, Argentina.":
        "Webinar lecture: Invited by ESAD University of Moron, Escuela Superior de Arquitectura y Diseño. Webinar on their professional practice. Buenos Aires, Argentina.",
    "Conferencia en seminario web: Invited by Sociedad Central de Arquitectos & Museo de Arquitectura to give a lecture about it’s trajectory. (SCA http://www.socearq.org/ ). Buenos Aires, Argentina.":
        "Webinar lecture: Invited by Sociedad Central de Arquitectos & Museo de Arquitectura to give a lecture about its trajectory. (SCA http://www.socearq.org/ ). Buenos Aires, Argentina.",
    "Conferencia en seminario web: Invited by University of Buenos Aires to give a lecture about “in the face of a paradigm shift versatile responses“. Buenos Aires, Argentina.":
        "Webinar lecture: Invited by University of Buenos Aires to give a lecture about “in the face of a paradigm shift versatile responses“. Buenos Aires, Argentina.",
    "Conferencia en seminario web: Invited by University of Buenos Aires to give a lecture about “in the face of a paradigm shift versatile responses“ en la Sociedad Central de Arquitectos (SCA). Buenos Aires, Argentina.":
        "Webinar lecture: Invited by University of Buenos Aires to give a lecture about “in the face of a paradigm shift versatile responses“ at the Sociedad Central de Arquitectos (SCA). Buenos Aires, Argentina.",
    "Orador: Lecture at the International architecture festival ARQfestival 2019. Se celebró en las instalaciones del Teatro Diana, en la ciudad de Guadalajara, México. ARQfestival 2019 es un evento organizado por DESIGNFEST, el mayor festival internacional de diseño de México, que garantiza una experiencia contrastada y de calidad a lo largo de más de 12 años de conferencias, talleres, seminarios y exposiciones del sector de las industrias creativas en México. Integrado por 8 arquitectos de renombre, tanto nacionales como extranjeros, que impartirán conferencias magistrales; cada uno de ellos es un referente en el mundo de la arquitectura y es reconocido como un icono en sus respectivas disciplinas. https://www.arqfestival.com/#about Guadalajara, México.":
        "Speaker: Lecture at the International architecture festival ARQfestival 2019. Held at the Teatro Diana, in Guadalajara, Mexico. ARQfestival 2019 is an event organised by DESIGNFEST, Mexico’s largest international design festival, which guarantees a proven, high-quality experience across more than 12 years of lectures, workshops, seminars and exhibitions in Mexico’s creative industries. Made up of 8 renowned architects, Argentine and international, who deliver masterclasses; each of them is a benchmark in the world of architecture and is recognised as an icon in their own discipline. https://www.arqfestival.com/#about Guadalajara, Mexico.",
    "Orador: Invitado por TENDIEZ (Tendencias de Diseño ) to lecture on its trajectory at the architectural congress de la Sociedad Central de Arquitectos (SCA). “Experiencias en arquitectura de interiores”. Buenos Aires, Argentina.":
        "Speaker: Invited by TENDIEZ (Tendencias de Diseño) to lecture on its trajectory at the architectural congress of the Sociedad Central de Arquitectos (SCA). “Experiences in interior architecture”. Buenos Aires, Argentina.",
    "Profesor de Arquitectura de Marca en la Haus: Leonardo Militello https://www.holahaus.com/ Buenos Aires, Argentina":
        "Professor of Brand Architecture at la Haus: Leonardo Militello https://www.holahaus.com/ Buenos Aires, Argentina",
    "Orador en la Cumbre Latinoamericana de Tendencias y Creatividad. Universidad de Palermo. Buenos Aires, Argentina.":
        "Speaker at the Latin American Summit of Trends and Creativity. Universidad de Palermo. Buenos Aires, Argentina.",
    "Profesores de Diseño Arquitectónico I: Leonardo Militello y Fernando Hitzig Cátedra Lestard,Cajide & Janchez. FADU - Universidad de Buenos Aires. Buenos Aires, Argentina.":
        "Professors of Architectural Design I: Leonardo Militello and Fernando Hitzig. Lestard, Cajide & Janchez studio. FADU - University of Buenos Aires. Buenos Aires, Argentina.",
    "Graduado en Arquitectura Leonardo Militello. FADU, University of Buenos Aires. Buenos Aires, Argentina.":
        "Architecture graduate Leonardo Militello. FADU, University of Buenos Aires. Buenos Aires, Argentina.",
    "Profesor ayudante de Diseño Arquitectónico I: Leonardo Militello Cátedra LLauro-Soler - FADU, Universidad de Buenos Aires. Buenos Aires, Argentina.":
        "Teaching assistant in Architectural Design I: Leonardo Militello. LLauro-Soler studio - FADU, University of Buenos Aires. Buenos Aires, Argentina.",
    "Profesor ayudante de Historia de la Arquitectura III: Leonardo Militello Cátedra Brugnoli. FADU, Universidad de Buenos Aires. Buenos Aires, Argentina.":
        "Teaching assistant in History of Architecture III: Leonardo Militello. Brugnoli studio. FADU, University of Buenos Aires. Buenos Aires, Argentina.",
    "Graduado en Arquitectura Fernando Hitzig. FADU, University of Buenos Aires. Buenos Aires, Argentina.":
        "Architecture graduate Fernando Hitzig. FADU, University of Buenos Aires. Buenos Aires, Argentina.",
})
