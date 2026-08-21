# -*- coding: utf-8 -*-
"""Aplica una sola vez las correcciones de contenido recibidas en agosto.

Cada cambio comprueba primero el valor anterior. Asi, el build corrige la base
que ya estaba publicada pero no vuelve a pisar una edicion posterior hecha por
el estudio desde el panel.

    python docs/panel_correcciones_agosto.py
    python docs/panel_correcciones_agosto.py --supabase
"""
import io
import json
import os
import re
import sys
import urllib.request


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def reemplazo(prefijo_viejo, prefijo_nuevo):
    def aplicar(valor):
        if isinstance(valor, str) and valor.startswith(prefijo_viejo):
            return prefijo_nuevo + valor[len(prefijo_viejo):]
        return valor
    return aplicar


def valor(viejo, nuevo):
    return lambda actual: nuevo if actual == viejo else actual


def alguno(viejos, nuevo):
    """Como valor(), pero acepta varios valores anteriores conocidos."""
    return lambda actual: nuevo if actual in viejos else actual


def completar_vacio(nuevo):
    return lambda actual: nuevo if not actual else actual


def texto_normalizado(viejo, nuevo):
    """Corrige el texto viejo aunque Supabase use saltos CRLF."""
    esperado = re.sub(r'\s+', ' ', viejo).strip()

    def aplicar(actual):
        if isinstance(actual, str) and re.sub(r'\s+', ' ', actual).strip() == esperado:
            return nuevo
        return actual
    return aplicar


PRESENTACION_ANTERIOR_ES = (
    'En Hitzig Militello Arquitectos llevamos a cabo proyectos comerciales y '
    'residenciales de alta calidad en toda Latinoamérica, Europa, Oriente Medio '
    'y Estados Unidos. Con un enfoque especial en hotelería y espacios de '
    'trabajo, nos hemos convertido en auténticos artesanos de las marcas, con '
    'reconocimiento internacional.')
PRESENTACION_NUEVA_ES = (
    'En Hitzig Militello arquitectos realizamos proyectos comerciales de forma '
    'local y regional tanto en América Latina, como en Europa, Medio Oriente y '
    'EEUU, con especial enfoque en la industria de la hospitalidad. Más de dos '
    'décadas de trayectoria creado arquitectura e interiorismos de reconocimiento '
    'internacional.')
PRESENTACION_ANTERIOR_EN = (
    'At Hitzig Militello Architects we deliver high-quality commercial and '
    'residential projects across Latin America, Europe, the Middle East and the '
    'United States. With a particular focus on hospitality and workspaces, we '
    'have become genuine craftsmen of brands, with international recognition.')
PRESENTACION_NUEVA_EN = (
    'At Hitzig Militello Architects, we deliver commercial projects locally and '
    'regionally across Latin America, Europe, the Middle East and the United '
    'States, with a particular focus on the hospitality industry. For more than '
    'two decades, we have created internationally recognised architecture and '
    'interior design.')

BIENAL_MEMORIA_ANTERIOR_ES = (
    'Es un circuito en el que identificamos seis (6) tipos de inteligencia que '
    'articulan el accionar humano a lo largo de su evolución: '
    'individual_colectiva_natural_artificial_emocional_racional. Cada una de '
    'estas inteligencias actúa individualmente, pero interaccionan entre sí de '
    'forma diversa. De esta interacción entre dos inteligencias surge una '
    'tensión (un caos) que se evidencia a través de la expresividad sin una '
    'lógica aparente de las estructuras que las sostienen.\n\n'
    ', una interconexión, una relación entre partes, una estructura que -caos '
    'mediante- pretende\n\n'
    ') las inteligencias en cuestión, aportando a modo de soporte el contenido '
    'de la exhibición. De esta forma, el pabellón se recorre hilvanando las seis '
    'inteligencias que producen cinco intersecciones, siendo finalmente estos '
    'cinco focos de atención los que exhiben, sostienen e iluminan la totalidad '
    'de la obra.\n\n'
    'La disposición de estos cinco soportes recorribles, materializados '
    'mediante andamiaje y articulaciones, se encuentran dispuestos en el '
    'espacio de forma a priori aleatoria contraponiéndose al camino central, '
    'sereno y lineal que ofrece al visitante la posibilidad de detenerse, '
    'sentarse bajo la nube de supuestas inteligencias y recuperar la capacidad '
    'de contemplación.\n\n'
    'El contenido se propone bajo un criterio curatorial en las 5 '
    'intersecciones según un orden cronológico. El criterio expositivo que '
    'define a cada una de las intersecciones exhibe entonces una selección de '
    'obras que conlleva una relación integral y directa a lo expuesto, y '
    'responde a una línea temporal que se inicia en la inteligencia individual '
    'y culmina en la artificial.\n\n'
    'El pabellón se levanta a partir de la combinación y disposición de piezas '
    'tubulares y nudos que conforman andamios, siendo dichas estructuras la '
    'representación de la capacidad humana de evolucionar desde la inteligencia '
    'en las que tablones macizos de madera dan formato a la aplicación del '
    'contenido audio visual. A su vez, las estructuras de andamiaje sostienen y '
    'elevan los seis volúmenes colgantes que levitan en el espacio generando el '
    'circuito de la propuesta. Los volúmenes livianos que coronan las '
    'estructuras están materializadas mediante lienzos blancos y etéreos a '
    'través de la recuperación de bolsones de arpillera plástica de descarte.')

BIENAL_MEMORIA_NUEVA_ES = (
    'Es un circuito en el que identificamos seis (6) tipos de inteligencia que '
    'articulan el accionar humano a lo largo de su evolución: individual, '
    'colectiva, natural, artificial, emocional y racional. Cada una de estas '
    'inteligencias actúa individualmente, pero interaccionan entre sí de forma '
    'diversa. De esta interacción entre dos inteligencias surge una tensión '
    '(un caos) que se evidencia a través de la expresividad sin una lógica '
    'aparente de las estructuras que las sostienen.\n\n'
    'De estos puntos de conflicto emerge una sinapsis: una interconexión, una '
    'relación entre partes, una estructura que —caos mediante— pretende '
    'interligar las inteligencias en cuestión y aportar, a modo de soporte, el '
    'contenido de la exhibición. De esta forma, el pabellón se recorre '
    'hilvanando las seis inteligencias que producen cinco intersecciones; estos '
    'cinco focos de atención exhiben, sostienen e iluminan la totalidad de la '
    'obra.\n\n'
    'La disposición de estos cinco soportes recorribles, materializados '
    'mediante andamiaje y articulaciones, se encuentran dispuestos en el '
    'espacio de forma a priori aleatoria contraponiéndose al camino central, '
    'sereno y lineal que ofrece al visitante la posibilidad de detenerse, '
    'sentarse bajo la nube de supuestas inteligencias y recuperar la capacidad '
    'de contemplación.\n\n'
    'El contenido se propone bajo un criterio curatorial en las 5 '
    'intersecciones según un orden cronológico. El criterio expositivo que '
    'define a cada una de las intersecciones exhibe entonces una selección de '
    'obras que conlleva una relación integral y directa a lo expuesto, y '
    'responde a una línea temporal que se inicia en la inteligencia individual '
    'y culmina en la artificial.\n\n'
    'El pabellón se levanta a partir de la combinación y disposición de piezas '
    'tubulares y nudos que conforman andamios, siendo dichas estructuras la '
    'representación de la capacidad humana de evolucionar desde la inteligencia '
    'en las que tablones macizos de madera dan formato a la aplicación del '
    'contenido audio visual. A su vez, las estructuras de andamiaje sostienen y '
    'elevan los seis volúmenes colgantes que levitan en el espacio generando el '
    'circuito de la propuesta. Los volúmenes livianos que coronan las '
    'estructuras están materializadas mediante lienzos blancos y etéreos a '
    'través de la recuperación de bolsones de arpillera plástica de descarte.')

