# -*- coding: utf-8 -*-
"""Rehace el archivo de Prensa desde las tres fuentes del estudio.

El Word del 21/08/2026 pide que Prensa deje de ser nueve tarjetas: cada nota
tiene que estar, con su medio, su año, su pais y su obra, y al clickear tiene
que ir a la nota online si existe o a una pagina propia con el escaneo si no.
Nueve tarjetas no alcanzaban ni para empezar, y el dato no estaba en la base:
estaba repartido en tres lados que nadie habia cruzado.

    WordPress   el export de 2026-08-03. El sitio viejo tenia una pagina por
                nota -cpt_prensa- con medio, pais, fecha, obra y link externo.
                Es la unica fuente que dice si la nota existe online, que es
                justo lo que el Word usa para decidir a donde lleva la tarjeta.
                Ojo: el sitio era bilingue, cada nota aparece dos veces con el
                mismo slug, y lo unico que las separa es el <link> -/prensa/
                contra /en/prensa/-.
    Drive       publicaciones/<anio>/<nota>/: las paginas escaneadas de la
                revista. Es la unica fuente con imagenes, porque los archivos
                del WordPress viejo ya no responden: el dominio sirve el sitio
                nuevo y staging quedo con otro WordPress, asi que las 1426 URLs
                del export dan 404.
    CV          el Word extendido. Trae las clases y las conferencias, que el
                Word manda a una lista aparte, y los links de las notas que el
                export no tenia.

Corre en la maquina del desarrollador, como drive_sync.py: necesita Pillow y
los ZIP del Drive. Desde la nube no se puede. Lo que si viaja al repositorio es
el resultado -docs/prensa_datos.json y assets/prensa/-, y de ahi lo toman los
pasos del build, que si corren en Vercel.

    python docs/prensa_desde_fuentes.py --verificar   # no escribe, informa
    python docs/prensa_desde_fuentes.py
"""
import difflib
import glob
import io
import json
import os
import re
import sys
import unicodedata
import zipfile
from collections import defaultdict
from xml.sax.saxutils import unescape

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIPS = os.environ.get('HMA_DRIVE_ZIPS', r'E:\descargas\pagina hma-*.zip')
EXPORT = os.environ.get(
    'HMA_WP_EXPORT',
    os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads',
                 'estudiohma.WordPress.2026-08-03.xml'))
CV = os.environ.get(
    'HMA_CV',
    os.path.join(os.environ.get('USERPROFILE', ''), 'Downloads',
                 'CV HITZIG MILITELLO ARCHITECTS-EXTENDIDO.docx'))

DATOS = os.path.join(RAIZ, 'docs', 'prensa_datos.json')
NOVEDADES = os.path.join(RAIZ, 'docs', 'prensa_novedades.json')
GALERIAS = os.path.join(RAIZ, 'assets', 'prensa')
TAPAS = os.path.join(RAIZ, 'assets', 'press')

# Mismos numeros que drive_sync.py: las fichas y las notas comparten visor.
LADO_MAYOR = 1800
CALIDAD = 82
ANCHO_PORTADA = 1200

# Las nueve notas que ya estan publicadas conservan su slug. No es cosmetico:
# esas URLs estan compartidas, y ademas son las nueve filas que el panel ya
# tiene en prensa_publicaciones. Cambiarles el slug las duplicaria; perderlas
# hace que panel_prensa borre sus carpetas y las nueve pasen a dar 404.
#
# Cada una se lleva UNA nota y despues la reserva se apaga. La primera version
# de esto ataba por (medio, año) sin consumir la reserva y las tres notas de La
# Nacion de 2025 salieron con el mismo slug: tres paginas escribiendose encima.
#   slug ya publicado -> (medio de referencia, año, mes o '')
YA_PUBLICADAS = {
    'comer-solo-sin-pedir-perdon': ('Newsweek', '2026', ''),
    'el-nuevo-restaurante-de-belgrano-en-un-patio-lleno': ('La Nacion', '2025', 'febrero'),
    'antiche-tentazioni-heladeria': ('G&G Magazine', '2023', 'febrero'),
    'stella-artois-stand-hitzig-militello-arquitectos': ('ArchDaily', '2023', ''),
    'un-lugar-para-sentarse-al-aire-libre-en-la': ('Metalocus', '2020', 'octubre'),
    'williamsburg-espacio-al-aire-libre-en-buenos-aires': ('Designboom', '2020', 'octubre'),
    # La ficha viva dice "Mayo 2019" y el export tiene Marzo y Diciembre: se
    # ata por año, que la URL importa mas que el mes.
    'entrevista-a-hitzig-militello-architects': ('Hospitality Design', '2019', ''),
    'fogon-restaurante-y-bar-en-riad-arabia-saudi': ('Designboom', '2019', ''),
    'the-nim-bar-fotografia-de-federico-kulekdjian': ('Designboom', '2018', ''),
}

