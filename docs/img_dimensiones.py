# -*- coding: utf-8 -*-
"""Le pone width y height a las imagenes que no los tienen.

Sin esas medidas el navegador no sabe cuanto espacio reservar hasta que la
imagen baja, asi que el texto salta hacia abajo cuando cada foto aparece.
En las galerias, que son decenas de imagenes, el salto es constante.

Las medidas se leen del archivo, no se estiman. El espejo en ingles no se
toca: se regenera despues del castellano.

    python docs/img_dimensiones.py
"""
import io, os, re, glob
from PIL import Image

CACHE = {}


def medidas(ruta):
    if ruta in CACHE:
        return CACHE[ruta]
    try:
        with Image.open(ruta) as im:
            CACHE[ruta] = im.size
    except Exception:
        CACHE[ruta] = None
    return CACHE[ruta]


def main():
    total = paginas = 0
    for f in sorted(glob.glob('**/*.html', recursive=True)):
        if 'node_modules' in f or f.replace(os.sep, '/').startswith('en/'):
            continue
        h = io.open(f, encoding='utf-8').read()
        n = [0]

        def poner(m):
            tag = m.group(0)
            if 'width=' in tag and 'height=' in tag:
                return tag
            src = re.search(r'src="([^"]+)"', tag)
            if not src or src.group(1).startswith('http'):
                return tag
            p = src.group(1).lstrip('/').split('?')[0]
            d = medidas(p)
            if not d:
                return tag
            n[0] += 1
            # Van justo despues del src, como en el resto del sitio.
            return tag.replace(src.group(0),
                               '%s width="%d" height="%d"' % (src.group(0), d[0], d[1]), 1)

        h2 = re.sub(r'<img\b[^>]*>', poner, h)
        if n[0]:
            io.open(f, 'w', encoding='utf-8').write(h2)
            total += n[0]
            paginas += 1
    print('imagenes completadas: %d en %d paginas' % (total, paginas))


if __name__ == '__main__':
    main()