BIENAL_MEMORIA_ANTERIOR_EN = (
    'It is a circuit in which we identify six kinds of intelligence that shape '
    'human action across its evolution: individual, collective, natural, '
    'artificial, emotional and rational. Each of these acts on its own, but '
    'they interact with one another in many ways. From the interaction between '
    'two intelligences a tension arises — a chaos — made visible through the '
    'expressiveness, with no apparent logic, of the structures that hold them '
    'up.\n\n'
    ', an interconnection, a relationship between parts, a structure that — '
    'through chaos — sets out to\n\n'
    ') the intelligences in question, providing the content of the exhibition '
    'as its support. The pavilion is walked through by threading together the '
    'six intelligences, which produce five intersections; these five focal '
    'points are what finally display, support and light the work as a whole.\n\n'
    'The five walkable supports, built from scaffolding and joints, are laid '
    'out in space in an apparently random way, set against a central path — '
    'calm and linear — that offers the visitor the chance to stop, sit beneath '
    'the cloud of supposed intelligences and recover the capacity for '
    'contemplation.\n\n'
    'The content is arranged under a curatorial criterion across the five '
    'intersections, in chronological order. The criterion defining each '
    'intersection displays a selection of works with a direct, integral '
    'relationship to what is shown, following a timeline that begins with '
    'individual intelligence and ends with artificial intelligence.\n\n'
    'The pavilion is raised from the combination and arrangement of tubular '
    'pieces and joints that form scaffolding, those structures standing for '
    'the human capacity to evolve through intelligence, with solid timber '
    'planks framing the audiovisual content. The scaffolding also holds and '
    'lifts the six hanging volumes that levitate in the space, creating the '
    'circuit of the proposal. The light volumes crowning the structures are '
    'built from white, ethereal canvases made by recovering discarded plastic '
    'burlap sacks.')

BIENAL_MEMORIA_NUEVA_EN = (
    'It is a circuit in which we identify six kinds of intelligence that shape '
    'human action across its evolution: individual, collective, natural, '
    'artificial, emotional and rational. Each of these acts on its own, but '
    'they interact with one another in many ways. From the interaction between '
    'two intelligences a tension arises — a chaos — made visible through the '
    'expressiveness, with no apparent logic, of the structures that hold them '
    'up.\n\n'
    'From these points of conflict emerges a synapse: an interconnection, a '
    'relationship between parts, a structure that, through chaos, seeks to '
    'interlink the intelligences in question while supporting the exhibition '
    'content. In this way, the pavilion is traversed by threading together the '
    'six intelligences, which produce five intersections; these five focal '
    'points ultimately display, support and illuminate the work as a whole.\n\n'
    'The five walkable supports, built from scaffolding and joints, are laid '
    'out in space in an apparently random way, set against a central path — '
    'calm and linear — that offers the visitor the chance to stop, sit beneath '
    'the cloud of supposed intelligences and recover the capacity for '
    'contemplation.\n\n'
    'The content is arranged under a curatorial criterion across the five '
    'intersections, in chronological order. The criterion defining each '
    'intersection displays a selection of works with a direct, integral '
    'relationship to what is shown, following a timeline that begins with '
    'individual intelligence and ends with artificial intelligence.\n\n'
    'The pavilion is raised from the combination and arrangement of tubular '
    'pieces and joints that form scaffolding, those structures standing for '
    'the human capacity to evolve through intelligence, with solid timber '
    'planks framing the audiovisual content. The scaffolding also holds and '
    'lifts the six hanging volumes that levitate in the space, creating the '
    'circuit of the proposal. The light volumes crowning the structures are '
    'built from white, ethereal canvases made by recovering discarded plastic '
    'burlap sacks.')

TEXTOS_CORRECCIONES = {
    'estudio.presentacion': {
        'es': texto_normalizado(PRESENTACION_ANTERIOR_ES, PRESENTACION_NUEVA_ES),
        'en': texto_normalizado(PRESENTACION_ANTERIOR_EN, PRESENTACION_NUEVA_EN),
    },
}


