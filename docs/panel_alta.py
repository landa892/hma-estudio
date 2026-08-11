# -*- coding: utf-8 -*-
"""Crea en el sitio la pagina de una obra que el estudio dio de alta en el panel.

   panel_generar.py reescribe zonas de paginas que ya existen; una obra nueva no
   tiene pagina y la saltaba con "no existe la pagina". Cargar una obra desde el
   panel la dejaba en la base y el sitio no cambiaba.

   Que hace por cada obra publicada que todavia no tiene pagina:

   - baja sus fotos de Supabase Storage a assets/gallery/<slug>/
   - crea proyectos/<slug>/index.html partiendo de una ficha existente
   - le suma la tarjeta y la fila al listado de /proyectos/
   - le suma la entrada al buscador, en los dos idiomas

   Las fotos se bajan al repo en vez de apuntar las paginas a Storage. Servirlas
   desde Storage obligaria a abrir el CSP del sitio publico a supabase.co y a
   gastar trafico de la cuota gratuita en cada visita; bajadas, una obra nueva
   queda igual que las 61 que ya estaban.

   El molde es una ficha real del sitio y no una plantilla aparte: una plantilla
   se desactualiza en silencio en cuanto alguien toca el diseño de las fichas.

       python docs/panel_alta.py --verificar   # no toca nada, solo informa
       python docs/panel_alta.py               # desde el JSON local
       python docs/panel_alta.py --supabase    # desde la base
"""
import glob
import io
import json
import os
import re
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'docs'))

MOLDE = os.path.join(RAIZ, 'proyectos', 'benedetta', 'index.html')
MOLDE_SLUG = 'benedetta'
LISTADO = os.path.join(RAIZ, 'proyectos', 'index.html')
BUSCADOR = os.path.join(RAIZ, 'scripts', 'search-index.js')
BUSCADOR_EN = os.path.join(RAIZ, 'scripts', 'search-index-en.js')

SITIO = 'https://estudiohma.com'
VISIBLES_GRILLA = 6      # las demas entran con el boton, igual que el resto

# Como llama el sitio a cada categoria. No se reusa el mapa de obras_grilla.py:
# ese quedo de antes de que "comercial" fuera su propia categoria y hoy le
# faltan valores del enum, asi que daria KeyError con una obra comercial.
CAT_ROTULO = {
    'gastronomico': 'Gastronómico',
    'hoteleria': 'Hotelería',
    'comercial': 'Comercial',
    'oficinas': 'Oficinas',
    'residencial': 'Residencial',
    'cultural': 'Cultural & Institucional',
}

ESTADOS = {
    'concluida': 'Obra concluida',
    'en_progreso': 'Proyecto en proceso',
    'en_proyecto': 'Proyecto',
}


