# -*- coding: utf-8 -*-
"""Impide publicar si lo guardado en el panel no llego al sitio generado.

Esta comprobacion corre despues de generar el castellano y el espejo ingles,
pero antes de marcar el build como publicado. No corrige nada: si encuentra
una diferencia termina con error y Vercel conserva el deploy anterior.

La regla es deliberadamente global. Revisa obras, fichas, memorias, textos
fijos, novedades del Inicio, destacadas, Prensa y Conferencias y clases.
Tambien recorre todos los HTML para detectar referencias locales a imagenes
que no existen.
"""
import html
import io
import json
import os
import re
import subprocess
import sys
import datetime
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(RAIZ, 'docs')
sys.path.insert(0, DOCS)

import panel_home
import panel_novedades
import panel_textos
import prensa_paginas


def configuracion():
    url = (os.environ.get('SUPABASE_URL') or '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY') or ''
    if not url or not clave:
        raise RuntimeError('faltan SUPABASE_URL o SUPABASE_SERVICE_KEY')
    return url, clave


def pedir(url, clave, ruta):
    pedido = urllib.request.Request(
        url + ruta,
        headers={'apikey': clave, 'Authorization': 'Bearer ' + clave})
    with urllib.request.urlopen(pedido, timeout=45) as respuesta:
        crudo = respuesta.read()
        return json.loads(crudo.decode('utf-8')) if crudo else []


def leer(relativa):
    ruta = os.path.join(RAIZ, *relativa.replace('/', os.sep).split(os.sep))
    return io.open(ruta, encoding='utf-8').read() if os.path.isfile(ruta) else None


def visible(codigo):
    codigo = re.sub(r'(?is)<script\b.*?</script>|<style\b.*?</style>', ' ', codigo or '')
    codigo = re.sub(r'(?i)<br\s*/?>', '\n', codigo)
    codigo = re.sub(r'(?s)<[^>]+>', ' ', codigo)
    return re.sub(r'\s+', ' ', html.unescape(codigo)).strip()


def plano(texto):
    return re.sub(r'\s+', ' ', html.unescape(texto or '')).strip()


def correr_verificador(script, argumentos):
    resultado = subprocess.run(
        [sys.executable, os.path.join(DOCS, script)] + argumentos,
        cwd=RAIZ)
    return resultado.returncode == 0


def verificar_obras_y_textos(problemas):
    # Las obras se comparan usando exactamente el molde que escribe la salida.
    if not correr_verificador('panel_generar.py', ['--supabase', '--verificar']):
        problemas.append('las fichas o memorias de obras no coinciden con la base')


def verificar_textos_es(textos, problemas):
    """Compara el valor visible sin confundir enlaces y rotulos agregados."""
    por_clave = {f.get('clave'): f for f in textos}
    por_archivo = {}
    for clave, ruta, patron in panel_textos.ubicaciones(textos):
        por_archivo.setdefault(ruta, []).append((clave, patron))
    for ruta, campos in por_archivo.items():
        codigo = leer(ruta)
        if codigo is None:
            problemas.append('%s: falta la pagina de un texto editable' % ruta)
            continue
        desde = panel_textos.zona_de_contenido(codigo)
        for clave, patron in campos:
            fila = por_clave.get(clave)
            if not fila or not (fila.get('es') or '').strip():
                continue
            m = re.search(patron, codigo[desde:], re.S)
            if not m:
                problemas.append('%s: no se encuentra su campo en %s' % (clave, ruta))
                continue
            actual = panel_textos.como_lo_dice_el_sitio(m.group(1))
            if clave == 'contacto.telefonos':
                actual = re.sub(r'(?m)^WhatsApp:\s*', '', actual)
            if plano(actual) != plano(fila['es']):
                problemas.append('%s: el texto castellano no coincide con el panel' % clave)


