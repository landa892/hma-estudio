# -*- coding: utf-8 -*-
"""Arma una pagina propia para cada nota de prensa.

El cliente lo pidio el 19/08/2026: "Al cliquear en cada encuadre te tiene que
llevar a una pagina similar a la que lleva por cada trabajo". Y antes, sobre
las tarjetas que no abrian nada: "En los marcados en rojo no se puede
ingresar. Corregi para que todos te lleven a cada pagina".

Cada nota queda en /prensa/<slug>/ con la misma estructura que una ficha de
obra: el titulo, la obra de la que habla, una ficha con Medio, Año, Pais y
Link, y la galeria de imagenes de la nota. La fila Link aparece solo si la
nota existe online -"ESTE RENGLON SOLO APARECE SI EXISTE LA NOTICIA DE FORMA
DIGITAL"-, que es justamente el caso de las cuatro que marco en rojo.

La cascara -cabecera, menu, pie- se toma de una ficha de obra ya publicada en
vez de repetirla aca: asi un cambio en el menu o en el pie llega solo a las
notas, sin tener que acordarse de este archivo.

Los datos viven en docs/prensa_datos.json. Las imagenes de cada nota van en
assets/prensa/<slug>/.

    python docs/prensa_paginas.py --verificar   # no escribe, informa
    python docs/prensa_paginas.py
"""
import io
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, 'docs', 'prensa_datos.json')
LISTADO = os.path.join(RAIZ, 'prensa', 'index.html')
MOLDE = os.path.join(RAIZ, 'proyectos', 'nim-bar', 'index.html')
IMAGENES = os.path.join(RAIZ, 'assets', 'prensa')
SITIO = 'https://estudiohma.com'
TARJETAS_INICIO = '<!-- PRENSA-TARJETAS-INICIO -->'
TARJETAS_FIN = '<!-- PRENSA-TARJETAS-FIN -->'


