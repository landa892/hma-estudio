# -*- coding: utf-8 -*-
"""Reutiliza imagenes exactas del ultimo sitio publicado durante el build."""
import hashlib
import os
import urllib.error
import urllib.request


SITIO_PUBLICADO = (os.environ.get('HMA_SITIO_PUBLICADO')
                   or 'https://estudiohma.com').rstrip('/')


def huella_ruta(ruta):
    """Nombre estable que cambia cuando el panel reemplaza el archivo."""
    return hashlib.sha256(ruta.encode('utf-8')).hexdigest()[:12]


def es_webp(contenido):
    return (len(contenido) >= 12 and contenido[:4] == b'RIFF'
            and contenido[8:12] == b'WEBP')


def guardar_webp(destino, contenido):
    """Escribe en forma atomica para no dejar un asset cortado si falla el build."""
    if not es_webp(contenido):
        raise ValueError('la descarga no es una imagen WebP valida')
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    temporal = destino + '.tmp'
    try:
        with open(temporal, 'wb') as archivo:
            archivo.write(contenido)
        os.replace(temporal, destino)
    finally:
        if os.path.isfile(temporal):
            os.remove(temporal)


def recuperar_publicada(ruta_publica, destino):
    """Copia el asset de produccion; False significa que aun hay que ir a Storage.

    La ruta publica incluye la huella del storage_path. Por eso un reemplazo
    desde el panel produce otra URL y nunca puede recuperar una foto anterior.
    """
    pedido = urllib.request.Request(
        SITIO_PUBLICADO + ruta_publica,
        headers={'User-Agent': 'HMA build cache/1.0'})
    try:
        with urllib.request.urlopen(pedido, timeout=45) as respuesta:
            contenido = respuesta.read()
        guardar_webp(destino, contenido)
        return True
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
            OSError, ValueError):
        return False
