# -*- coding: utf-8 -*-
"""Conserva las URLs anteriores de una obra despues de cambiar su slug."""
import io
import json
import os
import sys
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pedir(url, clave, ruta):
    pedido = urllib.request.Request(url + ruta, headers={
        'apikey': clave, 'Authorization': 'Bearer ' + clave})
    with urllib.request.urlopen(pedido, timeout=45) as respuesta:
        return json.loads(respuesta.read().decode('utf-8'))


def pagina(destino, idioma):
    titulo = 'Obra trasladada' if idioma == 'es' else 'Project moved'
    texto = 'Ir a la nueva direccion' if idioma == 'es' else 'Go to the new address'
    return '''<!doctype html><html lang="%s"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="0;url=%s"><link rel="canonical" href="%s">
<meta name="robots" content="noindex,follow"><title>%s | HMA</title></head>
<body><p><a href="%s">%s</a></p><script>location.replace(%s)</script></body></html>\n''' % (
        idioma, destino, destino, titulo, destino, texto, json.dumps(destino))


def main():
    url = (os.environ.get('SUPABASE_URL') or '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY') or ''
    if not url or not clave:
        raise RuntimeError('faltan SUPABASE_URL o SUPABASE_SERVICE_KEY')
    try:
        aliases = pedir(url, clave,
            '/rest/v1/obra_aliases?select=slug,obras!inner(slug,publicada)&obras.publicada=is.true')
    except urllib.error.HTTPError as error:
        texto = error.read().decode('utf-8', 'replace')
        if error.code in (400, 404) and 'obra_aliases' in texto:
            print('aliases: migracion 0017 pendiente; siguen los redirects fijos')
            return 0
        raise

    hechas = 0
    for alias in aliases:
        viejo = alias.get('slug') or ''
        actual = (alias.get('obras') or {}).get('slug') or ''
        if not viejo or not actual or viejo == actual:
            continue
        for idioma, carpeta, destino in (
            ('es', os.path.join(RAIZ, 'proyectos', viejo), '/proyectos/%s/' % actual),
            ('en', os.path.join(RAIZ, 'en', 'projects', viejo), '/en/projects/%s/' % actual),
        ):
            os.makedirs(carpeta, exist_ok=True)
            io.open(os.path.join(carpeta, 'index.html'), 'w', encoding='utf-8',
                    newline='\n').write(pagina(destino, idioma))
        hechas += 1
    print('aliases: %d direcciones anteriores conservadas' % hechas)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print('ERROR al generar aliases: %s' % error)
        sys.exit(1)