def E(t):
    return (t or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ---------------------------------------------------------------------------
# De donde salen los datos
# ---------------------------------------------------------------------------

def _pedir(url, clave, ruta):
    pedido = urllib.request.Request(
        url + ruta, headers={'apikey': clave, 'Authorization': 'Bearer ' + clave})
    with urllib.request.urlopen(pedido, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def desde_supabase():
    url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY', '')
    if not url or not clave:
        raise SystemExit('Faltan SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno.')
    obras = _pedir(url, clave, '/rest/v1/obras?select=*&publicada=is.true&order=orden.asc')
    fotos = _pedir(url, clave,
                   '/rest/v1/obra_imagenes?select=obra_id,storage_path,orden,'
                   'es_portada,ancho,alto&order=orden.asc')
    porobra = {}
    for f in fotos:
        porobra.setdefault(f['obra_id'], []).append(f)
    for o in obras:
        o['_fotos'] = porobra.get(o['id'], [])
    return obras, url


def desde_json():
    p = os.path.join(RAIZ, 'docs', 'panel_datos.json')
    if not os.path.isfile(p):
        raise SystemExit('No existe docs/panel_datos.json. Corre con --supabase.')
    obras = json.load(io.open(p, encoding='utf-8'))
    for o in obras:
        o.setdefault('_fotos', [])
    return [o for o in obras if o.get('publicada')], None


# ---------------------------------------------------------------------------
# Fotos
# ---------------------------------------------------------------------------

def bajar_fotos(slug, imagenes, base_storage):
    """Deja las fotos como assets/gallery/<slug>/1.webp, 2.webp… y las describe.

    Se renumeran por orden: el nombre del archivo en Storage lleva un azar para
    no colisionar, pero las paginas del sitio piden 1.webp, 2.webp y asi.
    """
    if not imagenes:
        return []
    destino = os.path.join(RAIZ, 'assets', 'gallery', slug)
    if not os.path.isdir(destino):
        os.makedirs(destino)

    fuera = []
    for i, im in enumerate(imagenes, 1):
        local = os.path.join(destino, '%d.webp' % i)
        if not os.path.isfile(local):
            url = base_storage + '/storage/v1/object/public/obras/' + im['storage_path']
            with urllib.request.urlopen(url, timeout=120) as r:
                datos = r.read()
            io.open(local, 'wb').write(datos)
        fuera.append({'n': i,
                      'w': im.get('ancho') or 1800,
                      'h': im.get('alto') or 1200})
    return fuera


def fotos_del_disco(slug):
    """Para el modo sin base: lo que ya haya en assets/gallery/<slug>/."""
    d = os.path.join(RAIZ, 'assets', 'gallery', slug)
    fuera = []
    for n in range(1, 16):
        if os.path.isfile(os.path.join(d, '%d.webp' % n)):
            fuera.append({'n': n, 'w': 1800, 'h': 1200})
    return fuera


# ---------------------------------------------------------------------------
# La pagina
# ---------------------------------------------------------------------------

def ciudad(direccion):
    p = [x.strip() for x in (direccion or '').replace('.', '').split(',') if x.strip()]
    return p[-1] if p else ''


def bloque_filas(slug, titulo, fotos):
    if not fotos:
        return '\n'
    trozos = []
    for f in fotos[:3]:
        carga = (' loading="eager" decoding="async" fetchpriority="high"'
                 if f['n'] == 1 else ' loading="lazy" decoding="async"')
        trozos.append(
            '      <div class="project-row project-row--sola reveal">\n'
            '        <div class="project-row__photo"><img src="/assets/gallery/%s/%d.webp" '
            'width="%d" height="%d" alt="%s — foto %d"%s></div>\n      </div>\n'
            % (slug, f['n'], f['w'], f['h'], E(titulo), f['n'], carga))
    return ('\n    <section class="project-gallery">\n%s    </section>\n'
            % '\n'.join(trozos))


def bloque_grilla(slug, titulo, fotos):
    if not fotos:
        return '\n'
    items = '\n'.join(
        '          <figure class="gallery-grid__item%s"><img src="/assets/gallery/%s/%d.webp" '
        'alt="%s — foto %d" loading="lazy" decoding="async"></figure>'
        % ('' if i < VISIBLES_GRILLA else ' is-extra', slug, f['n'], E(titulo), f['n'])
        for i, f in enumerate(fotos))
    boton = ''
    if len(fotos) > VISIBLES_GRILLA:
        boton = ('\n        <button type="button" class="btn gallery-more" data-total="%d" '
                 'data-mas="Ver las %d fotos" data-menos="Ver menos fotos" '
                 'aria-expanded="false">Ver las %d fotos</button>'
                 % (len(fotos), len(fotos), len(fotos)))
    return ('\n    <section class="section no-border" id="galeria">\n'
            '      <div class="container">\n'
            '        <div class="section-head"><div><span class="eyebrow">Galería</span>'
            '<h2 class="display-3 mt-10">Todas las fotos</h2></div></div>\n'
            '        <div class="gallery-grid reveal">\n%s\n        </div>%s\n'
            '      </div>\n    </section>\n' % (items, boton))


def bloque_specs(o):
    """Solo los rotulos con valor. panel_generar respeta despues este orden."""
    orden = [('Estado', ESTADOS.get(o.get('estado'), '')),
             ('Tipo', o.get('tipologia')),
             ('Ubicación', o.get('ubicacion')),
             ('País', o.get('pais')),
             ('Superficie', o.get('superficie')),
             ('Año', o.get('anio')),
             ('Comitente', o.get('comitente'))]
    filas = ['          <div class="spec-row"><dt>%s</dt><dd>%s</dd></div>' % (r, E(v))
             for r, v in orden if (v or '').strip()]
    equipo = [x for x in (o.get('equipo') or []) if x.strip()]
    if equipo:
        filas.append('          <div class="spec-row spec-row--team"><dt>Equipo</dt>'
                     '<dd>%s</dd></div>' % '<br>'.join(E(x) for x in equipo))
    return '\n'.join(filas)


def crear_pagina(molde, o, fotos):
    slug, titulo = o['slug'], o['titulo']
    lede = (o.get('bajada') or '').strip()
    rotulo_cat = CAT_ROTULO.get(o.get('categoria') or '', '')

    meta = ('<div class="project-meta-row"><span>%s</span><span>%s</span>'
            '<span>%s</span><span>%s</span></div>'
            % (E(o.get('tipologia')), E(ciudad(o.get('ubicacion'))),
               E((o.get('superficie') or '').split(' · ')[0]), E(o.get('anio'))))

    h = molde
    h = re.sub(r'<title>.*?</title>',
               '<title>%s | Hitzig Militello Arquitectos</title>' % E(titulo), h)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + E(lede) + m.group(2), h)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
               lambda m: m.group(1) + E(titulo) + ' | Hitzig Militello Arquitectos'
               + m.group(2), h)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
               lambda m: m.group(1) + E(lede) + m.group(2), h)

    # Las rutas del molde: canonical, og:url, hreflang y boton de idioma.
    h = h.replace('/assets/gallery/%s/1.webp' % MOLDE_SLUG,
                  '/assets/gallery/%s/1.webp' % slug)
    # El og:image del molde apunta a su caratula de assets/covers/, que una obra
    # nueva no tiene: esas se recortan a mano desde el Drive. Va la primera foto
    # de la galeria, que es la que el estudio eligio como portada en el panel.
    h = h.replace('/assets/covers/%s.webp' % MOLDE_SLUG,
                  '/assets/gallery/%s/1.webp' % slug)
    h = h.replace('/proyectos/%s/' % MOLDE_SLUG, '/proyectos/%s/' % slug)
    h = h.replace('/en/projects/%s/' % MOLDE_SLUG, '/en/projects/%s/' % slug)

    h = re.sub(r'<span class="eyebrow">.*?</span>',
               '<span class="eyebrow">%s</span>' % E(rotulo_cat), h, count=1)
    h = re.sub(r'<h1 class="display-2 mt-14">.*?</h1>',
               '<h1 class="display-2 mt-14">%s</h1>' % E(titulo), h, count=1)
    h = re.sub(r'<p class="lede">.*?</p>', '<p class="lede">%s</p>' % E(lede), h, count=1)
    h = re.sub(r'(?s)<div class="project-meta-row">.*?</div>', meta, h, count=1)
    h = re.sub(r'(?s)(<dl class="project-specs">).*?(\n\s*</dl>)',
               lambda m: m.group(1) + '\n' + bloque_specs(o) + m.group(2), h, count=1)

    # La memoria la escribe panel_generar; aca se saca la del molde para no
    # dejar publicada la de otra obra si esta no tiene.
    h = re.sub(r'(?s)\n    <section class="project-memoria">.*?\n    </section>\n',
               '\n', h, count=1)
    h = re.sub(r'(?s)\n    <section class="project-gallery">.*?\n    </section>\n',
               lambda _: bloque_filas(slug, titulo, fotos), h, count=1)
    # La grilla del molde trae sus planos; los de otra obra no van aca.
    h = re.sub(r'(?s)\n    <section class="section no-border" id="galeria">.*?\n    </section>\n',
               lambda _: bloque_grilla(slug, titulo, fotos), h, count=1)

    # El dominio se fuerza en vez de heredarse del molde: una obra nueva no tiene
    # por que arrastrar el host que tuviera la ficha que se uso de plantilla, y
    # con el host equivocado la vista previa al compartir sale sin imagen.
    h = re.sub(r'(<meta property="og:(?:url|image)" content=")https?://[^/"]+',
               lambda m: m.group(1) + SITIO, h)

    if MOLDE_SLUG in h:
        raise SystemExit('%s: quedo una referencia al molde (%s). No se escribe.'
                         % (slug, MOLDE_SLUG))
    return h