def verificar_listado(obras, problemas):
    codigo = leer('proyectos/index.html')
    if codigo is None:
        problemas.append('no existe proyectos/index.html')
        return
    tarjetas = re.findall(r'<a\b[^>]*class="[^"]*project-card[^"]*".*?</a>',
                           codigo, re.S)
    filas = re.findall(r'<a\b[^>]*class="[^"]*project-list-row[^"]*".*?</a>',
                       codigo, re.S)
    por_tarjeta = {m.group(1): b for b in tarjetas
                   for m in [re.search(r'data-slug="([^"]+)"', b)] if m}
    por_fila = {m.group(1): b for b in filas
                for m in [re.search(r'data-slug="([^"]+)"', b)] if m}
    esperadas = {o['slug'] for o in obras}
    if set(por_tarjeta) != esperadas:
        problemas.append('la grilla de Trabajos no tiene exactamente las obras publicadas')
    if set(por_fila) != esperadas:
        problemas.append('la lista de Trabajos no tiene exactamente las obras publicadas')
    for obra in obras:
        for nombre, bloques in (('tarjeta', por_tarjeta), ('fila', por_fila)):
            bloque = bloques.get(obra['slug'], '')
            if bloque and plano(obra.get('titulo')) not in visible(bloque):
                problemas.append('%s: titulo viejo en la %s de Trabajos'
                                  % (obra['slug'], nombre))


def verificar_portadas(url, clave, obras, problemas):
    """Prueba que la portada elegida llego a todas sus salidas publicas.

    Antes se comprobaba que las obras y sus titulos estuvieran en el listado,
    pero no que su imagen fuera la seleccionada en el panel. Una tarjeta podia
    conservar la tapa vieja y el build terminaba en verde. El mapa contiene el
    id de la fila que panel_galerias resolvio; compararlo con la base evita que
    una ruta valida o un alias historico escondan una portada desactualizada.
    """
    ruta_mapa = os.path.join(DOCS, 'panel_portadas.json')
    if not os.path.isfile(ruta_mapa):
        problemas.append('Trabajos: no se genero el mapa de portadas')
        return
    portadas = json.load(io.open(ruta_mapa, encoding='utf-8'))
    por_slug = {o['slug']: o for o in obras}
    filas = pedir(
        url, clave,
        '/rest/v1/obra_imagenes?select=id,obra_id&tipo=eq.foto&es_portada=is.true')
    por_obra = {}
    for fila in filas:
        por_obra.setdefault(fila['obra_id'], []).append(fila['id'])

    listado = leer('proyectos/index.html') or ''
    buscador_crudo = leer('scripts/search-index.js') or ''
    try:
        inicio = buscador_crudo.index('[')
        fin = buscador_crudo.rindex(']') + 1
        buscador = json.loads(buscador_crudo[inicio:fin])
    except (ValueError, TypeError):
        buscador = []
        problemas.append('Trabajos: no se puede leer el indice del buscador')
    imagen_buscador = {
        m.group(1): entrada.get('img')
        for entrada in buscador
        for m in [re.match(r'/proyectos/([^/]+)/', entrada.get('url', ''))]
        if m
    }

    def src_en_bloque(patron, codigo):
        m = re.search(patron, codigo, re.S)
        if not m:
            return ''
        img = re.search(r'<img\b[^>]*\bsrc="([^"]+)"', m.group(0))
        return html.unescape(img.group(1)) if img else ''

    for slug, portada in portadas.items():
        obra = por_slug.get(slug)
        if not obra:
            problemas.append('%s: hay una portada para una obra no publicada' % slug)
            continue
        elegidas = por_obra.get(obra['id'], [])
        if len(elegidas) != 1:
            problemas.append('%s: la base debe tener exactamente una portada' % slug)
            continue
        if portada.get('imagen_id') != elegidas[0]:
            problemas.append('%s: la portada generada no es la elegida en el panel' % slug)
            continue

        esperada = portada.get('src') or ''
        tarjeta = src_en_bloque(
            r'<a\b[^>]*class="[^"]*project-card[^"]*"[^>]*data-slug="%s".*?</a>'
            % re.escape(slug), listado)
        fila = src_en_bloque(
            r'<a\b[^>]*class="[^"]*project-list-row[^"]*"[^>]*data-slug="%s".*?</a>'
            % re.escape(slug), listado)
        if tarjeta != esperada:
            problemas.append('%s: la grilla de Trabajos conserva otra portada' % slug)
        if fila != esperada:
            problemas.append('%s: la lista de Trabajos conserva otra portada' % slug)
        if imagen_buscador.get(slug) != esperada:
            problemas.append('%s: el buscador conserva otra portada' % slug)

        ficha = leer('proyectos/%s/index.html' % slug) or ''
        seccion = re.search(
            r'<section class="project-gallery">.*?</section>', ficha, re.S)
        primera = src_en_bloque(r'<section class="project-gallery">.*?</section>',
                                ficha)
        if not seccion or primera != esperada:
            problemas.append('%s: la ficha conserva otra portada' % slug)
        og = re.search(r'<meta property="og:image" content="([^"]+)"', ficha)
        if not og or html.unescape(og.group(1)) != 'https://estudiohma.com' + esperada:
            problemas.append('%s: la imagen para compartir conserva otra portada' % slug)


