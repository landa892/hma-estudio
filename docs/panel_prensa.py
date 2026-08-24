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


def tapa_local(url, clave, fila, respaldo=''):
    ruta = fila.get('storage_path') or ''
    # Los dos prefijos, no solo @site:. Una ruta con @ es un archivo del
    # repositorio y pedirsela al Storage devuelve 400, que corta el build
    # entero: fue lo que paso en panel_alta el 24/08/2026. Hoy las 186 tapas
    # son @site:, pero si alguna llegara sembrada como @seed: rompia igual.
    if ruta.startswith('@site:') or ruta.startswith('@seed:'):
        return ruta.split(':', 1)[1]
    if not ruta and respaldo:
        return respaldo
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

    Desde que prensa_galerias.py siembra los escaneos historicos, las filas de
    prensa_imagenes pueden venir de dos lados. Las @seed: son la seleccion
    heredada: apuntan a un archivo que ya esta en el repositorio, no hay nada
    que bajar y se devuelve su nombre tal cual. Pedirle al Storage una ruta
    "@seed:/assets/..." daria 404 y la galeria de esa nota se publicaria vacia.

    Mientras la nota siga entera en @seed: manda el repositorio. En cuanto el
    estudio toca la galeria, el panel pasa esas filas a @site: y desde entonces
    manda la base: el orden es el de la base y lo que el estudio borro deja de
    salir.
    """
    carpeta = os.path.join(GALERIAS, fila['slug'])
    if os.path.isdir(carpeta):
        for vieja in glob.glob(os.path.join(carpeta, 'panel-*.webp')):
            os.remove(vieja)
    if not imagenes:
        return []

    heredadas = [i for i in imagenes
                 if (i.get('storage_path') or '').startswith('@seed:')]
    if len(heredadas) == len(imagenes):
        return [os.path.basename(i['storage_path']) for i in
                sorted(imagenes, key=lambda x: x.get('orden', 0))]
    os.makedirs(carpeta, exist_ok=True)
    nombres, subidas = [], 0
    for imagen in sorted(imagenes, key=lambda x: x.get('orden', 0)):
        ruta = imagen.get('storage_path') or ''
        # Una galeria ya administrada mezcla las dos cosas: las que ya estaban
        # en el repositorio -marcadas @site: cuando el estudio la toco por
        # primera vez- y las que subio despues, que si viven en el Storage.
        # Solo las segundas se bajan; a las primeras alcanza con nombrarlas.
        if ruta.startswith('@site:') or ruta.startswith('@seed:'):
            nombres.append(os.path.basename(ruta))
            continue
        subidas += 1
        nombre = 'panel-%03d.webp' % subidas
        destino = os.path.join(carpeta, nombre)
        contenido = pedir(
            url, clave,
            '/storage/v1/object/obras/' + urllib.parse.quote(ruta, safe='/'),
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

    # Se siembra lo que falta, no solamente cuando la tabla esta vacia. Antes
    # era "if not filas": con las nueve publicaciones de la primera siembra ya
    # cargadas, las doscientas diez que docs/prensa_desde_fuentes.py armo desde
    # el Drive y el WordPress viejo no habrian entrado nunca, y peor: el paso
    # reescribe prensa_datos.json con lo que dice la base, asi que el build las
    # habria borrado del sitio en la primera publicacion.
    #
    # La siembra va por slug y solo agrega los que no estan. Una publicacion
    # que el estudio despublico desde el panel sigue despublicada: su fila
    # existe, asi que no se vuelve a sembrar.
    ya = {fila['slug'] for fila in filas}
    faltan = [fila_desde_json(nota, i)
              for i, nota in enumerate(anteriores) if nota['slug'] not in ya]
    if faltan:
        # De a tandas: doscientas filas en un solo POST es un cuerpo grande y
        # si falla no se sabe cual quedo a medias.
        nuevas = []
        for desde in range(0, len(faltan), 50):
            tanda = faltan[desde:desde + 50]
            nuevas.extend(pedir(url, clave, '/rest/v1/prensa_publicaciones',
                                metodo='POST', cuerpo=tanda) or tanda)
        filas = filas + nuevas
        print('prensa: %d publicaciones sembradas (%d ya estaban)'
              % (len(nuevas), len(ya)))

        # Las nueve que ya estaban tienen orden 0..8 y las nuevas vienen con el
        # que les toca por fecha, asi que sin esto habria nueve empates y el
        # listado saldria alternando 2018 con 2026. Se reacomodan una sola vez:
        # de aca en mas manda el panel, y como la siembra ya no vuelve a
        # correr, un reordenamiento del estudio no se pisa.
        orden_json = {nota['slug']: i for i, nota in enumerate(anteriores)}
        for fila in filas:
            nuevo = orden_json.get(fila['slug'])
            if nuevo is None or fila.get('orden') == nuevo:
                continue
            pedir(url, clave,
                  '/rest/v1/prensa_publicaciones?slug=eq.'
                  + urllib.parse.quote(fila['slug'], safe=''),
                  metodo='PATCH', cuerpo={'orden': nuevo})
            fila['orden'] = nuevo
        filas.sort(key=lambda f: f.get('orden') or 0)

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

    # Una tapa @site: que apunta a un archivo que ya no esta en el repositorio
    # se corrige con la que dice el JSON. Pasa cuando se rehace el archivo de
    # prensa: la siembra vieja guardo /assets/press/newsweek-2026.webp y al
    # regenerar las tapas quedaron con el nombre del slug, asi que seis
    # tarjetas salieron publicadas con la imagen rota.
    for fila in filas:
        ruta = fila.get('storage_path') or ''
        if not ruta.startswith('@site:'):
            continue
        archivo = ruta[len('@site:'):]
        if os.path.isfile(os.path.join(RAIZ, archivo.lstrip('/').replace('/', os.sep))):
            continue
        nueva = (por_slug.get(fila['slug'], {}) or {}).get('tapa') or ''
        destino = ('@site:' + nueva) if nueva else None
        pedir(url, clave,
              '/rest/v1/prensa_publicaciones?slug=eq.'
              + urllib.parse.quote(fila['slug'], safe=''),
              metodo='PATCH', cuerpo={'storage_path': destino})
        fila['storage_path'] = destino
        print('prensa: tapa corregida en %s (%s ya no existe)'
              % (fila['slug'], archivo))

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
            'tapa': tapa_local(url, clave, fila, vieja.get('tapa', '')),
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
