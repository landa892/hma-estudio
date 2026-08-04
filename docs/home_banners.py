# -*- coding: utf-8 -*-
"""Arma los dos ultimos banners del home y les pone el estado a todos.

El cliente pidio que el home cierre con dos trabajos que se lean como cosas
distintas: la ultima obra terminada y el ultimo proyecto todavia en
proceso. Y que en cada banner se vea cual es cual.

Los dos se eligen por año desde el listado de proyectos, salteando los que
ya aparecen mas arriba en el home, para no repetir.

    python docs/home_banners.py
"""
import io, os, re, html

ROTULO = {'obra': 'Obra concluida', 'proyecto': 'Proyecto en proceso'}
# Los cuatro primeros banners son eleccion del estudio y no se tocan.
FIJOS = ['osten-foa', 'kavak-hub', 'benedetta', 'cerveceria-austral']


def anio(t):
    a = re.findall(r'(19|20)(\d{2})', t)
    return max(int(x + y) for x, y in a) if a else 0


def catalogo():
    h = io.open('proyectos/index.html', encoding='utf-8').read()
    out = []
    for m in re.finditer(
            r'(?s)<a href="/proyectos/([^"]+)/" class="project-card"[^>]*'
            r'data-estado="([^"]+)">.*?class="p-name">(.*?)<.*?class="p-meta">(.*?)</div>', h):
        out.append({'slug': m.group(1), 'estado': m.group(2),
                    'nombre': html.unescape(m.group(3)), 'anio': anio(m.group(4))})
    return out


def datos_ficha(slug):
    h = io.open(os.path.join('proyectos', slug, 'index.html'), encoding='utf-8').read()
    g = lambda p: html.unescape((re.search(p, h, re.S) or [None, ''])[1]).strip()
    img = re.search(r'<img src="(/assets/gallery/%s/1\.webp)" width="(\d+)" height="(\d+)"' % slug, h)
    return {'lede': g(r'<p class="lede">(.*?)</p>'),
            'img': img.group(1) if img else '/assets/gallery/%s/1.webp' % slug,
            'w': img.group(2) if img else '2000',
            'h': img.group(3) if img else '1333'}


def banner(d, n):
    f = datos_ficha(d['slug'])
    e = html.escape
    return (
'      <a href="/proyectos/%s/" class="project-banner reveal" id="section-%d">\n'
'        <div class="banner-stage">\n'
'        <img src="%s" width="%s" height="%s" alt="%s" loading="lazy" decoding="async">\n'
'        <div class="project-banner__content">\n'
'          <div class="pb-content-inner">\n'
'            <span class="banner-estado banner-estado--%s">%s</span>\n'
'            <h2>%s</h2>\n'
'            <p>%s</p>\n'
'          </div>\n'
'        </div>\n'
'      </div>\n'
'      </a>\n'
        % (d['slug'], n, f['img'], f['w'], f['h'], e(d['nombre'], False),
           d['estado'], ROTULO[d['estado']], e(d['nombre'], False), e(f['lede'], False)))


BANNER = re.compile(r'(?s)      <a href="/proyectos/([^"]+)/" class="project-banner reveal" '
                    r'id="section-(\d+)">.*?\n      </a>\n')


def main():
    cat = catalogo()
    en_home = set(FIJOS)
    ultima_obra = next(d for d in cat if d['estado'] == 'obra' and d['slug'] not in en_home)
    ultimo_proy = next(d for d in cat if d['estado'] == 'proyecto' and d['slug'] not in en_home)
    print('  ultima obra concluida : %-22s %d' % (ultima_obra['slug'], ultima_obra['anio']))
    print('  ultimo proyecto       : %-22s %d' % (ultimo_proy['slug'], ultimo_proy['anio']))

    estado = {d['slug']: d for d in cat}
    p = 'index.html'
    h = io.open(p, encoding='utf-8').read()
    vistos = []

    def cambiar(m):
        slug, n = m.group(1), int(m.group(2))
        vistos.append(slug)
        if n == 5:
            return banner(ultima_obra, 5)
        if n == 6:
            return banner(ultimo_proy, 6)
        d = estado.get(slug)
        if not d:
            return m.group(0)
        # A los cuatro fijos solo se les agrega el rotulo de estado.
        if 'banner-estado' in m.group(0):
            return m.group(0)
        return m.group(0).replace(
            '            <h2>',
            '            <span class="banner-estado banner-estado--%s">%s</span>\n            <h2>'
            % (d['estado'], ROTULO[d['estado']]), 1)

    h2 = BANNER.sub(cambiar, h)
    if h2 == h:
        print('  nada que cambiar')
        return
    io.open(p, 'w', encoding='utf-8').write(h2)
    print('\n  banners en el home: %s' % ', '.join(vistos[:4] + [ultima_obra['slug'], ultimo_proy['slug']]))


if __name__ == '__main__':
    main()
