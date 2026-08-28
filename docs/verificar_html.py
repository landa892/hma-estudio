# -*- coding: utf-8 -*-
"""Audita la estructura estatica antes de permitir que Vercel publique.

No consulta la base: esa comparacion la hace panel_verificar_salida.py en el
paso siguiente. Aca se busca la otra mitad de los errores, los que pueden
aparecer aunque el contenido coincida: enlaces internos sin destino, recursos
locales inexistentes, ids repetidos y paginas incompletas.
"""
import html.parser
import json
import os
import re
import sys
import urllib.parse


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARPETAS_IGNORADAS = {
    '.git', '.vercel', 'node_modules', 'docs', 'admin',
    'claude-seo', 'graphify-out',
}
HOSTS_PROPIOS = {'estudiohma.com', 'www.estudiohma.com'}
PROTOCOLOS_EXTERNOS = ('mailto:', 'tel:', 'javascript:', 'data:', 'blob:')


class Documento(html.parser.HTMLParser):
    def __init__(self):
        html.parser.HTMLParser.__init__(self, convert_charrefs=True)
        self.ids = []
        self.enlaces = []
        self.recursos = []
        self.titulos = []
        self._en_title = False
        self.h1 = 0
        self.main = 0
        self.imagenes = 0
        self.redireccion = False

    def handle_starttag(self, tag, attrs):
        datos = dict(attrs)
        if datos.get('id'):
            self.ids.append(datos['id'])
        if tag == 'a' and datos.get('href'):
            self.enlaces.append(datos['href'])
        if (tag == 'meta'
                and (datos.get('http-equiv') or '').lower() == 'refresh'
                and 'url=' in (datos.get('content') or '').lower()):
            self.redireccion = True
        if tag == 'img':
            self.imagenes += 1
            if datos.get('src'):
                self.recursos.append(datos['src'])
        elif tag in ('script', 'source', 'video') and datos.get('src'):
            self.recursos.append(datos['src'])
        elif (tag == 'link' and datos.get('href')
              and ('stylesheet' in (datos.get('rel') or '')
                   or datos.get('rel') in ('icon', 'preload'))):
            self.recursos.append(datos['href'])
        if tag == 'title':
            self._en_title = True
            self.titulos.append('')
        elif tag == 'h1':
            self.h1 += 1
        elif tag == 'main':
            self.main += 1

    def handle_endtag(self, tag):
        if tag == 'title':
            self._en_title = False

    def handle_data(self, data):
        if self._en_title and self.titulos:
            self.titulos[-1] += data


def html_publicos():
    for base, carpetas, archivos in os.walk(RAIZ):
        carpetas[:] = [c for c in carpetas if c not in CARPETAS_IGNORADAS]
        for nombre in archivos:
            if nombre not in ('index.html', '404.html'):
                continue
            absoluta = os.path.join(base, nombre)
            yield os.path.relpath(absoluta, RAIZ).replace(os.sep, '/')


def url_de_archivo(ruta):
    if ruta == 'index.html':
        return 'https://estudiohma.com/'
    if ruta.endswith('/index.html'):
        return 'https://estudiohma.com/' + ruta[:-10]
    return 'https://estudiohma.com/' + ruta


def rutas_dinamicas():
    """Rutas que Vercel resuelve sin que exista un index.html en el repo."""
    ruta = os.path.join(RAIZ, 'vercel.json')
    if not os.path.isfile(ruta):
        return []
    datos = json.load(open(ruta, encoding='utf-8'))
    fuentes = []
    for grupo in ('redirects', 'rewrites'):
        for regla in datos.get(grupo, []):
            fuente = regla.get('source') or ''
            # Los parametros de las rewrites se aceptan como patron.
            # re.escape dejo de escapar los dos puntos en versiones nuevas de Python.
            # Cubrimos ambos comportamientos para reconocer las rutas dinamicas de Vercel.
            patron = re.escape(fuente).replace(r'\:slug', r'[^/]+').replace(':slug', r'[^/]+')
            fuentes.append(re.compile('^' + patron.rstrip('/') + '/?$'))
    return fuentes


def es_ruta_dinamica(ruta, patrones):
    return any(p.match(ruta) for p in patrones)


