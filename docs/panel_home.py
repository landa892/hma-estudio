# -*- coding: utf-8 -*-
"""Pone en los banners del home las obras que el estudio marco como destacadas.

   La casilla "destacada" del panel se guardaba y no cambiaba nada. El home
   cierra con tres banners de obra —Indusparquet, Parfumerie y Hyatt Ziva hoy— y
   no habia forma de cambiar cual sale.

   Lo que hace: toma las obras publicadas y destacadas, ordenadas por su orden, y
   reescribe esos tres banners con la primera, la segunda y la tercera.

   De cada banner, tres de las cuatro cosas ya salen de la obra: el enlace, el
   titulo y el parrafo, que es su bajada. Se verifico contra los tres banners que
   ya estaban: el h2 es igual al titulo y el <p> igual a la bajada, palabra por
   palabra. Lo unico propio del banner es el rotulo de arriba, que vive en
   obras.banner_rotulo desde la migracion 0006.

   Que NO toca:

   - El banner de Movistar Arena, que es otro molde: tiene la mencion del
     Architizer con negritas y cursivas adentro y linkea a Instagram. Eso no se
     puede editar desde un panel de campos de texto sin inventar un editor de
     texto rico.
   - El banner de YouTube, que se llena solo.
   - Los separadores entre banners.
   - El id="section-N" de cada banner: la navegacion por puntos de la derecha los
     usa como destino. Se conservan en su lugar aunque cambie la obra.

   La foto es exactamente la misma caratula que usa la obra en Trabajos. Si el
   panel ya publico una portada, usa esa; si no, cae en assets/covers/<slug>.webp
   y despues en la primera foto de la galeria. Asi el home y el listado no
   pueden mostrar dos tapas distintas para una misma obra.

       python docs/panel_home.py --verificar   # no toca nada, solo informa
       python docs/panel_home.py               # desde el JSON local
       python docs/panel_home.py --supabase    # desde la base
"""
import io
import json
import os
import re
import struct
import sys
import urllib.request

from tapas_wordpress import versionar

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.join(RAIZ, 'index.html')
DESTINO_EN = os.path.join(RAIZ, 'docs', 'en_textos_banner.json')
PORTADAS_PANEL = os.path.join(RAIZ, 'docs', 'panel_portadas.json')

# Cuantos banners de este molde hay en el home. Si algun dia se suma o se saca
# uno, este numero y el home se mueven juntos.
RANURAS = 3


