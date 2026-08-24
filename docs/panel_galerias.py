# -*- coding: utf-8 -*-
"""Conecta las galerias historicas y las nuevas con el panel.

Las obras anteriores al panel conservan su galeria publica hasta que el estudio
hace el primer cambio. En la base se carga una seleccion inicial de hasta 30
fotos con el prefijo ``@seed:``. El panel cambia ese prefijo a ``@site:`` al
reordenar, borrar, subir o elegir portada; desde entonces este generador toma la
base como fuente y reescribe la galeria.

Los planos entran igual, como filas de obra_imagenes con tipo='plano': la
seleccion inicial sale de docs/planos.json (lo que arma drive_sync.py a mano
desde el Drive) en vez de panel_datos.json, y llevan su propio cupo de 40,
separado del de las fotos. Antes vivian aparte del todo -planos_fichas.py los
escribia directo en el HTML, sin pasar por el panel- y por eso el formulario
de edicion de una obra no los mostraba nunca.
"""
import glob
import io
import hashlib
import json
import os
import re
import shutil
import struct
import sys
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, 'docs', 'panel_datos.json')
DATOS_PLANOS = os.path.join(RAIZ, 'docs', 'planos.json')
LISTADO = os.path.join(RAIZ, 'proyectos', 'index.html')
BUSCADOR = os.path.join(RAIZ, 'scripts', 'search-index.js')
MAPA_PORTADAS = os.path.join(RAIZ, 'docs', 'panel_portadas.json')
SITIO = 'https://estudiohma.com'
VISIBLES = 6
TOPE = 30
# Las fichas heredadas conservan tres fotos principales. Cuando el estudio
# carga fotos de cuerpo desde el panel, esas filas pasan a ser la seleccion
# explicita y no llevan limite.
PRINCIPALES = 3
# Los planos llevan su propio tope, mas alto: no se cotizan ni se suben a
# mano, salen del Drive y son los que son. Tostado tiene 35. Tiene que
# coincidir con el de la migracion 0012.
TOPE_PLANOS = 40


def migracion_editorial_disponible(url, clave):
    """La 0014 se aplica a mano; el deploy anterior tiene que seguir andando.

    Sin esta comprobacion, subir TOPE de 15 a 30 hace que la primera
    sincronizacion borre una seleccion heredada y que el trigger viejo rechace
    la reposicion. La columna premios pertenece a la misma migracion y sirve
    como marca inequivoca, sin depender de contar filas ni de sus contenidos.
    """
    pedido = urllib.request.Request(
        url + '/rest/v1/obras?select=premios&limit=1',
        headers={'apikey': clave, 'Authorization': 'Bearer ' + clave})
    try:
        with urllib.request.urlopen(pedido, timeout=120):
            return True
    except urllib.error.HTTPError as error:
        if error.code in (400, 404):
            return False
        raise


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


PAGINA = 1000


def pedir(url, clave, ruta, metodo='GET', cuerpo=None):
    """Una consulta a la base, trayendo todas las filas.

    PostgREST devuelve como mucho mil por pedido y no avisa: sin paginar, la
    consulta de obra_imagenes se cortaba en silencio. Al sumarse los planos las
    filas pasaron de 741 a 1231 y la Bienal de Venecia se publico con diez de
    sus veintiun planos, porque el orden global dejaba los suyos del once en
    adelante fuera del corte.

    Solo se pagina en las lecturas: un PATCH o un POST no devuelven lista.
    """
    datos = None if cuerpo is None else json.dumps(cuerpo).encode('utf-8')

    def una(desde):
        cabeceras = {'apikey': clave, 'Authorization': 'Bearer ' + clave,
                     'Content-Type': 'application/json', 'Prefer': 'return=minimal'}
        if metodo == 'GET':
            cabeceras['Range-Unit'] = 'items'
            cabeceras['Range'] = '%d-%d' % (desde, desde + PAGINA - 1)
        pedido = urllib.request.Request(url + ruta, data=datos, method=metodo,
                                        headers=cabeceras)
        with urllib.request.urlopen(pedido, timeout=120) as respuesta:
            crudo = respuesta.read()
            return json.loads(crudo.decode('utf-8')) if crudo else None

    if metodo != 'GET':
        return una(0)

    fuera, desde = [], 0
    while True:
        tanda = una(desde)
        if not tanda:
            break
        fuera.extend(tanda)
        if len(tanda) < PAGINA:
            break
        desde += PAGINA
    return fuera


