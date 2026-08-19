# -*- coding: utf-8 -*-
"""Conecta las galerias historicas y las nuevas con el panel.

Las obras anteriores al panel conservan su galeria publica hasta que el estudio
hace el primer cambio. En la base se carga una seleccion inicial de hasta 15
fotos con el prefijo ``@seed:``. El panel cambia ese prefijo a ``@site:`` al
reordenar, borrar, subir o elegir portada; desde entonces este generador toma la
base como fuente y reescribe la galeria.
"""
import io
import hashlib
import json
import os
import re
import struct
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, 'docs', 'panel_datos.json')
LISTADO = os.path.join(RAIZ, 'proyectos', 'index.html')
BUSCADOR = os.path.join(RAIZ, 'scripts', 'search-index.js')
MAPA_PORTADAS = os.path.join(RAIZ, 'docs', 'panel_portadas.json')
SITIO = 'https://estudiohma.com'
VISIBLES = 6
TOPE = 15


def e(texto):
    return (texto or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def medidas_webp(ruta):
    try:
        with io.open(ruta, 'rb') as archivo:
            cab = archivo.read(30)
    except OSError:
        return None
    if len(cab) < 30 or cab[:4] != b'RIFF' or cab[8:12] != b'WEBP':
        return None
    if cab[12:16] == b'VP8X':
        w = cab[24] | (cab[25] << 8) | (cab[26] << 16)
        h = cab[27] | (cab[28] << 8) | (cab[29] << 16)
        return w + 1, h + 1
    if cab[12:16] == b'VP8 ':
        w, h = struct.unpack('<HH', cab[26:30])
        return w & 0x3FFF, h & 0x3FFF
    if cab[12:16] == b'VP8L':
        bits = struct.unpack('<I', cab[21:25])[0]
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    return None


def pedir(url, clave, ruta, metodo='GET', cuerpo=None):
    datos = None if cuerpo is None else json.dumps(cuerpo).encode('utf-8')
    pedido = urllib.request.Request(
        url + ruta, data=datos, method=metodo,
        headers={'apikey': clave, 'Authorization': 'Bearer ' + clave,
                 'Content-Type': 'application/json', 'Prefer': 'return=minimal'})
    with urllib.request.urlopen(pedido, timeout=120) as respuesta:
        crudo = respuesta.read()
        return json.loads(crudo.decode('utf-8')) if crudo else None


def ruta_local(publica):
    return os.path.join(RAIZ, publica.lstrip('/').replace('/', os.sep))


REPETIDAS = os.path.join(RAIZ, 'docs', 'galeria_repetidas.json')


def fotos_repetidas():
    """{slug: {archivos que repiten la portada u otra foto de la misma obra}}.

    La lista la calcula docs/galeria_repetidas.py comparando las imagenes, que
    necesita Pillow y por eso corre fuera del build. Aca solo se lee.

    El deduplicador de mas abajo compara por SHA1 y no alcanza: la portada y su
    copia dentro de la galeria son la misma foto guardada dos veces, con
    distinto peso, asi que los bytes no coinciden. Era el caso de once de las
    doce obras que el cliente marco como "foto repetida" el 19/08/2026.
    """
    if not os.path.isfile(REPETIDAS):
        return {}
    with io.open(REPETIDAS, encoding='utf-8') as archivo:
        return dict((slug, set(nombres))
                    for slug, nombres in json.load(archivo).items())


def seleccion_inicial(obra):
    candidatas = []
    portada = obra.get('portada')
    if portada:
        candidatas.append(portada)
    candidatas.extend('/assets/gallery/%s/%s' % (obra['slug'], nombre)
                      for nombre in obra.get('galeria') or [])

    sobran = fotos_repetidas().get(obra['slug'], set())

    vistas, contenidos, filas = set(), set(), []
    for publica in candidatas:
        if publica in vistas or len(filas) >= TOPE:
            continue
        if os.path.basename(publica) in sobran and publica != portada:
            continue
        local = ruta_local(publica)
        medidas = medidas_webp(local)
        if not medidas:
            continue
        with open(local, 'rb') as archivo:
            huella = hashlib.sha1(archivo.read()).digest()
        if huella in contenidos:
            continue
        vistas.add(publica)
        contenidos.add(huella)
        filas.append({
            'storage_path': '@seed:' + publica,
            'alt': '%s — foto %d' % (obra['titulo'], len(filas) + 1),
            'orden': len(filas),
            'es_portada': publica == portada if portada else len(filas) == 0,
            'ancho': medidas[0],
            'alto': medidas[1],
        })
    if filas and not any(f['es_portada'] for f in filas):
        filas[0]['es_portada'] = True
    return filas


def sembrar(obras, por_slug, existentes, url, clave):
    nuevas = []
    ids_con_fotos = {f['obra_id'] for f in existentes}
    for obra in obras:
        fila = por_slug.get(obra['slug'])
        if not fila or fila['id'] in ids_con_fotos:
            continue
        for foto in seleccion_inicial(obra):
            foto['obra_id'] = fila['id']
            nuevas.append(foto)
    if nuevas:
        pedir(url, clave, '/rest/v1/obra_imagenes', 'POST', nuevas)
        print('galerias historicas conectadas al panel: %d fotos' % len(nuevas))
    else:
        print('galerias historicas ya conectadas')
    return bool(nuevas)


def sincronizar_semillas(obras, por_slug, existentes, url, clave):
    """Actualiza sólo selecciones heredadas que el estudio todavía no editó.

    Si cambian las fotos locales de una obra, el panel no puede seguir mostrando
    rutas @seed que ya no existen. Las galerías administradas (@site o Storage)
    quedan fuera de esta sincronización para no pisar decisiones del estudio.
    """
    por_obra = {}
    for foto in existentes:
        por_obra.setdefault(foto['obra_id'], []).append(foto)

    actualizadas = 0
    for obra in obras:
        fila = por_slug.get(obra['slug'])
        if not fila:
            continue
        actuales = sorted(por_obra.get(fila['id'], []), key=lambda f: f['orden'])
        if not actuales or not all(f['storage_path'].startswith('@seed:') for f in actuales):
            continue
        deseadas = seleccion_inicial(obra)
        firma_actual = [(f['storage_path'], f['orden'], bool(f['es_portada']),
                         f.get('ancho'), f.get('alto')) for f in actuales]
        firma_deseada = [(f['storage_path'], f['orden'], bool(f['es_portada']),
                          f.get('ancho'), f.get('alto')) for f in deseadas]
        if firma_actual == firma_deseada:
            continue
        pedir(url, clave, '/rest/v1/obra_imagenes?obra_id=eq.%s' % fila['id'], 'DELETE')
        for foto in deseadas:
            foto['obra_id'] = fila['id']
        if deseadas:
            pedir(url, clave, '/rest/v1/obra_imagenes', 'POST', deseadas)
        actualizadas += 1
    if actualizadas:
        print('selecciones historicas actualizadas: %d obras' % actualizadas)
    return bool(actualizadas)


def resolver_foto(slug, foto, url):
    ruta = foto['storage_path']
    if ruta.startswith('@seed:') or ruta.startswith('@site:'):
        publica = ruta.split(':', 1)[1]
    else:
        carpeta = os.path.join(RAIZ, 'assets', 'gallery', slug)
        os.makedirs(carpeta, exist_ok=True)
        publica = '/assets/gallery/%s/panel-%s.webp' % (slug, foto['id'])
        local = ruta_local(publica)
        if not os.path.isfile(local):
            origen = url + '/storage/v1/object/public/obras/' + ruta
            with urllib.request.urlopen(origen, timeout=120) as respuesta:
                contenido = respuesta.read()
            with open(local, 'wb') as archivo:
                archivo.write(contenido)
    return {
        'src': publica,
        'w': foto.get('ancho') or 1,
        'h': foto.get('alto') or 1,
        'alt': foto.get('alt') or '',
        'portada': bool(foto.get('es_portada')),
    }


def bloque_filas(actual, titulo, fotos):
    """Conserva los textos intercalados y cambia solamente sus fotografias."""
    portada = next((foto for foto in fotos if foto['portada']), fotos[0])
    fotos = [portada] + [foto for foto in fotos if foto is not portada]
    filas = re.findall(r'(?s)      <div class="project-row.*?\n      </div>', actual)
    if not filas:
        filas = ['      <div class="project-row project-row--sola reveal">\n'
                 '        <div class="project-row__photo"><img></div>\n      </div>'] * 3
    nuevas = []
    for i, (fila, foto) in enumerate(zip(filas, fotos), 1):
        carga = ('loading="eager" decoding="async" fetchpriority="high"'
                 if i == 1 else 'loading="lazy" decoding="async"')
        img = '<img src="%s" width="%s" height="%s" alt="%s" %s>' % (
            foto['src'], foto['w'], foto['h'], e(foto['alt'] or
            '%s — foto %d' % (titulo, i)), carga)
        nuevas.append(re.sub(r'<img\b[^>]*>', img, fila, count=1))
    return '\n    <section class="project-gallery">\n%s\n    </section>\n' % '\n\n'.join(nuevas)


def bloque_grilla(titulo, fotos, planos):
    items = []
    for i, foto in enumerate(fotos, 1):
        extra = '' if i <= VISIBLES else ' is-extra'
        items.append(
            '          <figure class="gallery-grid__item%s"><img src="%s" width="%s" '
            'height="%s" alt="%s" loading="lazy" decoding="async"></figure>'
            % (extra, foto['src'], foto['w'], foto['h'],
               e(foto['alt'] or '%s — foto %d' % (titulo, i))))
        if i == VISIBLES:
            items.extend(planos)
    if len(fotos) < VISIBLES:
        items.extend(planos)
    boton = ''
    if len(fotos) > VISIBLES:
        boton = ('\n        <button type="button" class="btn gallery-more" data-total="%d" '
                 'data-mas="Ver las %d fotos" data-menos="Ver menos fotos" '
                 'aria-expanded="false">Ver las %d fotos</button>'
                 % (len(fotos), len(fotos), len(fotos)))
    return ('\n    <section class="section no-border" id="galeria">\n'
            '      <div class="container">\n'
            '        <div class="section-head"><div><span class="eyebrow">Galería</span>'
            '<h2 class="display-3 mt-10">Todas las fotos</h2></div></div>\n'
            '        <div class="gallery-grid reveal">\n%s\n        </div>%s\n'
            '      </div>\n    </section>\n' % ('\n'.join(items), boton))


def actualizar_pagina(slug, titulo, fotos):
    ruta = os.path.join(RAIZ, 'proyectos', slug, 'index.html')
    if not os.path.isfile(ruta):
        return False
    html = io.open(ruta, encoding='utf-8').read()
    portada = next((f for f in fotos if f['portada']), fotos[0])
    planos = re.findall(
        r'<figure class="gallery-grid__item gallery-grid__item--plano">.*?</figure>',
        html, flags=re.S)
    nuevo = re.sub(r'(?s)\n    <section class="project-gallery">.*?\n    </section>\n',
                   lambda m: bloque_filas(m.group(0), titulo, fotos), html, count=1)
    nuevo = re.sub(r'(?s)\n    <section class="section no-border" id="galeria">.*?\n    </section>\n',
                   lambda _: bloque_grilla(titulo, fotos, planos), nuevo, count=1)
    nuevo = re.sub(r'(<meta property="og:image" content=")[^"]+',
                   r'\g<1>%s%s' % (SITIO, portada['src']), nuevo, count=1)
    if nuevo != html:
        io.open(ruta, 'w', encoding='utf-8', newline='\n').write(nuevo)
        return True
    return False


def actualizar_listado(portadas):
    html = io.open(LISTADO, encoding='utf-8').read()
    for slug, foto in portadas.items():
        patron = (r'(<a href="/proyectos/%s/" class="project-(card|list-row)".*?'
                  r'<img )[^>]+(>)' % re.escape(slug))
        def reemplazar(m):
            alt = '' if m.group(2) == 'list-row' else e(foto.get('titulo') or slug)
            attrs = 'src="%s" width="%s" height="%s" alt="%s" loading="lazy"' % (
                foto['src'], foto['w'], foto['h'], alt)
            return m.group(1) + attrs + m.group(3)
        html = re.sub(patron, reemplazar, html, flags=re.S)
    io.open(LISTADO, 'w', encoding='utf-8', newline='\n').write(html)


def actualizar_buscador(portadas):
    crudo = io.open(BUSCADOR, encoding='utf-8').read()
    inicio, fin = crudo.index('['), crudo.rindex(']') + 1
    indice = json.loads(crudo[inicio:fin])
    for entrada in indice:
        m = re.match(r'/proyectos/([^/]+)/', entrada.get('url', ''))
        if m and m.group(1) in portadas:
            entrada['img'] = portadas[m.group(1)]['src']
    io.open(BUSCADOR, 'w', encoding='utf-8', newline='\n').write(
        crudo[:inicio] + json.dumps(indice, ensure_ascii=False, indent=1) + ';\n')


def main():
    url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY', '')
    if not url or not clave:
        raise SystemExit('Faltan SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno.')
    catalogo = json.load(io.open(DATOS, encoding='utf-8'))
    obras = pedir(url, clave, '/rest/v1/obras?select=id,slug,titulo&publicada=is.true')
    por_slug = {o['slug']: o for o in obras}
    fotos = pedir(url, clave, '/rest/v1/obra_imagenes?select=*&order=orden.asc')
    sembradas = sembrar(catalogo, por_slug, fotos, url, clave)
    sincronizadas = sincronizar_semillas(catalogo, por_slug, fotos, url, clave)
    if sembradas or sincronizadas:
        fotos = pedir(url, clave, '/rest/v1/obra_imagenes?select=*&order=orden.asc')

    por_obra = {}
    for foto in fotos:
        por_obra.setdefault(foto['obra_id'], []).append(foto)

    portadas, cambiadas = {}, 0
    for obra in obras:
        filas = por_obra.get(obra['id'], [])
        if not filas or all(f['storage_path'].startswith('@seed:') for f in filas):
            continue
        resueltas = [resolver_foto(obra['slug'], f, url) for f in filas]
        if actualizar_pagina(obra['slug'], obra['titulo'], resueltas):
            cambiadas += 1
        portadas[obra['slug']] = next((f for f in resueltas if f['portada']), resueltas[0])
        portadas[obra['slug']]['titulo'] = obra['titulo']

    if portadas:
        actualizar_listado(portadas)
        actualizar_buscador(portadas)
    io.open(MAPA_PORTADAS, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(portadas, ensure_ascii=False, indent=2) + '\n')
    print('galerias administradas reescritas: %d' % cambiadas)
    return 0


if __name__ == '__main__':
    sys.exit(main())
