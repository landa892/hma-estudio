# -*- coding: utf-8 -*-
"""Arma la lista de conferencias y clases que va debajo de las tarjetas.

El Word del 21/08/2026 parte Prensa en dos. Las publicaciones pasan a ser
tarjetas -eso lo hace prensa_paginas.py-. Y aparte: "OJO CON LAS CLASES Y
CONFERENCIAS. Esas si vamos a tener que ponerlas en lista como esta", con la
captura de la lista que el sitio ya tenia.

Hasta ahora esa lista mezclaba las dos cosas: sesenta y seis filas donde las
publicaciones convivian con las clases. Ahora las publicaciones estan arriba en
tarjeta y aca quedan solamente las clases, las conferencias y las charlas, que
salen de docs/prensa_novedades.json -del CV extendido, seccion "EXPERIENCIA
ACADEMICA, CONFERENCIAS Y SEMINARIOS WEB"-.

docs/prensa-listado.html se conserva sin usar: son las sesenta y seis filas
como estaban, por si el estudio quiere reponer alguna. /prensa/publicaciones/
tambien se conserva, con las mismas filas, por los links ya compartidos.

    python docs/prensa_pagina.py
"""
import io
import json
import os
import re


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEN = os.path.join(RAIZ, 'prensa', 'index.html')
NOVEDADES = os.path.join(RAIZ, 'docs', 'prensa_novedades.json')
LISTADO = os.path.join(RAIZ, 'docs', 'prensa-listado.html')
DESTINO = os.path.join(RAIZ, 'prensa', 'publicaciones', 'index.html')
MARCA_INICIO = '<!-- PRENSA-ARCHIVO-INICIO -->'
MARCA_FIN = '<!-- PRENSA-ARCHIVO-FIN -->'


def leer(ruta):
    return io.open(ruta, encoding='utf-8').read()


