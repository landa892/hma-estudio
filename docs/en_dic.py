# -*- coding: utf-8 -*-
"""Diccionario castellano -> ingles del sitio de HMA.

   Tres capas, en este orden:
     1. REGLAS   patrones que se resuelven solos (titulos, alt de galeria)
     2. DIC      traduccion explicita
     3. PASA     lo que queda igual: nombres propios, direcciones, premios

   Lo que no cae en ninguna capa lo denuncia el generador, para que no se
   escape nada sin traducir.
"""
import re

# --- lo que no se traduce ----------------------------------------------------
PASA_EXACTO = {
    'HMA', 'Hitzig Militello Arquitectos', 'Fernando Hitzig', 'Leonardo Militello',
    'Instagram', 'LinkedIn', 'Facebook', 'YouTube', 'Behance', 'Pinterest', 'WhatsApp',
    'LinkedIn ↗', 'Argentina', 'Brasil', 'Chile', 'Barbados', 'Florida', 'Italia',
    'Chicago', 'Frankfurt', 'Londres', 'Las Vegas', 'Los Ángeles', 'Miami',
    'Buenos Aires', 'Buenos Aires, Argentina', 'Arabia Saudita', 'Estados Unidos',
    'Architecture MasterPrize', 'German Design Awards', 'A+ Awards — Architizer',
    'A+Firms — Architizer', 'IIDA International Interior Design Awards',
    'LIV Hospitality Design Awards', 'Hospitality Design Awards', 'Prix Versailles',
    'Bienal SCA-CPAU', 'Clarín ARQ — Categoría Interiorismo', 'Surface Design Awards',
    'Accor Hotels Design & Technical Summit', 'Design Boom', 'ArchDaily — Reino Unido',
    'La Nación — Argentina', 'Metalocus — España', 'Wallpaper* — Reino Unido',
    'Architectural Digest — México', 'Architectural Digest México',
    'G&amp;G Magazine — Italia', 'G&amp;G Magazine, Italia', 'Newsweek Argentina',
    'Hospitality Design — EE.UU.', 'Agencia de Acceso a la Información Pública',
    'Ley N° 25.326 de Protección de los Datos Personales',
    'Email', 'Formulario', 'Grilla', 'Lista',
}

PASA_PATRON = [
    re.compile(r'^[\d\s.,·—–\-+%/m²ºª°]+$'),                    # cifras y superficies sueltas
    re.compile(r'^[\w.+-]+@[\w.-]+$'),                          # correos
    re.compile(r'^https?://'),
    re.compile(r'^[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚÜÑáéíóúüñ\'’.\-]*'         # direcciones: Calle 123, Ciudad
               r'(?:\s+[\wÁÉÍÓÚÜÑáéíóúüñ\'’.\-]+)*\s+\d[\d\-]*'
               r'(?:,\s.+)?$'),
    re.compile(r'^(?:Av\.|Avenida|Calle|Camila|Edificio|Campo|Madero|Paseo)\s'),
]


def pasa(t):
    if t in PASA_EXACTO:
        return True
    # El patron de direcciones es "palabras + numero + , resto", y sin un tope
    # de largo se come parrafos enteros: "Al encontrarnos en un piso 23, con
    # una planta libre expuesta a visuales..." lo cumple al pie de la letra y
    # salia sin traducir. Una direccion entra comoda en setenta caracteres.
    if len(t) > 70:
        return any(p.match(t) for p in PASA_PATRON[:3])
    return any(p.match(t) for p in PASA_PATRON)


