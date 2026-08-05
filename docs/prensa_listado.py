# -*- coding: utf-8 -*-
"""Arma el listado completo de publicaciones a partir del CV del estudio.

La pagina mostraba quince notas. El CV extendido trae 255, con mes, medio,
pais y obra, desde 2003. No trae el link de cada una, asi que este listado
no reemplaza al bloque "Notas que se pueden leer online" —ese sigue siendo
el de las que se pueden abrir— sino que se suma como el registro completo.

Donde la obra existe en el sitio, el nombre enlaza a su ficha.

    python docs/prensa_listado.py
"""
import io, json, os, re, html, unicodedata, difflib, collections

DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prensa_cv.json')
MESES = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
         'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
MARCA = 'id="todasLasPublicaciones"'

# El CV nombra algunas obras distinto que el sitio.
ALIAS = {
    'manducamarket': 'manduca', 'mercadomanduca': 'manduca',
    'manducapaseolaplaza': 'manduca',
    'araoz757': 'araoz', 'edificioaraoz': 'araoz',
    'thebirraproject': 'the-birra',
    'edificiomultifamiliarbolivar': 'bolivar', 'edificiobolivar': 'bolivar',
    'edificiomalabia': 'malabia', 'malabia1918': 'malabia',
    'moshutreehouse': 'moshu', 'moshupalermo': 'moshu',
    'thenimbar': 'nim-bar', 'nimbar': 'nim-bar',
    'ostencoffeeshopcasafoa': 'osten-foa', 'casafoa': 'osten-foa',
    'torreosten': 'osten-tower',
    'movistararenaviplounges': 'movistar-arena', 'viploungemovistararena': 'movistar-arena',
    'stellaartoismercat': 'stella-artois-mercat', 'stellaartois': 'stella-artois-mercat',
    'williamsburgpaseodelainfanta': 'williamsburg',
    'antiquetentazioni': 'antiche', 'antichetentazioni': 'antiche',
    'burger7167': 'burger-7167', '7167burger': 'burger-7167',
    'atelliervilela': 'atelier-vilela',
    'centroculturaldeespanaenbuenosaires': 'cceba',
    'hyattzivabarbados': 'hyatt-ziva',
    'iolinvertironline': 'iol', 'iolsupervielle': 'iol',
}
# Notas sobre el estudio, no sobre una obra: no llevan enlace.
GENERICAS = {'entrevista', 'interview', 'concurso', 'hitzigmilitelloarchitects',
             'hitzigmilitelloarquitectos', ''}


def norm(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '', s)


def obras_del_sitio():
    h = io.open('proyectos/index.html', encoding='utf-8').read()
    d = {}
    for m in re.finditer(r'(?s)<a href="/proyectos/([^"]+)/" class="project-card".*?'
                         r'class="p-name">(.*?)<', h):
        slug, nom = m.group(1), html.unescape(m.group(2)).strip()
        d[norm(nom)] = (slug, nom)
        d[norm(slug)] = (slug, nom)
    return d


def resolver(notas, sitio):
    porslug = {s: n for s, n in sitio.values()}
    for n in notas:
        k = norm(n['obra'])
        if k in GENERICAS:
            n['slug'] = None
            continue
        if k in ALIAS and ALIAS[k] in porslug:
            n['slug'], n['titulo'] = ALIAS[k], porslug[ALIAS[k]]
            continue
        if k in sitio:
            n['slug'], n['titulo'] = sitio[k]
            continue
        c = difflib.get_close_matches(k, sitio.keys(), 1, 0.82)
        n['slug'], n['titulo'] = (sitio[c[0]] if c else (None, None))
    return notas


def bloque(notas):
    porانio = collections.OrderedDict()
    for n in sorted(notas, key=lambda x: (-x['anio'], -x['mes'])):
        porانio.setdefault(n['anio'], []).append(n)
    e = lambda s: html.escape(s or '', quote=False)
    fuera = []
    for i, (anio, ns) in enumerate(porانio.items()):
        filas = []
        for n in ns:
            obra = e(n['obra'])
            if n.get('slug'):
                obra = '<a href="/proyectos/%s/">%s</a>' % (n['slug'], e(n['titulo']))
            fecha = '%s %d' % (MESES[n['mes']].capitalize(), anio) if n['mes'] else str(anio)
            medio = e(n['medio']) + (' — ' + e(n['pais']) if n['pais'] else '')
            filas.append('            <div class="press-row">\n'
                         '              <div class="pr-date">%s</div>\n'
                         '              <div class="pr-text">%s</div>\n'
                         '              <div class="pr-outlet">%s</div>\n'
                         '            </div>' % (fecha, obra, medio))
        oculto = '' if i < 3 else ' is-extra'
        fuera.append('          <div class="pub-anio%s">\n'
                     '            <div class="press-year-head">%d</div>\n%s\n'
                     '          </div>' % (oculto, anio, '\n'.join(filas)))
    n_ocultos = sum(len(v) for k, v in list(porانio.items())[3:])
    boton = ''
    if n_ocultos:
        boton = ('\n        <button type="button" class="btn pub-more" '
                 'data-mas="Ver las %d publicaciones" data-menos="Ver menos publicaciones" '
                 'aria-expanded="false">Ver las %d publicaciones</button>'
                 % (len(notas), len(notas)))
    return ('\n    <section class="section no-border" id="todasLasPublicaciones">\n'
            '      <div class="container">\n'
            '        <div class="section-head"><div><span class="eyebrow">Archivo</span>'
            '<h2 class="display-3 mt-10">Todas las publicaciones</h2></div></div>\n'
            '        <div class="pub-lista reveal">\n%s\n        </div>%s\n'
            '      </div>\n    </section>\n' % ('\n'.join(fuera), boton))


def main():
    notas = json.load(io.open(DATOS, encoding='utf-8'))
    notas = resolver(notas, obras_del_sitio())
    con = sum(1 for n in notas if n.get('slug'))
    p = 'prensa/index.html'
    h = io.open(p, encoding='utf-8').read()
    if MARCA in h:
        h = re.sub(r'(?s)\n    <section class="section no-border" id="todasLasPublicaciones">.*?\n    </section>\n',
                   '\n', h)
    ancla = '\n    <!-- BLOQUE YOUTUBE -->'
    if ancla not in h:
        raise SystemExit('no se encontro donde insertar el listado')
    io.open(p, 'w', encoding='utf-8').write(h.replace(ancla, bloque(notas) + ancla, 1))
    anios = sorted({n['anio'] for n in notas})
    print('publicaciones: %d   con enlace a la obra: %d   años: %d-%d'
          % (len(notas), con, anios[0], anios[-1]))


if __name__ == '__main__':
    main()
