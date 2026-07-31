# -*- coding: utf-8 -*-
"""Segunda capa del diccionario: mas patrones y las entradas que quedaban."""
import re
import en_dic
from en_dic import DIC, REGLAS

DIC.update({
    'Osten Coffee Shop — Casa FOA': 'Osten Coffee Shop — Casa FOA',
    'Osten Coffee Shop, Casa FOA 2025': 'Osten Coffee Shop, Casa FOA 2025',
    'Casa FOA 2025': 'Casa FOA 2025',
    'Cafetería — Casa FOA 2025': 'Coffee shop — Casa FOA 2025',
    'Creando&nbsp;&amp; construyendo ideas': 'Creating&nbsp;&amp; building ideas',
    'Página no encontrada — Hitzig Militello Arquitectos':
        'Page not found — Hitzig Militello Architects',
    'Hitzig Militello Arquitectos — Arquitectura y diseño comercial':
        'Hitzig Militello Architects — Architecture and commercial design',
    'Estudio de Arquitectura en Buenos Aires | Hitzig Militello Arquitectos':
        'Architecture Studio in Buenos Aires | Hitzig Militello Architects',
    '© 2026 Hitzig Militello Arquitectos': '© 2026 Hitzig Militello Architects',
    'Última actualización: 29 de julio de 2026': 'Last updated: 29 July 2026',
    'Restaurant &amp; Bar Design Awards': 'Restaurant &amp; Bar Design Awards',
    'Restaurant & Bar Design Awards': 'Restaurant & Bar Design Awards',
    'Premios Nacionales ARCH FADEA': 'ARCH FADEA National Awards',
    'Ver Premio Nacional ARQ-FADEA': 'See ARQ-FADEA National Award',
    'Society of British and International Interior Design (SBID)':
        'Society of British and International Interior Design (SBID)',
    'Bienal de Arquitectura de Venecia': 'Venice Architecture Biennale',
    '18ª Bienal Internacional de Arquitectura': '18th International Architecture Biennale',
    'Pabellón argentino, Bienal de Arquitectura de Venecia':
        'Argentine pavilion, Venice Architecture Biennale',
    'Pabellón de exposición temporal': 'Temporary exhibition pavilion',
    'Residencias y restauración — concurso privado':
        'Residences and hospitality — private competition',
    'Sala de concierto, night club y restaurante — en proceso':
        'Concert hall, night club and restaurant — in progress',
    'Reforma de oficinas — Buenos Aires.': 'Office refurbishment — Buenos Aires.',
    'Concurso privado para el Centro Cultural de España en Buenos Aires.':
        'Private competition for the Spanish Cultural Centre in Buenos Aires.',
    'Centro Cultural de España en Buenos Aires': 'Spanish Cultural Centre in Buenos Aires',
    'Restaurante en Av. del Libertador y Blanco Encalada — en proceso.':
        'Restaurant on Av. del Libertador and Blanco Encalada — in progress.',
    'Restaurante argentino en el Saedan Mall de Riad.':
        'Argentine restaurant at the Saedan Mall in Riyadh.',
    'Cafetería Juan Valdez sobre Avenida Las Heras.':
        'Juan Valdez coffee shop on Avenida Las Heras.',
    'Local de Tostado Café Club en Miami.': 'Tostado Café Club venue in Miami.',
    'Local de perfumería de 131 m² en el shopping Terrazas de Mayo.':
        '131 m² perfumery at the Terrazas de Mayo shopping centre.',
    'Nueva sede de Ualá en el Paseo Gigena: 9.002 m² de oficinas.':
        'New Ualá headquarters at Paseo Gigena: 9,002 m² of offices.',
    'Lobby y rooftop de una torre residencial en Madero Harbour.':
        'Lobby and rooftop of a residential tower at Madero Harbour.',
    '50.000 m² de zonas comunes y locales comerciales en Barbados, Caribe.':
        '50,000 m² of common areas and retail in Barbados, Caribbean.',
    '300 m² cubiertos y 15.000 m² de playa de estacionamiento':
        '300 m² indoor and 15,000 m² of parking',
    '950 m² de intervención general': '950 m² of overall intervention',
    'Terrazas de Mayo Shopping, Los Polvorines, Buenos Aires':
        'Terrazas de Mayo Shopping, Los Polvorines, Buenos Aires',
    'Shopping Dot Baires, Buenos Aires': 'Dot Baires Shopping, Buenos Aires',
    'Rambla Wilson y Av. Sarmiento, Montevideo':
        'Rambla Wilson and Av. Sarmiento, Montevideo',
    'C1425, Buenos Aires, Argentina': 'C1425, Buenos Aires, Argentina',
    '100 NE 38th St &amp; NE 1st Ave, Design District, Miami, Florida':
        '100 NE 38th St &amp; NE 1st Ave, Design District, Miami, Florida',
    'Áreas VIP — Buenos Aires, Argentina — 640 m².':
        'VIP areas — Buenos Aires, Argentina — 640 m².',
    'Selección de materiales y bocetos sobre la mesa del estudio':
        'Materials and sketches on the studio table',
    'Revisión de planos de obra en el estudio':
        'Reviewing construction drawings at the studio',
    'Interior de Hyatt Ziva, Barbados': 'Interior of Hyatt Ziva, Barbados',
    '¿Querés ver estos principios aplicados? Conocé los':
        'Want to see these principles applied? Take a look at the',
    'proyectos que llevamos construidos.': 'projects we have built.',
    'premios y distinciones internacionales desde 2008.':
        'international awards and distinctions since 2008.',
    'm² de arquitectura gastronómica, de la barra íntima al mercado.':
        'm² of hospitality architecture, from the intimate bar to the market hall.',
    'm² proyectados en hotelería y espacios comerciales.':
        'm² designed across hotels and retail spaces.',
    'Para cualquier consulta sobre esta política podés escribir a':
        'For any question about this policy you can write to',
    'Podés solicitarnos en cualquier momento el':
        'You may request from us at any time the',
    'Tratamos tus datos sobre la base de tu':
        'We process your data on the basis of your',
    'nombre, dirección de correo electrónico y el mensaje que escribas.':
        'name, email address and the message you write.',
    '— envío de los correos que generan los formularios.':
        '— delivery of the emails generated by the forms.',

    # titulares de prensa
    'El nuevo restaurante de Belgrano en un patio lleno de plantas':
        "Belgrano's new restaurant in a courtyard full of plants",
    'Comer solo sin pedir perdón': 'Eating alone without apologising',
    'Antiche Tentazioni, heladería': 'Antiche Tentazioni, ice cream shop',
    'Stella Artois Stand / Hitzig Militello arquitectos':
        'Stella Artois Stand / Hitzig Militello arquitectos',
    'Williamsburg, espacio al aire libre en Buenos Aires':
        'Williamsburg, an outdoor space in Buenos Aires',
    'Entrevista a Hitzig Militello Architects':
        'Interview with Hitzig Militello Architects',
    'Fogón, restaurante y bar en Riad, Arabia Saudí':
        'Fogón, restaurant and bar in Riyadh, Saudi Arabia',
    'The Nim Bar, fotografía de Federico Kulekdjian':
        'The Nim Bar, photography by Federico Kulekdjian',
    'Tostado Café Club, Buenos Aires': 'Tostado Café Club, Buenos Aires',
    'Reportaje de vivienda en Buenos Aires': 'Feature on a home in Buenos Aires',
    'Aire Libre — arquitectura, naturaleza y gastronomía en equilibrio':
        'Aire Libre — architecture, nature and food in balance',
    'Charla FADU UBA — Taller Maldonado': 'FADU UBA talk — Taller Maldonado',
    'Charla «Arquitectura e Interiorismo», organizada por MARQ y SCA':
        '«Architecture and Interior Design» talk, organised by MARQ and SCA',
    'Oradores Tendiez Experiencias — Auditorio del Museo MALBA':
        'Tendiez Experiencias speakers — MALBA Museum Auditorium',
    'Entrevista «Los Destacados» — Hitzig Militello Arquitectos':
        '«Los Destacados» interview — Hitzig Militello Architects',
    'Entrevista — Galería de Arte Objeto A': 'Interview — Objeto A Art Gallery',
})

