# -*- coding: utf-8 -*-
"""Sube el numero de version de las hojas de estilo y los scripts.

Sirve para invalidar la cache del navegador cuando cambia el CSS o el JS.
Toca solo "algo.css?v=N" y "algo.js?v=N": un reemplazo generico de "?v=N"
pisa los identificadores de los videos de YouTube, que tienen la misma
forma y no son versiones de nada.

El espejo en ingles no se toca aca: se regenera despues con en_gen.py, que
lo copia del castellano ya actualizado.

    python docs/version.py 42
"""
import io, re, glob, sys

PATRON = re.compile(r'(\.(?:css|js)\?v=)(\d+)')


def main(nueva):
    tocados = total = 0
    for p in sorted(glob.glob('**/*.html', recursive=True)):
        if p.replace(chr(92), '/').startswith('en/'):
            continue
        d = io.open(p, encoding='utf-8').read()
        d2, n = PATRON.subn(lambda m: m.group(1) + str(nueva), d)
        if n and d2 != d:
            io.open(p, 'w', encoding='utf-8').write(d2)
            tocados += 1
            total += n
    print('version %s: %d referencias en %d paginas' % (nueva, total, tocados))


if __name__ == '__main__':
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        raise SystemExit('uso: python docs/version.py <numero>')
    main(int(sys.argv[1]))