def e(texto):
    return ((texto or '').replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;'))


def ea(texto):
    return e(texto).replace('"', '&quot;')


def fila(novedad):
    """Una fila: el rubro a la izquierda, el titulo en negrita, el año a la derecha.

    Es el mismo marcado que usaban las filas del archivo -press-row con pr-date,
    pr-text y pr-outlet-, para que la lista se vea igual que en la captura del
    Word y para no tocar el CSS ni el filtro por año, que ya andan.
    """
    # Manda el detalle y no el titulo. El titulo de prensa_novedades.json esta
    # construido cortandole el arranque al detalle -las 28 entradas, sin
    # excepcion- para deducir el rubro, y lo que queda empieza a mitad de
    # frase: "2026: impartido en DINA", "marco de la feria HOTELGA 2024",
    # "Arquitectura Comercial Interior en la Haus" sin el "Profesor de". Los
    # prefijos que se comio son Profesor de, Ciclo de conferencias, Conferencia
    # en, Clase magistral, Orador:, Graduado en.
    #
    # Ademas la fila mostraba titulo y detalle uno detras del otro, y como el
    # detalle contiene al titulo cada linea decia lo mismo dos veces. La guarda
    # que habia solo miraba la igualdad exacta, que no se daba nunca.
    #
    # El detalle esta entero y bien formado, asi que es el que va. El titulo
    # queda de reserva por si alguna entrada futura no trae detalle.
    texto = e((novedad.get('detalle') or novedad.get('titulo') or '').strip())
    if novedad.get('link'):
        texto = ('<a href="%s" target="_blank" rel="noopener">%s</a>'
                 % (ea(novedad['link']), texto))
    detalle = ''
    titulo = texto
    return ('          <div class="press-row" data-group="news" data-year="%s">'
            '<div class="pr-date">%s</div>'
            '<div class="pr-text"><b>%s</b>%s</div>'
            '<div class="pr-outlet">%s</div></div>'
            % (ea(novedad['anio']), e(novedad['rubro'].capitalize()), titulo,
               detalle, ea(novedad['anio'])))


def barra_de_anios(anios):
    """Los años que existen, y solamente esos.

    Estaban escritos a mano y no coincidian con el contenido: la barra ofrecia
    años sin ninguna fila y se filtraba a una lista vacia.
    """
    botones = ['          <button class="filter-btn active" data-year="all">'
               'Todos los años</button>']
    for anio in anios:
        botones.append('          <button class="filter-btn" data-year="%s">'
                       '%s</button>' % (anio, anio))
    return '\n'.join(botones)


def buscador():
    return '''        <div class="press-barra">
          <div class="buscador-obras" id="buscadorPrensa">
            <button type="button" class="buscador-obras__lupa" aria-expanded="false"
              aria-controls="buscadorPrensaCampo" aria-label="Buscar una conferencia">
              <svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true" focusable="false">
                <circle cx="8.5" cy="8.5" r="5.5" fill="none" stroke="currentColor" stroke-width="1.6" />
                <path d="M12.8 12.8 17 17" fill="none" stroke="currentColor" stroke-width="1.6"
                  stroke-linecap="round" />
              </svg>
            </button>
            <input type="search" id="buscadorPrensaCampo" class="buscador-obras__campo"
              placeholder="Buscar" autocomplete="off" aria-label="Buscar una conferencia">
          </div>
        </div>'''


def bloque_portada(novedades):
    anios = sorted({n['anio'] for n in novedades if n['anio']}, reverse=True)
    filas = '\n'.join(fila(n) for n in novedades)
    return '''%s
    <section class="section press-archive-home" id="archivo-prensa">
      <div class="container">
        <div class="section-head section-head--eje">
          <div>
            <span class="eyebrow eyebrow--seccion">Novedades</span>
            <h2 class="display-3 mt-10">Conferencias y clases</h2>
          </div>
        </div>
%s

        <div class="press-filter-bar" id="pressYears">
%s
        </div>

        <p class="press-count" id="pressCount" role="status" aria-live="polite"></p>

        <div class="press-feed" id="pressFeed">
%s
        </div>

        <nav class="press-pagination" aria-label="Páginas de conferencias y clases">
          <button type="button" class="btn link-arrow press-archive-link" id="pressAnterior">← Anteriores</button>
          <span class="press-pagination__status" id="pressPagina" aria-live="polite"></span>
          <button type="button" class="btn link-arrow press-archive-link" id="pressSiguiente">Siguientes →</button>
        </nav>
      </div>
    </section>
    %s''' % (MARCA_INICIO, buscador(), barra_de_anios(anios), filas, MARCA_FIN)


def actualizar_portada(molde, novedades):
    if MARCA_INICIO not in molde or MARCA_FIN not in molde:
        raise SystemExit('Faltan las marcas del archivo en prensa/index.html')
    patron = re.escape(MARCA_INICIO) + r'.*?' + re.escape(MARCA_FIN)
    return re.sub(patron, lambda _: bloque_portada(novedades), molde,
                  count=1, flags=re.S)


def contenido_listado():
    """Las sesenta y seis filas viejas, para /prensa/publicaciones/."""
    bloque = leer(LISTADO)
    bloque = re.sub(r'^<!--.*?-->', '', bloque, count=1, flags=re.S).strip()
    bloque = bloque.replace('<section class="section no-border pt-32">', '')
    bloque = bloque.replace('      <div class="container">', '', 1)
    bloque = re.sub(r'\s*</div>\s*</section>\s*$', '', bloque)
    bloque = re.sub(r'^[ \t]+$', '', bloque, flags=re.M)
    return bloque.strip()


def main():
    if not os.path.isfile(NOVEDADES):
        raise SystemExit('Falta docs/prensa_novedades.json. Lo escribe '
                         'docs/prensa_desde_fuentes.py en la maquina del '
                         'desarrollador.')
    novedades = json.load(io.open(NOVEDADES, encoding='utf-8'))

    molde = leer(ORIGEN)
    head = molde[:molde.index('<body>')]
    cuerpo = molde[molde.index('<body>'):]
    pie = cuerpo[cuerpo.index('<footer class="site-footer">'):]
    cabecera = cuerpo[:cuerpo.index('<main id="main">')]

    head = re.sub(r'<title>.*?</title>',
                  '<title>Publicaciones | Hitzig Militello Arquitectos</title>',
                  head, count=1, flags=re.S)
    descripcion = ('Archivo de publicaciones, entrevistas, conferencias y '
                   'novedades de Hitzig Militello Arquitectos desde 2003.')
    head = re.sub(r'(<meta name="description"\s+content=")[^"]*(">)',
                  r'\1%s\2' % descripcion, head, count=1, flags=re.S)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*(">)',
                  r'\1Publicaciones | Hitzig Militello Arquitectos\2', head,
                  count=1)
    head = re.sub(r'(<meta property="og:description"\s+content=")[^"]*(">)',
                  r'\1%s\2' % descripcion, head, count=1, flags=re.S)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*(">)',
                  r'\1https://estudiohma.com/prensa/publicaciones/\2', head,
                  count=1)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*(">)',
                  r'\1https://estudiohma.com/prensa/publicaciones/\2', head,
                  count=1)
    head = re.sub(r'\n\s*<link rel="alternate" hreflang="[^"]*"[^>]*>', '', head)
    head = re.sub(r'(<meta name="twitter:title" content=")[^"]*(">)',
                  r'\1Publicaciones | Hitzig Militello Arquitectos\2', head,
                  count=1)

    portada = actualizar_portada(molde, novedades)
    io.open(ORIGEN, 'w', encoding='utf-8', newline='\n').write(portada)

    listado = contenido_listado()
    main_html = '''<main id="main">
    <section class="hero-home pb-32">
      <div class="container">
        <span class="eyebrow">Prensa</span>
        <h1 class="display-2 mt-14">Todas las publicaciones</h1>
        <p class="lede mt-16">Publicaciones, entrevistas, conferencias y novedades del estudio desde 2003.</p>
      </div>
    </section>
    <section class="section no-border press-archive-page">
      <div class="container">
%s
      </div>
    </section>
  </main>

''' % listado

    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    pagina = re.sub(r'[ \t]+(?=\n)', '', head + cabecera + main_html + pie)
    io.open(DESTINO, 'w', encoding='utf-8', newline='\n').write(pagina)
    print('conferencias y clases en la portada de Prensa: %d' % len(novedades))
    print('archivo cronologico conservado en /prensa/publicaciones/: %d filas'
          % len(re.findall(r'class="press-row"', listado)))


if __name__ == '__main__':
    main()