# Subcarpetas que no son una nota aparte sino el formato del mismo escaneo.
# Sin esto "Newsweek Mayo 2026/JPG/" salia como un medio llamado "Newsweek Mayo
# 2026 JPG".
FORMATOS = {'jpg', 'jpeg', 'png', 'pdf', 'tif', 'tiff', 'web', 'alta', 'baja',
            'originales', 'original', 'fotos', 'imagenes', 'imagenes web',
            'prensa', 'scan', 'scans', 'escaneos', 'planos', 'fotos obras',
            'fotos estudio', 'material', 'texto', 'textos'}


def es_carpeta_envoltorio(sub):
    """Si la subcarpeta es el envoltorio de un archivo y no una nota aparte.

    Las carpetas de 2003 y 2004 vienen del Drive con cada archivo adentro de
    una carpeta que se llama igual que el archivo -"hm7.jpg/hm7.jpg"-, que es
    como Google empaqueta lo que convivia con un .7z. Sin esto salian notas
    llamadas "Diario Pagina 12 tapa pg12 JPG".
    """
    nombre = sin_tildes(sub).strip()
    return (nombre in FORMATOS
            or nombre.endswith(('.jpg', '.jpeg', '.png', '.pdf', '.doc',
                                '.docx', '.tif', '.tiff', '.7z')))

# Lo que el CV manda a la lista y no a las tarjetas. El Word: "OJO CON LAS
# CLASES Y CONFERENCIAS. Esas si vamos a tener que ponerlas en lista".
RUBROS = (
    ('CONFERENCIA', ('conferencia', 'conferencias', 'congreso', 'jornada')),
    ('CHARLA', ('charla', 'charlas', 'panel', 'mesa redonda', 'tendiez')),
    ('DOCENCIA', ('profesor', 'profesora', 'docencia', 'catedra', 'titular',
                  'uade', 'fadi', 'universidad', 'master in', 'kunsthal')),
    ('CLASE MAGISTRAL', ('clase magistral', 'masterclass', 'workshop')),
    ('PODCAST', ('podcast',)),
    ('EXPOSICION', ('exposicion', 'muestra', 'bienal', 'expone')),
    ('JURADO', ('jurado',)),
)

# Palabras que aparecen de un lado y no del otro y no distinguen nada.
RUIDO = re.compile(r'\b(revista|diario|magazine|nota|entrevista|n|nro|no|num|'
                   r'vol|edicion|the)\b')

MES = re.compile(r'^(ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|JULIO|AGOSTO|'
                 r'SEPTIEMBRE|OCTUBRE|NOVIEMBRE|DICIEMBRE)\s+(\d{4})$', re.I)


# --------------------------------------------------------------- utilidades

def sin_tildes(texto):
    t = unicodedata.normalize('NFD', (texto or '').lower())
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn')


def normal(texto):
    """Sin acentos, sin signos y sin las palabras que no distinguen."""
    t = re.sub(r'[^a-z0-9]+', ' ', sin_tildes(texto))
    return ' '.join(RUIDO.sub(' ', t).split())


def parecido(a, b):
    """Cuanto se parecen dos nombres ya normalizados, de 0 a 1.

    Dos medidas y se toma la mejor. Por palabras sola no alcanza: el Drive
    escribe "Revista Linving n#91" con una ene de mas y "revistaplot.com" sin
    el espacio, y en los dos casos no comparten ni un token con lo que dice el
    WordPress. Comparar tambien las cadenas pegadas, letra a letra, los
    recupera: el cruce sube de 130 notas a 142.
    """
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    pa, pb = set(a.split()), set(b.split())
    tokens = len(pa & pb) / float(len(pa | pb)) if pa and pb else 0.0
    letras = difflib.SequenceMatcher(
        None, a.replace(' ', ''), b.replace(' ', '')).ratio()
    return max(tokens, letras)


MESES = ('enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
         'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre')
# El export mezcla idiomas en el mismo campo: "November 2025" y "Noviembre 2025"
# conviven porque el sitio era bilingue.
MESES_EN = ('january', 'february', 'march', 'april', 'may', 'june', 'july',
            'august', 'september', 'october', 'november', 'december')


def orden_de_fecha(fecha):
    """(año, mes) para ordenar. El campo viene escrito de cinco maneras.

    "Mayo 2026", "November 2025", "21.04.2026", "2019", "setiembre 2014": es un
    campo que se cargo a mano durante veinte años. Sin normalizarlo, ordenar por
    texto pone Abril antes que Mayo y 2003 antes que 2026.
    """
    t = sin_tildes(fecha or '')
    anio = re.search(r'(19|20)\d{2}', t)
    anio = int(anio.group(0)) if anio else 0
    mes = 0
    punto = re.match(r'\s*(\d{1,2})[./-](\d{1,2})[./-](?:19|20)\d{2}', t)
    if punto:
        mes = int(punto.group(2))
    else:
        for i, nombre in enumerate(MESES, 1):
            if nombre in t or (nombre == 'septiembre' and 'setiembre' in t):
                mes = i
                break
        else:
            for i, nombre in enumerate(MESES_EN, 1):
                if re.search(r'\b%s\b' % nombre, t):
                    mes = i
                    break
    return (anio, mes)


