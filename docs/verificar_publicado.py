# -*- coding: utf-8 -*-
"""Comprueba el dominio real despues de que Vercel termina un deploy.

Se usa desde GitHub Actions. Espera que deployment.json contenga el commit del
push y recien entonces recorre todas las URLs del sitemap, sus imagenes,
recursos y enlaces internos. No escribe contenido ni necesita credenciales.
"""
import argparse
import concurrent.futures
import html.parser
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


AGENTE = 'HMA-verificacion-automatica/1.0'
OBLIGATORIAS = ('/', '/estudio/', '/proyectos/', '/prensa/', '/premios/', '/contacto/')


class Pagina(html.parser.HTMLParser):
    def __init__(self):
        html.parser.HTMLParser.__init__(self, convert_charrefs=True)
        self.titulos = []
        self._en_title = False
        self.main = 0
        self.h1 = 0
        self.imagenes = 0
        self.enlaces = []
        self.recursos = []

    def handle_starttag(self, tag, attrs):
        datos = dict(attrs)
        if tag == 'title':
            self._en_title = True
            self.titulos.append('')
        elif tag == 'main':
            self.main += 1
        elif tag == 'h1':
            self.h1 += 1
        elif tag == 'a' and datos.get('href'):
            self.enlaces.append(datos['href'])
        elif tag == 'img':
            self.imagenes += 1
            if datos.get('src'):
                self.recursos.append(datos['src'])
        elif tag in ('script', 'source', 'video') and datos.get('src'):
            self.recursos.append(datos['src'])
        elif (tag == 'link' and datos.get('href')
              and ('stylesheet' in (datos.get('rel') or '')
                   or datos.get('rel') in ('icon', 'preload'))):
            self.recursos.append(datos['href'])

    def handle_endtag(self, tag):
        if tag == 'title':
            self._en_title = False

    def handle_data(self, data):
        if self._en_title and self.titulos:
            self.titulos[-1] += data


def pedir(url, metodo='GET', limite=None):
    cabeceras = {'User-Agent': AGENTE, 'Cache-Control': 'no-cache'}
    if limite:
        cabeceras['Range'] = 'bytes=0-%d' % (limite - 1)
    pedido = urllib.request.Request(url, headers=cabeceras, method=metodo)
    with urllib.request.urlopen(pedido, timeout=35) as respuesta:
        cuerpo = respuesta.read() if metodo != 'HEAD' else b''
        return respuesta.geturl(), respuesta.status, dict(respuesta.headers), cuerpo


def esperar_commit(base, commit, segundos):
    limite = time.time() + segundos
    ultimo = ''
    while time.time() < limite:
        try:
            _url, _estado, _cabeceras, cuerpo = pedir(
                base + '/deployment.json?t=' + str(int(time.time())))
            ultimo = json.loads(cuerpo.decode('utf-8')).get('commit', '')
            if ultimo == commit:
                print('Deploy %s confirmado en el dominio.' % commit[:12])
                return
        except Exception as error:
            ultimo = str(error)
        print('Esperando el deploy (online: %s)...' % (ultimo[:12] or 'sin marca'))
        time.sleep(15)
    raise RuntimeError('el commit no llego al dominio dentro de %d segundos' % segundos)


def propia(url, base):
    partes = urllib.parse.urlsplit(url)
    origen = urllib.parse.urlsplit(base)
    return partes.scheme in ('http', 'https') and partes.netloc.lower() in {
        origen.netloc.lower(), 'www.' + origen.netloc.lower()
    }


def absoluta(valor, pagina, base):
    if not valor or valor.startswith(('#', 'mailto:', 'tel:', 'javascript:', 'data:', 'blob:')):
        return None
    url = urllib.parse.urljoin(pagina, valor)
    if not propia(url, base):
        return None
    partes = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((partes.scheme, partes.netloc, partes.path,
                                    partes.query, ''))


