# -*- coding: utf-8 -*-
"""Pone el sitio de acuerdo con lo que dice la base: saca lo que ya no va.

   panel_generar.py reescribe las paginas de las obras publicadas, pero no sabe
   nada de las que dejaron de estarlo. Sin este paso, eliminar una obra en el
   panel la saca de la base y su pagina sigue publicada, y despublicarla igual:
   el modo borrador solo funcionaba para obras que nunca se habian publicado.

   Que saca de una obra que ya no esta publicada:

   - la carpeta proyectos/<slug>/
   - sus galerias, planos y portada del build publico
   - su tarjeta y su fila en /proyectos/
   - sus entradas en el buscador, en los dos idiomas
   - los enlaces que la apuntaban desde premios, prensa u otras secciones

   Lo que NO hace: crear las que faltan —eso es otro paso— ni tocar el sitemap,
   que se regenera despues con docs/sitemap_gen.py leyendo el disco. El espejo
   en ingles tampoco: en_gen.py borra /en/ y lo rehace de cero.

   Antes de borrar algo revisa quien lo linkea. Una obra puede estar nombrada en
   /premios/ o en un banner del home, y sacar la pagina sin sacar el enlace deja
   un 404 que nadie ve hasta que un visitante lo encuentra.

       python docs/panel_sitio.py --verificar   # no toca nada, solo informa
       python docs/panel_sitio.py               # aplica, leyendo el JSON local
       python docs/panel_sitio.py --supabase    # aplica, leyendo la base
"""
import glob
import io
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'docs'))

LISTADO = os.path.join(RAIZ, 'proyectos', 'index.html')
BUSCADOR = os.path.join(RAIZ, 'scripts', 'search-index.js')
BUSCADOR_EN = os.path.join(RAIZ, 'scripts', 'search-index-en.js')

# Freno de mano. Si la consulta a la base falla a medias y devuelve poco, sin
# este tope el script borraria medio sitio sin preguntar.
TOPE_BAJAS = 5
RENOMBRES_FIJOS = os.path.join(RAIZ, 'docs', 'slugs_renombrados.json')


# ---------------------------------------------------------------------------
# De donde salen las obras
# ---------------------------------------------------------------------------

