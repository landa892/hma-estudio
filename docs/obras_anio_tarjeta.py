# -*- coding: utf-8 -*-
"""Devuelve el año a las tarjetas del listado y aplica las correcciones
que mando el cliente por chat.

Al rehacerse el listado, diecisiete tarjetas se quedaron sin el año en su
linea de datos. En casi todas el dato seguia estando en la ficha, asi que
se copia de ahi en vez de escribirlo a mano: la ficha es la fuente.

    python docs/obras_anio_tarjeta.py
"""
import io, os, re, html

# Correcciones del cliente sobre lo que figuraba en el sitio.
ANIO_NUEVO = {
    'indusparquet': '2026',   # no tenia año
    'roket': '2026',          # decia 2023
}
# "Ya es una obra": pasan de proyecto en proceso a obra concluida.
A_CONCLUIDA = ['osten-foa', 'indusparquet']


def anio_de_ficha(slug):
    p = os.path.join('proyectos', slug, 'index.html')
    if not os.path.isfile(p):
        return None, ''
    h = io.open(p, encoding='utf-8').read()
    m = re.search(r'<dt>A[ñn]o</dt><dd>(.*?)</dd>', h)
    return (html.unescape(m.group(1)).strip() if m else ''), h


def poner_en_ficha(slug, anio):
    """Escribe el año en la ficha y en su linea de datos."""
    p = os.path.join('proyectos', slug, 'index.html')
    h = io.open(p, encoding='utf-8').read()
    if re.search(r'<dt>A[ñn]o</dt>', h):
        h = re.sub(r'(<dt>A[ñn]o</dt><dd>).*?(</dd>)',
                   lambda m: m.group(1) + anio + m.group(2), h, count=1)
    else:
        i = h.find('</dl>', h.find('class="project-specs"'))
        j = h.rindex('\n', 0, i) + 1
        h = h[:j] + ('          <div class="spec-row"><dt>Año</dt><dd>%s</dd></div>\n' % anio) + h[j:]
    # La linea de datos de arriba tambien lo lleva.
    def meta(m):
        cuerpo = m.group(2)
        if re.search(r'<span>[^<]*(19|20)\d{2}', cuerpo):
            cuerpo = re.sub(r'<span>([^<]*(?:19|20)\d{2}[^<]*)</span>',
                            '<span>%s</span>' % anio, cuerpo, count=1)
        else:
            cuerpo = cuerpo + '<span>%s</span>' % anio
        return m.group(1) + cuerpo + m.group(3)
    h = re.sub(r'(?s)(<div class="project-meta-row">)(.*?)(</div>)', meta, h, count=1)
    io.open(p, 'w', encoding='utf-8').write(h)


def main():
    # 1. Correcciones de año que vinieron del cliente.
    for slug, anio in sorted(ANIO_NUEVO.items()):
        viejo, _ = anio_de_ficha(slug)
        poner_en_ficha(slug, anio)
        print('  %-22s año %s -> %s' % (slug, viejo or '(vacio)', anio))

    # 2. El año vuelve a la tarjeta, copiado de la ficha.
    p = 'proyectos/index.html'
    h = io.open(p, encoding='utf-8').read()
    puestos, faltan = [], []

    def por_tarjeta(m):
        slug, cuerpo = m.group(1), m.group(2)
        if re.search(r'class="p-meta">.*?(19|20)\d{2}', cuerpo, re.S):
            return m.group(0)
        anio, _ = anio_de_ficha(slug)
        if not anio:
            faltan.append(slug)
            return m.group(0)
        puestos.append((slug, anio))
        return m.group(0).replace(
            '</div>\n            </div>',
            '<span>%s</span></div>\n            </div>' % anio, 1) \
            if False else re.sub(
                r'(class="p-meta">.*?)(</div>)',
                lambda x: x.group(1) + '<span>%s</span>' % anio + x.group(2),
                m.group(0), count=1, flags=re.S)

    for clase in ('project-card', 'project-list-row'):
        h = re.sub(r'(?s)<a href="/proyectos/([^"]+)/" class="%s"(.*?)</a>' % clase,
                   por_tarjeta, h)
    io.open(p, 'w', encoding='utf-8').write(h)

    vistos = []
    for s, a in puestos:
        if s not in vistos:
            vistos.append(s)
            print('  %-22s año en la tarjeta: %s' % (s, a))
    if faltan:
        print('\n  sin año en ningun lado: %s' % ', '.join(sorted(set(faltan))))

    # 3. Estado: las que el cliente dio por terminadas.
    h = io.open(p, encoding='utf-8').read()
    for slug in A_CONCLUIDA:
        h = re.sub(r'(data-slug="%s" data-estado=")proyecto(")' % re.escape(slug),
                   r'\1obra\2', h)
    io.open(p, 'w', encoding='utf-8').write(h)
    print('\n  pasan a obra concluida: %s' % ', '.join(A_CONCLUIDA))


if __name__ == '__main__':
    main()