def verificar_fotos_del_cuerpo(obras, problemas):
    """La cantidad del panel debe tomar las primeras N fotos de la galeria."""
    for obra in obras:
        cantidad = obra.get('fotos_cuerpo_cantidad')
        if cantidad is None:
            continue
        slug = obra['slug']
        ficha = leer('proyectos/%s/index.html' % slug) or ''
        cuerpo = re.search(
            r'<section class="project-gallery">(.*?)</section>', ficha, re.S)
        galeria = re.search(
            r'<section class="section no-border" id="galeria">(.*?)</section>',
            ficha, re.S)
        if not cuerpo or not galeria:
            problemas.append('%s: falta el cuerpo o la galeria de la obra' % slug)
            continue
        fotos_cuerpo = re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', cuerpo.group(1))
        fotos_galeria = [
            m.group(1) for m in re.finditer(
                r'<figure class="gallery-grid__item(?![^"]*--plano)[^"]*">\s*'
                r'<img\b[^>]*\bsrc="([^"]+)"', galeria.group(1), re.S)
        ]
        esperadas = fotos_galeria[:int(cantidad)]
        if fotos_cuerpo != esperadas:
            problemas.append(
                '%s: las fotos del cuerpo no son las primeras %d de la galeria'
                % (slug, int(cantidad)))


def verificar_destacadas(obras, problemas):
    codigo = leer('index.html')
    if codigo is None:
        problemas.append('no existe index.html')
        return
    destacadas = [o for o in obras if o.get('destacada')]
    destacadas.sort(key=lambda o: (o.get('orden') is None, o.get('orden') or 0,
                                   (o.get('titulo') or '').lower()))
    bloques = list(panel_home.BANNER.finditer(codigo))
    for obra, coincidencia in zip(destacadas[:panel_home.RANURAS], bloques):
        esperado, aviso = panel_home.armar(obra, coincidencia.group(1))
        if esperado is None:
            problemas.append('%s: no se puede construir su banner (%s)'
                              % (obra['slug'], aviso))
        elif esperado != coincidencia.group(0):
            problemas.append('%s: el banner del Inicio no refleja el panel' % obra['slug'])


def verificar_novedades_inicio(textos, problemas):
    codigo = leer('index.html') or ''
    por_clave = {f.get('clave'): f for f in textos}
    for red in ('instagram', 'linkedin', 'youtube'):
        for campo in ('titulo', 'texto'):
            fila = por_clave.get('home.%s_%s' % (red, campo))
            if not fila or not (fila.get('es') or '').strip():
                continue
            patron = (r'<(?:h2|p)\b[^>]*data-%s-%s\b[^>]*>(.*?)</(?:h2|p)>'
                      % (red, 'title' if campo == 'titulo' else 'text'))
            m = re.search(patron, codigo, re.S)
            if not m or visible(m.group(1)) != plano(fila['es']):
                problemas.append('Inicio: %s de %s no coincide con el panel'
                                  % (campo, red))
        for campo, atributo in (('url', 'href'), ('imagen', 'src')):
            fila = por_clave.get('home.%s_%s' % (red, campo))
            if not fila or not (fila.get('es') or '').strip():
                continue
            valor = fila['es'].strip()
            if campo == 'imagen':
                valor = panel_novedades.ruta_imagen_salida(red, valor)
            dato = 'data-%s-%s' % (red, 'link' if campo == 'url' else 'image')
            etiquetas = re.findall(r'<[^>]*\b%s\b[^>]*>' % dato, codigo)
            valores = []
            for etiqueta in etiquetas:
                m = re.search(r'\b%s="([^"]*)"' % atributo, etiqueta)
                if m:
                    valores.append(html.unescape(m.group(1)))
            if valor not in valores:
                problemas.append('Inicio: %s de %s no coincide con el panel'
                                  % (campo, red))