def E(t):
    return (t or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ---------------------------------------------------------------------------
# Medidas de un WebP, sin dependencias
# ---------------------------------------------------------------------------

def medidas_webp(ruta):
    """(ancho, alto) de un WebP leyendo la cabecera, o None.

    A mano y no con Pillow: este script corre en el build de Vercel, donde no
    hay nada instalado mas que Python. Una dependencia para leer dos numeros
    seria una razon mas para que el deploy falle.
    """
    try:
        with io.open(ruta, 'rb') as f:
            cab = f.read(30)
    except OSError:
        return None
    if len(cab) < 30 or cab[:4] != b'RIFF' or cab[8:12] != b'WEBP':
        return None
    formato = cab[12:16]
    if formato == b'VP8X':
        # 24 bits little-endian, y guardan ancho-1 y alto-1.
        ancho = cab[24] | (cab[25] << 8) | (cab[26] << 16)
        alto = cab[27] | (cab[28] << 8) | (cab[29] << 16)
        return ancho + 1, alto + 1
    if formato == b'VP8 ':
        w, h = struct.unpack('<HH', cab[26:30])
        return w & 0x3FFF, h & 0x3FFF
    if formato == b'VP8L':
        bits = struct.unpack('<I', cab[21:25])[0]
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    return None


def foto_del_banner(slug):
    """(ruta publica, ancho, alto, aviso)."""
    portada_panel = None
    if os.path.isfile(PORTADAS_PANEL):
        mapa = json.load(io.open(PORTADAS_PANEL, encoding='utf-8'))
        portada_panel = mapa.get(slug)
    candidatas = [
        ((portada_panel or {}).get('src'), None),
        ('/assets/covers/%s.webp' % slug, None),
        ('/assets/gallery/%s/1.webp' % slug,
         'no tiene ninguna caratula: va la primera foto de la galeria'),
    ]
    for publica, aviso in candidatas:
        if not publica:
            continue
        local = os.path.join(RAIZ, publica.lstrip('/').replace('/', os.sep))
        m = medidas_webp(local)
        if m:
            # Las tapas locales llevan el mismo cache-buster que el listado.
            # Las URLs remotas del panel se conservan sin tocar.
            if publica.startswith('/assets/covers/'):
                publica = versionar(slug, publica)
            if m[0] < m[1] and aviso:
                aviso += ' y es vertical, en el banner se va a ver mal'
            return publica, m[0], m[1], aviso
    return None, 0, 0, 'no encuentro ninguna foto'


# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------

def desde_supabase():
    url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY', '')
    if not url or not clave:
        raise SystemExit('Faltan SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno.')
    pedido = urllib.request.Request(
        url + '/rest/v1/obras?select=slug,titulo,bajada,destacada,orden,'
              'banner_rotulo,banner_rotulo_en&publicada=is.true&order=orden.asc',
        headers={'apikey': clave, 'Authorization': 'Bearer ' + clave})
    with urllib.request.urlopen(pedido, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def desde_json():
    p = os.path.join(RAIZ, 'docs', 'panel_datos.json')
    if not os.path.isfile(p):
        raise SystemExit('No existe docs/panel_datos.json. Corre con --supabase.')
    return [o for o in json.load(io.open(p, encoding='utf-8')) if o.get('publicada')]


# ---------------------------------------------------------------------------
# El banner
# ---------------------------------------------------------------------------

# Los tres banners de este molde, en el orden en que estan en el home.
BANNER = re.compile(
    r'<a href="/proyectos/[^"]*" class="project-banner reveal" id="(section-\d+)">'
    r'.*?</a>', re.S)


def armar(o, ident):
    slug = o['slug']
    foto, w, h, aviso = foto_del_banner(slug)
    if not foto:
        return None, aviso
    molde = (
        '<a href="/proyectos/%s/" class="project-banner reveal" id="%s">\n'
        '      <div class="banner-stage">\n'
        '        <img src="%s" width="%d" height="%d" alt="%s"\n'
        '          loading="lazy" decoding="async">\n'
        '        <div class="project-banner__content">\n'
        '          <div class="pb-content-inner">\n'
        '            <span class="eyebrow">%s</span>\n'
        '            <h2>%s</h2>\n'
        '            <p>%s</p>\n'
        '          </div>\n'
        '        </div>\n'
        '      </div>\n'
        '    </a>')
    bloque = molde % (slug, ident, foto, w, h, E(o['titulo']),
                      E((o.get('banner_rotulo') or '').strip()),
                      E(o['titulo']), E((o.get('bajada') or '').strip()))
    return bloque, aviso


# ---------------------------------------------------------------------------

def main(verificar, supabase):
    obras = desde_supabase() if supabase else desde_json()
    destacadas = [o for o in obras if o.get('destacada')]
    # El orden puede venir vacio: las que no lo tengan van al final, por titulo,
    # para que el resultado no dependa del orden en que la base devolvio las filas.
    destacadas.sort(key=lambda o: (o.get('orden') is None, o.get('orden') or 0,
                                   (o.get('titulo') or '').lower()))

    print('destacadas y publicadas: %d   ranuras en el home: %d'
          % (len(destacadas), RANURAS))
    for i, o in enumerate(destacadas, 1):
        marca = 'ranura %d' % i if i <= RANURAS else 'no entra'
        print('  %-10s %-24s %s' % (marca, o['slug'],
                                    (o.get('banner_rotulo') or '(sin rotulo)')))

    if not destacadas:
        print('\nNinguna obra marcada como destacada: el home queda como esta.')
        return 0
    if len(destacadas) > RANURAS:
        print('\nAviso: hay mas destacadas que ranuras. Entran las %d primeras '
              'por orden; el resto no se muestra.' % RANURAS)

    html = io.open(HOME, encoding='utf-8').read()
    idents = BANNER.findall(html)
    if len(idents) != RANURAS:
        print('\nERROR: encontre %d banners de este molde en el home y esperaba '
              '%d. No se toca nada.' % (len(idents), RANURAS))
        return 1

    faltan = [o['slug'] for o in destacadas[:RANURAS]
              if not (o.get('banner_rotulo') or '').strip()]
    if faltan:
        print('\nAviso: sin rotulo de banner: %s. El banner sale sin la linea '
              'de arriba.' % ', '.join(faltan))

    nuevos, avisos = [], []
    for o, ident in zip(destacadas[:RANURAS], idents):
        bloque, aviso = armar(o, ident)
        if bloque is None:
            print('\nERROR: %s: %s. No se toca nada.' % (o['slug'], aviso))
            return 1
        if aviso:
            avisos.append('%s: %s' % (o['slug'], aviso))
        nuevos.append(bloque)

    # Si hay menos destacadas que ranuras, las que sobran quedan como estaban:
    # es mejor un home con la obra de antes que un hueco.
    salida, i = [], 0

    def cambiar(m):
        nonlocal i
        if i < len(nuevos):
            bloque = nuevos[i]
            i += 1
            return bloque
        return m.group(0)

    nuevo_html = BANNER.sub(cambiar, html)

    if avisos:
        print('\navisos de foto:')
        for a in avisos:
            print('  ' + a)

    if verificar:
        print('\n%s' % ('el home cambia' if nuevo_html != html
                        else 'el home queda igual'))
        print('(--verificar: no se toco nada)')
        return 0

    if nuevo_html != html:
        io.open(HOME, 'w', encoding='utf-8', newline='\n').write(nuevo_html)
        print('\nhome reescrito')
    else:
        print('\nel home ya decia lo mismo')

    # Los rotulos para el espejo: son texto visible y no estan en ningun
    # diccionario, asi que sin esto el banner de /en/ sale en castellano.
    pares = {}
    for o in destacadas[:RANURAS]:
        es = (o.get('banner_rotulo') or '').strip()
        en = (o.get('banner_rotulo_en') or '').strip()
        if es and en:
            pares[E(re.sub(r'\s+', ' ', es))] = E(re.sub(r'\s+', ' ', en))
    io.open(DESTINO_EN, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(pares, ensure_ascii=False, indent=1, sort_keys=True) + '\n')
    print('rotulos para el espejo: %d' % len(pares))
    return 0


if __name__ == '__main__':
    sys.exit(main('--verificar' in sys.argv, '--supabase' in sys.argv))