# --- interfaz y navegacion ---------------------------------------------------
DIC = {
    # menu y estructura
    'Inicio': 'Home',
    'Proyectos': 'Projects',
    'Prensa': 'Press',
    'Prensa y News': 'Press & News',
    'Premios': 'Awards',
    'Estudio': 'Studio',
    'Contacto': 'Contact',
    'Buscar': 'Search',
    'Navegación': 'Navigation',
    'Menú de navegación': 'Navigation menu',
    'Abrir menú': 'Open menu',
    'Cerrar menú': 'Close menu',
    'Saltar al contenido': 'Skip to content',
    'Ir al buscador': 'Go to search',
    'Ir a inicio': 'Go to home',
    'Ir a contacto': 'Go to contact',
    'Hitzig Militello Arquitectos — Inicio': 'Hitzig Militello Architects — Home',
    'Abrir opciones de contacto': 'Open contact options',
    'Seguinos': 'Follow us',
    'Legales': 'Legal',
    'Política de privacidad': 'Privacy policy',
    'Este sitio': 'This site',
    'Hablemos': "Let's talk",
    'Hablemos de tu proyecto': "Let's talk about your project",
    'Conocer el estudio': 'About the studio',
    'Galería': 'Gallery',
    'Todas las fotos': 'All photos',
    'La obra en video': 'The project on video',
    'Ver en YouTube': 'Watch on YouTube',
    'Ver el canal': 'Visit the channel',
    'Más proyectos': 'More projects',
    'Ver todos los proyectos': 'See all projects',
    'Ver el proyecto': 'See the project',
    'Datos técnicos:': 'Project specs:',

    # buscador
    'Buscar en el sitio': 'Search the site',
    'Escribí para buscar': 'Type to search',
    'Buscador del sitio de Hitzig Militello Arquitectos.':
        'Site search for Hitzig Militello Architects.',

    # contacto y formularios
    'Enviá tu consulta': 'Send us a message',
    'Enviar mensaje': 'Send message',
    'Enviar un mensaje': 'Send a message',
    'Contanos sobre tu proyecto': 'Tell us about your project',
    'Iniciar conversación': 'Start a conversation',
    'Chatear ahora': 'Chat now',
    'Formulario de contacto:': 'Contact form:',
    'Formulario previo a WhatsApp:': 'Pre-WhatsApp form:',
    'Dejanos tu nombre y teléfono y seguimos la charla por WhatsApp.':
        'Leave your name and phone and we can continue on WhatsApp.',
    'Contactá a Hitzig Militello Arquitectos, en Buenos Aires.':
        'Get in touch with Hitzig Militello Architects, in Buenos Aires.',
    '; responderemos a la brevedad.': '; we will get back to you shortly.',

    # error
    'Error 404': 'Error 404',
    'Esta página no existe': 'This page does not exist',

    # ficha tecnica
    'Tipo': 'Type',
    'Ubicación': 'Location',
    'País': 'Country',
    'Superficie': 'Area',
    'Año': 'Year',

    # categorias y programas
    'Gastronómico': 'Hospitality',
    'Hotelería &amp; Comercial': 'Hotels &amp; Retail',
    'Cultural &amp; Institucional': 'Cultural &amp; Institutional',
    'Corporativo': 'Corporate',
    'Residencial': 'Residential',
    'Bar de cocktails': 'Cocktail bar',
    'Bar y restaurante': 'Bar and restaurant',
    'Restaurante y bar': 'Restaurant and bar',
    'Restaurante': 'Restaurant',
    'Restaurante y pastelería': 'Restaurant and patisserie',
    'Cafetería': 'Coffee shop',
    'Cafetería y restaurante': 'Coffee shop and restaurant',
    'Café': 'Café',
    'Heladería': 'Ice cream shop',
    'Cremería': 'Creamery',
    'Comida rápida': 'Fast food',
    'Club nocturno': 'Night club',
    'Mercado': 'Market',
    'Hotel': 'Hotel',
    'Hotel — concurso internacional': 'Hotel — international competition',
    'Hotel — en progreso': 'Hotel — in progress',
    'Oficina': 'Office',
    'Oficinas': 'Offices',
    'Co-work y co-living': 'Co-working and co-living',
    'Hub comercial y oficinas': 'Retail hub and offices',
    'Edificio multifamiliar': 'Multi-family building',
    'Edificio residencial — en proceso': 'Residential building — in progress',
    'Vivienda multifamiliar': 'Multi-family housing',
    'Atelier, artes y oficios': 'Atelier, arts and crafts',
    'Centro cultural — concurso privado': 'Cultural centre — private competition',
    'Centro de desarrollo gastronómico': 'Hospitality development centre',
    'Diseño integral': 'Integral design',
    'Stand': 'Stand',
    'Showroom': 'Showroom',
    'Perfumería': 'Perfumery',
    'Templo': 'Temple',
    'Pabellón': 'Pavilion',

    # premios
    'Ganador': 'Winner',
    'Finalista': 'Finalist',
    'Mención': 'Mention',
    'Seleccionado': 'Selected',
    'Premios y distinciones': 'Awards and distinctions',
    'Años de trayectoria': 'Years of practice',

    # prensa
    'Destacadas': 'Featured',
    'Actualidad': 'Latest',
    'Lo último': 'Latest videos',
    'Medios': 'Media',

    # estudio
    '01 — Fundadores': '01 — Founders',
    '02 — Qué hacemos': '02 — What we do',
    '03 — Cómo trabajamos': '03 — How we work',
    '04 — Reconocimientos': '04 — Recognition',
    '05 — Docencia y conferencias': '05 — Teaching and talks',
    '06 — Contacto': '06 — Contact',
    'Cómo trabajamos': 'How we work',
    'Qué hacemos': 'What we do',
    'Autenticidad': 'Authenticity',
    'Enfoque creativo': 'Creative approach',
    'Identidad de ADN': 'DNA identity',
    'Artesanos de las marcas': 'Craftsmen of brands',
    'Fernando Hitzig y Leonardo Militello, socios fundadores':
        'Fernando Hitzig and Leonardo Militello, founding partners',
    'El equipo trabajando sobre un proyecto en pantalla':
        'The team working on a project on screen',
    'Arquitecto, FADU — Universidad de Buenos Aires, 2002.':
        'Architect, FADU — University of Buenos Aires, 2002.',
    'Desde 2006 — Buenos Aires': 'Since 2006 — Buenos Aires',
    'Desde 2006 — obra construida en': 'Since 2006 — built work in',
    'Más de': 'More than',
    'proyectos construidos en Argentina y el mundo — este es uno de ellos.':
        'projects built in Argentina and around the world — this is one of them.',
    'premios y distinciones internacionales desde 2004.':
        'international awards and distinctions since 2004.',
    'países.': 'countries.',

    # privacidad
    '1. Quién es responsable': '1. Who is responsible',
    '2. Qué datos recogemos': '2. What data we collect',
    '3. Para qué los usamos': '3. What we use it for',
    '4. Con qué base legal': '4. On what legal basis',
    '5. Con quién los compartimos': '5. Who we share it with',
    '6. Cuánto tiempo los conservamos': '6. How long we keep it',
    '7. Cookies y seguimiento': '7. Cookies and tracking',
    '8. Tus derechos': '8. Your rights',
    '9. Seguridad': '9. Security',
    '10. Menores de edad': '10. Minors',
    '11. Cambios en esta política': '11. Changes to this policy',
    'El responsable del tratamiento de los datos es':
        'The data controller is',
    'En Argentina, el tratamiento de datos personales está regulado por la':
        'In Argentina, the processing of personal data is governed by',

    # idioma
    'English': 'Español',
}


