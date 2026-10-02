# -*- coding: utf-8 -*-
"""Suma a /premios/ los galardones cargados desde el panel.

La pagina historica conserva sus filas en el repositorio. Las filas nuevas
viven en premios_panel y se escriben entre dos marcas para que cada build las
reemplace sin duplicarlas. Si la migracion todavia no se aplico, el contenido
historico queda intacto y el build puede seguir publicando.
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


def e(valor):
    return html.escape(str(valor or ''), quote=True)


def fila(premio):
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
    if obra:
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


def bloque(premios):
    grupos = {}
    for premio in premios:
        grupos.setdefault(int(premio.get('anio') or 0), []).append(premio)
    partes = []
    for anio in sorted(grupos, reverse=True):
        partes.append('          <div class="award-year-block" data-year="%s">\n'
                      '            <div class="press-year-head">%s</div>\n%s\n'
                      '          </div>' % (anio, anio,
                      '\n'.join(fila(p) for p in grupos[anio])))
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


def main():
    pagina = io.open(PAGINA, encoding='utf-8').read()
    if INICIO not in pagina or FIN not in pagina:
        raise RuntimeError('faltan las marcas PREMIOS-PANEL en premios/index.html')
    try:
        url, clave = configuracion()
        premios = pedir(url, clave)
    except urllib.error.HTTPError as error:
        texto = error.read().decode('utf-8', 'replace')
        if error.code in (400, 404) and 'premios_panel' in texto:
            print('premios: migracion 0020 pendiente; se conserva el contenido actual')
            return 0
        raise
    bloque_nuevo = INICIO + ('\n' + bloque(premios) if premios else '') + '\n' + FIN
    pagina = re.sub(re.escape(INICIO) + r'.*?' + re.escape(FIN), bloque_nuevo,
                    pagina, count=1, flags=re.S)
    pagina = sumar_filtros(pagina, [p.get('anio') for p in premios])
    io.open(PAGINA, 'w', encoding='utf-8', newline='\n').write(pagina)
    print('premios: %d filas nuevas publicadas' % len(premios))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print('ERROR al sincronizar premios: %s' % error)
        sys.exit(1)
