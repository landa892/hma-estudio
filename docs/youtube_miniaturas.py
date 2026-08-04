# -*- coding: utf-8 -*-
"""Arregla las miniaturas de YouTube que salian en gris.

Varios videos del canal son verticales. Para esos, YouTube no genera
hqdefault.jpg y devuelve un rectangulo gris de unos 5 KB —con codigo 200,
asi que la pagina no se entera y lo muestra igual. maxresdefault.jpg si
trae el cuadro real.

Aca se prueba cada variante y queda la que de verdad tiene imagen. El corte
son 8 KB: por debajo de eso lo que viene es el gris.

    python docs/youtube_miniaturas.py
"""
import io, re, glob, sys, urllib.request

VARIANTES = ('maxresdefault', 'sddefault', 'hqdefault', 'mqdefault')
MINIMO = 8000
ID = re.compile(r'https://i\.ytimg\.com/vi/([A-Za-z0-9_-]{11})/([a-z0-9]+)\.jpg')


def peso(url):
    try:
        r = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(r, timeout=20) as x:
            return len(x.read())
    except Exception:
        return 0


def mejor(vid, cache):
    if vid in cache:
        return cache[vid]
    for v in VARIANTES:
        u = 'https://i.ytimg.com/vi/%s/%s.jpg' % (vid, v)
        p = peso(u)
        if p >= MINIMO:
            cache[vid] = (v, p)
            return cache[vid]
    cache[vid] = ('hqdefault', 0)
    return cache[vid]


def main():
    cache = {}
    for p in ['index.html'] + sorted(glob.glob('*/index.html')):
        if p.startswith('en'):
            continue
        h = io.open(p, encoding='utf-8').read()
        vids = sorted(set(ID.findall(h)))
        if not vids:
            continue
        cambios = 0

        def cambiar(m):
            global_v, actual = m.group(1), m.group(2)
            v, _ = mejor(global_v, cache)
            if v == actual:
                return m.group(0)
            return 'https://i.ytimg.com/vi/%s/%s.jpg' % (global_v, v)

        h2 = ID.sub(cambiar, h)
        cambios = sum(1 for a, b in zip(ID.findall(h), ID.findall(h2)) if a != b)
        if h2 != h:
            io.open(p, 'w', encoding='utf-8').write(h2)
        print('  %-22s %2d videos, %d miniaturas cambiadas' % (p, len(vids), cambios))
        sys.stdout.flush()

    grises = [v for v, (n, pe) in cache.items() if pe == 0]
    print('\nvideos sin ninguna miniatura util: %s' % (', '.join(grises) or 'ninguno'))


if __name__ == '__main__':
    main()