# --- superficies -------------------------------------------------------------
AREA = [
    (re.compile(r'^([\d.,]+) m² cubiertos y ([\d.,]+) m² descubiertos$'),
     r'\1 m² indoor and \2 m² outdoor'),
    (re.compile(r'^([\d.,]+) m² cubiertos y ([\d.,]+) m² semicubiertos$'),
     r'\1 m² indoor and \2 m² semi-covered'),
    (re.compile(r'^([\d.,]+) m² cubiertos · ([\d.,]+) m² descubiertos$'),
     r'\1 m² indoor · \2 m² outdoor'),
    (re.compile(r'^([\d.,]+) m² cubiertos · ([\d.,]+) m² semicubiertos$'),
     r'\1 m² indoor · \2 m² semi-covered'),
    (re.compile(r'^([\d.,]+) m² interiores y ([\d.,]+) m² exteriores$'),
     r'\1 m² indoor and \2 m² outdoor'),
    (re.compile(r'^([\d.,]+) m² interior · ([\d.,]+) m² exterior$'),
     r'\1 m² indoor · \2 m² outdoor'),
    (re.compile(r'^([\d.,]+) m² planta baja · ([\d.,]+) m² exterior$'),
     r'\1 m² ground floor · \2 m² outdoor'),
    (re.compile(r'^Lobby ([\d.,]+) m² y rooftop ([\d.,]+) m²$'),
     r'\1 m² lobby and \2 m² rooftop'),
]