CORRECCIONES = {
    'bienal-venecia': {
        'memoria': texto_normalizado(
            BIENAL_MEMORIA_ANTERIOR_ES, BIENAL_MEMORIA_NUEVA_ES),
        'memoria_en': texto_normalizado(
            BIENAL_MEMORIA_ANTERIOR_EN, BIENAL_MEMORIA_NUEVA_EN),
    },
    'edificio-del-plata': {
        'memoria': reemplazo('corresponde a oficinas:', 'Corresponde a oficinas:'),
        'memoria_en': reemplazo('corresponds to offices:', 'Corresponds to offices:'),
    },
    'osten-tower': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Sofía Kesting', 'Arq. Camila Lacarpia',
             'Arq. Victoria Nabias', 'Arq. Milagros Rivelli',
             'Arq. Chiara Beltrami', 'Arq. Paula Miano'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Sofía Kesting', 'Arq. Camila Lacarpia',
             'Arq. Victoria Nabias', 'Arq. Milagros Rivelli']),
    },
    'indusparquet': {
        # En la ficha que devolvio el estudio, todas las personas listadas son
        # arquitectas. "Direccion de obra" es un rotulo, no un integrante.
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Dolores Gayoso', 'Alfana Nizza', 'Josué Solano',
             'Dirección de obra:', 'Joaquín Medina'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Dolores Gayoso', 'Arq. Alfana Nizza', 'Arq. Josué Solano',
             'Dirección de obra:', 'Arq. Joaquín Medina']),
    },
    'cerveceria-austral': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Camila Lacarpia', 'Arq. Luciano Cichanowski',
             'Arq. Josué Solano'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Camila Lacarpia', 'Luciano Cichanowski', 'Josué Solano']),
    },
    'juan-valdez': {
        'bajada': valor(
            'Cafetería Juan Valdez sobre Avenida Las Heras.',
            'Dos cafeterías Juan Valdez en Buenos Aires.'),
    },
    'movistar-arena': {
        'memoria': reemplazo(
            'A diferencia de la generalidad de los proyectos gastronómicos, '
            'en los que a priori se tiene bien definido el tipo de usuario…el\n\n'
            ', ya sea por rango etario, por tipo de propuesta gastronómica, '
            'por ubicación y horario de apertura, o incluso por el valor del '
            'cubierto, en este proyecto ninguna de esas variables era fija.',
            'A diferencia de la generalidad de los proyectos gastronómicos, '
            'en los que a priori se tiene bien definido el tipo de usuario '
            '—ya sea por rango etario, por tipo de propuesta gastronómica, '
            'por ubicación y horario de apertura, o incluso por el valor del '
            'cubierto—, en este proyecto ninguna de esas variables era fija.'),
        'memoria_en': reemplazo(
            'Unlike most gastronomic projects, where the type of user is well '
            'defined from the start — the\n\n, whether by age range, by the kind '
            'of food offered, by location and opening hours, or even by the '
            'price of a cover — in this project none of those variables was fixed.',
            'Unlike most gastronomic projects, where the type of user is well '
            'defined from the start — whether by age range, by the kind of food '
            'offered, by location and opening hours, or even by the price of a '
            'cover — none of those variables was fixed in this project.'),
    },
    'tostado': {
        'bajada': alguno(
            ('Local de Tostado Café Club en Miami.',
             'Locales de Tostado Café Club en Argentina, Uruguay, Miami y São Paulo.'),
            'Locales de Tostado Café Club en Buenos Aires, São Paulo, Montevideo, Miami y Madrid.'),
        # La ficha agrupaba todas las sucursales bajo Miami. El estudio marco
        # que la obra representa cinco ciudades y deben verse todas.
        'ubicacion': valor(
            'Miami, Florida',
            'Buenos Aires · São Paulo · Montevideo · Miami · Madrid'),
        'pais': valor(
            'Estados Unidos',
            'Argentina · Brasil · Uruguay · Estados Unidos · España'),
    },
    'hausscape': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Vanik Margossian', 'Arq. Milca Amado,', 'Arq. Julieta Setton'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Vanik Margossian', 'Arq. Milca Amado', 'Arq. Julieta Setton']),
    },
    'moshu': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Vanik Margossian', 'Arq. Dolores Gayoso',
             'Arq. Marcela Bernat/ Arq. Vanik Margossian'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Vanik Margossian', 'Arq. Dolores Gayoso',
             'Arq. Marcela Bernat']),
    },
    'mamba-bar': {
        'bajada': valor(
            'Un bar de geometrías facetadas en cobre y hormigón, con un patio '
            'selvático al fondo.',
            'Un bar organizado por una pieza de hierro y paneles facetados, con '
            'un patio selvático al fondo.'),
    },
    'goodsten': {
        'bajada': valor(
            'Una cremería que se presenta como un volumen facetado de pizarra '
            'negra con una cuña de cobre.',
            'Una cremería concebida como una envolvente diamantada de superficies '
            'facetadas.'),
    },
    'iguanafix': {
        'bajada': valor(
            'Oficinas resueltas con tabiques y mobiliario de OSB, y la gráfica '
            'de la empresa sobre los vidrios.',
            'Remodelación integral de las oficinas de IguanaFix en Buenos Aires.'),
        # El estudio la clasifica como proyecto dentro del filtro de oficinas.
        'estado': valor('concluida', 'en_proyecto'),
    },
    'victoria-brown': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Magdalena Molinari', 'Arq. Leonardo G. Militello'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Magdalena Molinari']),
    },
    'dos-casas-conde': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Leonardo G. Militello', 'Arq. Ruben Ruiz'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello', 'Arq. Ruben Ruiz']),
    },
    'oficina-casa-luna': {
        'titulo': valor('Oficina + casa Luna', 'Casa Luna'),
        # El Word del 06/08 dice "oficina + casa luna esta en oficinas, no en
        # residencial", igual que "manduca es gastronomico no hoteleria" y
        # "kavak es oficina": el primer termino es el correcto. La regla
        # anterior leyo la frase al reves y la mandaba a residencial.
        'categoria': valor('residencial', 'oficinas'),
        'estado': valor('en_proyecto', 'concluida'),
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Leonardo G. Militello', 'Arq. Florencia Schvartzman',
             'Arq. Belen Lepro Delelis'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Florencia Schvartzman', 'Arq. Belen Lepro Delelis']),
    },
    'ph-el-salvador': {
        'estado': valor('en_proyecto', 'concluida'),
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Leonardo G. Militello', 'Arq. Carmela Zuleta',
             'Arq. Juliana Zorza', 'Arq. Samira Attar'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Carmela Zuleta', 'Arq. Juliana Zorza', 'Arq. Samira Attar']),
    },
    'uala-gigena': {
        # El Word del 11/08 dice "Uala gigena es proyecto". La regla anterior
        # la daba por concluida, que es lo contrario.
        'estado': valor('concluida', 'en_proyecto'),
        # Las fichas originales de Uala Gigena fueron creadas en 2022. El
        # cliente tambien marco ese ano en la revision final del contenido.
        'anio': valor('2024', '2022'),
        # Habia quedado al final del listado con orden 60 aunque es de 2022.
        'orden': valor(60, 27),
    },
    'uala-ii': {
        'estado': valor('concluida', 'en_proyecto'),
    },
    'kavak-oficinas': {
        'estado': valor('concluida', 'en_proyecto'),
    },
    'abasto-patio-comidas': {
        # Ninguno de los dos Words pide mover esta obra. Es un patio de
        # comidas y la ficha siempre dijo Gastronómico; la regla anterior la
        # pasaba a Comercial sin respaldo. Se deshace.
        'categoria': valor('comercial', 'gastronomico'),
    },
    'ph-loft-arias': {
        'estado': valor('en_proyecto', 'concluida'),
    },
    'galeria-objeto-a': {
        'estado': valor('en_proyecto', 'concluida'),
    },
}

# Uala Gigena habia quedado ultima al darse de alta sin ano visible. Se ubica
# dentro del bloque 2022 y se desplazan los ordenes siguientes una posicion.
for _slug, _orden_anterior in {
    'burger-7167': 27, 'kavak-oficinas': 28, 'kavak-hub': 29,
    'moshu': 30, 'abasto-patio-comidas': 31,
    'stella-artois-mercat': 32, 'uala-ii': 33, 'williamsburg': 34,
    'fogon': 35, 'fresco': 36, 'malita': 37, 'accor-hotels': 38,
    'cafe-artois': 39, 'clasico-quilmes': 40, 'elyaki': 41,
    'mamba-bar': 42, 'nim-bar': 43, 'casa-olmo': 44, 'goodsten': 45,
    'iguanafix': 46, 'malabia': 47, 'the-birra': 48, 'uala-office': 49,
    'bolivar': 50, 'luccianos-olivos': 51, 'luccianos-caballito': 52,
    'atelier-vilela': 53, 'victoria-brown': 54, 'dos-casas-conde': 55,
    'oficina-casa-luna': 56, 'ph-loft-arias': 57,
    'ph-el-salvador': 58, 'galeria-objeto-a': 59,
}.items():
    CORRECCIONES.setdefault(_slug, {})['orden'] = valor(
        _orden_anterior, _orden_anterior + 1)


# --------------------------------------------------------------------------
# Correcciones recibidas el 19/08/2026 (dos Words del estudio).
# --------------------------------------------------------------------------
#
# Los tres Uala eran el punto mas grave: el Word abre con "SE MEZCLARON
# PROYECTOS" y aclara que son obras distintas. Los nombres salen del Word y no
# de la carpeta del Drive -que dice "82-Uala III (Gigena)" y llevo a nombrarla
# mal-. Nicaragua I y II son las dos oficinas de la calle Nicaragua; Gigena es
# la del Paseo Gigena.

MEMORIA_IGUANAFIX = (
    'Las oficinas de Iguanafix se conciben a partir de una arquitectura directa '
    'y esencial, donde la materialidad expresa la identidad y el carácter '
    'operativo de la empresa.\n\n'
    'El proyecto utiliza placas de OSB en estado natural y estructuras tubulares '
    'de acero a la vista, elementos propios del universo de la construcción '
    'que se incorporan como parte del lenguaje arquitectónico. La '
    'materialidad se presenta sin revestimientos ni artificios, poniendo en valor '
    'su textura, lógica constructiva y condición funcional.\n\n'
    'Las divisiones de vidrio y OSB organizan los distintos sectores de trabajo, '
    'favoreciendo la transparencia, la integración visual y la dinámica '
    'entre los equipos. A su vez, sistemas de estanterías modulares funcionan '
    'como equipamiento, almacenamiento y elementos de división espacial.\n\n'
    'La iluminación natural se complementa con un sistema puntual de spots '
    'LED, enfatizando materiales y superficies. La comunicación gráfica '
    'se integra a la arquitectura mediante vinilos aplicados sobre los planos de '
    'vidrio.\n\n'
    'El conjunto se plantea como un sistema flexible, modular y adaptable, capaz '
    'de acompañar los cambios y el crecimiento de la compañía. Una '
    'arquitectura en permanente transformación, donde materiales, estructura '
    'y equipamiento construyen una identidad coherente con el espíritu de '
    'Iguanafix.')