def desde_supabase():
    url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY', '')
    if not url or not clave:
        raise SystemExit('Faltan SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno.')
    pedido = urllib.request.Request(
        url + '/rest/v1/obras?select=slug,titulo,publicada',
        headers={'apikey': clave, 'Authorization': 'Bearer ' + clave})
    with urllib.request.urlopen(pedido, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def desde_json():
    p = os.path.join(RAIZ, 'docs', 'panel_datos.json')
    if not os.path.isfile(p):
        raise SystemExit('No existe docs/panel_datos.json. Corre con --supabase.')
    return json.load(io.open(p, encoding='utf-8'))


def aliases_publicados(supabase):
    """{slug anterior: slug actual} para distinguir renombres de bajas.

    La ruta anterior se guarda automaticamente en obra_aliases desde la
    migracion 0017. El JSON queda como respaldo local para poder verificar los
    dos renombres que ocurrieron antes de que esa tabla existiera.
    """
    if supabase:
        url = os.environ.get('SUPABASE_URL', '').rstrip('/')
        clave = os.environ.get('SUPABASE_SERVICE_KEY', '')
        pedido = urllib.request.Request(
            url + '/rest/v1/obra_aliases?select=slug,obras!inner(slug,publicada)'
                  '&obras.publicada=is.true',
            headers={'apikey': clave, 'Authorization': 'Bearer ' + clave})
        try:
            with urllib.request.urlopen(pedido, timeout=30) as respuesta:
                filas = json.loads(respuesta.read().decode('utf-8'))
            return dict((fila.get('slug'), (fila.get('obras') or {}).get('slug'))
                        for fila in filas if fila.get('slug')
                        and (fila.get('obras') or {}).get('slug'))
        except urllib.error.HTTPError as error:
            texto = error.read().decode('utf-8', 'replace')
            if error.code not in (400, 404) or 'obra_aliases' not in texto:
                raise

    if not os.path.isfile(RENOMBRES_FIJOS):
        return {}
    filas = json.load(io.open(RENOMBRES_FIJOS, encoding='utf-8'))
    return dict((viejo, datos.get('ahora')) for viejo, datos in filas.items()
                if datos.get('ahora'))


# ---------------------------------------------------------------------------
# Que hay hoy en el sitio
# ---------------------------------------------------------------------------

def slugs_con_pagina():
    fuera = set()
    for p in glob.glob(os.path.join(RAIZ, 'proyectos', '*', 'index.html')):
        fuera.add(os.path.basename(os.path.dirname(p)))
    return fuera


def bloque_del_listado(html, clase, slug):
    """(inicio, fin) del <a> de esa tarjeta o fila, o None.

    Se busca la apertura por sus atributos y despues su </a>. Un <a> de tarjeta
    no anida otro <a>, asi que el primer cierre es el suyo.
    """
    for m in re.finditer(r'<a\b[^>]*class="%s"[^>]*>' % re.escape(clase), html):
        if 'data-slug="%s"' % slug not in m.group(0):
            continue
        fin = html.find('</a>', m.end())
        if fin < 0:
            return None
        fin += len('</a>')
        # Se lleva tambien la sangria de la linea y el salto final, para no
        # dejar una linea en blanco donde estaba el bloque.
        ini = html.rfind('\n', 0, m.start()) + 1
        if html[fin:fin + 1] == '\n':
            fin += 1
        return ini, fin
    return None


def quien_linkea(slug, salvo):
    """Archivos del sitio que linkean a la obra, sin contar los que se van."""
    aguja = '/proyectos/%s/' % slug
    fuera = []
    for p in glob.glob(os.path.join(RAIZ, '**', '*.html'), recursive=True):
        rel = os.path.relpath(p, RAIZ).replace(os.sep, '/')
        if rel.startswith(('docs/', 'en/', 'admin/', 'node_modules/')):
            continue
        if rel in salvo:
            continue
        if aguja in io.open(p, encoding='utf-8').read():
            fuera.append(rel)
    return fuera


def desvincular(html, slug):
    """Saca enlaces a una obra dada de baja, conservando su contenido visible.

    El build parte siempre del repo limpio. Si la obra se vuelve a publicar, el
    enlace original reaparece y no hace falta reconstruirlo desde la base.
    """
    rutas = (
        '/proyectos/%s/' % slug,
        'https://estudiohma.com/proyectos/%s/' % slug,
    )
    for ruta in rutas:
        patron = re.compile(
            r'<a\b[^>]*href=["\']%s["\'][^>]*>(.*?)</a>' % re.escape(ruta),
            re.DOTALL | re.IGNORECASE)
        html = patron.sub(lambda m: m.group(1), html)
    return html


def sacar_recursos(slug):
    """Quita del resultado publico los archivos de una obra no publicada."""
    for carpeta in ('gallery', 'planos'):
        destino = os.path.join(RAIZ, 'assets', carpeta, slug)
        if os.path.isdir(destino):
            shutil.rmtree(destino)
    portada = os.path.join(RAIZ, 'assets', 'covers', slug + '.webp')
    if os.path.isfile(portada):
        os.remove(portada)


def actualizar_tarjeta_renombrada(bloque, viejo, actual, titulo):
    """Actualiza una tarjeta copiada dentro de la ficha de otra obra."""
    nombre = ((titulo or actual).replace('&', '&amp;').replace('<', '&lt;')
              .replace('>', '&gt;').replace('"', '&quot;'))
    bloque = bloque.replace('/proyectos/%s/' % viejo,
                            '/proyectos/%s/' % actual)
    bloque = bloque.replace('data-slug="%s"' % viejo,
                            'data-slug="%s"' % actual)
    bloque = re.sub(
        r'(/assets/covers/)%s\.webp(?:\?[^"\s]*)?' % re.escape(viejo),
        r'\g<1>%s.webp' % actual, bloque)
    bloque = re.sub(r'(<img\b[^>]*\balt=")[^"]*(")',
                    lambda m: m.group(1) + nombre + m.group(2), bloque, count=1)
    bloque = re.sub(r'(<div class="p-name">).*?(</div>)',
                    lambda m: m.group(1) + nombre + m.group(2), bloque,
                    count=1, flags=re.S)
    return bloque


def migrar_referencias_de_aliases(aliases, titulos, verificar):
    """Mueve enlaces y tarjetas al slug vigente antes de borrar el anterior.

    Un renombre no es una baja editorial. Si se lo trata como baja, se quita
    el enlace de las tarjetas relacionadas pero queda la portada vieja; cuando
    esa portada se borra, varias fichas muestran una imagen rota. Resolver la
    referencia completa conserva enlace, nombre y foto en un solo paso.
    """
    cambiados = []
    for p in glob.glob(os.path.join(RAIZ, '**', '*.html'), recursive=True):
        rel = os.path.relpath(p, RAIZ).replace(os.sep, '/')
        if rel.startswith(('docs/', 'en/', 'admin/', 'node_modules/')):
            continue
        if rel == 'proyectos/index.html':
            # El listado tiene su propio generador y todavia contiene la fila
            # vieja que este mismo paso va a retirar unos renglones mas abajo.
            continue
        crudo = io.open(p, encoding='utf-8').read()
        nuevo = crudo
        for viejo, actual in aliases.items():
            if not viejo or not actual or viejo == actual:
                continue
            # Las tarjetas necesitan mas que cambiar el href: portada, alt y
            # nombre visible tambien pertenecen a la obra actual.
            while True:
                corte = bloque_del_listado(nuevo, 'project-card', viejo)
                if corte is None:
                    break
                bloque = nuevo[corte[0]:corte[1]]
                reemplazo = actualizar_tarjeta_renombrada(
                    bloque, viejo, actual, titulos.get(actual, actual))
                nuevo = nuevo[:corte[0]] + reemplazo + nuevo[corte[1]:]
            # Premios, prensa y cualquier enlace de texto tambien deben seguir
            # llevando a la ficha, aunque no sean una tarjeta.
            nuevo = nuevo.replace('/proyectos/%s/' % viejo,
                                  '/proyectos/%s/' % actual)
            nuevo = nuevo.replace('https://estudiohma.com/proyectos/%s/' % viejo,
                                  'https://estudiohma.com/proyectos/%s/' % actual)
        if nuevo != crudo:
            cambiados.append(rel)
            if not verificar:
                io.open(p, 'w', encoding='utf-8', newline='\n').write(nuevo)
    return cambiados


# ---------------------------------------------------------------------------

def main(verificar, supabase):
    obras = desde_supabase() if supabase else desde_json()
    publicadas = set(o['slug'] for o in obras if o.get('publicada'))
    titulo = dict((o['slug'], o.get('titulo') or o['slug']) for o in obras)
    aliases = dict((viejo, actual) for viejo, actual
                   in aliases_publicados(supabase).items()
                   if actual in publicadas)

    if not publicadas:
        print('ERROR: la base no devolvio ninguna obra publicada. No se toca nada.')
        return 1

    en_disco = slugs_con_pagina()
    sobran = sorted(en_disco - publicadas)
    faltan = sorted(publicadas - en_disco)

    print('publicadas en la base: %d' % len(publicadas))
    print('con pagina en el sitio: %d' % len(en_disco))

    if faltan:
        print('\nsin pagina en el sitio (%d) — las crea el paso de alta:' % len(faltan))
        for s in faltan:
            print('  %-28s %s' % (s, titulo.get(s, '')))

    if not sobran:
        print('\nNada que sacar: el sitio no tiene obras que la base no publique.')
        return 0

    print('\npublicadas en el sitio y no en la base (%d):' % len(sobran))
    for s in sobran:
        print('  ' + s)

    if len(sobran) > TOPE_BAJAS and not verificar:
        print('\nERROR: son mas de %d bajas de una vez. Puede ser una consulta a '
              'la base que fallo a medias.\nRevisar la lista y, si esta bien, '
              'subir TOPE_BAJAS a mano en este archivo.' % TOPE_BAJAS)
        return 1

    migradas = migrar_referencias_de_aliases(aliases, titulo, verificar)
    if migradas:
        print('\nreferencias de obras renombradas actualizadas: %d' % len(migradas))
        for rel in migradas:
            print('  ' + rel)

    # --- enlaces que quedarian colgados ---
    # El propio listado no cuenta: su tarjeta y su fila se van en este mismo paso.
    salvo = set(['proyectos/index.html'] +
                ['proyectos/%s/index.html' % s for s in sobran])
    colgados = {}
    for s in sobran:
        donde = quien_linkea(s, salvo)
        if donde:
            colgados[s] = donde

    if colgados:
        print('\nOJO — enlaces que quedan apuntando a una pagina que ya no existe:')
        for s, donde in sorted(colgados.items()):
            print('  %s  <-  %s' % (s, ', '.join(donde)))
        print('  Se conservara el contenido visible y se sacara solo el enlace.')

    if verificar:
        print('\n(--verificar: no se toco nada)')
        return 0

    # --- enlaces externos a las fichas que se van ---
    # Se hace antes de borrar las paginas. Premios y prensa conservan el texto
    # o la imagen, pero ya no mandan a una URL inexistente.
    archivos_a_desvincular = set()
    for donde in colgados.values():
        archivos_a_desvincular.update(donde)
    for rel in sorted(archivos_a_desvincular):
        p = os.path.join(RAIZ, *rel.split('/'))
        crudo = io.open(p, encoding='utf-8').read()
        limpio = crudo
        for s in sobran:
            limpio = desvincular(limpio, s)
        if limpio != crudo:
            io.open(p, 'w', encoding='utf-8', newline='\n').write(limpio)
            print('  enlaces retirados de ' + rel)

    # --- listado ---
    html = io.open(LISTADO, encoding='utf-8').read()
    antes = html
    for s in sobran:
        for clase in ('project-card', 'project-list-row'):
            corte = bloque_del_listado(html, clase, s)
            if corte is None:
                print('  aviso: no encontre la %s de %s' % (clase, s))
                continue
            html = html[:corte[0]] + html[corte[1]:]
    if html != antes:
        io.open(LISTADO, 'w', encoding='utf-8', newline='\n').write(html)

    # --- buscador ---
    for archivo, molde in ((BUSCADOR, '/proyectos/%s/'),
                           (BUSCADOR_EN, '/en/projects/%s/')):
        if not os.path.isfile(archivo):
            continue
        crudo = io.open(archivo, encoding='utf-8').read()
        cabeza = crudo[:crudo.index('[')]
        indice = json.loads(crudo[crudo.index('['):crudo.rindex(']') + 1])
        urls = set(molde % s for s in sobran)
        quedan = [e for e in indice if e.get('url') not in urls]
        if len(quedan) != len(indice):
            io.open(archivo, 'w', encoding='utf-8', newline='\n').write(
                cabeza + json.dumps(quedan, ensure_ascii=False, indent=1) + ';\n')

    # --- las paginas ---
    for s in sobran:
        d = os.path.join(RAIZ, 'proyectos', s)
        if os.path.isdir(d):
            shutil.rmtree(d)
        sacar_recursos(s)

    tarjetas = len(re.findall(r'class="project-card"', html))
    filas = len(re.findall(r'class="project-list-row"', html))
    print('\nsacadas: %d   tarjetas que quedan: %d   filas: %d'
          % (len(sobran), tarjetas, filas))
    if tarjetas != filas:
        print('OJO: el listado quedo con distinta cantidad de tarjetas que de '
              'filas. Revisar antes de publicar.')
        return 1
    print('\nFalta correr docs/sitemap_gen.py y docs/en_gen.py para que el '
          'sitemap y el espejo se pongan al dia.')
    return 0


if __name__ == '__main__':
    sys.exit(main('--verificar' in sys.argv, '--supabase' in sys.argv))
