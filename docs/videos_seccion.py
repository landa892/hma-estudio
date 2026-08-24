# -*- coding: utf-8 -*-
"""Rehace la seccion de videos con los videos que el canal tiene de verdad.

Las tarjetas estaban escritas a mano: enlazaban al canal en general, no a un
video, mostraban recortes de revistas en lugar de la miniatura del video y
los titulos eran inventados ("Entrevista exclusiva sobre arquitectura
comercial" no es ningun video del canal).

Ahora salen del feed publico del canal. Se usan las mismas clases que arma
el script cuando la YOUTUBE_API_KEY esta configurada —.press-featured y
.press-card— para que lo escrito a mano y lo automatico se vean igual.

Los datos se toman de docs/yt_videos.json, que se regenera con
docs/videos_bajar.py.

    python docs/videos_seccion.py
"""
import io, json, os, re, html

DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'yt_videos.json')
MESES = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
         'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
POR_SECCION = 3


def tarjeta(v):
    e = lambda s: html.escape(s or '', quote=False)
    a, m = v['fecha'][:4], int(v['fecha'][5:7])
    # Capitalizado como el resto de las fechas del sitio: la regla que
    # traduce meses en el espejo espera 'Julio 2026', no 'julio 2026'.
    fecha = '%s %s' % (MESES[m].capitalize(), a) if m else a
    return (
'          <a class="press-card" href="https://www.youtube.com/watch?v=%s" target="_blank" rel="noopener">\n'
'            <div class="press-img"><img src="/api/youtube-thumbnail?id=%s" width="1280" height="720" alt="%s"\n'
'                loading="lazy" decoding="async"></div>\n'
'            <div class="press-body">\n'
'              <div class="press-outlet">YouTube — %s</div>\n'
'              <div class="press-title">%s</div>\n'
'            </div>\n'
'          </a>\n' % (v['id'], v['id'], e(v['titulo']), fecha, e(v['titulo'])))


def main():
    vs = json.load(io.open(DATOS, encoding='utf-8'))
    entrev = [v for v in vs if v['cat'] == 'entrevista']
    charlas = [v for v in vs if v['cat'] == 'charla']
    p = 'prensa/index.html'
    h = io.open(p, encoding='utf-8').read()

    if entrev:
        # Hay material para las dos secciones: cada una con lo suyo.
        secciones = [('youtubeEntrevistas', entrev[:POR_SECCION]),
                     ('youtubeCharlas', charlas[:POR_SECCION])]
    else:
        # El canal no publica entrevistas: en vez de poner despieces bajo el
        # rotulo "Entrevistas", se muestran los ultimos videos en una sola
        # lista y se saca el otro subtitulo. Cuando el estudio suba una
        # entrevista, este script vuelve a partirla en dos solo.
        # El archivo de datos ya viene con los videos elegidos, asi que
        # se muestran todos en vez de recortar de nuevo aca.
        secciones = [('youtubeEntrevistas', vs),
                     ('youtubeCharlas', [])]
        h = h.replace('<h3 class="col-sub">Entrevistas</h3>',
                      '<h3 class="col-sub">Últimos videos del canal</h3>', 1)
        h = re.sub(r'\n\s*<h3 class="col-sub mt-32">Charlas y Conferencias</h3>',
                   '', h, count=1)

    for idd, lista in secciones:
        pat = re.compile(r'(?s)(<div id="%s"[^>]*>).*?(\n        </div>)' % idd)
        if not pat.search(h):
            # Puede no estar: una corrida anterior lo saco porque el canal no
            # tenia videos de esa categoria. No es un error.
            if lista:
                raise SystemExit('falta el contenedor %s y hay videos para el' % idd)
            continue
        if not lista:
            h = pat.sub('', h, count=1)
            continue
        cuerpo = ''.join(tarjeta(v) for v in lista)
        h = pat.sub(lambda m: '<div id="%s" class="press-featured">\n%s        </div>'
                    % (idd, cuerpo), h, count=1)
    io.open(p, 'w', encoding='utf-8').write(h)

    if entrev:
        print('entrevistas: %d   charlas: %d' % (len(entrev[:POR_SECCION]), len(charlas[:POR_SECCION])))
    else:
        print('una sola lista con %d videos' % len(vs))
    for v in vs:
        print('   %s' % v['titulo'][:60])


if __name__ == '__main__':
    main()