MEMORIA_IGUANAFIX_EN = (
    'The Iguanafix offices are conceived through a direct and essential '
    'architectural approach, where materiality expresses the company’s '
    'identity and operational character.\n\n'
    'The project incorporates natural OSB panels and exposed tubular steel '
    'structures, elements closely associated with the construction industry that '
    'become an integral part of the architectural language. Materials are '
    'presented without cladding or unnecessary finishes, highlighting their '
    'texture, construction logic, and functional nature.\n\n'
    'Glass and OSB partitions organize the different work areas, promoting '
    'transparency, visual integration, and interaction between teams. Modular '
    'shelving systems also serve as furniture, storage, and spatial dividers.\n\n'
    'Natural light is complemented by a targeted LED spotlight system, '
    'emphasizing materials and surfaces. Graphic communication is integrated '
    'into the architecture through vinyl graphics applied directly to the glass '
    'partitions.\n\n'
    'The overall design is conceived as a flexible, modular, and adaptable '
    'system, capable of evolving alongside the company’s changes and growth. '
    'It is an architecture in constant transformation, where materials, '
    'structure, and furniture come together to create an identity that is '
    'consistent with the spirit of Iguanafix.')

MEMORIA_PARFUMERIE = (
    'En Parfumerie, la arquitectura se concibe como una herramienta para '
    'construir y expresar el ADN de la marca, transformando más de treinta '
    'años vinculados a la belleza y al cuidado personal en una experiencia '
    'espacial contemporánea. El proyecto propone una identidad basada en la '
    'sobriedad, la precisión y una elegancia contenida, donde cada material '
    'participa de un mismo relato.\n\n'
    'El GRC configura una secuencia rítmica de dispositivos de '
    'exhibición que ordenan el espacio y otorgan identidad al perímetro. '
    'En contraste, el mueble central de acero introduce una geometría '
    'orgánica que articula el recorrido e invita al descubrimiento. El piso '
    'de roble aporta calidez y una dimensión sensorial, mientras espejos, '
    'molduras y gargantas de iluminación expanden sutilmente los '
    'límites del espacio. La luz, precisa y silenciosa, acompaña al '
    'producto sin competir con él.\n\n'
    'Así, comprar deja de ser únicamente un acto comercial para '
    'convertirse en un ritual de elección y cuidado. Materialidad, luz, '
    'reflejos y recorridos construyen un lenguaje reconocible: una arquitectura '
    'que traduce el ADN de Parfumerie y entiende la belleza y el consumo como '
    'parte de un modo de vida.')

MEMORIA_PARFUMERIE_EN = (
    'At Parfumerie, architecture is conceived as a tool to shape and express the '
    'brand’s DNA, translating more than thirty years of experience in beauty '
    'and personal care into a contemporary spatial experience. The project '
    'proposes an identity rooted in restraint, precision, and understated '
    'elegance, where every material contributes to a unified narrative.\n\n'
    'GRC defines a rhythmic sequence of display elements that organizes the space '
    'and gives identity to its perimeter. In contrast, the central steel fixture '
    'introduces an organic geometry that structures the circulation and '
    'encourages discovery. Oak flooring brings warmth and a sensory dimension, '
    'while mirrors, moldings, and recessed lighting details subtly expand the '
    'perceived boundaries of the space. The lighting, precise and unobtrusive, '
    'enhances the products without competing with them.\n\n'
    'In this way, shopping moves beyond a purely commercial act to become a '
    'ritual of selection and care. Materiality, light, reflections, and '
    'circulation come together to create a recognizable language: an architecture '
    'that translates Parfumerie’s DNA and understands beauty and consumption '
    'as part of a way of life.')

CORRECCIONES_19_08 = {
    # Los tres Uala. Los nombres los fija el Word; el estado de Nicaragua II
    # tambien ("OBRA CONCLUIDA").
    'uala-gigena': {
        'titulo': alguno(('Ualá Gigena', 'Ualá 1', 'Ualá III'),
                         'Ualá Gigena'),
    },
    'uala-office': {
        'titulo': alguno(('Ualá', 'Ualá 1'), 'Ualá Nicaragua I'),
    },
    'uala-ii': {
        'titulo': alguno(('Ualá II', 'Ualá 2'), 'Ualá Nicaragua II'),
        'estado': valor('en_proyecto', 'concluida'),
    },

    # Estados marcados en rojo sobre la ficha.
    'cafe-artois':    {'estado': valor('concluida', 'en_proyecto')},
    'kavak-oficinas': {'estado': valor('en_proyecto', 'concluida')},

    # IguanaFix: estado, superficie y la memoria que subieron al Drive.
    'iguanafix': {
        'estado': valor('en_proyecto', 'concluida'),
        'superficie': completar_vacio('320 m²'),
        'memoria': completar_vacio(MEMORIA_IGUANAFIX),
        'memoria_en': completar_vacio(MEMORIA_IGUANAFIX_EN),
    },

    # Parfumerie: solo faltaba la memoria; el resto de la ficha ya coincidia
    # con la del Drive.
    'parfumerie': {
        'memoria': completar_vacio(MEMORIA_PARFUMERIE),
        'memoria_en': completar_vacio(MEMORIA_PARFUMERIE_EN),
    },

    'luccianos-caballito': {'superficie': completar_vacio('220 m²')},

    # "Sacar el arq de Luciano y josue. - Solo saca el arq, deja sus nombres."
    # Se habian borrado los dos nombres enteros; van de vuelta, sin el titulo.
    'cerveceria-austral': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Camila Lacarpia'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Camila Lacarpia', 'Luciano Cichanowski', 'Josué Solano']),
    },
}

# Tercer Word, del 20/08/2026.
CORRECCIONES_20_08 = {
    # "CORREGIR ANO PROYECTO ROKET (2023)". Lo confirma el Drive, donde la
    # carpeta 81-Roket cuelga del ano 2023.
    'roket': {
        'anio': valor('2024', '2023'),
    },
    # El tercer Word contesta los dos metrajes que faltaban. Eran las dos
    # unicas fichas del sitio sin superficie, porque el dato no estaba cargado
    # en ningun lado.
    'aire-libre': {
        'superficie': completar_vacio('988 m\u00b2'),
    },
    'juan-valdez': {
        'superficie': completar_vacio('177 m\u00b2'),
    },
    # "La memoria descriptiva de Comedor Diario: sacar esta obra". La obra se
    # habia dado de alta el 20/08 con sus once fotos y su ficha tecnica, pero
    # sin memoria, porque en el Drive no hay. El estudio prefiere no publicarla
    # antes que publicarla sin texto.
    #
    # Se despublica y no se borra: los datos y las fotos quedan, y alcanza con
    # volver publicada a true para que aparezca de nuevo. Del sitio la saca
    # panel_sitio.py, que es el paso que borra las paginas de las obras que la
    # base ya no publica.
    'comedor-diario': {
        'publicada': valor(True, False),
    },
}

for _slug, _campos in CORRECCIONES_20_08.items():
    CORRECCIONES.setdefault(_slug, {}).update(_campos)