def slugificar(texto):
    t = re.sub(r'[^a-z0-9]+', '-', sin_tildes(texto)).strip('-')
    return re.sub(r'-{2,}', '-', t)[:70].strip('-')


def cdata(bloque, etiqueta):
    m = re.search(r'<%s><!\[CDATA\[(.*?)\]\]></%s>' % (etiqueta, etiqueta),
                  bloque, re.S)
    if m:
        return m.group(1)
    m = re.search(r'<%s>(.*?)</%s>' % (etiqueta, etiqueta), bloque, re.S)
    return unescape(m.group(1)) if m else ''


# ------------------------------------------------------------- las fuentes

def leer_wordpress():
    """Las notas en castellano y publicadas del export, con su obra y su link."""
    if not os.path.isfile(EXPORT):
        raise SystemExit('No esta el export del WordPress: %s' % EXPORT)
    xml = io.open(EXPORT, encoding='utf-8', errors='replace').read()

    notas, obras = [], {}
    for bloque in re.findall(r'<item>.*?</item>', xml, re.S):
        tipo = cdata(bloque, 'wp:post_type')
        if tipo == 'cpt_proyectos':
            # El titulo y no el slug: los slugs del WordPress viejo son otros
            # -numeros sueltos, "a757", "es4633"- y de las 44 obras que las
            # notas mencionan solo 15 coincidian con las del sitio.
            obras[cdata(bloque, 'wp:post_id')] = cdata(bloque, 'title').strip()
            continue
        if tipo != 'cpt_prensa':
            continue
        link = cdata(bloque, 'link')
        if '/en/prensa/' in link or cdata(bloque, 'wp:status') != 'publish':
            continue
        meta = dict(re.findall(
            r'<wp:meta_key><!\[CDATA\[(.*?)\]\]></wp:meta_key>\s*'
            r'<wp:meta_value><!\[CDATA\[(.*?)\]\]></wp:meta_value>',
            bloque, re.S))
        notas.append({
            'medio': cdata(bloque, 'title').strip(),
            'slug_viejo': cdata(bloque, 'wp:post_name'),
            'fecha_post': cdata(bloque, 'wp:post_date'),
            'pais': (meta.get('pais_prensa') or '').strip(),
            'fecha': (meta.get('fecha_prensa') or '').strip(),
            'descripcion': (meta.get('descripcion_corta_prensa') or '').strip(),
            'link': (meta.get('link_externo_prensa') or '').strip(),
            'obras_id': re.findall(r's:\d+:"(\d+)"',
                                   meta.get('seleccion_proyecto') or ''),
        })
    for n in notas:
        n['obra_titulo'] = next((obras[i] for i in n['obras_id'] if i in obras), '')
    return notas


def leer_drive():
    """{(anio, carpeta): [(zip, entrada), ...]} de publicaciones/ en los ZIP.

    La forma normal es publicaciones/<anio>/<nota>/<pagina>.jpg. Pero algunas
    carpetas no tienen paginas propias y si una subcarpeta por obra -"RETHINKING
    THE FUTURE/Antiche", "RETHINKING THE FUTURE/Benedetta"-: ahi cada subcarpeta
    es una nota distinta y hay que bajar un nivel. Solo se baja cuando arriba no
    hay ninguna imagen, para no partir en pedazos una nota que ademas guarda
    material suelto.
    """
    directas, hondas = defaultdict(list), defaultdict(list)
    archivos = sorted(glob.glob(ZIPS))
    if not archivos:
        raise SystemExit('No hay ZIP del Drive en %s' % ZIPS)
    for ruta in archivos:
        with zipfile.ZipFile(ruta) as z:
            for nombre in z.namelist():
                if '/publicaciones/' not in nombre or nombre.endswith('/'):
                    continue
                if not nombre.lower().endswith(
                        ('.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff')):
                    continue
                partes = nombre.split('/')
                if len(partes) < 5 or '__MACOSX' in partes:
                    continue
                if len(partes) == 5:
                    directas[(partes[2], partes[3])].append((ruta, nombre))
                elif len(partes) == 6:
                    hondas[(partes[2], partes[3])].append(
                        (partes[4], ruta, nombre))

    carpetas = dict(directas)
    for clave, lista in hondas.items():
        if clave in carpetas:
            continue
        for sub, ruta, nombre in lista:
            # "Newsweek Mayo 2026/JPG/" es el mismo escaneo en otro formato, no
            # otra nota: el nombre de la nota se queda como estaba.
            # "MAS ARQ/aire libre jpg" es la nota de una obra guardada en un
            # formato: la obra distingue, el formato no.
            limpio = re.sub(r'[\s_-]+(jpg|jpeg|png|pdf|tif|tiff)\s*$', '',
                            sub, flags=re.I).strip()
            nombre_nota = (clave[1] if not limpio or es_carpeta_envoltorio(limpio)
                           else '%s %s' % (clave[1], limpio))
            carpetas.setdefault((clave[0], nombre_nota), []).append((ruta, nombre))
    for lista in carpetas.values():
        lista.sort(key=lambda x: orden_natural(x[1]))
    return carpetas


