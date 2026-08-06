# -*- coding: utf-8 -*-
"""Convierte la caratula que bajo el conector de Drive en la portada de una obra.

El conector devuelve la imagen en base64 dentro de un JSON. Cuando el archivo
pesa, la respuesta no entra en la conversacion y queda escrita en el directorio
de resultados de la sesion; este script toma el JSON mas reciente de ahi, lo
decodifica y guarda la portada en assets/covers/<slug>.webp.

    python docs/caratulas.py <slug>

Imprime la linea lista para pegar en el mapa PORTADAS de docs/tapas_wordpress.py.
"""
import base64, glob, io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTADOS = os.path.join(
    os.path.expanduser('~'), '.claude', 'projects',
    'C--Users-El-Ni-o-Desktop-Trabajo-para-naza-hma-estudio',
    '402aee3f-451f-4e0a-92b2-c35be99cfa72', 'tool-results')

# La portada solo se ve en tarjetas, filas del listado y Open Graph: nunca a
# tamaño completo. A 1800 px las 20 portadas pesaban 6,6 MB para nada.
LADO_MAX = 1200


def descargas():
    """Indexa por id todas las descargas guardadas, no solo la ultima.

    Asi se pueden pedir varias imagenes seguidas y recien despues convertirlas
    todas juntas, en vez de intercalar una descarga y una conversion por obra.
    """
    porid = {}
    for ruta in glob.glob(os.path.join(RESULTADOS, '*download_file_content*')):
        try:
            d = json.load(io.open(ruta, encoding='utf-8'))
        except ValueError:
            continue
        if 'content' in d and 'id' in d:
            porid[d['id']] = d
    return porid


def main(slug, fileid=None):
    from PIL import Image

    bajadas = descargas()
    if fileid:
        if fileid not in bajadas:
            raise SystemExit('%s: no encuentro la descarga %s' % (slug, fileid))
        datos = bajadas[fileid]
    else:
        ruta = max(glob.glob(os.path.join(RESULTADOS, '*download_file_content*')),
                   key=os.path.getmtime)
        datos = json.load(io.open(ruta, encoding='utf-8'))
    crudo = base64.b64decode(datos['content'])
    im = Image.open(io.BytesIO(crudo))
    im = im.convert('RGB')
    if max(im.size) > LADO_MAX:
        escala = LADO_MAX / float(max(im.size))
        im = im.resize((int(im.size[0] * escala), int(im.size[1] * escala)),
                       Image.LANCZOS)

    destino = os.path.join(ROOT, 'assets', 'covers', slug + '.webp')
    im.save(destino, 'WEBP', quality=80, method=6)
    peso = os.path.getsize(destino) // 1024
    print('%s  <-  %s' % (destino[len(ROOT) + 1:], datos['title']))
    print('  %dx%d, %d KB' % (im.size[0], im.size[1], peso))
    print("    '%s': ('/assets/covers/%s.webp', %d, %d),"
          % (slug, slug, im.size[0], im.size[1]))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        raise SystemExit('uso: python docs/caratulas.py <slug> [fileId]')
