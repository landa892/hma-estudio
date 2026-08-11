# -*- coding: utf-8 -*-
"""Arma el sitemap enumerando las paginas del disco.

   Antes se mantenia a mano y la version anterior de este script se leia a si
   misma, asi que una obra nueva no entraba nunca: quedaron 14 obras publicadas
   afuera del sitemap sin que nadie se enterara. Ahora la fuente son los
   archivos, que es lo unico que no puede desincronizarse del sitio.

   Que hace:

   - Lista todas las paginas en castellano (los index.html, salvo docs, en y
     admin) y para cada una agrega su par en /en/ si existe en el disco.

   - Anota los <xhtml:link> de idioma en las dos versiones. Sin ese par, Google
     puede tomar las dos como duplicadas y quedarse con una sola.

   - Conserva el changefreq y el priority que ya tenia cada URL listada, para
     que sumar una obra no reescriba el archivo entero.

       python docs/sitemap_gen.py
"""
import glob
import io
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'docs'))

import en_rutas

SITEMAP = os.path.join(RAIZ, 'sitemap.xml')
BASE = 'https://estudiohma.com'

# Lo que se le pone a una pagina que todavia no estaba en el sitemap. Una obra
# cambia poco despues de publicada; las secciones se mueven mas.
POR_DEFECTO_OBRA = ('yearly', '0.7')
POR_DEFECTO_SECCION = ('monthly', '0.8')


NOINDEX = re.compile(r'<meta\s+name="robots"[^>]*content="[^"]*noindex', re.I)


def paginas_del_disco():
    """Las rutas publicas en castellano, en un orden estable."""
    fuera = []
    for p in glob.glob(os.path.join(RAIZ, '**', 'index.html'), recursive=True):
        rel = os.path.relpath(p, RAIZ).replace(os.sep, '/')
        if rel.startswith(('docs/', 'en/', 'admin/', 'node_modules/')):
            continue
        # Una pagina con noindex no va en el sitemap: seria pedirle a Google que
        # indexe algo que la propia pagina le prohibe, y Search Console lo
        # reporta como error. Es el caso de /buscar/.
        if NOINDEX.search(io.open(p, encoding='utf-8').read()):
            continue
        ruta = '/' + rel[:-len('index.html')]
        fuera.append(ruta)
    # La portada primero y despues alfabetico: el orden del archivo no le
    # importa a Google, pero un orden estable hace que el diff sea legible.
    fuera.sort(key=lambda r: (r != '/', r))
    return fuera


def existe_en_ingles(ruta_en):
    return os.path.isfile(os.path.join(RAIZ, ruta_en.strip('/').replace('/', os.sep),
                                       'index.html'))


def ajustes_previos():
    """{ruta: (changefreq, priority)} de lo que ya estaba listado."""
    if not os.path.isfile(SITEMAP):
        return {}
    t = io.open(SITEMAP, encoding='utf-8').read()
    fuera = {}
    for b in re.findall(r'(?s)<url>(.*?)</url>', t):
        m = re.search(r'<loc>(.*?)</loc>', b)
        if not m:
            continue
        ruta = m.group(1).replace(BASE, '')
        f = re.search(r'<changefreq>(.*?)</changefreq>', b)
        p = re.search(r'<priority>(.*?)</priority>', b)
        if f and p:
            fuera[ruta] = (f.group(1).strip(), p.group(1).strip())
    return fuera


def main():
    previos = ajustes_previos()
    rutas = paginas_del_disco()
    if not rutas:
        print('ERROR: no encontre ninguna pagina.')
        return 1

    filas, nuevas, sin_ingles = [], [], []
    for ruta in rutas:
        ruta_en = en_rutas.a_ingles(ruta)
        hay_en = existe_en_ingles(ruta_en)
        if not hay_en:
            sin_ingles.append(ruta)

        if ruta in previos:
            freq, prio = previos[ruta]
        else:
            es_obra = ruta.startswith('/proyectos/') and ruta != '/proyectos/'
            freq, prio = POR_DEFECTO_OBRA if es_obra else POR_DEFECTO_SECCION
            nuevas.append(ruta)

        # Cada URL del grupo declara el grupo completo, incluida a si misma:
        # asi lo pide la especificacion de hreflang.
        alternos = ['    <xhtml:link rel="alternate" hreflang="es" href="%s%s"/>'
                    % (BASE, ruta)]
        if hay_en:
            alternos.append('    <xhtml:link rel="alternate" hreflang="en" href="%s%s"/>'
                            % (BASE, ruta_en))
        alternos.append('    <xhtml:link rel="alternate" hreflang="x-default" href="%s%s"/>'
                        % (BASE, ruta))

        for destino in ([ruta, ruta_en] if hay_en else [ruta]):
            filas.append('\n'.join(
                ['  <url>', '    <loc>%s%s</loc>' % (BASE, destino)] + alternos
                + ['    <changefreq>%s</changefreq>' % freq,
                   '    <priority>%s</priority>' % prio, '  </url>']))

    salida = '\n'.join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ] + filas + ['</urlset>']) + '\n'

    io.open(SITEMAP, 'w', encoding='utf-8', newline='\n').write(salida)

    print('paginas en castellano: %d' % len(rutas))
    print('con par en ingles:     %d' % (len(rutas) - len(sin_ingles)))
    print('URLs en el sitemap:    %d' % len(filas))
    if nuevas:
        print('\nnuevas en el sitemap (%d):' % len(nuevas))
        for r in nuevas:
            print('  ' + r)
    if sin_ingles:
        print('\nsin version en ingles en el disco (%d):' % len(sin_ingles))
        for r in sin_ingles:
            print('  ' + r)
    return 0


if __name__ == '__main__':
    sys.exit(main())