def orden_natural(nombre):
    """Ordena Pagina_2 antes que Pagina_10, que es como se lee la revista."""
    base = os.path.basename(nombre)
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r'(\d+)', base)]


def parrafos_del_cv():
    """[(texto, [urls])] en el orden del documento.

    Los hipervinculos de un .docx no estan en el texto: el parrafo referencia un
    rId y la URL vive en word/_rels/document.xml.rels. Hay que cruzarlos.
    """
    with zipfile.ZipFile(CV) as z:
        destino = dict(re.findall(
            r'Id="([^"]+)"[^>]*Target="([^"]+)"',
            z.read('word/_rels/document.xml.rels').decode('utf-8', 'replace')))
        xml = z.read('word/document.xml').decode('utf-8', 'replace')

    fuera = []
    for p in re.findall(r'<w:p[ >].*?</w:p>', xml, re.S):
        # <w:t...> y no <w:t[^>]*>: lo segundo tambien matchea <w:tcPr> y a
        # partir de ahi se traga el XML de la tabla como si fuera texto.
        texto = unescape(u''.join(
            re.findall(r'<w:t(?:\s[^>]*)?>(.*?)</w:t>', p, re.S))).strip()
        links = [destino[r]
                 for r in re.findall(r'<w:hyperlink[^>]*r:id="([^"]+)"', p)
                 if destino.get(r, '').startswith('http')]
        fuera.append((texto, links))
    return fuera


def leer_cv():
    """(prensa, academica) del CV extendido.

    Son dos listas distintas del mismo Word y el Word del 21/08 las manda a dos
    lugares distintos de la pagina. La de prensa arranca en "PUBLICACIONES:
    REVISTAS, LIBROS..." y se agrupa por mes; la academica es "EXPERIENCIA
    ACADEMICA, CONFERENCIAS Y SEMINARIOS WEB" y se agrupa por año. Buscar las
    clases dentro del bloque de prensa no encontraba ninguna: no estan ahi.
    """
    if not os.path.isfile(CV):
        print('aviso: no esta el CV (%s); la lista de novedades queda vacia' % CV)
        return [], []
    ps = parrafos_del_cv()

    def indice(patron):
        return next((i for i, (t, _) in enumerate(ps)
                     if re.match(patron, sin_tildes(t))), None)

    # --- publicaciones, por mes
    prensa, mes = [], None
    inicio = indice(r'publicaciones\s*:') or 0
    for texto, links in ps[inicio:]:
        m = MES.match(texto)
        if m:
            mes = '%s %s' % (m.group(1).capitalize(), m.group(2))
            continue
        if texto and mes:
            prensa.append({'fecha': mes, 'texto': texto.lstrip('- ').strip(),
                           'links': links, 'anio': mes.split()[-1]})

    # --- experiencia academica, por año
    academica = []
    desde = indice(r'experiencia academica')
    hasta = indice(r'afiliaciones')
    if desde is not None:
        anio = ''
        for texto, links in ps[desde + 1:hasta or len(ps)]:
            if not texto:
                continue
            m = re.match(r'^((?:19|20)\d{2})(?:\s*[-–]\s*(?:19|20)\d{2})?\s*:?\s*$',
                         texto)
            if m:
                anio = m.group(1)
                continue
            if texto.startswith('-'):
                academica.append({'texto': texto.lstrip('- ').strip(),
                                  'links': list(links), 'anio': anio})
            elif academica:
                # Renglon de continuacion: el CV parte varias entradas en dos
                # parrafos y el segundo trae la ciudad y a veces el link.
                academica[-1]['texto'] += ' ' + texto
                academica[-1]['links'].extend(links)
    return prensa, academica


# ---------------------------------------------------------------- el cruce

def anio_de(nota):
    m = re.search(r'(19|20)\d{2}', nota.get('fecha') or '')
    return m.group(0) if m else (nota.get('fecha_post') or '')[:4]


