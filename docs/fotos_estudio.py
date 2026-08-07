# -*- coding: utf-8 -*-
"""Convierte las fotos del estudio que bajo el conector de Drive.

Mismo mecanismo que docs/caratulas.py: la descarga pesada queda escrita en el
directorio de resultados de la sesion y de ahi se lee por id.

    python docs/fotos_estudio.py <nombre-destino> <fileId> [lado_max]

Guarda assets/<nombre-destino>.webp y muestra las medidas.
"""
import base64, glob, io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTADOS = os.path.join(
    os.path.expanduser('~'), '.claude', 'projects',
    'C--Users-El-Ni-o-Desktop-Trabajo-para-naza-hma-estudio',
    '402aee3f-451f-4e0a-92b2-c35be99cfa72', 'tool-results')


def descargas():
    porid = {}
    for ruta in glob.glob(os.path.join(RESULTADOS, '*download_file_content*')):
        try:
            d = json.load(io.open(ruta, encoding='utf-8'))
        except ValueError:
            continue
        if 'content' in d and 'id' in d:
            porid[d['id']] = d
    return porid


def main(nombre, fid, lado_max=2000):
    from PIL import Image

    bajadas = descargas()
    if fid not in bajadas:
        raise SystemExit('no encuentro la descarga %s' % fid)
    d = bajadas[fid]
    im = Image.open(io.BytesIO(base64.b64decode(d['content'])))
    original = im.size
    # Todas las fotos de la pagina Estudio estan en blanco y negro dentro del
    # archivo, no por filtro: una en color cantaria al lado de las otras.
    im = im.convert('L').convert('RGB')
    if max(im.size) > lado_max:
        escala = lado_max / float(max(im.size))
        im = im.resize((int(im.size[0] * escala), int(im.size[1] * escala)),
                       Image.LANCZOS)
    destino = os.path.join(ROOT, 'assets', nombre + '.webp')
    im.save(destino, 'WEBP', quality=84, method=6)
    print('%s  <-  %s' % (nombre + '.webp', d['title']))
    print('  original %dx%d   guardada %dx%d   %d KB'
          % (original[0], original[1], im.size[0], im.size[1],
             os.path.getsize(destino) // 1024))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise SystemExit('uso: python docs/fotos_estudio.py <nombre> <fileId> [lado]')
    main(sys.argv[1], sys.argv[2],
         int(sys.argv[3]) if len(sys.argv) > 3 else 2000)
