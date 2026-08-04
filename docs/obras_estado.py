# -*- coding: utf-8 -*-
"""Deja claro en cada trabajo si es obra concluida o proyecto en proceso.

Hasta ahora el dato vivia dentro del campo "Tipo" y con palabras distintas
segun la ficha: "en proceso", "en progreso", "concurso internacional". Y en
tres casos el texto decia una cosa y el atributo data-estado otra.

Aca pasa a ser un renglon propio de la ficha y un sello en la tarjeta, con
dos valores unicos. La fuente es data-estado del listado de proyectos, que
es lo que ya usan los filtros.

    python docs/obras_estado.py
"""
import io, os, re, html

ROTULO = {'obra': 'Obra concluida', 'proyecto': 'Proyecto en proceso'}
SELLO = {'obra': 'Concluida', 'proyecto': 'En proceso'}

# Coletillas de estado que quedaron pegadas al tipo y ahora sobran.
COLETILLA = re.compile(r'\s*(—|-|·)?\s*(en proceso|en progreso|en curso)\s*$', re.I)


def estados():
    h = io.open('proyectos/index.html', encoding='utf-8').read()
    return dict(re.findall(r'data-slug="([^"]+)" data-estado="([^"]+)"', h))


def ficha(slug, est):
    p = os.path.join('proyectos', slug, 'index.html')
    h = io.open(p, encoding='utf-8').read()
    antes = h
    if '<dt>Estado</dt>' not in h:
        # El renglon nuevo va primero, que es lo que se mira antes que nada.
        h = h.replace(
            '<dl class="project-specs">\n',
            '<dl class="project-specs">\n'
            '          <div class="spec-row"><dt>Estado</dt><dd>%s</dd></div>\n'
            % ROTULO[est], 1)

    def limpiar(m):
        v = COLETILLA.sub('', html.unescape(m.group(1))).strip(' —-·')
        return '<dt>Tipo</dt><dd>%s</dd>' % html.escape(v, quote=False)

    h = re.sub(r'<dt>Tipo</dt><dd>(.*?)</dd>', limpiar, h, count=1)
    # El renglon de datos de arriba repetia la coletilla.
    def limpiar_meta(m):
        v = COLETILLA.sub('', html.unescape(m.group(1))).strip(' —-·')
        return '<span>%s</span>' % html.escape(v, quote=False)
    h = re.sub(r'(?s)(<div class="project-meta-row">)(.*?)(</div>)',
               lambda m: m.group(1) + re.sub(r'<span>(.*?)</span>', limpiar_meta,
                                             m.group(2), count=1) + m.group(3), h, count=1)
    if h != antes:
        io.open(p, 'w', encoding='utf-8').write(h)
        return True
    return False


def listado(ests):
    p = 'proyectos/index.html'
    h = io.open(p, encoding='utf-8').read()
    if 'card-estado' in h:
        print('  el listado ya tiene los sellos')
        return 0
    n = [0]

    def poner(m):
        slug, est = m.group(1), m.group(2)
        n[0] += 1
        return (m.group(0) + '\n            <span class="card-estado card-estado--%s">%s</span>'
                % (est, SELLO[est]))

    # Solo en las tarjetas: la fila de lista es una grilla de cuatro columnas
    # y un hijo mas la desarma.
    h = re.sub(r'class="project-card" data-cat="[^"]*" data-slug="([^"]+)" '
               r'data-estado="([^"]+)">', poner, h, count=0)
    io.open(p, 'w', encoding='utf-8').write(h)
    return n[0]


def main():
    ests = estados()
    tocadas = 0
    for slug, est in sorted(ests.items()):
        if not os.path.isfile(os.path.join('proyectos', slug, 'index.html')):
            continue
        if ficha(slug, est):
            tocadas += 1
    print('fichas con estado propio: %d' % tocadas)
    print('sellos puestos en el listado: %d' % listado(ests))
    en_proceso = sorted(s for s, e in ests.items() if e == 'proyecto')
    print('\nen proceso (%d): %s' % (len(en_proceso), ', '.join(en_proceso)))


if __name__ == '__main__':
    main()
