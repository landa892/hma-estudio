# -*- coding: utf-8 -*-
"""Arma la galeria de una obra con las fotos que bajo el conector de Drive.

Mismo mecanismo que docs/caratulas.py: las descargas pesadas quedan escritas
en el directorio de resultados de la sesion y de ahi se leen por id, asi que
se pueden pedir todas las fotos seguidas y convertirlas despues de una.

Ademas de guardar assets/gallery/<slug>/N.webp deja anotada la galeria en
docs/obras_alta.json, que es de donde obras_alta.py saca el ancho y el alto
de cada <img>.

    python docs/galeria_drive.py <slug> <fileId> [fileId ...]

El orden de los ids es el orden de la galeria.
"""
import base64, glob, io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTADOS = os.path.join(
    os.path.expanduser('~'), '.claude', 'projects',
    'C--Users-El-Ni-o-Desktop-Trabajo-para-naza-hma-estudio',
    '402aee3f-451f-4e0a-92b2-c35be99cfa72', 'tool-results')
DATOS = os.path.join(ROOT, 'docs', 'obras_alta.json')

# Lo mismo que ya usan las galerias que vinieron del WordPress.
LADO_MAX = 1800


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


def main(slug, ids):
    from PIL import Image

    bajadas = descargas()
    faltan = [i for i in ids if i not in bajadas]
    if faltan:
        raise SystemExit('faltan descargas: %s' % ', '.join(faltan))

    destino = os.path.join(ROOT, 'assets', 'gallery', slug)
    os.makedirs(destino, exist_ok=True)

    galeria = []
    for n, fid in enumerate(ids, 1):
        im = Image.open(io.BytesIO(base64.b64decode(bajadas[fid]['content'])))
        im = im.convert('RGB')
        if max(im.size) > LADO_MAX:
            escala = LADO_MAX / float(max(im.size))
            im = im.resize((int(im.size[0] * escala), int(im.size[1] * escala)),
                           Image.LANCZOS)
        im.save(os.path.join(destino, '%d.webp' % n), 'WEBP',
                quality=80, method=6)
        galeria.append({'n': n, 'w': im.size[0], 'h': im.size[1]})

    d = json.load(io.open(DATOS, encoding='utf-8'))
    if slug not in d:
        raise SystemExit('%s no figura en obras_alta.json' % slug)
    d[slug]['galeria'] = galeria
    io.open(DATOS, 'w', encoding='utf-8').write(
        json.dumps(d, ensure_ascii=False, indent=1))

    peso = sum(os.path.getsize(os.path.join(destino, '%d.webp' % g['n']))
               for g in galeria) // 1024
    print('%s: %d fotos, %d KB' % (slug, len(galeria), peso))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise SystemExit('uso: python docs/galeria_drive.py <slug> <fileId>...')
    main(sys.argv[1], sys.argv[2:])