# ---------------------------------------------------------------------------
# Listado y buscador
# ---------------------------------------------------------------------------

def tarjeta_y_fila(o, fotos):
    slug, titulo = o['slug'], o['titulo']
    cat = o.get('categoria') or ''
    rotulo = E(CAT_ROTULO.get(cat, ''))
    metas = [E(o.get('tipologia')), E(ciudad(o.get('ubicacion'))),
             E((o.get('superficie') or '').split(' · ')[0]), E(o.get('anio'))]
    metas = [m for m in metas if m]
    spans = ''.join('<span>%s</span>' % m for m in metas)
    img = '/assets/gallery/%s/1.webp' % slug
    w = fotos[0]['w'] if fotos else 1800
    hh = fotos[0]['h'] if fotos else 1200
    anio = metas[-1] if metas else ''

    tarjeta = (
        '          <a href="/proyectos/%s/" class="project-card" data-cat="%s" '
        'data-slug="%s" data-estado="obra">\n'
        '            <span class="card-cat">%s</span>\n'
        '            <img src="%s" width="%d" height="%d" alt="%s" loading="lazy" decoding="async">\n'
        '            <div class="card-plate">\n'
        '              <div class="p-name">%s</div>\n'
        '              <div class="p-meta">%s</div>\n'
        '            </div>\n'
        '          </a>\n'
        % (slug, cat, slug, rotulo, img, w, hh, E(titulo), E(titulo), spans))

    fila = (
        '          <a href="/proyectos/%s/" class="project-list-row" data-cat="%s" '
        'data-slug="%s" data-estado="obra">\n'
        '            <div class="plr-thumb"><img src="%s" width="%d" height="%d" alt="" loading="lazy"></div>\n'
        '            <div><div class="plr-name">%s</div><div class="plr-meta">%s</div></div>\n'
        '            <div class="plr-cat">%s</div><div class="plr-loc">%s</div>\n'
        '          </a>\n'
        % (slug, cat, slug, img, w, hh, E(titulo), spans, rotulo, anio))
    return tarjeta, fila