REGLAS = [
    # "Moshu | Hitzig Militello Arquitectos"
    (re.compile(r'^(.*?) \| Hitzig Militello Arquitectos$'),
     lambda m, tr: '%s | Hitzig Militello Architects' % tr(m.group(1))),
    # alt de galeria: "moshu — foto 7"
    (re.compile(r'^(.*?) — foto (\d+)$'),
     lambda m, tr: '%s — photo %s' % (tr(m.group(1)), m.group(2))),

    # alt de los planos: "Moshu — plano 3"
    (re.compile(r'^(.*?) — plano (\d+)$'),
     lambda m, tr: '%s — plan %s' % (tr(m.group(1)), m.group(2))),
    # "Ir a Benedetta"
    (re.compile(r'^Ir a (.+)$'),
     lambda m, tr: 'Go to %s' % tr(m.group(1))),
    # "Ver las 39 fotos" / "Ver los 30 videos"
    (re.compile(r'^Ver las (\d+) fotos$'),
     lambda m, tr: 'See all %s photos' % m.group(1)),
    (re.compile(r'^Ver los (\d+) videos$'),
     lambda m, tr: 'See all %s videos' % m.group(1)),
    (re.compile(r'^Ver menos fotos$'), lambda m, tr: 'See fewer photos'),
    (re.compile(r'^Ver menos videos$'), lambda m, tr: 'See fewer videos'),
    # "YouTube — 22 may 2024"
    (re.compile(r'^YouTube — (\d+) (\w+) (\d{4})$'),
     lambda m, tr: 'YouTube — %s %s %s' % (m.group(1), MESES.get(m.group(2), m.group(2)), m.group(3))),
]

MESES = {'ene': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'abr': 'Apr', 'may': 'May',
         'jun': 'Jun', 'jul': 'Jul', 'ago': 'Aug', 'sep': 'Sep', 'oct': 'Oct',
         'nov': 'Nov', 'dic': 'Dec'}

MESES_LARGOS = {'Enero': 'January', 'Febrero': 'February', 'Marzo': 'March',
                'Abril': 'April', 'Mayo': 'May', 'Junio': 'June', 'Julio': 'July',
                'Agosto': 'August', 'Septiembre': 'September', 'Octubre': 'October',
                'Noviembre': 'November', 'Diciembre': 'December'}


def traducir(t):
    """Devuelve la traduccion, o None si nadie la cubre."""
    if t in DIC:
        return DIC[t]
    # Los meses van ANTES de pasa(): "Junio 2023" cumple el patron de
    # direcciones (palabras + numero) y salia intacto, en castellano.
    m = re.match(r'^(%s) (\d{4})$' % '|'.join(MESES_LARGOS), t)
    if m:
        return '%s %s' % (MESES_LARGOS[m.group(1)], m.group(2))
    if pasa(t):
        return t
    for pat, fn in REGLAS:
        mm = pat.match(t)
        if mm:
            return fn(mm, lambda x: traducir(x) or x)
    return None
