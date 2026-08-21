# -*- coding: utf-8 -*-
"""Sincroniza las publicaciones destacadas de Prensa con el panel.

La base guarda los datos, la portada y las imagenes internas; los generadores
que siguen conservan la responsabilidad de armar las tarjetas y las paginas
estaticas. Si la migracion 0014 todavia no se aplico, deja el JSON existente
intacto para que un deploy anterior al cambio de base no rompa Prensa.
"""
import glob
import io
import json
import os
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, 'docs', 'prensa_datos.json')
ASSETS = os.path.join(RAIZ, 'assets', 'press')
GALERIAS = os.path.join(RAIZ, 'assets', 'prensa')


def configuracion():
    url = (os.environ.get('SUPABASE_URL') or '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY') or ''
    if not url or not clave:
        raise RuntimeError('faltan SUPABASE_URL o SUPABASE_SERVICE_KEY')
    return url, clave


def pedir(url, clave, ruta, metodo='GET', cuerpo=None, binario=False):
    datos = None if cuerpo is None else json.dumps(cuerpo).encode('utf-8')
    req = urllib.request.Request(url + ruta, data=datos, method=metodo)
    req.add_header('apikey', clave)
    req.add_header('Authorization', 'Bearer ' + clave)
    if datos is not None:
        req.add_header('Content-Type', 'application/json')
        req.add_header('Prefer', 'return=representation')
    with urllib.request.urlopen(req, timeout=45) as respuesta:
        contenido = respuesta.read()
        if binario:
            return contenido
        return json.loads(contenido.decode('utf-8')) if contenido else None


def fila_desde_json(nota, orden):
    return {
        'slug': nota['slug'],
        'titulo': nota['titulo'],
        'medio': nota['medio'],
        'pais': nota.get('pais') or None,
        'fecha': nota.get('fecha') or None,
        'obra': nota.get('obra') or None,
        'link': nota.get('link') or None,
        'storage_path': '@site:' + nota['tapa'] if nota.get('tapa') else None,
        'orden': orden,
        'publicada': True,
    }


def tapa_local(url, clave, fila):
    ruta = fila.get('storage_path') or ''
    if ruta.startswith('@site:'):
        return ruta[len('@site:'):]
    if not ruta:
        return ''
    os.makedirs(ASSETS, exist_ok=True)
    nombre = 'panel-%s.webp' % fila['slug']
    destino = os.path.join(ASSETS, nombre)
    contenido = pedir(url, clave, '/storage/v1/object/obras/'
                      + urllib.parse.quote(ruta, safe='/'), binario=True)
    with open(destino, 'wb') as archivo:
        archivo.write(contenido)
    return '/assets/press/' + nombre


def sincronizar_imagenes(url, clave, fila, imagenes):
    """Baja las fotos internas administradas sin tocar los escaneos historicos.

    Los archivos del panel llevan el prefijo panel-. Asi una nota anterior
    conserva sus recortes del Drive y una edicion desde el panel solo reemplaza
    lo que el propio panel administra.
    """
    carpeta = os.path.join(GALERIAS, fila['slug'])
    if os.path.isdir(carpeta):
        for vieja in glob.glob(os.path.join(carpeta, 'panel-*.webp')):
            os.remove(vieja)
    if not imagenes:
        return []
    os.makedirs(carpeta, exist_ok=True)
    nombres = []
    for indice, imagen in enumerate(sorted(imagenes, key=lambda x: x.get('orden', 0)), 1):
        nombre = 'panel-%03d.webp' % indice
        destino = os.path.join(carpeta, nombre)
        contenido = pedir(
            url, clave,
            '/storage/v1/object/obras/'
            + urllib.parse.quote(imagen['storage_path'], safe='/'),
            binario=True)
        with open(destino, 'wb') as archivo:
            archivo.write(contenido)
        nombres.append(nombre)
    return nombres


def main():
    url, clave = configuracion()
    anteriores = json.load(io.open(DATOS, encoding='utf-8'))
    por_slug = {n['slug']: n for n in anteriores}

    try:
        filas = pedir(url, clave,
                      '/rest/v1/prensa_publicaciones?select=*&order=orden.asc,created_at.desc')
    except urllib.error.HTTPError as error:
        texto = error.read().decode('utf-8', 'replace')
        if error.code in (400, 404) and 'prensa_publicaciones' in texto:
            print('prensa: migracion 0014 pendiente; se conserva el contenido actual')
            return 0
        raise

    if not filas:
        semillas = [fila_desde_json(nota, i) for i, nota in enumerate(anteriores)]
        filas = pedir(url, clave, '/rest/v1/prensa_publicaciones',
                      metodo='POST', cuerpo=semillas) or semillas
        print('prensa: %d publicaciones iniciales sembradas' % len(filas))

    try:
        imagenes = pedir(
            url, clave,
            '/rest/v1/prensa_imagenes?select=*&order=publicacion_id.asc,orden.asc') or []
    except urllib.error.HTTPError as error:
        texto = error.read().decode('utf-8', 'replace')
        if error.code in (400, 404) and 'prensa_imagenes' in texto:
            imagenes = []
        else:
            raise
    imagenes_por_publicacion = {}
    for imagen in imagenes:
        imagenes_por_publicacion.setdefault(imagen['publicacion_id'], []).append(imagen)

    activas = []
    for fila in filas:
        if not fila.get('publicada'):
            continue
        vieja = por_slug.get(fila['slug'], {})
        internas = sincronizar_imagenes(
            url, clave, fila, imagenes_por_publicacion.get(fila.get('id'), []))
        activas.append({
            'slug': fila['slug'],
            'titulo': fila['titulo'],
            'obra': fila.get('obra') or '',
            'medio': fila['medio'],
            'pais': fila.get('pais') or '',
            'fecha': fila.get('fecha') or '',
            'link': fila.get('link') or '',
            'tapa': tapa_local(url, clave, fila),
            # Las galerias historicas siguen en el repo; las nuevas llevan
            # nombres panel-* y se descargan arriba en cada build.
            'imagenes': internas or vieja.get('imagenes', []),
        })

    activas_slugs = {n['slug'] for n in activas}
    for vieja in anteriores:
        if vieja['slug'] in activas_slugs:
            continue
        carpeta = os.path.join(RAIZ, 'prensa', vieja['slug'])
        if os.path.isdir(carpeta):
            shutil.rmtree(carpeta)

    io.open(DATOS, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(activas, ensure_ascii=False, indent=1) + '\n')
    print('prensa: %d publicaciones publicadas sincronizadas' % len(activas))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print('ERROR al sincronizar Prensa: %s' % error)
        sys.exit(1)