def ruta_local(publica):
    return os.path.join(RAIZ, publica.lstrip('/').replace('/', os.sep))


REPETIDAS = os.path.join(RAIZ, 'docs', 'galeria_repetidas.json')
EXCLUIDAS = os.path.join(RAIZ, 'docs', 'galeria_excluidas.json')


def fotos_fuera():
    """{slug: {archivos que no van en la galeria}}.

    Junta dos listas con motivos distintos: galeria_repetidas.json, que lo
    calcula docs/galeria_repetidas.py comparando las imagenes, y
    galeria_excluidas.json, que se escribe a mano para las fotos que no son
    de la obra -placas de presentacion, moodboards- y que por eso no deberian
    aparecer aunque no esten repetidas.

    El deduplicador de mas abajo compara por SHA1 y no alcanza para el primer
    caso: la portada y su copia dentro de la galeria son la misma foto
    guardada dos veces, con distinto peso, asi que los bytes no coinciden.
    Era el caso de once de las doce obras que el cliente marco como "foto
    repetida" el 19/08/2026.
    """
    fuera = {}
    if os.path.isfile(REPETIDAS):
        with io.open(REPETIDAS, encoding='utf-8') as archivo:
            for slug, nombres in json.load(archivo).items():
                fuera.setdefault(slug, set()).update(nombres)
    if os.path.isfile(EXCLUIDAS):
        with io.open(EXCLUIDAS, encoding='utf-8') as archivo:
            for slug, entradas in json.load(archivo).items():
                if slug.startswith('_'):
                    continue
                fuera.setdefault(slug, set()).update(
                    e['archivo'] for e in entradas if e.get('archivo'))
    return fuera


def seleccion_inicial(obra):
    candidatas = []
    portada = obra.get('portada')
    if portada:
        candidatas.append(portada)
    candidatas.extend('/assets/gallery/%s/%s' % (obra['slug'], nombre)
                      for nombre in obra.get('galeria') or [])

    sobran = fotos_fuera().get(obra['slug'], set())

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
            'tipo': 'foto',
        })
    if filas and not any(f['es_portada'] for f in filas):
        filas[0]['es_portada'] = True
    return filas


def cargar_planos():
    if not os.path.isfile(DATOS_PLANOS):
        return {}
    with io.open(DATOS_PLANOS, encoding='utf-8') as archivo:
        return json.load(archivo)


def planos_iniciales(obra, catalogo_planos):
    """Misma idea que seleccion_inicial pero para los planos de drive_sync.py.

    No hay deduplicado ni portada aca: drive_sync.py ya descarta las laminas
    repetidas (el mismo plano en castellano e ingles) antes de escribir
    planos.json, y un plano nunca es portada de la obra.
    """
    filas = []
    for plano in (catalogo_planos.get(obra['slug']) or [])[:TOPE_PLANOS]:
        filas.append({
            'storage_path': '@seed:/assets/planos/%s/%d.webp' % (obra['slug'], plano['n']),
            'alt': '%s — plano %d' % (obra['titulo'], plano['n']),
            'orden': len(filas),
            'es_portada': False,
            'ancho': plano.get('w'),
            'alto': plano.get('h'),
            'tipo': 'plano',
        })
    return filas


TIPOS = (('foto', lambda obra, catalogo_planos: seleccion_inicial(obra)),
         ('plano', lambda obra, catalogo_planos: planos_iniciales(obra, catalogo_planos)))


