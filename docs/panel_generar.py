# -*- coding: utf-8 -*-
"""Escribe en las paginas del sitio lo que el estudio edita desde el panel.

No regenera la pagina entera: reemplaza solo las zonas que salen de la base
—titulo, bajada, ficha tecnica y memoria— y deja intacto todo lo demas. Es a
proposito. Una pagina de obra tiene planos, sellos de premio, banners y
correcciones acumuladas que no viven en la base: rehacerla desde una plantilla
las borraria sin que nadie se entere hasta verlo publicado.

Que se toca de cada obra:
  - el <h1> con el titulo
  - el parrafo de bajada y sus copias en SEO y preview social
  - la ficha tecnica (estado, tipo, ubicacion, pais, superficie, año, equipo)
  - el bloque de memoria descriptiva

Como se prueba que es fiel: docs/panel_exportar.py saca los datos de estas
mismas paginas, asi que correr el exportador y despues este generador tiene que
dejar el sitio exactamente igual. Si algun archivo cambia, la plantilla perdio
un dato. Eso es lo que revisa --verificar.

    python docs/panel_generar.py --verificar    # no escribe, solo compara
    python docs/panel_generar.py                # escribe desde el JSON
    python docs/panel_generar.py --supabase     # escribe desde la base

Con --supabase lee de la base en vez del JSON. Necesita SUPABASE_URL y
SUPABASE_SERVICE_KEY en el entorno. Va la clave de servicio y no la anon a
proposito: es la unica que ve los borradores, y este script corre en el
servidor de build, nunca en un navegador.
"""
import io, json, os, re, sys
import urllib.request

# El parrafo de subtitulo que va debajo del titulo en la ficha. Se saca entero,
# con el salto que lo precede, para no dejar una linea vacia.
SUBTITULO = re.compile(r'\n?\s*<p class="lede[^"]*"[^>]*>.*?</p>', re.S)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ESTADOS = {
    'concluida': 'Obra concluida',
    'en_progreso': 'Proyecto en proceso',
    'en_proyecto': 'Proyecto',
}


