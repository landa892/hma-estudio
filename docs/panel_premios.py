# -*- coding: utf-8 -*-
"""Suma a /premios/ los galardones del panel y los vincula con sus obras.

La pagina historica conserva sus filas en el repositorio. Las filas nuevas
viven en premios_panel y se escriben entre dos marcas para que cada build las
reemplace sin duplicarlas. Los reconocimientos relacionados tambien se suman
a la banda negra de la ficha de cada obra. Si la migracion todavia no se aplico,
el contenido historico queda intacto y el build puede seguir publicando.
"""
import html
import io
import os
import re
import sys
import urllib.error
import urllib.request
import json

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINA = os.path.join(RAIZ, 'premios', 'index.html')
INICIO = '<!-- PREMIOS-PANEL-INICIO -->'
FIN = '<!-- PREMIOS-PANEL-FIN -->'
INICIO_OBRA = '<!-- PREMIOS-PANEL-OBRA-INICIO -->'
FIN_OBRA = '<!-- PREMIOS-PANEL-OBRA-FIN -->'


def configuracion():
    url = (os.environ.get('SUPABASE_URL') or '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY') or ''
    if not url or not clave:
        raise RuntimeError('faltan SUPABASE_URL o SUPABASE_SERVICE_KEY')
    return url, clave


def pedir(url, clave):
    req = urllib.request.Request(
        url + '/rest/v1/premios_panel?select=*&publicada=is.true'
        '&order=anio.desc,orden.asc,created_at.asc',
        headers={'apikey': clave, 'Authorization': 'Bearer ' + clave})
    with urllib.request.urlopen(req, timeout=45) as respuesta:
        crudo = respuesta.read()
        return json.loads(crudo.decode('utf-8')) if crudo else []


def pedir_slugs_publicados(url, clave):
    req = urllib.request.Request(
        url + '/rest/v1/obras?select=slug&publicada=is.true',
        headers={'apikey': clave, 'Authorization': 'Bearer ' + clave})
    with urllib.request.urlopen(req, timeout=45) as respuesta:
        crudo = respuesta.read()
        obras = json.loads(crudo.decode('utf-8')) if crudo else []
        return {obra.get('slug') for obra in obras if obra.get('slug')}


def e(valor):
    return html.escape(str(valor or ''), quote=True)


def fila(premio, slugs_publicados):
    logo = (premio.get('logo') or '').strip()
    obra = (premio.get('obra_slug') or '').strip()
    enlace = (premio.get('enlace') or '').strip()
    nombre = e(premio.get('nombre'))
    if enlace:
        nombre = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (e(enlace), nombre)
    logo_html = ('<div class="award-row__logo"><img src="%s" width="400" height="300" '
                 'alt="" loading="lazy" decoding="async"></div>' % e(logo)) if logo else (
                 '<div class="award-row__logo award-row__logo--plain"><span class="award-platform">%s</span></div>'
                 % e(premio.get('nombre')))
    descripcion = premio.get('descripcion') or ''
    obra_html = ''
    if obra and obra in slugs_publicados:
        obra_html = ('\n                  <span class="award-row__obra"><a href="/proyectos/%s/">%s</a></span>'
                     % (e(obra), e(obra.replace('-', ' ').title())))
    return ('            <div class="award-row">\n'
            '              <div class="award-row__left">\n'
            '                %s\n'
            '                <div class="award-row__content">\n'
            '                  <div class="award-row__name">%s</div>\n'
            '                  <span class="award-row__desc">%s</span>%s\n'
            '                </div>\n'
            '              </div>\n'
            '              <div class="award-row__res">%s</div>\n'
            '              <div class="award-row__city">%s</div>\n'
            '            </div>' % (logo_html, nombre, e(descripcion), obra_html,
                                   e(premio.get('resultado')), e(premio.get('ciudad'))))


def bloque(premios, slugs_publicados):
    grupos = {}
    for premio in premios:
        grupos.setdefault(int(premio.get('anio') or 0), []).append(premio)
    partes = []
    for anio in sorted(grupos, reverse=True):
        partes.append('          <div class="award-year-block" data-year="%s">\n'
                      '            <div class="press-year-head">%s</div>\n%s\n'
                      '          </div>' % (anio, anio,
                      '\n'.join(fila(p, slugs_publicados) for p in grupos[anio])))
    return '\n'.join(partes)


def sumar_filtros(html_pagina, anios):
    if not anios:
        return html_pagina
    existentes = set(re.findall(r'data-year="(\d{4})"', html_pagina))
    nuevos = [a for a in sorted(set(anios), reverse=True) if str(a) not in existentes]
    if not nuevos:
        return html_pagina
    botones = ''.join('\n          <button class="filter-btn" data-year="%s">%s</button>' % (a, a)
                     for a in nuevos)
    return html_pagina.replace('        </div>\n\n        <div class="award-feed">',
                               botones + '\n        </div>\n\n        <div class="award-feed">', 1)


def bloque_obras(premios, slugs_publicados):
    """Prepara los reconocimientos vinculados para la banda de cada ficha."""
    por_obra = {}
    for premio in premios:
        slug = (premio.get('obra_slug') or '').strip()
        if slug and slug in slugs_publicados:
            por_obra.setdefault(slug, []).append(premio)
    return por_obra