def sembrar(obras, por_slug, existentes, url, clave, catalogo_planos):
    nuevas = []
    tipos_con_filas = {}
    for f in existentes:
        tipos_con_filas.setdefault(f['obra_id'], set()).add(f['tipo'])

    for obra in obras:
        fila = por_slug.get(obra['slug'])
        if not fila:
            continue
        ya = tipos_con_filas.get(fila['id'], set())
        for tipo, generar in TIPOS:
            if tipo in ya:
                continue
            for imagen in generar(obra, catalogo_planos):
                imagen['obra_id'] = fila['id']
                nuevas.append(imagen)
    if nuevas:
        pedir(url, clave, '/rest/v1/obra_imagenes', 'POST', nuevas)
        print('galerias historicas conectadas al panel: %d imagenes' % len(nuevas))
    else:
        print('galerias historicas ya conectadas')
    return bool(nuevas)


def sincronizar_semillas(obras, por_slug, existentes, url, clave, catalogo_planos):
    """Actualiza sólo selecciones heredadas que el estudio todavía no editó.

    Si cambian las fotos o los planos locales de una obra, el panel no puede
    seguir mostrando rutas @seed que ya no existen. Las galerías administradas
    (@site o Storage) quedan fuera de esta sincronización para no pisar
    decisiones del estudio. Fotos y planos se sincronizan por separado: que el
    estudio haya tocado las fotos no debe congelar los planos heredados, ni al
    revés.
    """
    por_obra_tipo = {}
    for foto in existentes:
        por_obra_tipo.setdefault((foto['obra_id'], foto['tipo']), []).append(foto)

    actualizadas = 0
    for obra in obras:
        fila = por_slug.get(obra['slug'])
        if not fila:
            continue
        for tipo, generar in TIPOS:
            actuales = sorted(por_obra_tipo.get((fila['id'], tipo), []), key=lambda f: f['orden'])
            if not actuales or not all(f['storage_path'].startswith('@seed:') for f in actuales):
                continue
            deseadas = generar(obra, catalogo_planos)
            firma_actual = [(f['storage_path'], f['orden'], bool(f['es_portada']),
                             f.get('ancho'), f.get('alto')) for f in actuales]
            firma_deseada = [(f['storage_path'], f['orden'], bool(f['es_portada']),
                              f.get('ancho'), f.get('alto')) for f in deseadas]
            if firma_actual == firma_deseada:
                continue
            pedir(url, clave, '/rest/v1/obra_imagenes?obra_id=eq.%s&tipo=eq.%s'
                  % (fila['id'], tipo), 'DELETE')
            for imagen in deseadas:
                imagen['obra_id'] = fila['id']
            if deseadas:
                pedir(url, clave, '/rest/v1/obra_imagenes', 'POST', deseadas)
            actualizadas += 1
    if actualizadas:
        print('selecciones historicas actualizadas: %d galerias' % actualizadas)
    return bool(actualizadas)


def resolver_imagen(slug, foto, url):
    ruta = foto['storage_path']
    if ruta.startswith('@seed:') or ruta.startswith('@site:'):
        publica = ruta.split(':', 1)[1]
        # La ruta guardada pertenece a la imagen, no al nombre actual de la
        # obra. Al cambiar cerveceria-austral por estancia-austral, la base
        # siguio apuntando correctamente al archivo anterior; panel_sitio lo
        # quitaba por ser un slug viejo y la ficha nueva quedaba rota. Se copia
        # al slug vigente durante el build y desde ese momento toda pagina
        # publicada usa la ruta nueva. Esto cubre portada, galeria y planos sin
        # pedirle al estudio que vuelva a subir nada.
        origen = ruta_local(publica)
        partes = publica.strip('/').split('/')
        if os.path.isfile(origen) and len(partes) >= 3 and partes[0] == 'assets':
            carpeta = partes[1]
            slug_guardado = partes[2] if carpeta in ('gallery', 'planos') else ''
            if carpeta == 'covers':
                slug_guardado = os.path.splitext(partes[2])[0]
                destino_publico = '/assets/covers/%s.webp' % slug
            elif carpeta in ('gallery', 'planos') and slug_guardado != slug:
                destino_publico = '/assets/%s/%s/%s' % (
                    carpeta, slug, os.path.basename(publica))
            else:
                destino_publico = publica
            if slug_guardado and slug_guardado != slug:
                destino = ruta_local(destino_publico)
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                shutil.copy2(origen, destino)
                publica = destino_publico
    else:
        carpeta_nombre = 'planos' if foto.get('tipo') == 'plano' else 'gallery'
        carpeta = os.path.join(RAIZ, 'assets', carpeta_nombre, slug)
        os.makedirs(carpeta, exist_ok=True)
        publica = '/assets/%s/%s/panel-%s.webp' % (carpeta_nombre, slug, foto['id'])
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