def escapar(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def escapar_atributo(t):
    return escapar(t).replace('"', '&quot;')


def formato_editorial(t):
    """Escapa todo y admite solamente **negrita** desde el panel."""
    seguro = escapar(t)
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', seguro)


# El orden en que van las filas de la ficha tecnica. Solo se usa para
# ubicar una fila que haya que agregar; las que ya estan no se mueven.
ORDEN_SPECS = ['Intervención', 'Estado', 'Tipología', 'Ubicación', 'País', 'Superficie', 'Año',
               'Comitente', 'Fotógrafo', 'Renderista', 'Equipo']


def rotulo_spec(rotulo):
    """Normaliza el nombre anterior del credito al pedido por el estudio."""
    limpio = re.sub(r'\s+', ' ', rotulo).strip()
    if limpio == 'Fotografía':
        return 'Fotógrafo'
    if limpio == 'Tipo':
        return 'Tipología'
    return limpio


def bloque_ficha(o, html):
    """Arma la ficha respetando el orden de rotulos que ya tiene la pagina.

    El orden no es igual en todas: algunas muestran Comitente y otras no. Se
    lee el orden actual y se completan los valores, en vez de imponer uno.
    Si la base tiene un dato para el que la pagina no tiene fila, la fila se
    agrega en el lugar que le toca; las que ya estaban no se mueven.
    """
    # Se guarda tambien la clase de cada fila: la del equipo lleva una propia
    # (spec-row--team) y reescribirla sin ella le cambia el estilo.
    filas_actuales = re.findall(
        r'<div class="(spec-row[^"]*)"><dt>(.*?)</dt>', html, re.S)
    rotulos = [r for _, r in filas_actuales]
    clases = dict((rotulo_spec(r), c) for c, r in filas_actuales)
    valor = {
        'Intervención': {
            'interiorismo': 'Interiorismo',
            'arquitectura': 'Arquitectura',
            'ambos': 'Arquitectura e interiorismo',
        }.get(o.get('intervencion'), 'A definir'),
        'Estado': ESTADOS.get(o['estado'], ''),
        'Tipología': o.get('tipologia') or '',
        'Ubicación': o.get('ubicacion') or '',
        'País': o.get('pais') or '',
        'Superficie': o.get('superficie') or '',
        'Año': o.get('anio') or '',
        'Comitente': o.get('comitente') or '',
        # El credito solo corresponde a obras terminadas con fotos reales. Un
        # valor viejo no debe hacer aparecer el renglon en un proyecto/render.
        'Fotógrafo': (o.get('fotografia') or '') if o['estado'] == 'concluida' else '',
        # El renderista puede corresponder tanto a un proyecto como a una obra
        # terminada; se publica siempre que el estudio cargue el credito.
        'Renderista': o.get('renderista') or '',
        'Equipo': '<br>'.join(escapar(x) for x in (o.get('equipo') or [])),
    }

    orden = [rotulo_spec(r) for r in rotulos]
    orden = [r for r in orden
             if r not in ('Fotógrafo', 'Renderista') or valor[r]]
    if any(rot not in valor for rot in orden):
        return None          # rotulo que el generador no conoce: no se toca

    # Y se suma la fila que la pagina no tenia pero la base si.
    #
    # Antes esto solo completaba los rotulos ya presentes, con lo cual un dato
    # cargado despues de armada la ficha no llegaba nunca a verse: IguanaFix
    # tenia sus 320 m2 en la base y la ficha no mostraba superficie, que es
    # justo lo que el cliente habia pedido agregar. Lo mismo con los 220 m2 de
    # Lucciano's Caballito, el comitente de Osten FOA y Parfumerie y el
    # fotografo de Comedor Diario.
    #
    # La fila nueva entra en el lugar que le toca segun ORDEN_SPECS, sin mover
    # las que ya estaban: el orden no es igual en todas las fichas y no se
    # impone uno.
    for rot in ORDEN_SPECS:
        if rot in orden or not valor.get(rot):
            continue
        posterior = [i for i, r in enumerate(orden)
                     if ORDEN_SPECS.index(r) > ORDEN_SPECS.index(rot)]
        orden.insert(posterior[0] if posterior else len(orden), rot)

    filas = []
    for rot in orden:
        v = valor[rot]
        if rot != 'Equipo':
            v = escapar(v)
        filas.append('          <div class="%s"><dt>%s</dt><dd>%s</dd></div>'
                     % (clases.get(rot, 'spec-row'), rot, v))
    return '\n'.join(filas)


def bloque_memoria(o):
    """El mismo molde que usan hoy las paginas, con boton si hay mas de dos."""
    texto = o.get('memoria')
    if not texto:
        return ''
    parrafos = [p.strip() for p in re.split(r'\n\s*\n', texto) if p.strip()]
    if not parrafos:
        return ''
    plegable = len(parrafos) > 2
    cuerpo = '\n'.join('          <p>%s</p>' % formato_editorial(p) for p in parrafos)
    boton = ''
    if plegable:
        boton = ('\n        <button class="memoria-more gallery-more" type="button"\n'
                 '          data-mas="Seguir leyendo" data-menos="Leer menos"\n'
                 '          aria-expanded="false">Seguir leyendo</button>')
    return ('    <section class="project-memoria">\n'
            '      <div class="container">\n'
            '        <div class="memoria-cuerpo%s reveal">\n%s\n        </div>%s\n'
            '      </div>\n'
            '    </section>\n' % ('' if plegable else ' is-open', cuerpo, boton))


def ciudad(direccion):
    p = [x.strip() for x in (direccion or '').replace('.', '').split(',') if x.strip()]
    return p[-1] if p else ''


def bloque_meta(o):
    """La linea de datos que va debajo del titulo: tipo, ciudad, superficie y ano.

    Se rehace entera desde la base. Antes no la escribia nadie -quedo como la
    dejaron los guiones que armaron el sitio- y en treinta y seis fichas venia
    incompleta: casi todas sin el ano, y IguanaFix, Lucciano's Caballito, Uala
    Nicaragua I y II, Aire Libre y Juan Valdez tampoco mostraban los metros
    cuadrados. Justamente los metros son lo que el cliente pidio agregar el
    19/08/2026.

    Un campo vacio no deja un hueco: simplemente no va.
    """
    partes = [o.get('tipologia') or '',
              ciudad(o.get('ubicacion')),
              (o.get('superficie') or '').split(' \u00b7 ')[0],
              o.get('anio') or '']
    return ''.join('<span>%s</span>' % escapar(p) for p in partes if p.strip())


def bloque_premios(o):
    texto = (o.get('premios') or '').strip()
    if not texto:
        return ''
    return ('    <section class="project-awards-panel">\n'
            '      <div class="container">\n'
            '        <span class="eyebrow">Reconocimientos</span>\n'
            '        <h2 class="display-3 mt-10">Premios y distinciones</h2>\n'
            '        <p class="project-awards-panel__text mt-16">%s</p>\n'
            '        <a class="btn link-arrow mt-16" href="/premios/">Ver premios</a>\n'
            '      </div>\n'
            '    </section>\n' % formato_editorial(texto))


# El texto de premios es lo que edita el estudio desde el panel. La barra de
# logos antes quedaba suelta en el HTML y una edicion o un alta nueva no la
# actualizaba. Estas equivalencias hacen que el mismo dato gobierne ambas
# presentaciones; un premio desconocido conserva su nombre aunque no tenga
# todavía un archivo de logo.
LOGOS_PREMIOS = (
    ('restaurant & bar design', 'rbda-2023.png', 'Restaurant & Bar Design Awards'),
    ('surface design', 'surface-design.png', 'Surface Design Awards'),
    ('next landmark', 'next-landmark.png', 'Next Landmark Awards'),
    ('bienal sca', 'bienal-sca.png', 'Bienal SCA-CPAU'),
    ('bienal internacional', 'biar.png', 'Bienal Internacional de Arquitectura'),
    ('liv hospitality', 'liv-2025.png', 'LIV Hospitality Design Awards'),
    ('hospitality design', 'hospitality-design.png', 'Hospitality Design Awards'),
    ('architizer', 'architizer.png', 'Architizer A+'),
    ('arq-fadea', 'fadea.png', 'ARQ-FADEA'),
    ('casa foa', 'casa-foa.png', 'Casa FOA'),
    ('german design', 'german-design-awards.png', 'German Design Awards'),
    ('prix versailles', 'prix-versailles.png', 'Prix Versailles'),
    ('sbid', 'sbid.png', 'SBID'),
    ('iida', 'iida.png', 'IIDA'),
    ('accor', 'accor.png', 'Accor Hotels Design & Technical Summit'),
    ('biar', 'biar.png', 'BIAR'),
)


def premios_individuales(texto):
    return [p.strip() for p in re.split(r'\s*(?:\n|\u00b7|\ufffd)\s*', texto) if p.strip()]


def bloque_barra_premios(o):
    texto = (o.get('premios') or '').strip()
    if not texto:
        return ''
    items = []
    for premio in premios_individuales(texto):
        encontrado = next((x for x in LOGOS_PREMIOS if x[0] in premio.lower()), None)
        if encontrado:
            _, archivo, nombre = encontrado
            items.append(
                '          <a class="award-bar__item" href="/premios/" aria-label="Ver %s">'
                '<img src="/assets/awards/%s" alt="%s" loading="lazy" decoding="async">'
                '<span>%s</span></a>' % tuple(escapar_atributo(x) for x in
                                             (nombre, archivo, nombre, nombre))
            )
        else:
            nombre = escapar(premio)
            items.append(
                '          <a class="award-bar__item award-bar__item--texto" '
                'href="/premios/" aria-label="Ver premios"><span>%s</span></a>' % nombre)
    return ('    <section class="award-bar">\n'
            '      <div class="container award-bar__inner">\n'
            '        <h2 class="award-bar__title">Premios y distinciones</h2>\n'
            '        <div class="award-bar__logos">\n%s\n'
            '        </div>\n'
            '      </div>\n'
            '    </section>\n' % '\n'.join(items))


def aplicar(o, html):
    """Devuelve el HTML con las zonas de la base reemplazadas."""
    problemas = []

    # --- titulo ---
    nuevo, n = re.subn(r'(<h1[^>]*>)(.*?)(</h1>)',
                       lambda m: m.group(1) + escapar(o['titulo']) + m.group(3),
                       html, count=1, flags=re.S)
    if not n:
        problemas.append('sin <h1>')
    html = nuevo

    # El titulo del navegador y el preview social deben seguir al <h1>. Si no,
    # editar el titulo desde el panel deja dos nombres distintos para la obra.
    titulo_pagina = escapar(o['titulo'] + ' | Hitzig Militello Arquitectos')
    html = re.sub(r'(<title>).*?(</title>)',
                  lambda m: m.group(1) + titulo_pagina + m.group(2),
                  html, count=1, flags=re.S)
    html = re.sub(r'(<meta property="og:title" content=")[^"]*(">)',
                  lambda m: m.group(1) + escapar_atributo(
                      o['titulo'] + ' | Hitzig Militello Arquitectos') + m.group(2),
                  html, count=1)

    # --- bajada ---
    # El 19/08/2026 el cliente pidio sacar el subtitulo de todas las fichas
    # ("EN TODOS los trabajos: Quita los subtitulos"), tachado en rojo sobre la
    # captura. La bajada se sigue usando: es el texto de la tarjeta del
    # listado, del buscador y del banner del home, y la descripcion que leen
    # Google y WhatsApp. Lo unico que se va es el parrafo visible de la ficha.
    html = SUBTITULO.sub('', html, count=1)

    if o.get('bajada'):
        # Google y WhatsApp leen estas etiquetas, no el texto visible.
        bajada_atributo = escapar_atributo(o['bajada'])
        html = re.sub(r'(<meta name="description" content=")[^"]*(">)',
                      lambda m: m.group(1) + bajada_atributo + m.group(2),
                      html, count=1)
        html = re.sub(r'(<meta property="og:description" content=")[^"]*(">)',
                      lambda m: m.group(1) + bajada_atributo + m.group(2),
                      html, count=1)

    # --- ficha ---
    filas = bloque_ficha(o, html)
    if filas is None:
        problemas.append('la ficha tiene un rotulo desconocido')
    else:
        nuevo, n = re.subn(
            r'(?s)(<dl class="project-specs">\n).*?(\n\s*</dl>)',
            lambda m: m.group(1) + filas + m.group(2), html, count=1)
        if not n:
            problemas.append('no encuentro la ficha')
        html = nuevo

    # --- la linea de datos debajo del titulo ---
    meta = bloque_meta(o)
    if meta:
        nuevo, n = re.subn(r'(?s)(<div class="project-meta-row">).*?(</div>)',
                           lambda m: m.group(1) + meta + m.group(2), html, count=1)
        if not n:
            problemas.append('no encuentro la linea de datos')
        html = nuevo

    # --- memoria ---
    tiene = re.search(r'(?s)\n    <section class="project-memoria">.*?\n    </section>\n',
                      html)
    nueva = bloque_memoria(o)
    if tiene:
        html = html[:tiene.start()] + ('\n' + nueva if nueva else '\n') + html[tiene.end():]
    elif nueva:
        # Va antes de la galeria, que es donde esta en todas las demas.
        ancla = '    <section class="project-gallery">'
        if ancla in html:
            html = html.replace(ancla, nueva + '\n' + ancla, 1)
        else:
            problemas.append('no hay donde poner la memoria')

    actual_premios = re.search(
        r'(?s)\n    <section class="project-awards-panel">.*?\n    </section>\n', html)
    premios = bloque_premios(o)
    if actual_premios:
        html = (html[:actual_premios.start()] + ('\n' + premios if premios else '\n')
                + html[actual_premios.end():])
    elif premios:
        ancla = '    <section class="project-gallery">'
        if ancla in html:
            html = html.replace(ancla, premios + '\n' + ancla, 1)

    actual_barra = re.search(
        r'(?s)\n    <section class="award-bar">.*?\n    </section>\n', html)
    barra = bloque_barra_premios(o)
    if actual_barra and barra:
        html = html[:actual_barra.start()] + '\n' + barra + html[actual_barra.end():]
    elif barra:
        # La franja acompaña la galería, igual que en las fichas heredadas.
        ancla = '    <section class="section no-border" id="galeria">'
        if ancla in html:
            html = html.replace(ancla, barra + '\n' + ancla, 1)
        else:
            problemas.append('no hay donde poner la barra de premios')
    # Si el campo todavia esta vacio se conserva la franja heredada. Hay tres
    # reconocimientos historicos que aun no fueron volcados al panel; borrarlos
    # por interpretar null como una orden de eliminacion repetiría la perdida
    # que motivo esta correccion.

    return html, problemas


def desde_supabase():
    """Trae las obras publicadas de la base.

    Los borradores se dejan afuera: son obras a medias que el estudio todavia
    no quiere mostrar, y el sitio publico no debe tener ni su pagina.
    """
    url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY', '')
    if not url or not clave:
        raise SystemExit(
            'Faltan SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno.')

    pedido = urllib.request.Request(
        url + '/rest/v1/obras?select=*&publicada=is.true&order=orden.asc',
        headers={'apikey': clave, 'Authorization': 'Bearer ' + clave})
    with urllib.request.urlopen(pedido, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def main(verificar, supabase):
    if supabase:
        datos = desde_supabase()
        print('obras traidas de la base: %d' % len(datos))
    else:
        datos = json.load(io.open(os.path.join(RAIZ, 'docs', 'panel_datos.json'),
                                  encoding='utf-8'))

    # La memoria en ingles no se escribe en la pagina castellana: el espejo la
    # toma de docs/en_memorias.json. Nadie llenaba ese archivo desde la base, asi
    # que una memoria inglesa cargada en el panel se guardaba y el sitio en ingles
    # seguia con la de antes -o sin bloque, si era nueva-. Aca se vuelca.
    if not verificar:
        mem_en = {}
        for o in datos:
            texto = (o.get('memoria_en') or '').strip()
            if not texto:
                continue
            parrafos = [p.strip() for p in re.split(r'\n\s*\n', texto) if p.strip()]
            if parrafos:
                mem_en[o['slug']] = parrafos
        io.open(os.path.join(RAIZ, 'docs', 'en_memorias.json'), 'w',
                encoding='utf-8', newline='\n').write(
            json.dumps(mem_en, ensure_ascii=False, indent=1, sort_keys=True) + '\n')
        print('memorias en ingles para el espejo: %d' % len(mem_en))

    cambiadas, iguales, avisos = [], 0, []
    for o in datos:
        ruta = os.path.join(RAIZ, 'proyectos', o['slug'], 'index.html')
        if not os.path.isfile(ruta):
            avisos.append('%s: no existe la pagina' % o['slug'])
            continue

        antes = io.open(ruta, encoding='utf-8').read()
        despues, problemas = aplicar(o, antes)
        for p in problemas:
            avisos.append('%s: %s' % (o['slug'], p))

        if despues == antes:
            iguales += 1
        else:
            cambiadas.append(o['slug'])
            if not verificar:
                io.open(ruta, 'w', encoding='utf-8', newline='\n').write(despues)

    print('obras: %d   sin cambios: %d   con cambios: %d'
          % (len(datos), iguales, len(cambiadas)))
    if cambiadas:
        print(('%s:\n  ' % ('DIFERENCIAS' if verificar else 'reescritas'))
              + ', '.join(cambiadas[:12])
              + ('…' if len(cambiadas) > 12 else ''))
    if avisos:
        print('\navisos (%d):' % len(avisos))
        for a in avisos[:15]:
            print('  ' + a)

    if verificar:
        if cambiadas:
            print('\nLa plantilla no reproduce el sitio tal cual: revisar antes '
                  'de dejar que el panel escriba.')
            return 1
        print('\nEl generador reproduce el sitio exactamente. Se puede confiar '
              'en que publicar desde el panel no pierde nada.')
    return 0


if __name__ == '__main__':
    sys.exit(main('--verificar' in sys.argv, '--supabase' in sys.argv))
