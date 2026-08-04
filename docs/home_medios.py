# -*- coding: utf-8 -*-
"""Arma la seccion partida del home: novedades a un lado, premios al otro.

El cliente lo pidio asi: "podemos hacer la mitad de la ventana algo de
YouTube, una ultima novedad con el detalle, y quizas aca algo de los
premios, por ahi tomamos la mitad con los sellitos. Esta bueno que en el
home aparezcan todos los sellos de los premios".

El video sale del mismo feed que usa prensa: el HTML trae el ultimo ya
escrito, y si esta configurada la YOUTUBE_API_KEY el script lo reemplaza
por el ultimo de verdad (data-max="1" para que entre uno solo).

Los sellos y el premio destacado se leen de la pagina de premios, para que
no puedan quedar diciendo cosas distintas.

    python docs/home_medios.py
"""
import io, os, re, glob, html

ANCLA = '\n    <section class="section pt-0">\n      <div class="stat-row reveal">'
MARCA = 'id="homeMedios"'


def ultimo_video():
    h = io.open('prensa/index.html', encoding='utf-8').read()
    i = h.find('id="youtubeFeed"')
    if i < 0:
        return None
    j = h.index('<a class="press-card"', i)
    return h[j:h.index('</a>', j) + 4]


def ultimo_premio():
    h = io.open('premios/index.html', encoding='utf-8').read()
    m = re.search(r'(?s)<div class="award-year-block" data-year="(\d+)">.*?'
                  r'award-row__logo"><img src="([^"]+)".*?'
                  r'<div class="award-row__name">(.*?)</div>.*?'
                  r'<div class="award-row__res">(.*?)</div>.*?'
                  r'<div class="award-row__city">(.*?)</div>', h)
    if not m:
        return None
    return {'anio': m.group(1), 'logo': m.group(2),
            'nombre': html.unescape(m.group(3)).strip(),
            'res': html.unescape(m.group(4)).strip(),
            'ciudad': html.unescape(m.group(5)).strip()}


def sellos():
    fs = sorted(os.path.basename(f) for f in glob.glob(os.path.join('assets', 'awards', '*.png')))
    return ''.join(
        '\n            <li><img src="/assets/awards/%s" width="400" height="300" alt="" '
        'loading="lazy" decoding="async"></li>' % f for f in fs), len(fs)


def main():
    h = io.open('index.html', encoding='utf-8').read()
    if MARCA in h:
        print('  la seccion ya estaba')
        return
    video = ultimo_video()
    premio = ultimo_premio()
    if not video or not premio:
        raise SystemExit('falta el video o el premio de referencia')
    marcas, n = sellos()
    e = lambda s: html.escape(s, quote=False)

    bloque = (
'\n    <!-- Dos mitades: la ultima novedad del canal y los premios. El video se\n'
'         actualiza solo si esta la YOUTUBE_API_KEY; si no, queda el que esta\n'
'         escrito aca. Los sellos salen de assets/awards. -->\n'
'    <section class="section no-border" id="homeMedios">\n'
'      <div class="container">\n'
'        <div class="dos-mitades">\n'
'          <div class="mitad">\n'
'            <div class="section-head"><div><span class="eyebrow">Actualidad</span>'
'<h2 class="display-3 mt-10">Lo último</h2></div></div>\n'
'            <div class="press-featured press-featured--col reveal" id="youtubeFeed" data-max="1">\n'
'              %s\n'
'            </div>\n'
'            <a href="/prensa/" class="btn link-arrow mt-14">Ver todas las novedades</a>\n'
'          </div>\n'
'\n'
'          <div class="mitad">\n'
'            <div class="section-head"><div><span class="eyebrow">Premios</span>'
'<h2 class="display-3 mt-10">Distinciones</h2></div></div>\n'
'            <a href="/premios/" class="premio-ultimo reveal">\n'
'              <img src="%s" width="400" height="300" alt="" loading="lazy" decoding="async">\n'
'              <div>\n'
'                <div class="premio-ultimo__anio">%s</div>\n'
'                <div class="premio-ultimo__nombre">%s</div>\n'
'                <div class="premio-ultimo__res">%s · %s</div>\n'
'              </div>\n'
'            </a>\n'
'            <ul class="sellos-premios reveal">%s\n'
'            </ul>\n'
'            <a href="/premios/" class="btn link-arrow mt-14">Ver todos los premios</a>\n'
'          </div>\n'
'        </div>\n'
'      </div>\n'
'    </section>\n'
        % (video.strip(), premio['logo'], e(premio['anio']), e(premio['nombre']),
           e(premio['res']), e(premio['ciudad']), marcas))

    if ANCLA not in h:
        raise SystemExit('no se encontro donde insertar la seccion')
    io.open('index.html', 'w', encoding='utf-8').write(h.replace(ANCLA, bloque + ANCLA, 1))
    print('  ultimo premio : %s %s — %s' % (premio['anio'], premio['nombre'], premio['res']))
    print('  sellos        : %d' % n)
    print('  video         : %s' % (re.search(r'press-title">(.*?)<', video) or ['', '?'])[1])


if __name__ == '__main__':
    main()