def bloque_filas(actual, titulo, fotos, cuerpo):
    """Portada mas cuerpo administrado; sin cuerpo, conserva el legado."""
    portada = next((foto for foto in fotos if foto['portada']), fotos[0])
    fotos = [portada] + [foto for foto in fotos if foto is not portada]
    seleccion = [portada] + cuerpo if cuerpo else fotos[:PRINCIPALES]
    filas = ['      <div class="project-row project-row--sola reveal">\n'
             '        <div class="project-row__photo"><img></div>\n      </div>'] * len(seleccion)
    nuevas = []
    for i, (fila, foto) in enumerate(zip(filas, seleccion), 1):
        carga = ('loading="eager" decoding="async" fetchpriority="high"'
                 if i == 1 else 'loading="lazy" decoding="async"')
        img = '<img src="%s" width="%s" height="%s" alt="%s" %s>' % (
            foto['src'], foto['w'], foto['h'], e(foto['alt'] or
            '%s — foto %d' % (titulo, i)), carga)
        nuevas.append(re.sub(r'<img\b[^>]*>', img, fila, count=1))
    return '\n    <section class="project-gallery">\n%s\n    </section>\n' % '\n\n'.join(nuevas)


def bloque_grilla(titulo, fotos, planos):
    """Primero todas las fotos, y los planos al final.

    Antes los planos se metian despues de la foto numero VISIBLES, que es
    donde corta el boton de "ver mas". En una obra con muchos planos eso
    partia la galeria al medio: Hyatt Ziva mostraba seis renders, despues
    veintiun planos y despues el resto de los renders. El estudio lo marco el
    24/08/2026 -"en varios trabajos aun aparecen los planos entre los renders,
    cuando deberian aparecer al final de todo"-.
    """
    items = []
    for i, foto in enumerate(fotos, 1):
        extra = '' if i <= VISIBLES else ' is-extra'
        items.append(
            '          <figure class="gallery-grid__item%s"><img src="%s" width="%s" '
            'height="%s" alt="%s" loading="lazy" decoding="async"></figure>'
            % (extra, foto['src'], foto['w'], foto['h'],
               e(foto['alt'] or '%s — foto %d' % (titulo, i))))
    # Si hay boton de "ver mas", los planos se esconden con el mismo is-extra
    # que las fotos que quedan abajo del corte. Sin eso quedaria la galeria al
    # reves de lo pedido: los planos a la vista y las fotos escondidas.
    if len(fotos) > VISIBLES:
        planos = [p.replace('gallery-grid__item gallery-grid__item--plano',
                            'gallery-grid__item is-extra gallery-grid__item--plano')
                  for p in planos]
    items.extend(planos)
    boton = ''
    if len(fotos) > VISIBLES:
        boton = ('\n        <button type="button" class="btn gallery-more" data-total="%d" '
                 'data-mas="Ver las %d fotos" data-menos="Ver menos fotos" '
                 'aria-expanded="false">Ver las %d fotos</button>'
                 % (len(fotos), len(fotos), len(fotos)))
    return ('\n    <section class="section no-border" id="galeria">\n'
            '      <div class="container">\n'
            '        <div class="section-head"><h2 class="display-3">Galería</h2></div>\n'
            '        <div class="gallery-grid reveal">\n%s\n        </div>%s\n'
            '      </div>\n    </section>\n' % ('\n'.join(items), boton))


