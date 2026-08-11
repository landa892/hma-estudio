# -*- coding: utf-8 -*-
"""Suma el espejo en ingles al sitemap y anota los pares de idioma.

   El sitemap se escribia a mano y solo listaba las 54 paginas en castellano.
   Las de /en/ se descubrian igual —por el hreflang del HTML y por el boton de
   idioma— pero tarde y sin garantia de que Google entendiera que son la misma
   pagina en otro idioma.

   Lo que agrega este script es el par <xhtml:link>. Sin el, Google puede
   indexar las dos versiones y elegir una sola como buena, descartando la otra
   por duplicada. Con el par declarado, sabe que son la misma pagina y sirve la
   que corresponde segun el idioma de quien busca.

   Es idempotente: lee las paginas en castellano del sitemap actual, ignora lo
   que ya haya de /en/, y reescribe el archivo entero. Correrlo dos veces da el
   mismo resultado.

   Una pagina en ingles que no exista en el disco no se lista. Vale mas un
   sitemap corto que uno que manda a Google a un 404.
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import en_rutas

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP = os.path.join(RAIZ, 'sitemap.xml')
BASE = 'https://estudiohma.com'

BLOQUE = re.compile(r'<url>(.*?)</url>', re.S)


def campo(bloque, nombre):
    m = re.search(r'<%s>(.*?)</%s>' % (nombre, nombre), bloque, re.S)
    return m.group(1).strip() if m else None


def existe(ruta):
    """/en/projects/moshu/ -> hay en/projects/moshu/index.html en el disco?"""
    relativo = ruta.strip('/').replace('/', os.sep)
    return os.path.isfile(os.path.join(RAIZ, relativo, 'index.html'))


def main():
    original = io.open(SITEMAP, encoding='utf-8').read()

    paginas = []
    for bloque in BLOQUE.findall(original):
        loc = campo(bloque, 'loc')
        if not loc:
            continue
        ruta = loc[len(BASE):] if loc.startswith(BASE) else loc
        # Si el sitemap ya venia con paginas en ingles, se descartan: se
        # regeneran abajo desde su par en castellano.
        if ruta.startswith('/en/'):
            continue
        paginas.append((ruta,
                        campo(bloque, 'changefreq') or 'monthly',
                        campo(bloque, 'priority') or '0.5'))

    if not paginas:
        print('ERROR: no se encontro ninguna pagina en castellano.')
        return 1

    sin_ingles = []
    filas = []
    for ruta, freq, prio in paginas:
        ruta_en = en_rutas.a_ingles(ruta)
        hay_en = existe(ruta_en)
        if not hay_en:
            sin_ingles.append(ruta)

        # Los dos <xhtml:link> van identicos en las dos versiones de la pagina:
        # asi lo pide la especificacion, cada URL del grupo declara el grupo
        # completo, incluida a si misma.
        alternos = [
            '    <xhtml:link rel="alternate" hreflang="es" href="%s%s"/>'
            % (BASE, ruta),
        ]
        if hay_en:
            alternos.append(
                '    <xhtml:link rel="alternate" hreflang="en" href="%s%s"/>'
                % (BASE, ruta_en))
        alternos.append(
            '    <xhtml:link rel="alternate" hreflang="x-default" href="%s%s"/>'
            % (BASE, ruta))

        for destino in ([ruta, ruta_en] if hay_en else [ruta]):
            filas.append('\n'.join([
                '  <url>',
                '    <loc>%s%s</loc>' % (BASE, destino),
            ] + alternos + [
                '    <changefreq>%s</changefreq>' % freq,
                '    <priority>%s</priority>' % prio,
                '  </url>',
            ]))

    salida = '\n'.join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ] + filas + ['</urlset>']) + '\n'

    io.open(SITEMAP, 'w', encoding='utf-8', newline='\n').write(salida)

    print('castellano: %d' % len(paginas))
    print('ingles:     %d' % (len(filas) - len(paginas)))
    print('total:      %d' % len(filas))
    if sin_ingles:
        print('\nSin version en ingles en el disco (%d):' % len(sin_ingles))
        for r in sin_ingles:
            print('  %s' % r)
    return 0


if __name__ == '__main__':
    sys.exit(main())