def cruzar(notas, carpetas):
    """Le pone a cada nota la carpeta de escaneos que le corresponde.

    Todos los pares posibles primero y despues se resuelven de mejor a peor.
    Ir nota por nota tomando la mejor carpeta libre daba pares peores: una nota
    temprana se llevaba la carpeta que le calzaba justo a otra del mismo año
    -once "Archidiaries" de 2024 compiten por las mismas carpetas-.
    """
    libres = {clave: {'archivos': v, 'norma': normal(clave[1]), 'usada': False}
              for clave, v in carpetas.items()}
    por_anio = defaultdict(list)
    for clave, dato in libres.items():
        por_anio[clave[0]].append((clave, dato))

    pares = []
    for i, nota in enumerate(notas):
        objetivo = normal(nota['medio'])
        for clave, dato in por_anio.get(anio_de(nota), []):
            p = parecido(objetivo, dato['norma'])
            if p >= 0.55:
                pares.append((p, i, clave))
    pares.sort(key=lambda x: (-x[0], x[1]))

    for p, i, clave in pares:
        if libres[clave]['usada'] or notas[i].get('archivos'):
            continue
        libres[clave]['usada'] = True
        notas[i]['archivos'] = libres[clave]['archivos']
        notas[i]['carpeta'] = clave[1]

    # Carpetas del Drive que ninguna nota reclamo: son publicaciones que el
    # export no tenia. Entran igual, con lo que se sabe del nombre y del año.
    sobrantes = []
    for clave, dato in sorted(libres.items()):
        if dato['usada']:
            continue
        sobrantes.append({
            'medio': clave[1],
            'slug_viejo': '',
            'fecha': clave[0],
            'fecha_post': '%s-01-01 00:00:00' % clave[0],
            'pais': '',
            'descripcion': '',
            'link': '',
            'obras_id': [],
            'obra_titulo': '',
            'archivos': dato['archivos'],
            'carpeta': clave[1],
            'solo_drive': True,
        })
    return sobrantes


def links_del_cv(entradas):
    """{(medio normalizado, año): link} para completar lo que el export no trajo."""
    fuera = {}
    for e in entradas:
        externos = [u for u in e['links'] if 'estudiohma.com' not in u]
        if not externos:
            continue
        # "- Aire Libre / Hitzig Militello Arquitectos ArchDaily. Argentina."
        # El medio es lo que va despues del nombre del estudio.
        m = re.search(r'(?:arquitectos|architects)\s*(.+)$', e['texto'], re.I)
        cola = m.group(1) if m else e['texto']
        medio = normal(re.split(r'[.,]', cola)[0])
        if medio:
            fuera.setdefault((medio, e['anio']), externos[0])
    return fuera


def rubro_de(texto):
    """El rotulo de la izquierda en la lista: DOCENCIA, CONFERENCIA, CHARLA."""
    t = sin_tildes(texto)
    for etiqueta, palabras in RUBROS:
        if any(p in t for p in palabras):
            return etiqueta
    return ''


def resumir(texto):
    """El titulo de la fila: la primera oracion, sin el rotulo repetido.

    El CV escribe "Conferencia en TENDIEZ LAB: «...». Buenos Aires, Argentina."
    En la lista el rotulo ya va en la columna de la izquierda, asi que
    repetirlo adelante del titulo lo unico que hace es correr todo a la derecha.
    """
    t = re.sub(r'\s+', ' ', texto).strip()
    t = re.sub(r'^(conferencia|charla|clase magistral|orador|profesor(?:es)?|'
               r'profesor ayudante|ciclo de conferencias|podcast|graduado)\b'
               r'[\s:,–-]*(?:en\s+(?:el|la|los|las)?\s*|de\s+)?', '', t,
               flags=re.I).strip()
    # La ciudad y el pais del final son dato de ficha, no de titulo.
    t = re.sub(r'\s*[.;]\s*[^.;]{0,40},\s*(argentina|espana|españa|mexico|'
               r'méxico|brasil|chile|uruguay|estados unidos|eeuu)\s*\.?\s*$',
               '', t, flags=re.I)
    t = t.strip(' .;,-–')
    return t or re.sub(r'\s+', ' ', texto).strip()


def novedades(academica):
    """Las clases y conferencias del CV, que van en lista y no en tarjeta."""
    fuera = []
    for e in academica:
        externos = [u for u in e['links'] if 'estudiohma.com' not in u]
        fuera.append({
            'rubro': rubro_de(e['texto']) or 'NOVEDAD',
            'titulo': resumir(e['texto']),
            'detalle': re.sub(r'\s+', ' ', e['texto']).strip(),
            'anio': e['anio'],
            'link': externos[0] if externos else '',
        })
    fuera.sort(key=lambda x: x['anio'], reverse=True)
    return fuera


# ------------------------------------------------------------- las imagenes