def figuras_planos(titulo, planos):
    """El HTML de la fila de planos, resuelta desde la base y no desde el
    archivo: antes esta fila la escribia planos_fichas.py como paso aparte del
    build y este generador la conservaba re-leyendola del HTML ya escrito."""
    return [
        '          <figure class="gallery-grid__item gallery-grid__item--plano">'
        '<img src="%s" width="%s" height="%s" alt="%s" loading="lazy" decoding="async"></figure>'
        % (plano['src'], plano['w'], plano['h'],
           e(plano['alt'] or '%s — plano %d' % (titulo, i)))
        for i, plano in enumerate(planos, 1)
    ]


def actualizar_pagina(slug, titulo, fotos, cuerpo, planos):
    ruta = os.path.join(RAIZ, 'proyectos', slug, 'index.html')
    if not os.path.isfile(ruta):
        return False
    html = io.open(ruta, encoding='utf-8').read()
    portada = next((f for f in fotos if f['portada']), fotos[0])
    nuevo = re.sub(r'(?s)\n    <section class="project-gallery">.*?\n    </section>\n',
                   lambda m: bloque_filas(m.group(0), titulo, fotos, cuerpo), html, count=1)
    nuevo = re.sub(r'(?s)\n    <section class="section no-border" id="galeria">.*?\n    </section>\n',
                   lambda _: bloque_grilla(titulo, fotos, figuras_planos(titulo, planos)),
                   nuevo, count=1)
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


def sacar_excluidas_de_las_fichas():
    """Borra de cada ficha las fotos que fotos_fuera() manda sacar.

    Hace falta porque la galeria de una obra que nunca paso por el panel vive
    en el HTML del repositorio y el paso de arriba no la reescribe: sus filas
    en la base son @seed y ahi se hace continue, para no pisar lo que el
    estudio haya elegido. Una exclusion nueva quedaba anotada en el JSON y no
    se veia en el sitio.

    Dos reglas que valen la pena entender:

    La foto de apertura no se toca nunca. Es la primera project-row__photo de
    la ficha y en varias obras es justamente la copia de la caratula que la
    lista manda excluir; la exclusion apunta a la repeticion de mas abajo, no
    a la apertura. seleccion_inicial hace la misma salvedad.

    En las demas filas editoriales la foto no se borra, se cambia. Cada fila
    es un texto con su imagen al lado, y borrarla dejaria el texto solo. Entra
    la primera foto de la galeria que no este excluida ni usada en otra fila,
    con sus medidas reales, porque el ancho y el alto del HTML reservan el
    lugar antes de que la imagen cargue.
    """
    figura = re.compile(r'\n?\s*<figure class="gallery-grid__item[^>]*>'
                        r'<img src="([^"]+)"[^>]*>\s*</figure>')
    editorial = re.compile(r'<div class="project-row__photo"><img src="([^"]+)"[^>]*>')
    fuera = fotos_fuera()
    tocadas = sacadas = 0
    for slug, sobran in sorted(fuera.items()):
        ruta = os.path.join(RAIZ, 'proyectos', slug, 'index.html')
        if not sobran or not os.path.isfile(ruta):
            continue
        html = io.open(ruta, encoding='utf-8').read()
        mia = '/assets/gallery/%s/' % slug
        cambios = []

        usadas = set(editorial.findall(html))
        libres = [m.group(1) for m in figura.finditer(html)
                  if mia in m.group(1)
                  and os.path.basename(m.group(1)) not in sobran
                  and m.group(1) not in usadas]

        vistas = [0]

        def cambiar(m):
            vistas[0] += 1
            url = m.group(1)
            # La primera es la apertura de la ficha.
            if vistas[0] == 1 or mia not in url:
                return m.group(0)
            if os.path.basename(url) not in sobran or not libres:
                return m.group(0)
            nuevo_url = libres.pop(0)
            medidas = medidas_webp(ruta_local(nuevo_url))
            trozo = m.group(0).replace(url, nuevo_url)
            if medidas:
                trozo = re.sub(r'width="\d+" height="\d+"',
                               'width="%d" height="%d"' % medidas, trozo, count=1)
            cambios.append('%s por %s' % (os.path.basename(url),
                                          os.path.basename(nuevo_url)))
            return trozo

        nuevo = editorial.sub(cambiar, html)

        def borrar(m):
            url = m.group(1)
            if mia in url and os.path.basename(url) in sobran:
                cambios.append('%s fuera de la grilla' % os.path.basename(url))
                return ''
            return m.group(0)

        nuevo = figura.sub(borrar, nuevo)
        if cambios:
            io.open(ruta, 'w', encoding='utf-8', newline='\n').write(nuevo)
            tocadas += 1
            sacadas += len(cambios)
            print('  %-24s %s' % (slug, '; '.join(cambios)))
    if sacadas:
        print('fichas con fotos excluidas: %d obras, %d cambios' % (tocadas, sacadas))