def e(texto):
    return ((texto or '').replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;'))


def ea(texto):
    return e(texto).replace('"', '&quot;')


def medidas(ruta):
    """Ancho y alto de un WebP, sin depender de Pillow."""
    try:
        with open(ruta, 'rb') as archivo:
            d = archivo.read(40)
    except OSError:
        return None
    if d[:4] != b'RIFF' or d[8:12] != b'WEBP':
        return None
    if d[12:16] == b'VP8X':
        return ((d[24] | d[25] << 8 | d[26] << 16) + 1,
                (d[27] | d[28] << 8 | d[29] << 16) + 1)
    if d[12:16] == b'VP8L':
        b = d[21] | d[22] << 8 | d[23] << 16 | d[24] << 24
        return ((b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1)
    if d[12:16] == b'VP8 ':
        return (int.from_bytes(d[26:28], 'little') & 0x3FFF,
                int.from_bytes(d[28:30], 'little') & 0x3FFF)
    return None


def cascara():
    """(todo lo previo a <main>, todo lo posterior a </main>) de una ficha."""
    html = io.open(MOLDE, encoding='utf-8').read()
    i = html.index('<main id="main">') + len('<main id="main">')
    j = html.index('</main>')
    return html[:i], html[j:]


def cabeza(html, nota):
    """Titulo, descripcion y etiquetas sociales de la nota."""
    url = '%s/prensa/%s/' % (SITIO, nota['slug'])
    titulo = '%s | Prensa | Hitzig Militello Arquitectos' % nota['titulo']
    desc = '%s en %s%s.' % (nota['titulo'], nota['medio'],
                            ', ' + nota['fecha'] if nota.get('fecha') else '')
    tapa = nota.get('tapa') or ''

    html = re.sub(r'<title>.*?</title>', '<title>%s</title>' % e(titulo),
                  html, count=1, flags=re.S)
    for etiqueta in ('name="description"', 'property="og:description"'):
        html = re.sub(r'(<meta %s content=")[^"]*(")' % re.escape(etiqueta),
                      lambda m: m.group(1) + ea(desc) + m.group(2),
                      html, count=1)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
                  lambda m: m.group(1) + ea(titulo) + m.group(2), html, count=1)
    for patron in (r'(<link rel="canonical" href=")[^"]*(")',
                   r'(<meta property="og:url" content=")[^"]*(")'):
        html = re.sub(patron, lambda m: m.group(1) + url + m.group(2),
                      html, count=1)
    if tapa:
        html = re.sub(r'(<meta property="og:image" content=")[^"]*(")',
                      lambda m: m.group(1) + SITIO + tapa + m.group(2),
                      html, count=1)
    # Los hreflang los mantiene en_gen.py, que espeja cada nota en
    # /en/press/<slug>/. Aca se reescriben a la URL de esta nota en vez de
    # borrarlos: si se borran, en_gen los vuelve a poner y las dos etapas se
    # pisan en cada build.
    for patron, destino in (
            (r'(<link rel="alternate" hreflang="es" href=")[^"]*(")', url),
            (r'(<link rel="alternate" hreflang="x-default" href=")[^"]*(")', url),
            (r'(<link rel="alternate" hreflang="en" href=")[^"]*(")',
             '%s/en/press/%s/' % (SITIO, nota['slug']))):
        html = re.sub(patron, lambda m, d=destino: m.group(1) + d + m.group(2),
                      html, count=1)

    # El boton EN del menu tambien viene apuntando a la obra del molde.
    html = re.sub(r'(class="site-menu__icon-btn site-menu__lang" href=")[^"]*(")',
                  lambda m: m.group(1) + '/en/press/%s/' % nota['slug'] + m.group(2),
                  html, count=1)
    return html


def ficha(nota):
    filas = [('Medio', e(nota['medio']))]
    if nota.get('fecha'):
        filas.append(('Año', e(nota['fecha'])))
    if nota.get('pais'):
        filas.append(('País', e(nota['pais'])))
    if nota.get('link'):
        # "ESTE RENGLON SOLO APARECE SI EXISTE LA NOTICIA DE FORMA DIGITAL".
        filas.append(('Link',
                      '<a class="btn link-arrow press-article__source" '
                      'href="%s" target="_blank" rel="noopener">'
                      'Ver noticia</a>' % ea(nota['link'])))
    return '\n'.join(
        '          <div class="spec-row"><dt>%s</dt><dd>%s</dd></div>' % f
        for f in filas)


def galeria(nota):
    carpeta = os.path.join(IMAGENES, nota['slug'])
    if not os.path.isdir(carpeta):
        return ''
    nombres = sorted((n for n in os.listdir(carpeta) if n.endswith('.webp')),
                     key=lambda n: (int(re.match(r'(\d+)', n).group(1))
                                    if re.match(r'\d', n) else 999, n))
    fotos = []
    for i, nombre in enumerate(nombres, 1):
        m = medidas(os.path.join(carpeta, nombre))
        if not m:
            continue
        carga = 'eager' if i == 1 else 'lazy'
        fotos.append(
            '          <figure class="gallery-grid__item"><img '
            'src="/assets/prensa/%s/%s" width="%d" height="%d" alt="%s — '
            'imagen %d" loading="%s" decoding="async"></figure>'
            % (nota['slug'], nombre, m[0], m[1], ea(nota['titulo']), i,
               carga))
    if not fotos:
        return ''
    return ('\n    <section class="section no-border" id="galeria">\n'
            '      <div class="container">\n'
            '        <div class="section-head"><div><span class="eyebrow">'
            'Galería</span><h2 class="display-3 mt-10">Todas las fotos</h2>'
            '</div></div>\n'
            '        <div class="gallery-grid gallery-grid--prensa reveal">'
            '\n%s\n        </div>\n'
            '      </div>\n    </section>\n' % '\n'.join(fotos))


def cuerpo(nota):
    obra = ''
    if nota.get('obra'):
        titulo_obra = nombre_de_obra(nota['obra'])
        if titulo_obra:
            obra = ('\n        <div class="project-meta-row"><a href="/proyectos/'
                    '%s/">%s</a></div>' % (nota['obra'], e(titulo_obra)))

    return ('\n    <section class="hero-home pb-32">\n'
            '      <div class="container">\n'
            '        <span class="eyebrow">%s</span>\n'
            '        <h1 class="display-2 mt-14">“%s”</h1>%s\n'
            '        <dl class="project-specs">\n%s\n        </dl>\n'
            '      </div>\n    </section>\n'
            '%s'
            '\n    <section class="section no-border">\n'
            '      <div class="container">\n'
            '        <a href="/prensa/" class="btn link-arrow">'
            'Ver todas las publicaciones</a>\n'
            '      </div>\n    </section>\n'
            % (e(nota['medio']), e(nota['titulo']), obra, ficha(nota),
               galeria(nota)))


_nombres = {}


def nombre_de_obra(slug):
    """El titulo con el que la obra se publica, leido de su propia ficha."""
    if slug in _nombres:
        return _nombres[slug]
    ruta = os.path.join(RAIZ, 'proyectos', slug, 'index.html')
    nombre = ''
    if os.path.isfile(ruta):
        m = re.search(r'<h1[^>]*>(.*?)</h1>',
                      io.open(ruta, encoding='utf-8').read(), re.S)
        if m:
            nombre = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    _nombres[slug] = nombre
    return nombre


def tarjeta(nota):
    """Tarjeta de portada generada desde la misma fuente que su ficha."""
    tapa = nota.get('tapa') or ''
    ruta_tapa = os.path.join(RAIZ, tapa.lstrip('/').replace('/', os.sep))
    m = medidas(ruta_tapa) or (900, 600)
    pais = (' — ' + nota['pais']) if nota.get('pais') else ''
    anio = re.search(r'\b(20\d{2}|19\d{2})\b', nota.get('fecha', ''))
    anio = anio.group(1) if anio else ''
    return ('              <a class="press-card" data-year="%s" href="/prensa/%s/">\n'
            '                <div class="press-img"><img src="%s" width="%d" height="%d" '
            'alt="%s%s" loading="lazy" decoding="async"></div>\n'
            '                <div class="press-body">\n'
            '                  <div class="press-outlet">%s%s</div>\n'
            '                  <div class="press-title">%s</div>\n'
            '                  <div class="press-date">%s</div>\n'
            '                  <span class="press-card__link" aria-hidden="true">↗</span>\n'
            '                </div>\n'
            '              </a>'
            % (anio, nota['slug'], ea(tapa), m[0], m[1], ea(nota['medio']),
               ea(pais), e(nota['medio']), e(pais), e(nota['titulo']),
               e(nota.get('fecha', ''))))


def actualizar_tarjetas(notas, verificar):
    """Rehace las tapas sin depender de cierres HTML heredados a mano."""
    html = io.open(LISTADO, encoding='utf-8').read()
    if TARJETAS_INICIO not in html or TARJETAS_FIN not in html:
        raise SystemExit('Faltan las marcas de tarjetas en prensa/index.html')
    bloque = (TARJETAS_INICIO + '\n' + '\n'.join(tarjeta(n) for n in notas)
              + '\n              ' + TARJETAS_FIN)
    patron = re.escape(TARJETAS_INICIO) + r'.*?' + re.escape(TARJETAS_FIN)
    nuevo = re.sub(patron, lambda _: bloque, html, count=1, flags=re.S)
    cambio = nuevo != html
    if cambio and not verificar:
        io.open(LISTADO, 'w', encoding='utf-8', newline='\n').write(nuevo)
    return len(notas) if cambio else 0


def main(verificar):
    if not os.path.isfile(DATOS):
        print('No existe docs/prensa_datos.json.')
        return 1
    notas = json.load(io.open(DATOS, encoding='utf-8'))
    antes, despues = cascara()

    escritas, con_galeria, sin_link = [], 0, []
    for nota in notas:
        pagina = cabeza(antes, nota) + cuerpo(nota) + despues
        carpeta = os.path.join(RAIZ, 'prensa', nota['slug'])
        ruta = os.path.join(carpeta, 'index.html')
        if galeria(nota):
            con_galeria += 1
        if not nota.get('link'):
            sin_link.append(nota['slug'])
        anterior = (io.open(ruta, encoding='utf-8').read()
                    if os.path.isfile(ruta) else '')
        if pagina == anterior:
            continue
        escritas.append(nota['slug'])
        if not verificar:
            if not os.path.isdir(carpeta):
                os.makedirs(carpeta)
            io.open(ruta, 'w', encoding='utf-8', newline='\n').write(pagina)

    tarjetas = actualizar_tarjetas(notas, verificar)

    print('notas: %d   paginas escritas: %d   con galeria: %d'
          % (len(notas), len(escritas), con_galeria))
    print('tarjetas de portada actualizadas: %d' % tarjetas)
    if sin_link:
        print('\nsin link a la nota online (no llevan la fila "Link"): %s'
              % ', '.join(sin_link))
    if verificar:
        print('\n(--verificar: no se escribio nada)')
    return 0


if __name__ == '__main__':
    sys.exit(main('--verificar' in sys.argv))