def verificar_prensa(url, clave, problemas):
    filas = pedir(url, clave,
                  '/rest/v1/prensa_publicaciones?select=*&publicada=is.true&order=orden.asc,created_at.desc')
    datos = json.load(io.open(os.path.join(DOCS, 'prensa_datos.json'), encoding='utf-8'))
    por_slug = {n['slug']: n for n in datos}
    if {f['slug'] for f in filas} != set(por_slug):
        problemas.append('Prensa: el archivo generado no coincide con las publicaciones activas')

    antes, despues = prensa_paginas.cascara()
    for nota in datos:
        ruta = 'prensa/%s/index.html' % nota['slug']
        actual = leer(ruta)
        if actual is None:
            problemas.append('%s: falta la pagina de Prensa' % nota['slug'])
            continue
        esperado = (prensa_paginas.cabeza(antes, nota)
                    + prensa_paginas.cuerpo(nota) + despues)
        # en_gen solo agrega estos enlaces al castellano. Se comparan las
        # zonas administrables, que son el cuerpo de la nota y sus metadatos.
        if prensa_paginas.cuerpo(nota) not in actual:
            problemas.append('%s: la ficha de Prensa no refleja el panel' % nota['slug'])
        titulo = prensa_paginas.titulo_seo(nota)
        if '<title>%s</title>' % prensa_paginas.e(titulo) not in actual:
            problemas.append('%s: titulo SEO de Prensa desactualizado' % nota['slug'])

    novedades = pedir(
        url, clave,
        '/rest/v1/prensa_novedades?select=*&publicada=is.true&eliminada=is.false&order=orden.asc,created_at.asc')
    generadas = json.load(io.open(
        os.path.join(DOCS, 'prensa_novedades.json'), encoding='utf-8'))
    esperado = [{
        'rubro': f.get('rubro') or 'CONFERENCIA',
        'titulo': f.get('titulo') or '',
        'detalle': f.get('detalle') or '',
        'anio': str(f.get('anio') or ''),
        'link': f.get('link') or '',
    } for f in novedades]
    if generadas != esperado:
        problemas.append('Conferencias y clases: el archivo generado no coincide con la base')
    pagina = leer('prensa/index.html') or ''
    for novedad in generadas:
        if prensa_paginas.e((novedad.get('detalle') or novedad.get('titulo') or '').strip()) not in pagina:
            problemas.append('Conferencias y clases: falta una entrada de %s'
                              % novedad.get('anio', 'sin fecha'))


def verificar_ingles(obras, textos, problemas):
    rutas = {
        'index.html': 'en/index.html',
        'estudio/index.html': 'en/studio/index.html',
        'proyectos/index.html': 'en/projects/index.html',
        'prensa/index.html': 'en/press/index.html',
        'premios/index.html': 'en/awards/index.html',
        'contacto/index.html': 'en/contact/index.html',
    }
    ruta_por_clave = {clave: ruta for clave, ruta, _patron
                      in panel_textos.ubicaciones(textos)}
    cache = {}
    for fila in textos:
        # URL, imagen y modo se verifican como configuracion del Inicio. No son
        # texto visible y por eso no corresponde buscarlos dentro del espejo.
        if fila.get('clave', '').endswith(('_url', '_imagen', '_modo')):
            continue
        valor = plano(fila.get('en'))
        ruta_es = ruta_por_clave.get(fila.get('clave'), 'index.html'
                                     if fila.get('seccion') == 'novedades' else None)
        ruta_en = rutas.get(ruta_es)
        if not valor or not ruta_en:
            continue
        if ruta_en not in cache:
            cache[ruta_en] = visible(leer(ruta_en) or '')
        partes = [plano(x) for x in (fila.get('en') or '').split('\n') if plano(x)]
        if any(parte not in cache[ruta_en] for parte in partes):
            problemas.append('%s: el texto ingles no llego al espejo' % fila['clave'])

    for obra in obras:
        memoria = plano(obra.get('memoria_en'))
        if not memoria:
            continue
        pagina = visible(leer('en/projects/%s/index.html' % obra['slug']) or '')
        partes = [plano(p) for p in re.split(r'\n\s*\n', obra['memoria_en']) if plano(p)]
        if any(parte not in pagina for parte in partes):
            problemas.append('%s: la memoria inglesa no llego al espejo' % obra['slug'])