# La memoria de Elyaki, del Drive, subida el 20/08/2026 a las 16:24 por
# publicaciones@estudiohma.com.
#
# El archivo que estaba en su carpeta -"Elyaki - Memoria Descriptiva.doc"-
# contenia el texto de Mamba Bar palabra por palabra. El estudio lo borro y
# subio en su lugar YAKITORI_VICTORIA_BROWN_Memoria, en castellano e ingles.
#
# Es de Elyaki y no de Victoria Brown, que comparte direccion y esta a dos
# metros: el texto dice "en menos de 60 metros cuadrados" y la ficha de Elyaki
# tiene 57 m2; Victoria Brown tiene 385 m2 y su propia memoria de 2013. Yakitori
# es la parrilla japonesa de adelante; Victoria Brown, el bar escondido detras
# de la puerta de ladrillo que el texto describe.
#
# Va tal cual lo mando el estudio, incluido "bandeolas" en el primer parrafo.
CORRECCIONES.setdefault('elyaki', {}).update({
    'memoria': texto_normalizado(
        "El proyecto parte de un gran reto, preservar la identidad del restaurante existente, oculto tras su puerta de ladrillo y fusionarla con el nuevo proyecto. El bar existente, Victoria Brown, tiene una identidad cercana al steampunk brit\u00e1nico, que nada tiene que ver con el nuevo proyecto.\r\n\r\nLa superposici\u00f3n de identidades deb\u00eda respetar la actual identidad del hidden bar, logrando una integraci\u00f3n con el nuevo proyecto. La decisi\u00f3n de un callej\u00f3n de Tokio ayudo con la est\u00e9tica de graffiti callejero, logrando un mix de identidades sobre la fachada y el muro ficticio de acceso al bar, como si hubiera sido intervenida espont\u00e1neamente realmente por artistas callejeros.\r\n\r\nEl existente muro ficticio sirvi\u00f3 como escenograf\u00eda de un muro del callej\u00f3n de la ciudad de Tokio. Partimos del concepto de contaminaci\u00f3n visual t\u00edpico de los Yakitori alley o Piss Alley, donde se estilan comer el yakitori tradicional, producto estrella de este restaurant & bar.\r\n\r\nLa utilizaci\u00f3n de cables el\u00e9ctricos simula la t\u00edpica contaminaci\u00f3n visual de Tokio. La reinterpretaci\u00f3n de transformadores de luz devenidos en artefactos cuelgan desde los cables formando figuras piramidales que rompen con la simetr\u00eda.\r\n\r\nLa modulaci\u00f3n estructural que divide el espacio frente a las barras, con sus cajones y banderas que cuelgan es referencia directa de estos puestos de comida callejera. Del mismo modo la presencia de la vegetaci\u00f3n.\r\n\r\nLos tonos fucsia y azul el\u00e9ctrico son parte integral de la identidad a partir de la influencia de la atmosfera de ne\u00f3n t\u00edpica de Tokio. El equipo de branding ha trabajado con el uso de im\u00e1genes de m\u00fasicos tradicionales del pop & tropical para la identidad visual. Su logo e isotipo componen un juego de figuras que rotadas simula el alfabeto Kanji, bajo la simple denominaci\u00f3n de elyaki (reductivo de yakitori).\r\n\r\nLa idea de arte callejero y cultura popular es parte integral de la decoraci\u00f3n, todo ello fusionado el isotipo intervenido con stencils sobre la grafica impresa aplicada sobre el interior y la fachada.\r\n\r\nLa presencias de las m\u00e1scaras sagradas japonesas Hannya, Tengu, Ko omote, Hyottoko, Kitsune, pintadas especialmente con los colores propios de la identidad del bar, todas ellas forman parte de la est\u00e9tica del espacio.\r\n\r\nAdem\u00e1s la presencia de una imponente huerta hidrop\u00f3nica forma parte de las visuales de este callej\u00f3n de Tokio, proponiendo una escena m\u00e1s que interesante para su visualizaci\u00f3n. La huerta est\u00e1 completa de especies para el consumo de ambos restaurantes elyaki y su hidden bar Victoria Brown tambi\u00e9n dise\u00f1o de nuestra autor\u00eda.",
        "Dos mundos, una puerta. En menos de 60 metros cuadrados se despliega un eclecticismo radical: un callej\u00f3n de ingreso donde la contaminaci\u00f3n visual neon, asfalto h\u00famedo, bandeolas, cables a\u00e9reos expresan su protagonismo. Aqu\u00ed se respira Yakitori\u2014comida al paso, urgencia, verdad de la noche urbana. Pero detr\u00e1s del muro de ladrillo rojo oxidado existe otro universo: Victoria Brown, bar de cocteler\u00eda refinada donde la Reina Victoria, transfigurada en Geisha, custodia la sofisticaci\u00f3n.\n\nLa arquitectura es acto de revelaci\u00f3n. El muro divisor no es muro\u2014es puerta secreta, frontera m\u00f3vil. Se desplaza, se corre, expone lo oculto. Frente a la calle: urgencia, est\u00e9tica del caos, paleta nocturna de neon verde y p\u00farpura, postes de luz industriales, carteles superpuestos en ideogramas y vinilos degradados. Materiales crudos: ladrillo, cables visibles, asfalto estampado en pavimento.\n\nDetr\u00e1s: quietud. Un gabinete de curiosidades donde la Reina Victoria\u2014en quimono negro y rojo, ojos afilados de Kabuki\u2014reina sobre botellas destiladas. Luz c\u00e1lida, m\u00f3vil, que tiembla sobre ornamentaci\u00f3n oriental y brit\u00e1nica fundidas. Iluminaci\u00f3n industrial suspendida convive con linternas de papel blanco calado.\n\nEl espacio funciona como paradoja: entra como turista al Yakitori, descubre como viajero en un gabinete de \u00e9poca. La puerta de ladrillo es met\u00e1fora y mecanismo. Atravesarla es abandonar la captura de Tokyo moderno para habitar un tiempo suspendido, donde Victoria Geisha presencia cada bebida como acto de transformaci\u00f3n. Neon y brocado cohabitan. Lo r\u00e1pido y lo ritual convergen. Dos Tokyos, un mismo latido."),
    'memoria_en': texto_normalizado(
        "The project starts from a great challenge, to preserve the identity of the existing bar hidden behind its back door and merge it with the new project. The existent bar , Victoria Brown, has a british steampunk identity, that has nothing to do with the new project. The superposition of identities had to respect the current hidden bar identity, achieving an integration with the new project. The decision of an alley in Tokyo helped with the aesthetics of street graffiti, achieving a mix of identities on the fa\u00e7ade and the fictitious wall of access to the bar, as if it had been spontaneously intervened by street artists. The existing fictitious wall (door entrance to the hidden bar) served as a scenography of a typical wall at a city Tokio's alley. We started from the concept of visual contamination typically from the \"Piss Alley\", where they usually eat the traditional yakitori, top product of this restaurant &amp; bar. The use of electric cables simulates the typical visual pollution of Tokyo. The reinterpretation of street lightings turned into artifacts hang from a bunch of electrical cables forming pyramidal figures, creating a plastic vegetation ceiling.\r\n\r\nThe structural modulation that divides the space at the bar area, with their wooden beer creates and branded hanged flags is a direct reference of the alleys street food stalls of Tokio. The fuchsia and electric blue tones are an integral part of the identity from the influence of the neon atmosphere typical of Tokyo. The branding team has worked with the use of images of traditional pop & tropical musicians for visual identity.\r\n\r\nTheir logo and isotype compose a set of figures that simulates the Kanji alphabet, under the simple name of elyaki (reductive of yakitori). The idea of street art and popular culture is an integral part of the decoration, all this fused with the isotype intervened with stencils on the printed graphic applied on the interior and facade. The presence of the Japanese sacred masks Hannya, Tengu, Ko omote, Hyottoko, Kitsune, specially painted with the colours of the bar\u2019s identity, all form part of the aesthetics of the space. In addition, the presence of an imposing hydroponic orchard forms part of the visuals of this Tokyo alley, proposing a scene that is more than interesting for its visualisation. The garden is full of species for consumption in both Elyaki restaurants and its hidden bar Victoria Brown also designed by our firm.",
        "Two worlds, one door. In less than 60 square meters, a radical eclecticism unfolds: an entrance alley where the visual overload of neon, wet asphalt, projecting signs, and overhead cables takes center stage. Here, the atmosphere is unmistakably Yakitori\u2014food on the go, urgency, the raw truth of the urban night. Yet behind the wall of weathered red brick lies another universe: Victoria Brown, a refined cocktail bar where Queen Victoria, transformed into a Geisha, presides over an atmosphere of sophistication.\n\nThe architecture becomes an act of revelation. The dividing wall is not merely a wall\u2014it is a secret door, a shifting boundary. It slides, moves aside, and exposes what has been concealed. Facing the street: urgency, an aesthetic of chaos, a nocturnal palette of green and purple neon, industrial light poles, overlapping signs with ideograms, and weathered vinyl graphics. Raw materials prevail: brick, exposed wiring, and asphalt-textured paving.\n\nBehind it: stillness. A cabinet of curiosities where Queen Victoria\u2014dressed in a black and red kimono, with the sharp, dramatic gaze of Kabuki\u2014reigns over bottles of distilled spirits. Warm, shifting light flickers across a fusion of Eastern and British ornamentation. Suspended industrial lighting coexists with intricately cut white paper lanterns.\n\nThe space operates as a paradox: one enters Yakitori as a tourist and discovers, as a traveler, a period cabinet of curiosities. The brick door is both metaphor and mechanism. Crossing its threshold means leaving behind the sensory rush of modern Tokyo and entering a suspended moment in time, where Victoria Geisha presides over each drink as an act of transformation. Neon and brocade coexist. Speed and ritual converge. Two Tokyos, one shared heartbeat."),
})


