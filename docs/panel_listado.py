# -*- coding: utf-8 -*-
"""Sincroniza las tarjetas de Trabajos con los datos editables del panel.

La ficha individual ya se regeneraba desde la base, pero el titulo y la
categoria del listado quedaban congelados en el HTML. Eso
hacia que una edicion correcta desde el panel pudiera mostrar dos versiones de
la misma obra. Este paso conserva la portada y la posicion de cada tarjeta, y
actualiza solamente sus textos y atributos.
"""
import io
import json
import os
import re
import sys
import urllib.request


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LISTADO = os.path.join(RAIZ, 'proyectos', 'index.html')
BUSCADOR = os.path.join(RAIZ, 'scripts', 'search-index.js')

CAT_ROTULO = {
    'hoteleria': 'Hotelería',
    'comercial': 'Comercial',
    'gastronomico': 'Gastronómico',
    'residencial': 'Residencial',
    'oficinas': 'Oficinas',
    'cultural': 'Cultural & Institucional',
}


def escapar(texto):
    return ((texto or '').replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


def desde_json():
    ruta = os.path.join(RAIZ, 'docs', 'panel_datos.json')
    return [o for o in json.load(io.open(ruta, encoding='utf-8'))
            if o.get('publicada')]


def desde_supabase():
    url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY', '')
    if not url or not clave:
        raise SystemExit('Faltan SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno.')
    campos = 'slug,titulo,categoria,publicada'
    pedido = urllib.request.Request(
        url + '/rest/v1/obras?select=' + campos + '&publicada=is.true',
        headers={'apikey': clave, 'Authorization': 'Bearer ' + clave})
    with urllib.request.urlopen(pedido, timeout=30) as respuesta:
        return json.loads(respuesta.read().decode('utf-8'))


def reemplazar_clase(html, clase, obras):
    cambios = []
    patron = re.compile(r'<a\b[^>]*class="%s"[^>]*>.*?</a>' % re.escape(clase), re.S)

    def aplicar(m):
        bloque = m.group(0)
        slug_m = re.search(r'data-slug="([^"]+)"', bloque)
        if not slug_m or slug_m.group(1) not in obras:
            return bloque
        o = obras[slug_m.group(1)]
        cat = o.get('categoria') or ''
        titulo = escapar(o.get('titulo'))
        rotulo = escapar(CAT_ROTULO.get(cat, ''))
        cat_actual = (re.search(r'data-cat="([^"]*)"', bloque) or [None, ''])[1]
        nuevo = bloque
        if cat_actual != cat:
            nuevo = re.sub(r'data-cat="[^"]*"', 'data-cat="%s"' % cat,
                           nuevo, count=1)
        if clase == 'project-card':
            titulo_actual = (re.search(r'<div class="p-name">(.*?)</div>',
                                       bloque, re.S) or [None, ''])[1]
            # Se compara el rotulo contra si mismo y no contra data-cat: el
            # sitio tenia tarjetas con la categoria correcta y el texto viejo
            # -Novotel decia "Hotelería & Comercial" con data-cat="hoteleria"-,
            # y atadas a data-cat esas nunca se corregian.
            rotulo_actual = (re.search(r'<span class="card-cat">(.*?)</span>',
                                       bloque, re.S) or [None, ''])[1]
            if rotulo_actual != rotulo:
                nuevo = re.sub(r'(<span class="card-cat">).*?(</span>)',
                               r'\g<1>%s\g<2>' % rotulo, nuevo,
                               count=1, flags=re.S)
            if titulo_actual != titulo:
                nuevo = re.sub(r'(<div class="p-name">).*?(</div>)',
                               r'\g<1>%s\g<2>' % titulo, nuevo,
                               count=1, flags=re.S)
                nuevo = re.sub(r'(<img\b[^>]*\balt=")[^"]*(")',
                               r'\g<1>%s\g<2>' % titulo, nuevo, count=1)
        else:
            titulo_actual = (re.search(r'<div class="plr-name">(.*?)</div>',
                                       bloque, re.S) or [None, ''])[1]
            if titulo_actual != titulo:
                nuevo = re.sub(r'(<div class="plr-name">).*?(</div>)',
                               r'\g<1>%s\g<2>' % titulo, nuevo,
                               count=1, flags=re.S)
            rotulo_actual = (re.search(r'<div class="plr-cat">(.*?)</div>',
                                       bloque, re.S) or [None, ''])[1]
            if rotulo_actual != rotulo:
                nuevo = re.sub(r'(<div class="plr-cat">).*?(</div>)',
                               r'\g<1>%s\g<2>' % rotulo, nuevo,
                               count=1, flags=re.S)
        if nuevo != bloque:
            cambios.append(slug_m.group(1) + ':' + clase)
        return nuevo

    return patron.sub(aplicar, html), cambios


def sincronizar_buscador(obras, slugs, verificar):
    if not slugs or not os.path.isfile(BUSCADOR):
        return 0
    crudo = io.open(BUSCADOR, encoding='utf-8').read()
    inicio, fin = crudo.index('['), crudo.rindex(']') + 1
    entradas = json.loads(crudo[inicio:fin])
    cambios = 0
    por_url = {'/proyectos/%s/' % slug: obras[slug] for slug in slugs}
    for entrada in entradas:
        o = por_url.get(entrada.get('url'))
        if not o:
            continue
        nuevos = {
            'titulo': o.get('titulo') or '',
            'sub': CAT_ROTULO.get(o.get('categoria') or '', ''),
        }
        for campo, valor in nuevos.items():
            if entrada.get(campo) != valor:
                entrada[campo] = valor
                cambios += 1
    if cambios and not verificar:
        io.open(BUSCADOR, 'w', encoding='utf-8', newline='\n').write(
            crudo[:inicio] + json.dumps(entradas, ensure_ascii=False, indent=1)
            + crudo[fin:])
    return cambios


def rotulo_en_fichas(obras, verificar):
    """El rotulo de arriba del titulo, dentro de cada ficha.

    El listado ya salia de la base, pero ese rotulo se habia cargado a mano y
    quedo viejo: Accor y Novotel seguian diciendo "Hotelería & Comercial", de
    antes de que el cliente pidiera separar las dos categorias.
    """
    cambios = []
    for slug, o in sorted(obras.items()):
        rotulo = escapar(CAT_ROTULO.get(o.get('categoria') or ''))
        if not rotulo:
            continue
        ruta = os.path.join(RAIZ, 'proyectos', slug, 'index.html')
        if not os.path.isfile(ruta):
            continue
        h = io.open(ruta, encoding='utf-8').read()
        m = re.search(r'<span class="eyebrow">(.*?)</span>', h)
        if not m or m.group(1).strip() == rotulo:
            continue
        cambios.append('%-22s %s -> %s' % (slug, m.group(1).strip(), rotulo))
        if not verificar:
            io.open(ruta, 'w', encoding='utf-8', newline='\n').write(
                h[:m.start(1)] + rotulo + h[m.end(1):])
    return cambios


def main(verificar, supabase):
    filas = desde_supabase() if supabase else desde_json()
    obras = {o['slug']: o for o in filas}
    html = io.open(LISTADO, encoding='utf-8').read()
    nuevo, cambios_tarjetas = reemplazar_clase(html, 'project-card', obras)
    nuevo, cambios_filas = reemplazar_clase(nuevo, 'project-list-row', obras)
    cambios = cambios_tarjetas + cambios_filas
    slugs = set(c.split(':', 1)[0] for c in cambios)
    cambios_buscador = sincronizar_buscador(obras, slugs, verificar)
    cambios_fichas = rotulo_en_fichas(obras, verificar)
    print('obras publicadas: %d   bloques sincronizados: %d' % (len(obras), len(cambios)))
    if cambios:
        print('  ' + ', '.join(cambios[:16]) + ('…' if len(cambios) > 16 else ''))
    print('entradas del buscador sincronizadas: %d' % cambios_buscador)
    if cambios_fichas:
        print('rotulo corregido en %d fichas:' % len(cambios_fichas))
        for c in cambios_fichas:
            print('  ' + c)
    if nuevo != html and not verificar:
        io.open(LISTADO, 'w', encoding='utf-8', newline='\n').write(nuevo)
    if verificar and cambios:
        print('\n(--verificar: no se toco nada)')
    return 0


if __name__ == '__main__':
    sys.exit(main('--verificar' in sys.argv, '--supabase' in sys.argv))