def descargar_pagina(url):
    final, estado, cabeceras, cuerpo = pedir(url)
    tipo = cabeceras.get('Content-Type', '')
    if estado != 200:
        raise RuntimeError('HTTP %s' % estado)
    if 'text/html' not in tipo:
        raise RuntimeError('no devolvio HTML (%s)' % tipo)
    return final, cuerpo.decode('utf-8', 'replace')


def probar_recurso(url):
    try:
        _final, estado, _cabeceras, _cuerpo = pedir(url, 'HEAD')
        if estado < 400:
            return None
    except urllib.error.HTTPError as error:
        if error.code not in (403, 405):
            return '%s: HTTP %s' % (url, error.code)
    except Exception:
        pass
    try:
        _final, estado, _cabeceras, _cuerpo = pedir(url, 'GET', 1)
        return None if estado < 400 else '%s: HTTP %s' % (url, estado)
    except urllib.error.HTTPError as error:
        return '%s: HTTP %s' % (url, error.code)
    except Exception as error:
        return '%s: %s' % (url, error)


def verificar(base):
    problemas = []
    _final, _estado, _cabeceras, cuerpo = pedir(base + '/sitemap.xml')
    urls = sorted(set(re.findall(r'<loc>(.*?)</loc>', cuerpo.decode('utf-8', 'replace'))))
    rutas = {urllib.parse.urlsplit(url).path for url in urls}
    for ruta in OBLIGATORIAS:
        if ruta not in rutas:
            problemas.append('el sitemap no incluye ' + ruta)

    resultados = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ejecutor:
        futuros = {ejecutor.submit(descargar_pagina, url): url for url in urls}
        for futuro in concurrent.futures.as_completed(futuros):
            url = futuros[futuro]
            try:
                resultados[url] = futuro.result()
            except Exception as error:
                problemas.append('%s: %s' % (url, error))

    recursos = set()
    enlaces = set()
    for original, (final, codigo) in resultados.items():
        doc = Pagina()
        doc.feed(codigo)
        if len(doc.titulos) != 1 or not ''.join(doc.titulos).strip():
            problemas.append('%s: title faltante o duplicado' % original)
        if doc.main != 1:
            problemas.append('%s: necesita exactamente un main' % original)
        ruta = urllib.parse.urlsplit(final).path
        es_ficha = (ruta.startswith(('/proyectos/', '/en/projects/', '/prensa/', '/en/press/'))
                    and ruta.rstrip('/').count('/') >= 2)
        if es_ficha and doc.h1 != 1:
            problemas.append('%s: la ficha necesita exactamente un h1' % original)
        if es_ficha and not doc.imagenes:
            problemas.append('%s: la ficha no tiene imagenes' % original)
        for valor in doc.recursos:
            url = absoluta(valor, final, base)
            if url:
                recursos.add(url)
        for valor in doc.enlaces:
            url = absoluta(valor, final, base)
            if url and not urllib.parse.urlsplit(url).path.startswith('/api/'):
                enlaces.add(url)

    # Las URLs del sitemap ya fueron descargadas completas; no se repiten.
    pendientes = sorted((recursos | enlaces) - set(urls))
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ejecutor:
        for error in ejecutor.map(probar_recurso, pendientes):
            if error:
                problemas.append(error)

    if problemas:
        print('\nVERIFICACION PUBLICA FALLIDA (%d):' % len(problemas))
        for problema in problemas[:100]:
            print('  - ' + problema)
        if len(problemas) > 100:
            print('  - ... y %d problemas mas' % (len(problemas) - 100))
        return 1
    print('\nVERIFICACION PUBLICA OK')
    print('  %d paginas, %d recursos y %d enlaces internos comprobados.'
          % (len(urls), len(recursos), len(enlaces)))
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', default='https://estudiohma.com')
    parser.add_argument('--commit')
    parser.add_argument('--esperar', type=int, default=0)
    args = parser.parse_args()
    base = args.base.rstrip('/')
    if args.commit:
        esperar_commit(base, args.commit, args.esperar)
    return verificar(base)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print('ERROR en la verificacion publicada: %s' % error)
        sys.exit(1)