for _slug, _campos in CORRECCIONES_19_08.items():
    CORRECCIONES.setdefault(_slug, {}).update(_campos)



def sumar_memorias_en_pendientes():
    ruta = os.path.join(RAIZ, 'docs', 'memorias_en_agosto.json')
    with io.open(ruta, encoding='utf-8') as archivo:
        traducciones = json.load(archivo)
    for slug, traduccion in traducciones.items():
        CORRECCIONES.setdefault(slug, {})['memoria_en'] = completar_vacio(traduccion)


sumar_memorias_en_pendientes()


def si_falta(marca, nuevo):
    """Reemplaza el texto solo si perdio un fragmento que el original si tiene.

    Sirve para reponer una memoria recortada sin pisar una edicion posterior
    del estudio: si el texto ya contiene la marca, se lo deja como esta.
    """
    def aplicar(actual):
        if isinstance(actual, str) and marca in actual:
            return actual
        return nuevo
    return aplicar


# Memoria original de Aire Libre, del Drive del estudio
# ("ESP Memoria AIRE LIBRE + ficha tecnica.docx"). La version cargada habia
# perdido el arranque del segundo parrafo -"Inspirados en los antiguos green
# houses"- y tenia otros dos parrafos partidos al medio.
MEMORIA_AIRE_LIBRE = (
    'Cada decisión en este proyecto fue concebida bajo un mismo enfoque, '
    'buscamos crear un oasis botánico emplazado en pleno caos urbano. Esta '
    'línea rectora marcó un norte que determinó cada una de las definiciones '
    'proyectuales desde lo espacial arquitectónico, pasando por la elección de '
    'materiales, equipamiento, recursos gráficos, y principalmente '
    'intervenciones paisajísticas.\n\n'
    'Inspirados en los antiguos “green houses” de la Inglaterra del fines del '
    'siglo XIX, estas grandes construcciones de acero y cristal prefabricadas '
    'que en plena revolución industrial albergaban tanto la exuberancia de la '
    'vegetación salvaje de los nuevos continentes y a su vez las reuniones de '
    'la realeza, en AIRE LIBRE buscamos reflejar desde el lenguaje '
    'arquitectónico contemporáneo esta misma dualidad: la rusticidad de un '
    'vivero junto a la sofisticación de la alta coctelería. Los antiguos '
    'cristales son ahora placas moduladas de policarbonato traslúcido que '
    'conforman fachadas tanto interiores como exteriores, y las viejas '
    'estructuras de acero se reemplazan por bastidores metálicos que modulan '
    'dichas fachadas.\n\n'
    'En el mismo sentido la propuesta gastronómica aporta desde su enfoque '
    'también ecléctico, clásico pero moderno, hecho posible combinando una '
    'cocina de fuegos a leña mediante un gran horno de barro construido '
    'artesanalmente, acompañada de una cocina de alta tecnología y complejidad '
    'técnica, siendo ambas complementarias y a la vista.\n\n'
    'El proyecto se desarrolla en dos plantas sumando más de 900m2 entre '
    'interiores y exteriores. A partir de un foyer de acceso que hace de '
    'recepción los espacios se articulan integrando áreas abiertas y cerradas, '
    'cubiertas y descubiertas, todas siempre abordadas bajo el mismo '
    'tratamiento conceptual, desde lo material, la iluminación y las '
    'estrategias de biofilia, generando como resultado la indefinición entre el '
    'adentro y el afuera.\n\n'
    'La paleta tanto cromática como material fue siempre regida a partir de la '
    'decisión de naturaleza y la nobleza de sus materiales, tanto en interiores '
    'como en exteriores. Texturas de hormigones pulidos y martelinados, '
    'aberturas en madera maciza, sumado a revestimientos pétreos, costras de '
    'granito en frentes de barra, espejos envejecidos y la utilización de '
    'tablones de madera recuperada, acompañados por la abundancia botánica en '
    'cada rincón del local logran a la perfección el ambiente buscado.\n\n'
    'Este proyecto no podría sostenerse sin tener resuelto desde un principio '
    'el alto grado de mantenimiento que requiere una intervención con semejante '
    'presencia de vegetación. Para ello se diseñó una compleja red de riego '
    'automatizado mediante un circuito cerrado de circulación de agua '
    'fertilizada que trabaja en conjunto con equipos de iluminación que, a '
    'contraturno del uso del local, se activan para garantizar riego y '
    'fotosíntesis en la totalidad de las plantas tanto interiores como '
    'exteriores. Para completar este sistema, se instaló en todos los espacios '
    'exteriores una red de foggers que en días especialmente calurosos '
    'proyectan al aire gotas de agua pulverizada garantizando el fresco y '
    'confort a los usuarios.\n\n'
    'La serenidad en los espacios y materiales, en contraposición a la '
    'complejidad técnica del proyecto supo lograr como resultados espacios de '
    'encuentro y de disfrute para brindar al AIRE LIBRE.')

