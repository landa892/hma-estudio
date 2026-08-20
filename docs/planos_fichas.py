# -*- coding: utf-8 -*-
"""Suma los planos a la galeria de cada obra.

El cliente los pidio en la ultima fila de las fotos que se ven de entrada:
primero las fotos repartidas con la memoria, despues la tanda de la grilla,
y al final una fila de planos. Lo que sigue queda detras de "ver mas fotos".

Los planos son dibujos sobre blanco: se muestran enteros y no recortados
como las fotos, porque recortar un plano es cortarle la planta.

    python docs/planos_fichas.py
"""
import io, json, os, re, html

DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'planos.json')
MARCA = 'gallery-grid__item--plano'


def bloque(slug, titulo, planos):
    e = lambda s: html.escape(s or '', quote=False)
    return '\n'.join(
        '          <figure class="gallery-grid__item gallery-grid__item--plano">'
        '<img src="/assets/planos/%s/%d.webp" width="%d" height="%d" '
        'alt="%s — plano %d" loading="lazy" decoding="async"></figure>'
        % (slug, p['n'], p['w'], p['h'], e(titulo), p['n']) for p in planos)


def main():
    datos = json.load(io.open(DATOS, encoding='utf-8'))
    puestas, sin = [], []
    for slug in sorted(datos):
        f = os.path.join('proyectos', slug, 'index.html')
        if not os.path.isfile(f):
            sin.append(slug)
            continue
        h = io.open(f, encoding='utf-8').read()
        m = re.search(r'(?s)(<div class="gallery-grid[^"]*"[^>]*>)(.*?)(\n        </div>)', h)
        if not m:
            sin.append(slug)
            continue
        titulo = html.unescape(
            (re.search(r'<h1 class="display-2 mt-14">(.*?)</h1>', h) or [None, slug])[1]).strip()

        items = re.findall(r'(?s)<figure class="gallery-grid__item.*?</figure>', m.group(2))
        # La fila de planos que ya estuviera se descarta y se vuelve a armar.
        # Antes esto se salteaba si la ficha ya tenia planos, y por eso una
        # ficha con planos viejos se quedaba con ellos para siempre: cuando la
        # sincronizacion con el Drive borro las laminas repetidas, doce fichas
        # siguieron pidiendo archivos que ya no existian.
        items = [x for x in items if MARCA not in x]
        # Los planos van despues de las fotos que se ven, antes de las ocultas.
        visibles = [x for x in items if 'is-extra' not in x]
        ocultas = [x for x in items if 'is-extra' in x]
        cuerpo = ('\n'.join('          ' + x.strip() for x in visibles) + '\n' +
                  bloque(slug, titulo, datos[slug]))
        if ocultas:
            cuerpo += '\n' + '\n'.join('          ' + x.strip() for x in ocultas)
        h = h[:m.start(2)] + '\n' + cuerpo + h[m.end(2):]

        # El boton cuenta fotos, no planos: se mantiene con las fotos.
        io.open(f, 'w', encoding='utf-8').write(h)
        puestas.append((slug, len(datos[slug]), len(visibles), len(ocultas)))

    for s, p, v, o in puestas:
        print('  %-22s %d planos  (%d fotos a la vista, %d detras del boton)' % (s, p, v, o))
    print('\nfichas con planos: %d' % len(puestas))
    if sin:
        print('sin poner: %s' % ', '.join(sin))


if __name__ == '__main__':
    main()