def item_barra(premio):
    nombre = e(premio.get('nombre'))
    logo = (premio.get('logo') or '').strip()
    if logo:
        visual = ('<img src="%s" alt="%s" loading="lazy" decoding="async">'
                  '<span>%s</span>' % (e(logo), nombre, nombre))
    else:
        visual = '<span>%s</span>' % nombre
    return ('          <a class="award-bar__item" href="/premios/" aria-label="Ver %s">'
            '%s</a>' % (nombre, visual))


def sincronizar_bandas(premios, slugs_publicados):
    """Suma premios vinculados a la banda sin reemplazar los reconocimientos viejos.

    Las marcas permiten sacar vínculos borrados o cambiados en cada build. Las
    bandas históricas se regeneran antes desde obras.premios y siguen intactas.
    """
    por_obra = bloque_obras(premios, slugs_publicados)
    carpeta = os.path.join(RAIZ, 'proyectos')
    if not os.path.isdir(carpeta):
        return
    for slug in os.listdir(carpeta):
        ruta = os.path.join(carpeta, slug, 'index.html')
        if not os.path.isfile(ruta):
            continue
        with io.open(ruta, encoding='utf-8') as archivo:
            pagina = archivo.read()
        if INICIO_OBRA in pagina and FIN_OBRA in pagina:
            pagina = re.sub(re.escape(INICIO_OBRA) + r'.*?' + re.escape(FIN_OBRA), '',
                            pagina, count=1, flags=re.S)
        relacionados = por_obra.get(slug, [])
        if relacionados:
            # No repetir una distinción que ya llega desde el campo histórico
            # obras.premios y su catálogo de logos.
            existentes = [html.unescape(x).strip().casefold() for x in re.findall(
                r'<a class="award-bar__item[^>]*>.*?<span>(.*?)</span>.*?</a>',
                pagina, flags=re.S)]
            nuevos = []
            for premio in relacionados:
                nombre = (premio.get('nombre') or '').strip()
                normalizado = nombre.casefold()
                if not normalizado or any(normalizado in x or x in normalizado for x in existentes):
                    continue
                nuevos.append(item_barra(premio))
                existentes.append(normalizado)
            if nuevos:
                contenido = INICIO_OBRA + '\n' + '\n'.join(nuevos) + '\n' + FIN_OBRA
                patron = r'(<div class="award-bar__logos">)(.*?)(</div>)'
                if re.search(patron, pagina, flags=re.S):
                    pagina = re.sub(patron, lambda m: m.group(1) + m.group(2) + '\n'
                                    + contenido + '\n        ' + m.group(3),
                                    pagina, count=1, flags=re.S)
                else:
                    banda = ('    <section class="award-bar">\n'
                             '      <div class="container award-bar__inner">\n'
                             '        <h2 class="award-bar__title">Premios y distinciones</h2>\n'
                             '        <div class="award-bar__logos">\n%s\n'
                             '        </div>\n      </div>\n    </section>\n' % contenido)
                    ancla = '    <section class="section no-border" id="galeria">'
                    if ancla in pagina:
                        pagina = pagina.replace(ancla, banda + ancla, 1)
                    else:
                        raise RuntimeError('%s: no encuentro dónde agregar la banda de premios' % slug)
        # Si el premio relacionado era el único elemento, al borrar o desvincular
        # el último se quita también la banda vacía que había creado el panel.
        patron_banda = r'(?s)\n    <section class="award-bar">.*?\n    </section>\n'
        coincidencia = re.search(patron_banda, pagina)
        if coincidencia and INICIO_OBRA not in coincidencia.group(0):
            caja = re.search(r'<div class="award-bar__logos">(.*?)</div>',
                             coincidencia.group(0), flags=re.S)
            if caja and not caja.group(1).strip():
                pagina = pagina[:coincidencia.start()] + '\n' + pagina[coincidencia.end():]
        with io.open(ruta, 'w', encoding='utf-8', newline='\n') as archivo:
            archivo.write(pagina)


def main():
    pagina = io.open(PAGINA, encoding='utf-8').read()
    if INICIO not in pagina or FIN not in pagina:
        raise RuntimeError('faltan las marcas PREMIOS-PANEL en premios/index.html')
    try:
        url, clave = configuracion()
        premios = pedir(url, clave)
        slugs_publicados = pedir_slugs_publicados(url, clave)
    except urllib.error.HTTPError as error:
        texto = error.read().decode('utf-8', 'replace')
        if error.code in (400, 404) and 'premios_panel' in texto:
            print('premios: migracion 0020 pendiente; se conserva el contenido actual')
            return 0
        raise
    bloque_nuevo = INICIO + ('\n' + bloque(premios, slugs_publicados) if premios else '') + '\n' + FIN
    pagina = re.sub(re.escape(INICIO) + r'.*?' + re.escape(FIN), bloque_nuevo,
                    pagina, count=1, flags=re.S)
    pagina = sumar_filtros(pagina, [p.get('anio') for p in premios])
    io.open(PAGINA, 'w', encoding='utf-8', newline='\n').write(pagina)
    sincronizar_bandas(premios, slugs_publicados)
    print('premios: %d filas nuevas publicadas' % len(premios))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print('ERROR al sincronizar premios: %s' % error)
        sys.exit(1)