def verificar_imagenes(problemas):
    rotas = []
    for base, carpetas, archivos in os.walk(RAIZ):
        carpetas[:] = [d for d in carpetas if d not in (
            '.git', '.vercel', 'node_modules', 'docs', 'admin')]
        for nombre in archivos:
            if nombre != 'index.html' and nombre != '404.html':
                continue
            ruta = os.path.join(base, nombre)
            codigo = io.open(ruta, encoding='utf-8').read()
            for fuente in re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', codigo):
                if (not fuente.startswith('/') or fuente.startswith('//')
                        or fuente.startswith('/api/')):
                    continue
                local = fuente.split('?', 1)[0].split('#', 1)[0]
                destino = os.path.join(RAIZ, *local.lstrip('/').split('/'))
                if not os.path.isfile(destino):
                    rotas.append('%s -> %s' % (os.path.relpath(ruta, RAIZ), local))
    if rotas:
        problemas.append('hay %d referencias a imagenes locales inexistentes: %s'
                          % (len(rotas), '; '.join(rotas[:8])))


def escribir_marca_de_deploy():
    """Deja una prueba publica de que commit termino todas las validaciones.

    El control posterior al deploy espera esta marca antes de recorrer el
    dominio. Sin ella podria probar la version anterior mientras Vercel aun
    esta construyendo y anunciar un falso positivo.
    """
    commit = (os.environ.get('VERCEL_GIT_COMMIT_SHA') or '').strip()
    if not os.environ.get('VERCEL') or not commit:
        print('  fuera de Vercel: no se escribe deployment.json')
        return
    marca = {
        'commit': commit,
        'generado': datetime.datetime.now(datetime.timezone.utc)
        .replace(microsecond=0).isoformat(),
    }
    with io.open(os.path.join(RAIZ, 'deployment.json'), 'w', encoding='utf-8') as salida:
        json.dump(marca, salida, ensure_ascii=False, sort_keys=True)
        salida.write('\n')
    print('  marca de deploy: ' + commit[:12])


def main():
    url, clave = configuracion()
    problemas = []
    obras = pedir(url, clave,
                  '/rest/v1/obras?select=*&publicada=is.true&order=orden.asc')
    textos = pedir(url, clave, '/rest/v1/textos?select=*&order=orden.asc')

    verificar_obras_y_textos(problemas)
    verificar_textos_es(textos, problemas)
    verificar_listado(obras, problemas)
    verificar_portadas(url, clave, obras, problemas)
    verificar_fotos_del_cuerpo(obras, problemas)
    verificar_destacadas(obras, problemas)
    verificar_novedades_inicio(textos, problemas)
    verificar_prensa(url, clave, problemas)
    verificar_ingles(obras, textos, problemas)
    verificar_imagenes(problemas)

    if problemas:
        print('\nVERIFICACION GLOBAL FALLIDA (%d):' % len(problemas))
        for problema in problemas:
            print('  - ' + problema)
        print('\nNo se marca el build como publicado y Vercel conserva el sitio anterior.')
        return 1
    print('\nVERIFICACION GLOBAL OK')
    print('  %d obras, %d textos y toda Prensa coinciden con la salida generada.'
          % (len(obras), len(textos)))
    escribir_marca_de_deploy()
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print('ERROR en la verificacion global: %s' % error)
        sys.exit(1)
