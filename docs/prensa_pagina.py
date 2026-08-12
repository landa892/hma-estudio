# -*- coding: utf-8 -*-
"""Genera el archivo de prensa y lo integra a la portada.

La portada de Prensa muestra una seleccion. Este segundo nivel contiene el
archivo completo con filtros, sin un contenedor de scroll interno que resulte
dificil de usar en telefono.

    python docs/prensa_pagina.py
"""
import io
import os
import re


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEN = os.path.join(RAIZ, 'prensa', 'index.html')
LISTADO = os.path.join(RAIZ, 'docs', 'prensa-listado.html')
DESTINO = os.path.join(RAIZ, 'prensa', 'publicaciones', 'index.html')
MARCA_INICIO = '<!-- PRENSA-ARCHIVO-INICIO -->'
MARCA_FIN = '<!-- PRENSA-ARCHIVO-FIN -->'


def leer(ruta):
    return io.open(ruta, encoding='utf-8').read()


def contenido_listado():
    bloque = leer(LISTADO)
    bloque = re.sub(r'^<!--.*?-->', '', bloque, count=1, flags=re.S).strip()
    bloque = bloque.replace('<section class="section no-border pt-32">', '')
    bloque = bloque.replace('      <div class="container">', '', 1)
    bloque = re.sub(r'\s*</div>\s*</section>\s*$', '', bloque)
    bloque = re.sub(r'^[ \t]+$', '', bloque, flags=re.M)
    return bloque.strip()


def bloque_portada(listado):
    return '''%s
    <section class="section no-border press-archive-page" id="archivo-prensa">
      <div class="container">
        <div class="section-head">
          <div>
            <span class="eyebrow">Archivo</span>
            <h2 class="display-3 mt-10">Todas las publicaciones</h2>
          </div>
        </div>
%s
        <button type="button" class="btn link-arrow press-load-more" id="pressLoadMore">Seguir viendo</button>
      </div>
    </section>
    %s''' % (MARCA_INICIO, listado, MARCA_FIN)


def actualizar_portada(molde, listado):
    bloque = bloque_portada(listado)
    if MARCA_INICIO in molde and MARCA_FIN in molde:
        patron = re.escape(MARCA_INICIO) + r'.*?' + re.escape(MARCA_FIN)
        return re.sub(patron, lambda _: bloque, molde, count=1, flags=re.S)
    ancla = '    <!-- BLOQUE YOUTUBE -->'
    if ancla not in molde:
        raise SystemExit('No encuentro donde insertar el archivo en prensa/index.html')
    return molde.replace(ancla, bloque + '\n\n\n' + ancla, 1)


def main():
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

    listado = contenido_listado()
    portada = actualizar_portada(molde, listado)
    io.open(ORIGEN, 'w', encoding='utf-8', newline='\n').write(portada)
    main = '''<main id="main">
    <section class="hero-home pb-32">
      <div class="container">
        <span class="eyebrow">Prensa y News</span>
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
    pagina = re.sub(r'[ \t]+(?=\n)', '', head + cabecera + main + pie)
    io.open(DESTINO, 'w', encoding='utf-8', newline='\n').write(pagina)
    cantidad = len(re.findall(r'class="press-row"', listado))
    print('archivo de prensa integrado y generado: %d entradas' % cantidad)


if __name__ == '__main__':
    main()