MEMORIA_AIRE_LIBRE_EN = (
    'Every decision in this project was conceived under the same approach: we '
    'sought to create a botanical oasis located in the middle of urban chaos. '
    'This guiding line marked a north that determined each of the project '
    'definitions from the architectural space, through the choice of materials, '
    'equipment, graphic resources, and mainly landscape interventions.\n\n'
    'Inspired by the old ‘green houses’ of late 19th century England, these '
    'large prefabricated steel and glass constructions that in the midst of the '
    'industrial revolution housed both the exuberance of the wild vegetation of '
    'the new continents and the gatherings of royalty, in AIRE LIBRE we seek to '
    'reflect this same duality in contemporary architectural language: the '
    'rusticity of a greenhouse together with the sophistication of the high '
    'cocktail bar. The old glass panes are now modulated translucent '
    'polycarbonate plates that form both interior and exterior facades, and the '
    'old steel structures are replaced by metal frames that modulate these '
    'facades.\n\n'
    'In the same sense, the gastronomic proposal is also eclectic in its '
    'approach, classic but modern, made possible by combining a wood-fired '
    'kitchen with a large handmade clay oven, accompanied by a high-tech and '
    'technically complex kitchen, both of which are complementary and '
    'visible.\n\n'
    'The project is developed over two floors, totalling more than 900m2 '
    'between indoors and outdoors. From an access foyer that acts as a '
    'reception, the spaces are articulated integrating open and closed, covered '
    'and uncovered areas, all of them always approached under the same '
    'conceptual treatment, from the material, lighting and biophilia '
    'strategies, generating as a result the indefinition between inside and '
    'outside.\n\n'
    'The chromatic and material palette was always governed by the decision of '
    'nature and the nobility of its materials, both in interiors and exteriors. '
    'Textures of polished and hammered concrete, solid wood openings, added to '
    'stone cladding, granite crusts on the bar fronts, aged mirrors and the use '
    'of reclaimed wood planks, accompanied by the abundance of botanical plants '
    'in every corner of the premises, perfectly achieve the desired '
    'ambience.\n\n'
    'This project could not be sustained without having resolved, in the first '
    'place, the high degree of maintenance required by the vegetation. A '
    'complex automated irrigation network was designed by a closed circuit of '
    'circulating fertilised water that works in conjunction with lighting '
    'equipment that is activated in counter-time with the use of the premises, '
    'to guarantee irrigation and photosynthesis in all the plants, both indoors '
    'and outdoors. To complete this system, a network of foggers was installed '
    'in all the outdoor spaces which, on particularly hot days, spray water '
    'droplets into the air, guaranteeing coolness and comfort for users.\n\n'
    'The serenity of the spaces and materials, in contrast to the technical '
    'complexity of the project, resulted in spaces for meeting and enjoyment in '
    'the outdoor.')

CORRECCIONES.setdefault('aire-libre', {}).update({
    'memoria': si_falta('Inspirados en los antiguos', MEMORIA_AIRE_LIBRE),
    'memoria_en': si_falta('Inspired by the old', MEMORIA_AIRE_LIBRE_EN),
})

MEMORIAS_DRIVE = os.path.join(RAIZ, 'docs', 'memorias_drive.json')


def _mas_larga(nueva):
    """Repone la memoria del Drive solo si la del sitio quedo mas corta.

    Varias memorias entraron recortadas. Hyatt Ziva es el extremo: el Drive
    tiene 1756 palabras repartidas en trece espacios -lobby, buffet, pool bar-
    y en el sitio habian quedado 179, o sea el primer parrafo.

    La condicion es que la del sitio sea mas corta: asi repone lo que falta y
    no pisa una memoria que el estudio haya editado desde el panel ni las
    correcciones que el cliente mando por Word.
    """
    def aplicar(actual):
        if isinstance(actual, str) and len(actual.split()) >= len(nueva.split()) * 0.9:
            return actual
        return nueva
    return aplicar


def _cargar_memorias_drive():
    if not os.path.isfile(MEMORIAS_DRIVE):
        return
    with io.open(MEMORIAS_DRIVE, encoding='utf-8') as archivo:
        datos = json.load(archivo)
    for slug, campos in datos.items():
        if slug.startswith('_'):
            continue
        CORRECCIONES.setdefault(slug, {}).update(
            (campo, _mas_larga(texto)) for campo, texto in campos.items() if texto)


_cargar_memorias_drive()

# La ficha tecnica aparecio despues en la carpeta 90-Supervielle del Drive.
# Solo completa los campos vacios para no pisar una edicion posterior del
# estudio desde el panel.
CORRECCIONES.setdefault('banco-supervielle', {}).update({
    'superficie': completar_vacio('550 m²'),
    'ubicacion': completar_vacio(
        'S. Fernández 198 esq. Laprida, San Isidro, Provincia de Buenos Aires'),
    'tipologia': completar_vacio('Banco + workplace'),
    'equipo': completar_vacio([
        'Arq. Fernando Hitzig',
        'Arq. Leonardo Militello',
        'Arq. Pilar Velasco',
        'Arq. Julieta Leibovich',
    ]),
})

MEMORIAS_ORIGINALES = os.path.join(RAIZ, 'docs', 'memorias_originales.json')


def _cargar_memorias_originales():
    """Repone la memoria del Drive donde el sitio publicaba una traduccion.

    Tres obras -Manduca, Kavak Hub y Mamba Bar- tenian su memoria traducida de
    ida y vuelta: el texto salio del castellano del estudio, paso por el ingles
    y volvio. Se nota en el vocabulario, que deja de ser el del estudio -en
    Manduca "porteños" habia quedado en "vecinos", "callejuelas" en "callejones"
    y "vieja aldea" en "antiguo pueblo"- y en Kavak Hub habia dejado ademas dos
    errores de gramatica a la vista: "El primero paso" y "el desarrollo lo
    grafico".

    El primer Word del 19/08/2026 pide lo contrario: "Utiliza las memorias
    descriptivas originales de cada proyecto. Que estan buenas para usarlas".

    La Bienal de Venecia entra por otro motivo: su texto no estaba traducido
    sino recortado a la mitad. El archivo del estudio trae las dos versiones
    una detras de la otra -castellano hasta el renglon "Abstract", ingles
    despues- y el sitio publicaba 350 palabras de las 802 que tiene la parte en
    castellano: faltaban los cinco cruces de inteligencias con sus obras y sus
    materiales, y el apartado de materiales. Por eso esta entrada repone
    tambien el campo en ingles.

    No entra por _mas_larga porque una traduccion mide casi lo mismo que su
    original -Kavak Hub tenia 241 palabras contra 250- y esa condicion nunca se
    cumplia. Entra por texto_normalizado, que compara contra el texto traducido
    palabra por palabra: si el estudio lo edita desde el panel deja de
    coincidir, y entonces no se pisa.
    """
    if not os.path.isfile(MEMORIAS_ORIGINALES):
        return
    with io.open(MEMORIAS_ORIGINALES, encoding='utf-8') as archivo:
        datos = json.load(archivo)
    for slug, campos in datos.items():
        if slug.startswith('_'):
            continue
        for campo, par in (('memoria', ('viejo', 'nuevo')),
                           ('memoria_en', ('viejo_en', 'nuevo_en'))):
            antes, despues = campos.get(par[0]), campos.get(par[1])
            if antes and despues:
                CORRECCIONES.setdefault(slug, {})[campo] = texto_normalizado(antes, despues)


_cargar_memorias_originales()

def reponer_arranque(cola, completo):
    """Le devuelve a un parrafo el comienzo que perdio al importarse.

    Aire Libre y Malabia llegaron con un parrafo empezando a mitad de frase.
    No estaban partidos -eso lo arregla unir_parrafos_cortados-: les faltaban
    las primeras palabras. Se compara contra el original del Drive.
    """
    def aplicar(actual):
        if not isinstance(actual, str) or completo in actual:
            return actual
        return actual.replace(cola, completo, 1)
    return aplicar