def sumar_al_listado(html, o, fotos):
    tarjeta, fila = tarjeta_y_fila(o, fotos)
    for clase, bloque in (('project-card', tarjeta), ('project-list-row', fila)):
        ultimo = html.rfind('class="%s"' % clase)
        if ultimo < 0:
            raise SystemExit('no encuentro el contenedor de %s' % clase)
        fin = html.index('</a>', ultimo) + len('</a>\n')
        html = html[:fin] + bloque + html[fin:]
    return html


def sumar_al_buscador(o, fotos):
    metas = [o.get('tipologia'), ciudad(o.get('ubicacion')),
             (o.get('superficie') or '').split(' · ')[0], o.get('anio')]
    desc = ' · '.join(x for x in metas if x)
    for archivo, url in ((BUSCADOR, '/proyectos/%s/' % o['slug']),
                         (BUSCADOR_EN, '/en/projects/%s/' % o['slug'])):
        if not os.path.isfile(archivo):
            continue
        crudo = io.open(archivo, encoding='utf-8').read()
        cabeza = crudo[:crudo.index('[')]
        indice = json.loads(crudo[crudo.index('['):crudo.rindex(']') + 1])
        if any(e.get('url') == url for e in indice):
            continue
        # En ingles va el titulo tal cual —es nombre propio— y la descripcion
        # queda en castellano hasta que en_gen la pase por el diccionario.
        indice.append({'tipo': 'Proyecto', 'titulo': o['titulo'],
                       'sub': CAT_ROTULO.get(o.get('categoria') or '', ''),
                       'desc': desc, 'url': url,
                       'img': '/assets/gallery/%s/1.webp' % o['slug']})
        io.open(archivo, 'w', encoding='utf-8', newline='\n').write(
            cabeza + json.dumps(indice, ensure_ascii=False, indent=1) + ';\n')


# ---------------------------------------------------------------------------

def main(verificar, supabase):
    obras, base_storage = desde_supabase() if supabase else desde_json()
    con_pagina = set(os.path.basename(os.path.dirname(p))
                     for p in glob.glob(os.path.join(RAIZ, 'proyectos', '*', 'index.html')))
    nuevas = [o for o in obras if o['slug'] not in con_pagina]

    print('publicadas: %d   ya con pagina: %d   nuevas: %d'
          % (len(obras), len(obras) - len(nuevas), len(nuevas)))
    if not nuevas:
        return 0

    for o in nuevas:
        print('  %-28s %s' % (o['slug'], o.get('titulo') or ''))
    if verificar:
        print('\n(--verificar: no se toco nada)')
        return 0

    molde = io.open(MOLDE, encoding='utf-8').read()
    html = io.open(LISTADO, encoding='utf-8').read()

    for o in nuevas:
        if not (o.get('titulo') or '').strip():
            print('  aviso: %s no tiene titulo, se saltea' % o['slug'])
            continue
        fotos = (bajar_fotos(o['slug'], o.get('_fotos') or [], base_storage)
                 if supabase else fotos_del_disco(o['slug']))
        if not fotos:
            print('  aviso: %s no tiene fotos; la pagina sale sin galeria'
                  % o['slug'])

        pagina = crear_pagina(molde, o, fotos)
        d = os.path.join(RAIZ, 'proyectos', o['slug'])
        if not os.path.isdir(d):
            os.makedirs(d)
        io.open(os.path.join(d, 'index.html'), 'w', encoding='utf-8',
                newline='\n').write(pagina)

        html = sumar_al_listado(html, o, fotos)
        sumar_al_buscador(o, fotos)
        print('  creada %-26s %d fotos' % (o['slug'], len(fotos)))

    io.open(LISTADO, 'w', encoding='utf-8', newline='\n').write(html)

    tarjetas = len(re.findall(r'class="project-card"', html))
    filas = len(re.findall(r'class="project-list-row"', html))
    print('\ntarjetas: %d   filas: %d' % (tarjetas, filas))
    if tarjetas != filas:
        print('OJO: el listado quedo descalzado. Revisar antes de publicar.')
        return 1
    print('\nFalta correr panel_generar.py, sitemap_gen.py y en_gen.py.')
    return 0


if __name__ == '__main__':
    sys.exit(main('--verificar' in sys.argv, '--supabase' in sys.argv))