def recortar_principales():
    """Deja tres fotos grandes en el cuerpo de cada ficha.

    "En todos los casos. Solo tres imagenes principales (una de ellas, la
    primera es la tapa)", del tercer Word del 20/08/2026. La mayoria de las
    fichas traia seis, que estiraban la pagina a lo largo.

    Se recorta aca y no solo en bloque_filas porque esa funcion corre unicamente
    sobre las fichas que el build reescribe, y son las menos: las galerias
    heredadas viven en el HTML del repositorio.

    Lo que se saca son filas de foto con su frase al lado -la bajada de la obra
    y las lineas del estudio, "mas de doscientos proyectos construidos"-. La
    memoria descriptiva no esta ahi: va en su propia seccion, mas abajo, y no
    se toca. La galeria completa tampoco: sigue mostrando todas las fotos.
    """
    fila = re.compile(r'(?s)\n      <div class="project-row.*?\n      </div>')
    tocadas = sacadas = 0
    for ruta in sorted(glob.glob(os.path.join(RAIZ, 'proyectos', '*', 'index.html'))):
        html = io.open(ruta, encoding='utf-8').read()
        m = re.search(r'(?s)\n    <section class="project-gallery">.*?\n    </section>\n', html)
        if not m:
            continue
        filas = fila.findall(m.group(0))
        if len(filas) <= PRINCIPALES:
            continue
        cuerpo = m.group(0)
        for sobra in filas[PRINCIPALES:]:
            cuerpo = cuerpo.replace(sobra, '', 1)
        io.open(ruta, 'w', encoding='utf-8', newline='\n').write(
            html[:m.start()] + cuerpo + html[m.end():])
        tocadas += 1
        sacadas += len(filas) - PRINCIPALES
        print('  %-24s %d -> %d' % (os.path.basename(os.path.dirname(ruta)),
                                    len(filas), PRINCIPALES))
    if tocadas:
        print('fichas recortadas a %d fotos principales: %d (%d filas menos)'
              % (PRINCIPALES, tocadas, sacadas))