def archivo_de_url(url, pagina):
    absoluta = urllib.parse.urljoin(url_de_archivo(pagina), url)
    partes = urllib.parse.urlsplit(absoluta)
    if partes.scheme not in ('', 'http', 'https'):
        return None, None
    if partes.netloc and partes.netloc.lower() not in HOSTS_PROPIOS:
        return None, None
    ruta = urllib.parse.unquote(partes.path or '/')
    if ruta.startswith('/api/'):
        return None, ruta
    limpia = ruta.lstrip('/')
    if not limpia:
        return 'index.html', ruta
    extension = os.path.splitext(limpia)[1].lower()
    if extension:
        return limpia, ruta
    return limpia.rstrip('/') + '/index.html', ruta


def version(recurso, nombre):
    m = re.search(r'/%s\?v=(\d+)(?:$|[&#])' % re.escape(nombre), recurso)
    return m.group(1) if m else None


def verificar():
    problemas = []
    patrones = rutas_dinamicas()
    versiones_css = set()
    versiones_js = set()
    cantidad = 0

    for ruta in sorted(html_publicos()):
        cantidad += 1
        absoluta = os.path.join(RAIZ, *ruta.split('/'))
        codigo = open(absoluta, encoding='utf-8').read()
        doc = Documento()
        try:
            doc.feed(codigo)
        except Exception as error:
            problemas.append('%s: HTML ilegible (%s)' % (ruta, error))
            continue

        repetidos = sorted({x for x in doc.ids if doc.ids.count(x) > 1})
        if repetidos:
            problemas.append('%s: ids repetidos (%s)' % (ruta, ', '.join(repetidos[:5])))
        if len(doc.titulos) != 1 or not ''.join(doc.titulos).strip():
            problemas.append('%s: necesita un solo title con contenido' % ruta)
        if not ruta.endswith('404.html') and not doc.redireccion and doc.main != 1:
            problemas.append('%s: necesita exactamente un elemento main' % ruta)

        if (not doc.redireccion
                and ruta.startswith(('proyectos/', 'en/projects/'))
                and ruta.count('/') == 2):
            if doc.h1 != 1:
                problemas.append('%s: la ficha necesita exactamente un h1' % ruta)
            if not doc.imagenes:
                problemas.append('%s: la ficha no tiene ninguna imagen' % ruta)
        if (not doc.redireccion
                and ruta.startswith(('prensa/', 'en/press/'))
                and ruta.count('/') == 2):
            if doc.h1 != 1:
                problemas.append('%s: la nota necesita exactamente un h1' % ruta)
            if not doc.imagenes:
                problemas.append('%s: la nota no tiene ninguna imagen' % ruta)

        for recurso in doc.recursos:
            if not recurso or recurso.startswith(PROTOCOLOS_EXTERNOS):
                continue
            local, _ruta_url = archivo_de_url(recurso, ruta)
            if local and not os.path.isfile(os.path.join(RAIZ, *local.split('/'))):
                problemas.append('%s: falta el recurso %s' % (ruta, recurso))
            css = version(recurso, 'styles/main.css')
            js = version(recurso, 'scripts/main.js')
            if css:
                versiones_css.add(css)
            if js:
                versiones_js.add(js)

        for enlace in doc.enlaces:
            if (not enlace or enlace.startswith(('#',) + PROTOCOLOS_EXTERNOS)):
                continue
            local, ruta_url = archivo_de_url(enlace, ruta)
            if local is None:
                continue
            if (not os.path.isfile(os.path.join(RAIZ, *local.split('/')))
                    and not es_ruta_dinamica(ruta_url, patrones)):
                problemas.append('%s: enlace interno sin destino %s' % (ruta, enlace))

        for patron in (r'youtu\.be/([A-Za-z0-9_-]+)',
                       r'youtube\.com/watch\?v=([A-Za-z0-9_-]+)'):
            for video_id in re.findall(patron, codigo):
                if len(video_id) != 11:
                    problemas.append('%s: id de YouTube alterado (%s)' % (ruta, video_id))

    if len(versiones_css) != 1:
        problemas.append('main.css tiene versiones mezcladas: %s'
                          % ', '.join(sorted(versiones_css)))
    if len(versiones_js) != 1:
        problemas.append('main.js tiene versiones mezcladas: %s'
                          % ', '.join(sorted(versiones_js)))
    return cantidad, problemas


def main():
    cantidad, problemas = verificar()
    if problemas:
        print('\nAUDITORIA HTML FALLIDA (%d):' % len(problemas))
        for problema in problemas[:100]:
            print('  - ' + problema)
        if len(problemas) > 100:
            print('  - ... y %d problemas mas' % (len(problemas) - 100))
        return 1
    print('\nAUDITORIA HTML OK')
    print('  %d paginas sin enlaces ni recursos locales rotos.' % cantidad)
    return 0


if __name__ == '__main__':
    sys.exit(main())
