# -*- coding: utf-8 -*-
"""Suma las obras nuevas al listado de proyectos, en grilla y en lista.

Cada obra aparece dos veces en /proyectos/: como tarjeta y como fila. Las
dos se arman desde la ficha ya generada, para que no puedan discrepar.

    python docs/obras_grilla.py
"""
import io, os, re, html

NUEVAS = ['abasto-patio-comidas', 'burger-7167', 'casa-olmo', 'clasico-quilmes',
          'elyaki', 'luccianos-olivos', 'malita', 'stella-artois-mercat',
          'the-birra',
          # segunda tanda: estaban escritas desde el WordPress viejo y
          # esperaban las fotos, que el estudio subio al Drive
          'oficina-casa-luna', 'ph-el-salvador', 'ph-loft-arias',
          'galeria-objeto-a']


def leer(slug):
    h = io.open(os.path.join('proyectos', slug, 'index.html'), encoding='utf-8').read()
    g = lambda p: (re.search(p, h, re.S) or [None, ''])[1].strip()
    metas = re.findall(r'<span>(.*?)</span>',
                       g(r'(?s)<div class="project-meta-row">(.*?)</div>'))
    img = re.search(r'<img src="(/assets/gallery/%s/1\.webp)" width="(\d+)" height="(\d+)"' % slug, h)
    return {
        'slug': slug,
        'titulo': g(r'<h1 class="display-2 mt-14">(.*?)</h1>'),
        'cat': g(r'<span class="eyebrow">(.*?)</span>'),
        'metas': metas,
        'img': img.group(1) if img else '/assets/gallery/%s/1.webp' % slug,
        'w': img.group(2) if img else '2000',
        'h': img.group(3) if img else '1333',
    }


CAT_SLUG = {'Gastronómico': 'gastronomico', 'Hotelería &amp; Comercial': 'hoteleria',
            'Hotelería & Comercial': 'hoteleria', 'Residencial': 'residencial',
            'Oficinas': 'oficinas', 'Cultural &amp; Institucional': 'cultural',
            'Cultural & Institucional': 'cultural'}


def tarjeta(d):
    cat = CAT_SLUG[html.unescape(d['cat'])]
    spans = ''.join('<span>%s</span>' % m for m in d['metas'])
    return ('          <a href="/proyectos/%s/" class="project-card" data-cat="%s" '
            'data-slug="%s" data-estado="obra">\n'
            '            <span class="card-cat">%s</span>\n'
            '            <img src="%s" width="%s" height="%s" alt="%s" loading="lazy" decoding="async">\n'
            '            <div class="card-plate">\n'
            '              <div class="p-name">%s</div>\n'
            '              <div class="p-meta">%s</div>\n'
            '            </div>\n'
            '          </a>\n'
            % (d['slug'], cat, d['slug'], d['cat'], d['img'], d['w'], d['h'],
               d['titulo'], d['titulo'], spans))


def fila(d):
    cat = CAT_SLUG[html.unescape(d['cat'])]
    spans = ''.join('<span>%s</span>' % m for m in d['metas'])
    anio = d['metas'][-1] if d['metas'] else ''
    return ('          <a href="/proyectos/%s/" class="project-list-row" data-cat="%s" '
            'data-slug="%s" data-estado="obra">\n'
            '            <div class="plr-thumb"><img src="%s" width="%s" height="%s" alt="" loading="lazy"></div>\n'
            '            <div><div class="plr-name">%s</div><div class="plr-meta">%s</div></div>\n'
            '            <div class="plr-cat">%s</div><div class="plr-loc">%s</div>\n'
            '          </a>\n'
            % (d['slug'], cat, d['slug'], d['img'], d['w'], d['h'],
               d['titulo'], spans, d['cat'], anio))


def main():
    p = 'proyectos/index.html'
    h = io.open(p, encoding='utf-8').read()
    puestas = []
    for slug in NUEVAS:
        if 'data-slug="%s"' % slug in h:
            print('  %-22s ya estaba' % slug)
            continue
        d = leer(slug)
        # Van al final de cada contenedor, antes de su cierre.
        for marca, arma in (('project-card', tarjeta), ('project-list-row', fila)):
            i = h.rfind('<a href="/proyectos/')
            j = h.rfind('class="%s"' % marca)
            if j < 0:
                raise SystemExit('no se encontro el contenedor de %s' % marca)
            fin = h.index('</a>', j) + len('</a>\n')
            h = h[:fin] + arma(d) + h[fin:]
        puestas.append(slug)
        print('  %-22s %s · %s' % (slug, d['titulo'], ' · '.join(d['metas'])))
    io.open(p, 'w', encoding='utf-8').write(h)
    n = len(re.findall(r'class="project-card"', h))
    m = len(re.findall(r'class="project-list-row"', h))
    print('\nsumadas: %d   tarjetas: %d   filas: %d' % (len(puestas), n, m))


if __name__ == '__main__':
    main()