def main():
    global TOPE
    url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY', '')
    if not url or not clave:
        raise SystemExit('Faltan SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno.')
    if not migracion_editorial_disponible(url, clave):
        TOPE = 15
        print('migracion 0014 pendiente: galerias en modo compatible de 15 fotos')
    catalogo = json.load(io.open(DATOS, encoding='utf-8'))
    catalogo_planos = cargar_planos()
    # Tambien las que estan en borrador. Antes se pedian solo las publicadas y
    # eso dejaba a una obra nueva sin salida: el panel exige al menos una foto
    # para publicar, y las fotos se las carga este paso, que no la miraba por
    # no estar publicada. Una obra que entra por el Drive -sus fotos estan en el
    # repositorio y Storage no sabe nada de ellas- no tenia forma de publicarse
    # desde el panel, habia que tocar la base a mano. Le paso a Banco
    # Supervielle el 21/08/2026.
    #
    # Sembrar un borrador no lo muestra en ningun lado: la pagina y la tarjeta
    # las escribe el bucle de mas abajo, que sigue mirando solo las publicadas.
    obras = pedir(url, clave, '/rest/v1/obras?select=id,slug,titulo,publicada')
    por_slug = {o['slug']: o for o in obras}
    imagenes = pedir(url, clave, '/rest/v1/obra_imagenes?select=*&order=orden.asc')
    sembradas = sembrar(catalogo, por_slug, imagenes, url, clave, catalogo_planos)
    sincronizadas = sincronizar_semillas(catalogo, por_slug, imagenes, url, clave, catalogo_planos)
    if sembradas or sincronizadas:
        imagenes = pedir(url, clave, '/rest/v1/obra_imagenes?select=*&order=orden.asc')

    por_obra_tipo = {}
    for imagen in imagenes:
        por_obra_tipo.setdefault((imagen['obra_id'], imagen['tipo']), []).append(imagen)

    def gestionada(filas):
        return bool(filas) and not all(f['storage_path'].startswith('@seed:') for f in filas)

    def sin_planos_todavia(slug):
        """Si la ficha no tiene ningun plano dibujado, hay que escribirla.

        Una obra recien dada de alta llega aca con su pagina creada por
        panel_alta.py, que solo pone fotos, y con sus planos ya sembrados como
        @seed. Sin esta salvedad la condicion de arriba la saltea por seed y la
        obra se publica sin planos: le paso a Comedor Diario, que tenia dos.

        A las demas no las toca. Sus fichas ya traen los planos escritos en el
        HTML del repositorio y ahi la condicion de @seed sigue mandando.
        """
        ruta = os.path.join(RAIZ, 'proyectos', slug, 'index.html')
        if not os.path.isfile(ruta):
            return False
        return 'gallery-grid__item--plano' not in io.open(ruta, encoding='utf-8').read()

    def le_faltan_fotos(slug, filas, sobran):
        """La ficha muestra menos fotos de las que la obra tiene sembradas.

        La condicion de @seed existe para no pisar lo que el estudio eligio,
        pero @seed no es una eleccion del estudio: es la seleccion heredada del
        sitio viejo, y lo que el estudio elige entra por Storage. Mientras
        tanto, las fichas del repositorio venian de una importacion recortada a
        catorce fotos, asi que una obra con treinta sembradas publicaba
        catorce y las otras dieciseis no las veia nadie.

        Medido el 24/08/2026: 43 obras en ese estado y 85 fotos sin salir.
        Tostado era el caso mas grande, 14 de 30. El estudio lo marco con
        "en la pg de edicion hay 20 fotos, pero en la pg principal solo se ven
        15".

        Solo mira las que estan enteras en @seed y solo devuelve True si a la
        ficha le faltan: nunca saca ninguna.
        """
        ruta = os.path.join(RAIZ, 'proyectos', slug, 'index.html')
        if not os.path.isfile(ruta):
            return False
        esperadas = sum(1 for f in filas
                        if f['es_portada']
                        or os.path.basename(f['storage_path']) not in sobran)
        html = io.open(ruta, encoding='utf-8').read()
        tiene = len(set(re.findall(
            r'assets/gallery/%s/([0-9]+\.webp)' % re.escape(slug), html)))
        return tiene < esperadas

    def planos_en_el_medio(slug):
        """La ficha tiene una foto despues de un plano.

        Es el orden viejo, de cuando bloque_grilla metia los planos justo
        despues de la foto numero VISIBLES. Las fichas que ya tenian todas sus
        fotos no entran por le_faltan_fotos y, al estar en @seed, tampoco se
        reescriben: se quedaban con la galeria partida al medio. Quedaban tres
        -galeria-objeto-a, oficina-casa-luna y ph-loft-arias-, todas con el
        mismo dibujo de seis fotos, los planos y el resto de las fotos.
        """
        ruta = os.path.join(RAIZ, 'proyectos', slug, 'index.html')
        if not os.path.isfile(ruta):
            return False
        html = io.open(ruta, encoding='utf-8').read()
        orden = ''.join(
            'P' if 'plano' in m.group(1) else 'F'
            for m in re.finditer(r'<figure class="(gallery-grid__item[^"]*)"', html))
        return 'P' in orden and 'F' in orden.split('P')[-1]

    portadas, cambiadas = {}, 0
    sobran_por_obra = fotos_fuera()
    # Las paginas y las tarjetas, solo de las publicadas: un borrador no tiene
    # pagina que actualizar ni tarjeta en el listado.
    for obra in [o for o in obras if o['publicada']]:
        filas_fotos = por_obra_tipo.get((obra['id'], 'foto'), [])
        filas_cuerpo = por_obra_tipo.get((obra['id'], 'cuerpo'), [])
        filas_planos = por_obra_tipo.get((obra['id'], 'plano'), [])
        # Se reescribe la ficha si el estudio toco las fotos o los planos: antes
        # alcanzaba con mirar las fotos porque era lo unico administrable.
        if not (gestionada(filas_fotos) or filas_cuerpo or gestionada(filas_planos)
                or (filas_planos and sin_planos_todavia(obra['slug']))
                or le_faltan_fotos(obra['slug'], filas_fotos,
                                   sobran_por_obra.get(obra['slug'], set()))
                or planos_en_el_medio(obra['slug'])):
            continue
        if not filas_fotos:
            continue  # sin fotos no hay portada que mostrar

        # Las repetidas tambien se sacan de una galeria heredada del sitio
        # viejo. Esas filas llegan como @site: y sincronizar_semillas no las
        # toca, para no pisar lo que el estudio haya elegido; pero @site: no es
        # una eleccion del estudio -lo que el estudio elige entra por Storage-,
        # es lo que habia antes. La Bienal de Venecia quedaba mostrando su
        # caratula dos veces por esto, y es una de las obras que el cliente
        # marco con "foto repetida" el 19/08/2026.
        sobran = sobran_por_obra.get(obra['slug'], set())
        if sobran:
            filas_fotos = [f for f in filas_fotos
                     if f['es_portada']
                     or os.path.basename(f['storage_path']) not in sobran]

        fotos_resueltas = [resolver_imagen(obra['slug'], f, url) for f in filas_fotos]
        cuerpo_resuelto = [resolver_imagen(obra['slug'], f, url) for f in filas_cuerpo]
        planos_resueltos = [resolver_imagen(obra['slug'], f, url) for f in filas_planos]
        if actualizar_pagina(obra['slug'], obra['titulo'], fotos_resueltas,
                             cuerpo_resuelto, planos_resueltos):
            cambiadas += 1
        portadas[obra['slug']] = next((f for f in fotos_resueltas if f['portada']), fotos_resueltas[0])
        portadas[obra['slug']]['titulo'] = obra['titulo']

    sacar_excluidas_de_las_fichas()
    # Las fichas heredadas ya quedaron recortadas. No se recorta de nuevo:
    # las filas de tipo cuerpo son una seleccion editorial explicita.

    if portadas:
        actualizar_listado(portadas)
        actualizar_buscador(portadas)
    io.open(MAPA_PORTADAS, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(portadas, ensure_ascii=False, indent=2) + '\n')
    print('galerias administradas reescritas: %d' % cambiadas)
    return 0


if __name__ == '__main__':
    sys.exit(main())
