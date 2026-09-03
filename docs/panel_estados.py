# -*- coding: utf-8 -*-
"""Pone en el listado el estado que dice la base, igual que en la ficha.

   panel_generar.py escribe la fila "Estado" de cada ficha, pero el listado de
   /proyectos/ no lo tocaba nadie. Resultado: el estudio cambiaba una obra de
   proyecto a concluida desde el panel, la ficha decia "Obra concluida" y la
   tarjeta seguia con el sello "Proyecto". Las dos paginas se contradecian, y
   ademas el filtro del listado trabaja contra ese mismo dato.

   De cada obra publicada actualiza, en su tarjeta y en su fila:

   - data-estado, que es contra lo que filtra el listado
   - los sellos "En progreso" / "Concurso" (las concluidas no llevan sello)

   Los concursos se distinguen por data-concurso: su estado de avance sigue en
   la base, pero en el listado forman una seccion aparte.

       python docs/panel_estados.py --verificar   # no escribe, solo informa
       python docs/panel_estados.py               # desde el JSON local
       python docs/panel_estados.py --supabase    # desde la base
"""
import io
import json
import os
import re
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LISTADO = os.path.join(RAIZ, 'proyectos', 'index.html')

# estado de la base -> (valor de data-estado, rotulo del sello)
SELLO = {
    'concluida':   ('obra', ''),
    'en_progreso': ('proyecto', 'En progreso'),
    'en_proyecto': ('proyecto', 'En progreso'),
}


def desde_supabase():
    url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY', '')
    if not url or not clave:
        raise SystemExit('Faltan SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno.')
    pedido = urllib.request.Request(
        url + '/rest/v1/obras?select=slug,estado&publicada=is.true',
        headers={'apikey': clave, 'Authorization': 'Bearer ' + clave})
    with urllib.request.urlopen(pedido, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def desde_json():
    p = os.path.join(RAIZ, 'docs', 'panel_datos.json')
    if not os.path.isfile(p):
        raise SystemExit('No existe docs/panel_datos.json. Corre con --supabase.')
    return [o for o in json.load(io.open(p, encoding='utf-8')) if o.get('publicada')]


def bloques(html, clase):
    """(inicio, fin, texto) de cada <a> de esa clase."""
    for m in re.finditer(r'<a\b[^>]*class="%s"[^>]*>' % re.escape(clase), html):
        fin = html.find('</a>', m.end())
        if fin < 0:
            continue
        yield m.start(), fin + len('</a>'), html[m.start():fin + len('</a>')]


def arreglar(bloque, valor, rotulo, con_sello):
    """Devuelve el bloque con el estado corregido, o el mismo si ya estaba bien."""
    nuevo = re.sub(r'data-estado="[^"]*"', 'data-estado="%s"' % valor, bloque, count=1)

    if con_sello:
        # Las concluidas siguen en Todas, pero ya no llevan un sello publico.
        # No cambiamos el estado guardado ni quitamos la tarjeta del listado.
        if not rotulo:
            return re.sub(r'<span class="card-estado[^"]*"[^>]*>[^<]*</span>',
                          '', nuevo)
        marca = ('<span class="card-estado card-estado--%s">%s</span>'
                 % (valor, rotulo))
        if 'card-estado' in nuevo:
            nuevo = re.sub(r'<span class="card-estado[^"]*"[^>]*>[^<]*</span>',
                           marca, nuevo, count=1)
        else:
            # Alguna tarjeta se cargo sin sello. Va apenas abierto el <a>, que es
            # donde esta en las demas.
            corte = nuevo.index('>') + 1
            nuevo = nuevo[:corte] + '\n            ' + marca + nuevo[corte:]
    return nuevo


def presentacion(html):
    """Mantiene los filtros y sellos pedidos aunque el molde tenga los viejos."""
    html = re.sub(r'\s*<button\b[^>]*data-estado-filtro="obra"[^>]*>.*?</button>',
                  '', html, flags=re.S)
    html = re.sub(r'(<button\b[^>]*data-estado-filtro="proyecto"[^>]*>).*?(</button>)',
                  r'\g<1>En progreso\g<2>', html, flags=re.S)
    for ini, fin, bloque in reversed(list(bloques(html, 'project-card'))):
        valor = (re.search(r'data-estado="([^"]+)"', bloque) or [None, ''])[1]
        rotulo = {'obra': '', 'proyecto': 'En progreso', 'concurso': 'Concurso'}.get(valor)
        if rotulo is not None:
            html = html[:ini] + arreglar(bloque, valor, rotulo, True) + html[fin:]
    return html


def main(verificar, supabase):
    obras = desde_supabase() if supabase else desde_json()
    estado = dict((o['slug'], o.get('estado')) for o in obras)
    if not estado:
        print('ERROR: la base no devolvio obras. No se toca nada.')
        return 1

    html = io.open(LISTADO, encoding='utf-8').read()
    original = html
    cambios, avisos = [], []

    for clase, con_sello in (('project-card', True), ('project-list-row', False)):
        # Se recorre de atras para adelante: cada reemplazo cambia el largo del
        # texto y hacia adelante correria las posiciones de los siguientes.
        for ini, fin, bloque in reversed(list(bloques(html, clase))):
            m = re.search(r'data-slug="([^"]+)"', bloque)
            if not m:
                continue
            slug = m.group(1)
            if slug not in estado:
                continue
            par = SELLO.get(estado[slug])
            if not par:
                avisos.append('%s: estado desconocido (%r)' % (slug, estado[slug]))
                continue

            if 'data-concurso="true"' in bloque:
                par = ('concurso', 'Concurso')

            nuevo = arreglar(bloque, par[0], par[1], con_sello)
            if nuevo != bloque:
                antes = (re.search(r'data-estado="([^"]*)"', bloque) or [None, '?'])[1]
                cambios.append('%-24s %-14s %s -> %s'
                               % (slug, clase.replace('project-', ''), antes, par[0]))
                html = html[:ini] + nuevo + html[fin:]

    html = presentacion(html)
    if html != original and not verificar:
        io.open(LISTADO, 'w', encoding='utf-8', newline='\n').write(html)

    print('obras publicadas: %d   corregidas en el listado: %d'
          % (len(estado), len(cambios)))
    for c in cambios:
        print('  ' + c)
    if avisos:
        print('\navisos:')
        for a in avisos:
            print('  ' + a)
    if verificar and html != original:
        print('\n(--verificar: no se toco nada)')
    return 0


if __name__ == '__main__':
    sys.exit(main('--verificar' in sys.argv, '--supabase' in sys.argv))
