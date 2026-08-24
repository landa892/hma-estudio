# -*- coding: utf-8 -*-
"""Sincroniza Conferencias y clases entre el panel y el JSON del sitio.

La 0017 se aplica a mano. Hasta entonces conserva el JSON actual para que el
deploy pueda publicarse sin dejar vacia la seccion.
"""
import hashlib
import io
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, 'docs', 'prensa_novedades.json')


def configuracion():
    url = (os.environ.get('SUPABASE_URL') or '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY') or ''
    if not url or not clave:
        raise RuntimeError('faltan SUPABASE_URL o SUPABASE_SERVICE_KEY')
    return url, clave


def pedir(url, clave, ruta, metodo='GET', cuerpo=None):
    datos = None if cuerpo is None else json.dumps(cuerpo).encode('utf-8')
    pedido = urllib.request.Request(url + ruta, data=datos, method=metodo,
        headers={'apikey': clave, 'Authorization': 'Bearer ' + clave,
                 'Content-Type': 'application/json',
                 'Prefer': 'return=representation'})
    with urllib.request.urlopen(pedido, timeout=45) as respuesta:
        crudo = respuesta.read()
        return json.loads(crudo.decode('utf-8')) if crudo else None


def clave_de(fila, indice):
    firma = '%s|%s|%s' % (fila.get('anio', ''), fila.get('rubro', ''),
                           fila.get('detalle') or fila.get('titulo') or '')
    return 'cv-%02d-%s' % (indice + 1, hashlib.sha1(
        firma.encode('utf-8')).hexdigest()[:10])


def main():
    url, clave = configuracion()
    actuales = json.load(io.open(DATOS, encoding='utf-8'))
    try:
        filas = pedir(url, clave,
            '/rest/v1/prensa_novedades?select=*&order=orden.asc,created_at.asc') or []
    except urllib.error.HTTPError as error:
        texto = error.read().decode('utf-8', 'replace')
        if error.code in (400, 404) and 'prensa_novedades' in texto:
            print('conferencias: migracion 0017 pendiente; se conserva el contenido actual')
            return 0
        raise

    # Solo una tabla realmente nueva se siembra. Las bajas son blandas para
    # que borrar las 28 no haga que reaparezcan en el deploy siguiente.
    if not filas:
        semillas = []
        for indice, fila in enumerate(actuales):
            semillas.append({
                'clave': clave_de(fila, indice),
                'rubro': fila.get('rubro') or 'CONFERENCIA',
                'titulo': fila.get('titulo') or fila.get('detalle') or 'Sin titulo',
                'detalle': fila.get('detalle') or None,
                'anio': str(fila.get('anio') or ''),
                'link': fila.get('link') or None,
                'orden': indice,
                'publicada': True,
                'eliminada': False,
            })
        filas = pedir(url, clave, '/rest/v1/prensa_novedades', 'POST', semillas) or semillas
        print('conferencias: %d filas conectadas al panel' % len(filas))

    publicadas = [{
        'rubro': f.get('rubro') or 'CONFERENCIA',
        'titulo': f.get('titulo') or '',
        'detalle': f.get('detalle') or '',
        'anio': str(f.get('anio') or ''),
        'link': f.get('link') or '',
    } for f in filas if f.get('publicada') and not f.get('eliminada')]
    io.open(DATOS, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(publicadas, ensure_ascii=False, indent=1) + '\n')
    print('conferencias: %d publicadas sincronizadas' % len(publicadas))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print('ERROR al sincronizar Conferencias y clases: %s' % error)
        sys.exit(1)