def convertir(datos, destino, ancho_fijo=None):
    """Guarda la imagen como WebP, del tamano que usa el sitio."""
    try:
        im = Image.open(io.BytesIO(datos)).convert('RGB')
    except Exception:
        return None
    if ancho_fijo:
        alto = max(1, round(im.height * ancho_fijo / im.width))
        im = im.resize((ancho_fijo, alto), Image.LANCZOS)
    elif max(im.size) > LADO_MAYOR:
        e = LADO_MAYOR / float(max(im.size))
        im = im.resize((max(1, round(im.width * e)), max(1, round(im.height * e))),
                       Image.LANCZOS)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    im.save(destino, 'WEBP', quality=CALIDAD, method=6)
    return im.size


def escribir_imagenes(nota, verificar, abiertos):
    """Deja assets/prensa/<slug>/1..N.webp y la tapa. Devuelve los nombres.

    La galeria se rehace entera: si el Drive tiene otra cantidad de paginas que
    la vez pasada, dejar las viejas mezcladas con las nuevas da una nota con
    paginas de dos escaneos distintos.
    """
    carpeta = os.path.join(GALERIAS, nota['slug'])
    if not nota.get('archivos'):
        # Sin carpeta en el Drive no se borra nada: varias de las notas ya
        # publicadas tienen recortes que se armaron antes y son lo unico que
        # hay. Se informan los que ya estan en el repositorio.
        if not os.path.isdir(carpeta):
            return []
        return sorted((n for n in os.listdir(carpeta) if n.endswith('.webp')),
                      key=orden_natural)
    if verificar:
        return ['%d.webp' % i for i in range(1, len(nota['archivos']) + 1)]

    for viejo in glob.glob(os.path.join(carpeta, '*.webp')):
        # Las que administra el panel llevan prefijo y no son del Drive.
        if not os.path.basename(viejo).startswith('panel-'):
            os.remove(viejo)

    nombres, primera = [], None
    for ruta_zip, entrada in nota['archivos']:
        z = abiertos.get(ruta_zip)
        if z is None:
            z = abiertos[ruta_zip] = zipfile.ZipFile(ruta_zip)
        datos = z.read(entrada)
        # La numeracion sigue a las que se pudieron convertir y no al indice del
        # ZIP: si una falla, saltear el numero deja un hueco en la galeria.
        if convertir(datos, os.path.join(carpeta, '%d.webp' % (len(nombres) + 1))):
            nombres.append('%d.webp' % (len(nombres) + 1))
            if primera is None:
                primera = datos

    # La tapa sale de la primera que se pudo convertir, no de la primera del
    # ZIP. G&G Magazine tenia adelante un archivo que Pillow no abre y quedaba
    # con las paginas puestas y sin tapa: la tarjeta salia con la imagen rota.
    if primera is not None:
        convertir(primera, os.path.join(TAPAS, nota['slug'] + '.webp'),
                  ancho_fijo=ANCHO_PORTADA)
    return nombres


# ------------------------------------------------------------------- salida

def titulo_de(nota, obras_del_sitio):
    """Lo que va en negrita en la tarjeta: de que habla la nota.

    Orden: la bajada que el estudio escribio, si la escribio; si no, la obra de
    la que habla; y recien al final el medio. Poner el medio de titulo cuando ya
    va de rotulo arriba deja la tarjeta diciendo dos veces lo mismo.
    """
    # La bajada sirve como titulo solo si es una bajada. En el WordPress viejo
    # ese campo se uso tambien de anotador: hay entradas de varios renglones
    # con los codigos internos de obra y los links pegados -"Obra Publicada:
    # - Office + house luna ( L250) https://..."-. Eso en una tarjeta no es un
    # titulo, es una nota al margen del estudio.
    desc = (nota.get('descripcion') or '').strip()
    if desc and '\n' not in desc and 'http' not in desc and len(desc) <= 120:
        return desc
    obra = nota.get('obra') or ''
    if obra and obra in obras_del_sitio:
        return obras_del_sitio[obra]
    if nota.get('obra_titulo'):
        return nota['obra_titulo']
    return nota['medio']


def atar_obras(notas, obras_del_sitio):
    """Le pone a cada nota el slug de la obra del sitio de la que habla.

    Por slug no se puede: el WordPress viejo numeraba las obras -"10", "a757",
    "es4633"- y de las 44 que las notas mencionan solo 15 coincidian. Por
    titulo normalizado si.
    """
    por_titulo = {normal(t): s for s, t in obras_del_sitio.items()}
    claves = list(por_titulo)
    for nota in notas:
        titulo = normal(nota.get('obra_titulo') or '')
        if not titulo:
            nota['obra'] = ''
            continue
        if titulo in por_titulo:
            nota['obra'] = por_titulo[titulo]
            continue
        cerca = difflib.get_close_matches(titulo, claves, n=1, cutoff=0.82)
        nota['obra'] = por_titulo[cerca[0]] if cerca else ''