REGLAS.extend([
    (re.compile(r'^(.+) — despiece de elementos$'),
     lambda m, tr: '%s — element breakdown' % tr(m.group(1))),
    (re.compile(r'^(.+?), nota sobre (.+)$'),
     lambda m, tr: '%s, article on %s' % (tr(m.group(1)), tr(m.group(2)))),
    (re.compile(r'^(.+?), entrevista$'),
     lambda m, tr: '%s, interview' % tr(m.group(1))),
    (re.compile(r'^Ver (.+)$'), lambda m, tr: 'See %s' % tr(m.group(1))),
    (re.compile(r'^★ (.+)$'), lambda m, tr: '★ %s' % tr(m.group(1))),
    (re.compile(r'^(.+?) · (.+?) — (.+?) — ([\d.,]+ m²\.?)$'),
     lambda m, tr: '%s · %s — %s — %s' % (tr(m.group(1)), m.group(2),
                                          tr(m.group(3)), m.group(4))),
    (re.compile(r'^(.+?) — (.+?) — ([\d.,]+ m²\.?)$'),
     lambda m, tr: '%s — %s — %s' % (tr(m.group(1)), tr(m.group(2)), m.group(3))),
    (re.compile(r'^(.+?) — (.+?) — en (?:proceso|progreso)\.?$'),
     lambda m, tr: '%s — %s — in progress' % (tr(m.group(1)), tr(m.group(2)))),
    (re.compile(r'^(.+?) de ([\d.,]+) m² en (.+?)\.$'),
     lambda m, tr: '%s m² %s in %s.' % (m.group(2), tr(m.group(1)).lower(), tr(m.group(3)))),
    (re.compile(r'^(.+?) – (.+)$'),
     lambda m, tr: '%s – %s' % (tr(m.group(1)), tr(m.group(2)))),
])

_base = en_dic.traducir


def traducir(t):
    r = _base(t)
    if r is not None:
        return r
    for pat, rep in AREA:
        if pat.match(t):
            return pat.sub(rep, t)
    return None


en_dic.traducir = traducir