# "En el 'encastre' entre patios y espacios interiores radica la expresion
# maxima del proyecto." El sitio arrancaba en "entre patios". Sale de
# HMA_M1918_Memoria descriptiva.docx, en la carpeta de Malabia del Drive.
CORRECCIONES.setdefault('malabia', {}).update({
    'memoria': reponer_arranque(
        'entre patios y espacios interiores radica la expresión máxima',
        'En el “encastre” entre patios y espacios interiores radica la expresión máxima'),
    'memoria_en': reponer_arranque(
        'between courtyards and interior spaces lies the fullest expression',
        'In the “encastre” between courtyards and interior spaces lies the fullest expression'),
})

# Cierre valido de parrafo. Se incluyen las dos comillas tipograficas porque
# PH El Salvador enumera pedidos del comitente entrecomillados y no llevan punto.
CIERRE_PARRAFO = re.compile(u'[.!?…:;)”“"»]\\s*$')


def unir_parrafos_cortados(texto):
    """Vuelve a unir un parrafo que quedo partido en mitad de una oracion.

    Al cargar las memorias varias quedaron cortadas: un parrafo termina sin
    puntuacion y el siguiente arranca en minuscula, o sea que era una sola
    oracion partida en dos. El cliente lo marco en Aire Libre -el texto cortaba
    en "A partir de un"-, en Edificio del Plata y en otras.

    Solo une ese caso. Si el parrafo siguiente empieza en mayuscula lo que
    falta es el punto final, no la union, y ahi el corte se respeta: unir dos
    oraciones distintas seria peor que dejar la puntuacion floja.

    Si no hay nada que unir devuelve el texto original tal cual, sin
    normalizar saltos, para no marcar como cambiada una memoria que esta bien.
    """
    if not isinstance(texto, str) or not texto.strip():
        return texto

    partes = [p.strip() for p in re.split(r'\n\s*\n', texto.replace('\r\n', '\n'))
              if p.strip()]
    unidas = []
    for parrafo in partes:
        if (unidas and not CIERRE_PARRAFO.search(unidas[-1])
                and parrafo[:1].islower()):
            unidas[-1] = unidas[-1] + ' ' + parrafo
        else:
            unidas.append(parrafo)

    if len(unidas) == len(partes):
        return texto
    return '\n\n'.join(unidas)


def corregir(obras):
    cambios = {}
    por_slug = {o['slug']: o for o in obras}
    for slug, campos in CORRECCIONES.items():
        obra = por_slug.get(slug)
        if not obra:
            continue
        for campo, transformar in campos.items():
            anterior = obra.get(campo)
            nuevo = transformar(anterior)
            if nuevo != anterior:
                obra[campo] = nuevo
                cambios.setdefault(slug, {})[campo] = nuevo

    # Pasada general: ningun parrafo de memoria puede terminar en mitad de una
    # oracion. Va sobre todas las obras, no solo sobre las que el cliente
    # alcanzo a marcar.
    for obra in obras:
        for campo in ('memoria', 'memoria_en'):
            anterior = obra.get(campo)
            unido = unir_parrafos_cortados(anterior)
            if unido != anterior:
                obra[campo] = unido
                cambios.setdefault(obra['slug'], {})[campo] = unido

    return cambios


def corregir_textos(textos):
    cambios = {}
    por_clave = {t['clave']: t for t in textos}
    for clave, campos in TEXTOS_CORRECCIONES.items():
        fila = por_clave.get(clave)
        if not fila:
            continue
        for campo, transformar in campos.items():
            anterior = fila.get(campo)
            nuevo = transformar(anterior)
            if nuevo != anterior:
                fila[campo] = nuevo
                cambios.setdefault(clave, {})[campo] = nuevo
    return cambios


def parchear_supabase(cambios, url, clave):
    cabeceras = {
        'apikey': clave,
        'Authorization': 'Bearer ' + clave,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal',
    }
    for slug, campos in cambios.items():
        pedido = urllib.request.Request(
            url + '/rest/v1/obras?slug=eq.' + slug,
            data=json.dumps(campos, ensure_ascii=False).encode('utf-8'),
            headers=cabeceras,
            method='PATCH')
        with urllib.request.urlopen(pedido, timeout=30):
            pass


def parchear_textos_supabase(cambios, url, clave):
    cabeceras = {
        'apikey': clave,
        'Authorization': 'Bearer ' + clave,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal',
    }
    for clave_texto, campos in cambios.items():
        pedido = urllib.request.Request(
            url + '/rest/v1/textos?clave=eq.' + clave_texto,
            data=json.dumps(campos, ensure_ascii=False).encode('utf-8'),
            headers=cabeceras,
            method='PATCH')
        with urllib.request.urlopen(pedido, timeout=30):
            pass


def desde_supabase(url, clave):
    campos = sorted({campo for cs in CORRECCIONES.values() for campo in cs})
    pedido = urllib.request.Request(
        url + '/rest/v1/obras?select=slug,' + ','.join(campos),
        headers={'apikey': clave, 'Authorization': 'Bearer ' + clave})
    with urllib.request.urlopen(pedido, timeout=30) as respuesta:
        return json.loads(respuesta.read().decode('utf-8'))


def textos_desde_supabase(url, clave):
    pedido = urllib.request.Request(
        url + '/rest/v1/textos?select=clave,es,en',
        headers={'apikey': clave, 'Authorization': 'Bearer ' + clave})
    with urllib.request.urlopen(pedido, timeout=30) as respuesta:
        return json.loads(respuesta.read().decode('utf-8'))


def main(supabase):
    if supabase:
        url = os.environ.get('SUPABASE_URL', '').rstrip('/')
        clave = os.environ.get('SUPABASE_SERVICE_KEY', '')
        if not url or not clave:
            raise SystemExit('Faltan SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno.')
        obras = desde_supabase(url, clave)
        cambios = corregir(obras)
        parchear_supabase(cambios, url, clave)
        print('correcciones aplicadas en Supabase: %d obras' % len(cambios))
        cambios_textos = corregir_textos(textos_desde_supabase(url, clave))
        parchear_textos_supabase(cambios_textos, url, clave)
        print('correcciones aplicadas en Supabase: %d textos' % len(cambios_textos))
        return

    ruta = os.path.join(RAIZ, 'docs', 'panel_datos.json')
    with io.open(ruta, encoding='utf-8') as archivo:
        obras = json.load(archivo)
    cambios = corregir(obras)
    if cambios:
        with io.open(ruta, 'w', encoding='utf-8', newline='\n') as archivo:
            json.dump(obras, archivo, ensure_ascii=False, indent=1)
            archivo.write('\n')
    print('correcciones aplicadas en panel_datos.json: %d obras' % len(cambios))

    ruta_textos = os.path.join(RAIZ, 'docs', 'panel_textos.json')
    with io.open(ruta_textos, encoding='utf-8') as archivo:
        textos = json.load(archivo)
    cambios_textos = corregir_textos(textos)
    if cambios_textos:
        with io.open(ruta_textos, 'w', encoding='utf-8', newline='\n') as archivo:
            json.dump(textos, archivo, ensure_ascii=False, indent=1)
            archivo.write('\n')
    print('correcciones aplicadas en panel_textos.json: %d textos' % len(cambios_textos))


if __name__ == '__main__':
    main('--supabase' in sys.argv[1:])