def reservar_slugs(notas):
    """Le devuelve su slug a las notas que ya estan publicadas.

    El nombre del medio tiene que coincidir exacto, no parecido. Con parecido
    pasaba lo peor que podia pasar: Fogon y The Nim Bar son de Designboom y el
    Drive no tiene carpeta suya ni el export ficha, asi que la reserva se
    llevaba puestas dos notas ajenas que se escriben parecido -"DESIGN" de 2019
    y "Designing ways" de 2018- y esas dos notas desaparecian del sitio con el
    contenido cambiado. Si no hay coincidencia exacta no se ata nada, y quien
    llama arrastra la ficha vieja tal cual estaba.

    Devuelve los slugs que quedaron sin atar.
    """
    sueltos = []
    for slug, (referencia, anio, mes) in YA_PUBLICADAS.items():
        objetivo = normal(referencia)
        elegida = None
        for nota in notas:
            if nota.get('slug') or anio_de(nota) != anio:
                continue
            if mes and mes not in sin_tildes(nota.get('fecha') or ''):
                continue
            if normal(nota['medio']) == objetivo:
                elegida = nota
                break
        if elegida is not None:
            elegida['slug'] = slug
        else:
            sueltos.append(slug)
    return sueltos


def medio_prolijo(nombre):
    """El nombre del medio a partir del de la carpeta del Drive.

    Las carpetas se nombraron a mano a lo largo de veinte años: algunas gritan
    en mayusculas -"LA NACION"-, otras arrastran el año -"Newsweek Mayo 2026"-
    y otras el numero de edicion con almohadilla -"BOB Mgazine n#170"-. En la
    tarjeta va el nombre del medio, no el de la carpeta.
    """
    t = re.sub(r'\s+', ' ', (nombre or '').replace('_', ' ')).strip()
    t = re.sub(r'\s*[-–]\s*$', '', t)
    # El año al final es dato de fecha, no parte del nombre.
    t = re.sub(r'\s+(?:de\s+)?(?:enero|febrero|marzo|abril|mayo|junio|julio|'
               r'agosto|septiembre|setiembre|octubre|noviembre|diciembre)?\s*'
               r'(?:19|20)\d{2}\s*$', '', t, flags=re.I).strip()
    # El numero de edicion, que las carpetas escriben "n#170", "n°170", "N 46".
    # Ojo con el alcance: una version de esto aceptaba tambien la letra o como
    # simbolo de numero y sin anclar a un digito, asi que "NOTA CLARIN MILANO"
    # salia "N° Ta Clarin Mila N°" y de ahi el slug n-ta-clarin-mila-n. Tiene
    # que haber un numero atras para que sea un numero de edicion.
    t = re.sub(r'\bn\s*[#°º]?\s*(\d+)', r'n° \1', t, flags=re.I).strip()
    # GRITAR no es un estilo: "LA NACION" se escribe como los demas medios.
    if t and t == t.upper() and len(t) > 4:
        t = t.title()
    return t or nombre


def obras_publicadas():
    """{slug: titulo} de las obras que hoy tienen ficha en el sitio."""
    fuera = {}
    for ruta in glob.glob(os.path.join(RAIZ, 'proyectos', '*', 'index.html')):
        slug = os.path.basename(os.path.dirname(ruta))
        m = re.search(r'<h1[^>]*>(.*?)</h1>',
                      io.open(ruta, encoding='utf-8').read(), re.S)
        if m:
            fuera[slug] = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(1))).strip()
    return fuera


