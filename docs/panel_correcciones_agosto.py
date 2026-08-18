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
        'bajada': valor(
            'Local de Tostado Café Club en Miami.',
            'Locales de Tostado Café Club en Argentina, Uruguay, Miami y São Paulo.'),
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
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Leonardo G. Militello', 'Arq. Florencia Schvartzman',
             'Arq. Belen Lepro Delelis'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Florencia Schvartzman', 'Arq. Belen Lepro Delelis']),
    },
    'ph-el-salvador': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Leonardo G. Militello', 'Arq. Carmela Zuleta',
             'Arq. Juliana Zorza', 'Arq. Samira Attar'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Carmela Zuleta', 'Arq. Juliana Zorza', 'Arq. Samira Attar']),
    },
    'uala-gigena': {
        # Las fichas originales de Uala Gigena fueron creadas en 2022. El
        # cliente tambien marco ese ano en la revision final del contenido.
        'anio': valor('2024', '2022'),
        # Habia quedado al final del listado con orden 60 aunque es de 2022.
        'orden': valor(60, 27),
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


def sumar_memorias_en_pendientes():
    ruta = os.path.join(RAIZ, 'docs', 'memorias_en_agosto.json')
    with io.open(ruta, encoding='utf-8') as archivo:
        traducciones = json.load(archivo)
    for slug, traduccion in traducciones.items():
        CORRECCIONES.setdefault(slug, {})['memoria_en'] = completar_vacio(traduccion)


sumar_memorias_en_pendientes()


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
