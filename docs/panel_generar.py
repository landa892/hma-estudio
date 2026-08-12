# -*- coding: utf-8 -*-
"""Escribe en las paginas del sitio lo que el estudio edita desde el panel.

No regenera la pagina entera: reemplaza solo las zonas que salen de la base
—titulo, bajada, ficha tecnica y memoria— y deja intacto todo lo demas. Es a
proposito. Una pagina de obra tiene planos, sellos de premio, banners y
correcciones acumuladas que no viven en la base: rehacerla desde una plantilla
las borraria sin que nadie se entere hasta verlo publicado.

Que se toca de cada obra:
  - el <h1> con el titulo
  - el parrafo de bajada
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

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ESTADOS = {
    'concluida': 'Obra concluida',
    'en_progreso': 'Proyecto en proceso',
    'en_proyecto': 'Proyecto',
}


def escapar(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def bloque_ficha(o, html):
    """Arma la ficha respetando el orden de rotulos que ya tiene la pagina.

    El orden no es igual en todas: algunas muestran Comitente y otras no. Se
    lee el orden actual y se completan los valores, en vez de imponer uno.
    """
    # Se guarda tambien la clase de cada fila: la del equipo lleva una propia
    # (spec-row--team) y reescribirla sin ella le cambia el estilo.
    filas_actuales = re.findall(
        r'<div class="(spec-row[^"]*)"><dt>(.*?)</dt>', html, re.S)
    rotulos = [r for _, r in filas_actuales]
    clases = dict((re.sub(r'\s+', ' ', r).strip(), c) for c, r in filas_actuales)
    valor = {
        'Estado': ESTADOS.get(o['estado'], ''),
        'Tipo': o.get('tipologia') or '',
        'Ubicación': o.get('ubicacion') or '',
        'País': o.get('pais') or '',
        'Superficie': o.get('superficie') or '',
        'Año': o.get('anio') or '',
        'Comitente': o.get('comitente') or '',
        'Fotografía': o.get('fotografia') or '',
        'Equipo': '<br>'.join(escapar(x) for x in (o.get('equipo') or [])),
    }

    filas = []
    for r in rotulos:
        rot = re.sub(r'\s+', ' ', r).strip()
        if rot not in valor:
            return None      # rotulo que el generador no conoce: no se toca
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
    cuerpo = '\n'.join('          <p>%s</p>' % escapar(p) for p in parrafos)
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

    # --- bajada ---
    if o.get('bajada'):
        nuevo, n = re.subn(r'(<p class="lede[^"]*"[^>]*>)(.*?)(</p>)',
                           lambda m: m.group(1) + escapar(o['bajada']) + m.group(3),
                           html, count=1, flags=re.S)
        if not n:
            problemas.append('sin bajada')
        html = nuevo

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