def main(verificar):
    print('leyendo el export del WordPress...')
    notas = leer_wordpress()
    print('  %d notas en castellano y publicadas' % len(notas))

    print('leyendo los ZIP del Drive...')
    carpetas = leer_drive()
    print('  %d carpetas de publicaciones, %d archivos'
          % (len(carpetas), sum(len(v) for v in carpetas.values())))

    print('cruzando...')
    sobrantes = cruzar(notas, carpetas)
    notas.extend(sobrantes)
    con = sum(1 for n in notas if n.get('archivos'))
    print('  %d notas con escaneos, %d sin escaneos, %d solo del Drive'
          % (con, len(notas) - con, len(sobrantes)))

    print('leyendo el CV...')
    prensa_cv, academica = leer_cv()
    enlaces = links_del_cv(prensa_cv)
    lista = novedades(academica)
    print('  %d publicaciones, %d links utiles, %d clases y conferencias'
          % (len(prensa_cv), len(enlaces), len(lista)))

    for nota in notas:
        if nota.get('solo_drive'):
            # El mes esta en el nombre de la carpeta -"Newsweek Mayo 2026"- y
            # la carpeta del año sola daria "2026" a secas.
            mes = re.search(r'\b(enero|febrero|marzo|abril|mayo|junio|julio|'
                            r'agosto|septiembre|setiembre|octubre|noviembre|'
                            r'diciembre)\b', sin_tildes(nota['medio']))
            if mes:
                nota['fecha'] = '%s %s' % (mes.group(1).capitalize(),
                                           nota['fecha'])
        nota['medio'] = medio_prolijo(nota['medio'])

    obras_sitio = obras_publicadas()
    atar_obras(notas, obras_sitio)

    for nota in notas:
        nota['anio'] = anio_de(nota)
        if not nota.get('link'):
            nota['link'] = enlaces.get((normal(nota['medio']), nota['anio']), '')

    sueltos = reservar_slugs(notas)

    usados = {n['slug'] for n in notas if n.get('slug')} | set(sueltos)
    for nota in notas:
        if nota.get('slug'):
            continue
        base = slugificar('%s %s' % (nota['medio'], nota['anio'])) or 'publicacion'
        slug, n = base, 2
        while slug in usados:
            slug = '%s-%d' % (base, n)
            n += 1
        usados.add(slug)
        nota['slug'] = slug

    notas.sort(key=lambda n: (orden_de_fecha(n.get('fecha') or n['anio']), n['medio']),
               reverse=True)

    # Lo que ya estaba, para no perder las tapas que se armaron a mano: las
    # nueve notas publicadas tienen su tapa en /assets/press/ con otro nombre
    # -designboom-fogon.webp- y algunas no tienen carpeta en el Drive con que
    # rehacerla.
    previas = {}
    if os.path.isfile(DATOS):
        previas = {n['slug']: n
                   for n in json.load(io.open(DATOS, encoding='utf-8'))}

    abiertos = {}
    salida = []
    for nota in notas:
        imagenes = escribir_imagenes(nota, verificar, abiertos)
        if nota.get('archivos'):
            tapa = '/assets/press/%s.webp' % nota['slug']
        else:
            tapa = (previas.get(nota['slug'], {}) or {}).get('tapa', '')
            if tapa and not os.path.isfile(
                    os.path.join(RAIZ, tapa.lstrip('/').replace('/', os.sep))):
                tapa = ''
        # Un titulo ya escrito no se pisa con el nombre del medio. "Comer solo
        # sin pedir perdon" estaba cargado a mano y el Drive de esa nota solo
        # sabe decir "Newsweek": quedarse con lo que da la fuente era cambiar
        # un titular por el nombre de la revista.
        titulo = titulo_de(nota, obras_sitio)
        viejo = (previas.get(nota['slug'], {}) or {}).get('titulo', '')
        if viejo and titulo == nota['medio'] and viejo != nota['medio']:
            titulo = viejo

        salida.append({
            'slug': nota['slug'],
            'titulo': titulo,
            'obra': nota['obra'],
            'medio': nota['medio'],
            'pais': nota['pais'],
            'fecha': nota['fecha'] or nota['anio'],
            'link': nota['link'],
            'tapa': tapa,
            'imagenes': imagenes,
        })
    for z in abiertos.values():
        z.close()

    # Las publicadas que ninguna fuente reclamo se arrastran como estaban. Son
    # notas que solo viven en el sitio -Designboom no dejo carpeta en el Drive
    # ni ficha en el export- y sacarlas seria romperles la URL.
    for slug in sueltos:
        if slug in previas:
            salida.append(previas[slug])
            print('  se conserva tal cual la nota ya publicada %s' % slug)
        else:
            print('  aviso: %s estaba publicada y no quedo en ninguna fuente'
                  % slug)
    salida.sort(key=lambda n: orden_de_fecha(n['fecha']), reverse=True)

    con_link = sum(1 for n in salida if n['link'])
    print()
    print('publicaciones     : %d' % len(salida))
    print('  con link online : %d  (la tarjeta va a la nota)' % con_link)
    print('  sin link online : %d  (la tarjeta va a su pagina)'
          % (len(salida) - con_link))
    print('  con tapa propia : %d' % sum(1 for n in salida if n['tapa']))
    print('  con obra atada  : %d' % sum(1 for n in salida if n['obra']))
    print('imagenes escritas : %d' % sum(len(n['imagenes']) for n in salida))
    print('novedades en lista: %d' % len(lista))

    if verificar:
        print('\n(--verificar: no se escribio nada)')
        return 0

    io.open(DATOS, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(salida, ensure_ascii=False, indent=1) + '\n')
    io.open(NOVEDADES, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(lista, ensure_ascii=False, indent=1) + '\n')
    print('\nescritos docs/prensa_datos.json y docs/prensa_novedades.json')
    return 0


if __name__ == '__main__':
    sys.exit(main('--verificar' in sys.argv))
