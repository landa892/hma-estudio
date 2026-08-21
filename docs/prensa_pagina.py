# -*- coding: utf-8 -*-
"""Genera el archivo completo de prensa en su propia pagina.

La portada de Prensa muestra las notas con tapa y enlaza a este segundo nivel,
que conserva el archivo completo con filtros. Antes el mismo archivo tambien se
inyectaba debajo de las tapas: repetia el contenido y contradecia el recorrido
que pidio el estudio en los audios del 20/08/2026.

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


def limpiar_portada(molde):
    """Retira el archivo duplicado que vivia debajo de las nueve tapas."""
    if MARCA_INICIO in molde and MARCA_FIN in molde:
        patron = re.escape(MARCA_INICIO) + r'.*?' + re.escape(MARCA_FIN)
        return re.sub(patron, '', molde, count=1, flags=re.S)
    return molde


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
    portada = limpiar_portada(molde)
    io.open(ORIGEN, 'w', encoding='utf-8', newline='\n').write(portada)
    main = '''<main id="main">
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
    pagina = re.sub(r'[ \t]+(?=\n)', '', head + cabecera + main + pie)
    io.open(DESTINO, 'w', encoding='utf-8', newline='\n').write(pagina)
    cantidad = len(re.findall(r'class="press-row"', listado))
    print('archivo de prensa generado: %d entradas' % cantidad)


if __name__ == '__main__':
    main()
