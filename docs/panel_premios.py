# -*- coding: utf-8 -*-
"""Suma a /premios/ los galardones del panel y los vincula con sus obras.

La pagina historica conserva sus filas en el repositorio. Las filas nuevas
viven en premios_panel y se escriben entre dos marcas para que cada build las
reemplace sin duplicarlas. Los reconocimientos relacionados tambien se suman
a la banda negra de la ficha de cada obra. Si la migracion todavia no se aplico,
el contenido historico queda intacto y el build puede seguir publicando.
"""
import glob
import html
import io
import os
import re
import sys
import urllib.error
import unicodedata
import urllib.request
import json

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINA = os.path.join(RAIZ, 'premios', 'index.html')
INICIO = '<!-- PREMIOS-PANEL-INICIO -->'
FIN = '<!-- PREMIOS-PANEL-FIN -->'
INICIO_OBRA = '<!-- PREMIOS-PANEL-OBRA-INICIO -->'
FIN_OBRA = '<!-- PREMIOS-PANEL-OBRA-FIN -->'

# Cada fila del panel va envuelta en su propio par de marcas, y el bloque de
# año que el panel haya tenido que crear lleva la suya. Asi cada build puede
# sacar lo que puso la vez anterior y volver a repartirlo, sin tocar las filas
# historicas que viven en el repositorio.
#
# Antes todo esto se escribia de corrido entre PREMIOS-PANEL-INICIO y -FIN, que
# estan al final del listado. El resultado es el que filmo el estudio el
# 16/10/2026: la pagina mostraba 2026, 2025, ... 2008 y despues otra vez 2026 y
# 2025, con los premios cargados desde el panel colgando abajo de todo en vez
# de estar con los de su año.
FILA_INICIO = '<!-- PREMIO-PANEL:%s -->'
FILA_FIN = '<!-- /PREMIO-PANEL -->'
FILTROS_INICIO = '<!-- PREMIOS-FILTROS-INICIO -->'
FILTROS_FIN = '<!-- PREMIOS-FILTROS-FIN -->'

# Los premios cuyo sello es una palabra y no una imagen guardan ese texto en
# el mismo campo logo, con este prefijo.
TEXTO = '@texto:'

# Reposiciones puntuales, con la misma idea que panel_correcciones_agosto: se
# comprueba el estado anterior antes de tocar nada, asi el build arregla lo que
# quedo mal pero no pisa una edicion posterior del estudio.
#
# El 16/10/2026 el logo de Valk Gallery desaparecio de la base al guardar el
# premio desde el panel -updated_at 14:59:43Z-, mientras el archivo seguia
# subido al Storage. Se repone. La guarda es doble: solo si el premio sigue sin
# logo y si nadie lo volvio a editar desde entonces. En cuanto el estudio lo
# toque, el updated_at cambia y esta reposicion deja de aplicarse sola; cuando
# eso pase se puede borrar esta entrada.
REPONER_LOGO = {
    '532a440e-52fd-4397-81d5-760bbbccab30': {
        'updated_at': '2026-10-16T14:59:43.727626+00:00',
        'logo': 'https://gbxtssedongadgorpxxs.supabase.co/storage/v1/object/'
                'public/obras/premios/1792160812748-e6e6ibd9.webp',
    },
}


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


def reponer_logos(url, clave, premios):
    """Devuelve a su logo los premios que lo perdieron, si nadie los edito despues.

    Escribe en la base y tambien en la lista que ya esta en memoria, para que el
    mismo build publique la pagina con el logo puesto y no haya que esperar al
    siguiente.
    """
    for premio in premios:
        esperado = REPONER_LOGO.get(str(premio.get('id')))
        if not esperado:
            continue
        if (premio.get('logo') or '').strip():
            continue
        if premio.get('updated_at') != esperado['updated_at']:
            print('premios: %s se edito despues; no se repone el logo'
                  % premio.get('nombre'))
            continue
        cuerpo = json.dumps({'logo': esperado['logo']}).encode('utf-8')
        pedido = urllib.request.Request(
            url + '/rest/v1/premios_panel?id=eq.' + str(premio['id']),
            data=cuerpo, method='PATCH',
            headers={'apikey': clave, 'Authorization': 'Bearer ' + clave,
                     'Content-Type': 'application/json'})
        with urllib.request.urlopen(pedido, timeout=45):
            pass
        premio['logo'] = esperado['logo']
        print('premios: logo repuesto en %s' % premio.get('nombre'))


LOGOS = os.path.join(RAIZ, 'assets', 'awards')
TIPOS = {'image/png': '.png', 'image/webp': '.webp', 'image/jpeg': '.jpg',
         'image/jpg': '.jpg', 'image/svg+xml': '.svg', 'image/gif': '.gif'}


def bajar_logos(premios):
    """Trae al repositorio los logos que apuntan a otro dominio.

    El sitio publicado declara img-src 'self' data: https://i.ytimg.com, asi
    que el navegador bloquea cualquier imagen que no salga de estudiohma.com:
    ni la que el panel sube al Storage de Supabase ni la que se pega de otra
    pagina. El estudio subia el logo, lo veia bien en el panel -que si tiene
    permitido supabase.co en su propio CSP- y en la pagina no aparecia nada.
    Eso es el premio "que se ve en blanco" del 16/10/2026.

    La salida no es abrir el CSP: dejaria el sitio mostrando imagenes de
    servidores ajenos y dependiendo de que el Gobierno de la Ciudad no mueva un
    archivo. Se bajan al repositorio, como ya hacen las galerias y las notas de
    prensa, y se sirven desde el propio dominio.
    """
    if not any((p.get('logo') or '').startswith(('http://', 'https://'))
               for p in premios):
        return
    os.makedirs(LOGOS, exist_ok=True)
    for premio in premios:
        origen = (premio.get('logo') or '').strip()
        if not origen.startswith(('http://', 'https://')):
            continue
        try:
            pedido = urllib.request.Request(
                origen, headers={'User-Agent': 'hma-estudio/build'})
            with urllib.request.urlopen(pedido, timeout=45) as respuesta:
                tipo = (respuesta.headers.get('Content-Type') or '').split(';')[0].strip()
                datos = respuesta.read()
        except Exception as error:
            # Un logo que no se puede bajar no tiene que voltear el build: la
            # fila sale sin sello y el resto de la pagina se publica igual.
            print('premios: no se pudo bajar el logo de %s (%s); queda sin sello'
                  % (premio.get('nombre'), error))
            premio['logo'] = ''
            continue
        extension = TIPOS.get(tipo)
        if not extension or not datos:
            print('premios: el logo de %s no es una imagen servible (%s); '
                  'queda sin sello' % (premio.get('nombre'), tipo or 'sin tipo'))
            premio['logo'] = ''
            continue
        nombre = 'panel-%s%s' % (premio.get('id'), extension)
        with open(os.path.join(LOGOS, nombre), 'wb') as archivo:
            archivo.write(datos)
        premio['logo'] = '/assets/awards/' + nombre
        print('premios: logo de %s guardado en %s'
              % (premio.get('nombre'), premio['logo']))

    # Los panel-* que ya no corresponden a ningun premio se van, para que la
    # carpeta no junte logos de premios borrados.
    vigentes = {os.path.basename(p['logo']) for p in premios
                if (p.get('logo') or '').startswith('/assets/awards/panel-')}
    for viejo in glob.glob(os.path.join(LOGOS, 'panel-*')):
        if os.path.basename(viejo) not in vigentes:
            os.remove(viejo)


HISTORICOS = os.path.join(RAIZ, 'docs', 'premios_historicos.json')


def sembrar_historicos(url, clave, premios):
    """Mete en la base los premios que vivian escritos en premios/index.html.

    El estudio pidio en audio el 16/10/2026 poder mover el orden: "si yo quiero
    poner otro arriba pueda hacerlo". Mientras los treinta y nueve premios
    viejos estuvieran en el HTML eso era imposible, porque el panel no podia
    tocarlos y siempre salian primero dentro de su año.

    Se siembra una sola vez: solo si NINGUNO de los historicos esta en la base.
    Asi, si el estudio borra uno desde el panel, el build no se lo vuelve a
    poner. Y a los premios que el panel ya tenia cargados se les corre el orden
    para que queden detras de los historicos de su mismo año, que es donde
    estaban cuando se publicaban.
    """
    if not os.path.isfile(HISTORICOS):
        return premios
    historicos = json.load(io.open(HISTORICOS, encoding='utf-8'))
    if not historicos:
        return premios

    def clave_de(premio):
        return (int(premio.get('anio') or 0), normalizar(premio.get('nombre')))

    en_base = {clave_de(p) for p in premios}
    if any(clave_de(h) in en_base for h in historicos):
        return premios

    # Los que ya estaban cargados desde el panel pasan atras de los historicos,
    # uno detras de otro. Sumarle a cada uno la cantidad de historicos de su año
    # no alcanza: los cuatro venian con orden 0 -que es el valor por defecto del
    # formulario- asi que los tres de 2026 terminaban los tres en 1.
    porque = {}
    for premio in sorted(premios, key=lambda p: (int(p.get('orden') or 0),
                                                 p.get('created_at') or '')):
        anio = int(premio.get('anio') or 0)
        if anio not in porque:
            porque[anio] = sum(1 for h in historicos if int(h['anio']) == anio)
        nuevo = porque[anio]
        porque[anio] += 1
        if nuevo != int(premio.get('orden') or 0):
            pedido = urllib.request.Request(
                url + '/rest/v1/premios_panel?id=eq.' + str(premio['id']),
                data=json.dumps({'orden': nuevo}).encode('utf-8'), method='PATCH',
                headers={'apikey': clave, 'Authorization': 'Bearer ' + clave,
                         'Content-Type': 'application/json'})
            with urllib.request.urlopen(pedido, timeout=45):
                pass
            premio['orden'] = nuevo

    cuerpo = [{
        'anio': h['anio'], 'orden': h['orden'], 'nombre': h['nombre'],
        'resultado': h.get('resultado') or None, 'ciudad': h.get('ciudad') or None,
        'descripcion': h.get('descripcion') or None,
        'enlace': h.get('enlace') or None, 'obra_slug': h.get('obra_slug') or None,
        'logo': h.get('logo') or None, 'publicada': True,
    } for h in historicos]

    nuevos = []
    for desde in range(0, len(cuerpo), 50):
        pedido = urllib.request.Request(
            url + '/rest/v1/premios_panel',
            data=json.dumps(cuerpo[desde:desde + 50]).encode('utf-8'), method='POST',
            headers={'apikey': clave, 'Authorization': 'Bearer ' + clave,
                     'Content-Type': 'application/json',
                     'Prefer': 'return=representation'})
        with urllib.request.urlopen(pedido, timeout=60) as respuesta:
            nuevos.extend(json.loads(respuesta.read().decode('utf-8')))
    print('premios: %d historicos sembrados; desde ahora los edita el panel'
          % len(nuevos))
    return premios + nuevos


def normalizar_orden(url, clave, premios):
    """Deja cada año numerado 0..n-1, sin empates ni huecos.

    Hace falta porque el panel guarda un premio nuevo con orden 0, que es el
    valor por defecto del formulario: cargar uno en un año que ya tiene premios
    lo empata con el primero. Y cambiar el año de un premio se lleva el orden
    del año viejo, que puede chocar en el nuevo.

    Un empate no rompe la pagina -se desempata por fecha de carga- pero deja el
    orden a merced de un dato que el estudio no ve ni controla, y las flechas
    del panel se mueven raro. Se repara en cada build, que es barato: se tocan
    solo los que cambian.
    """
    por_anio = {}
    for premio in premios:
        por_anio.setdefault(int(premio.get('anio') or 0), []).append(premio)

    arreglados = 0
    for anio, grupo in por_anio.items():
        ordenados = sorted(grupo, key=lambda p: (int(p.get('orden') or 0),
                                                 p.get('created_at') or ''))
        for puesto, premio in enumerate(ordenados):
            if int(premio.get('orden') or 0) == puesto:
                continue
            pedido = urllib.request.Request(
                url + '/rest/v1/premios_panel?id=eq.' + str(premio['id']),
                data=json.dumps({'orden': puesto}).encode('utf-8'), method='PATCH',
                headers={'apikey': clave, 'Authorization': 'Bearer ' + clave,
                         'Content-Type': 'application/json'})
            with urllib.request.urlopen(pedido, timeout=45):
                pass
            premio['orden'] = puesto
            arreglados += 1
    if arreglados:
        print('premios: %d ordenes reacomodados (habia empates o huecos)'
              % arreglados)


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


# Las obras que en esta pagina se nombraban distinto que en su propia ficha.
# Al pasar los premios a la base el texto del enlace pasa a salir del <h1> de
# la obra, y en cinco casos eso cambiaba lo que el visitante venia leyendo:
# "Mercado Manduca" se acortaba a "Manduca", "Mamba Bar" a "Mamba" y "Osten
# Coffee Shop" se alargaba a "Osten Coffee Shop — Casa FOA". Nadie pidio
# cambiar esos nombres, asi que se conservan tal cual estaban publicados.
# Si alguna vez se quiere unificar con el titulo de la ficha, se borra esta
# tabla y listo.
NOMBRES_EN_PREMIOS = {
    'accor-hotels': 'Accor',
    'dos-casas-conde': 'Dos casas Conde',
    'mamba-bar': 'Mamba Bar',
    'manduca': 'Mercado Manduca',
    'osten-foa': 'Osten Coffee Shop',
}

_titulos = {}


def titulo_de_obra(slug):
    """El texto del enlace a la obra.

    Primero las excepciones de arriba, y si no el titulo con el que la obra se
    publica, leido de su propia ficha. Del slug no alcanza:
    "galeria-objeto-a".title() da "Galeria Objeto A" y la obra se llama
    "Galería de arte Objeto A".
    """
    if slug in NOMBRES_EN_PREMIOS:
        return NOMBRES_EN_PREMIOS[slug]
    if slug in _titulos:
        return _titulos[slug]
    ruta = os.path.join(RAIZ, 'proyectos', slug, 'index.html')
    nombre = ''
    if os.path.isfile(ruta):
        marca = re.search(r'<h1[^>]*>(.*?)</h1>',
                          io.open(ruta, encoding='utf-8').read(), re.S)
        if marca:
            nombre = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', marca.group(1))).strip()
    _titulos[slug] = nombre or slug.replace('-', ' ').title()
    return _titulos[slug]


def fila(premio, slugs_publicados):
    logo = (premio.get('logo') or '').strip()
    obra = (premio.get('obra_slug') or '').strip()
    enlace = (premio.get('enlace') or '').strip()
    nombre = e(premio.get('nombre'))
    if enlace:
        nombre = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (e(enlace), nombre)

    # Un premio cuyo sello es una palabra y no una imagen -"Architizer", "ARQ"-
    # guarda ese texto en el mismo campo, con el prefijo @texto:. Es la idea de
    # los @site: y @seed: que ya usan las galerias: el campo lleva una marca en
    # vez de una ruta. Evita una columna nueva para seis filas.
    clase_fila = ''
    if logo.startswith(TEXTO):
        logo_html = ('<div class="award-row__logo award-row__logo--plain">'
                     '<span class="award-platform">%s</span></div>'
                     % e(logo[len(TEXTO):]))
        # Las filas de ranking se publicaban con esta clase, que aclara el
        # resultado en gris: son reconocimientos y no premios ganados.
        clase_fila = ' award-row--recognition'
    elif logo:
        logo_html = ('<div class="award-row__logo"><img src="%s" width="400" height="300" '
                     'alt="" loading="lazy" decoding="async"></div>' % e(logo))
    else:
        # El hueco va vacio, no con el nombre repetido. En las filas historicas
        # el texto de la izquierda es la plataforma y el de la derecha el premio
        # completo, que son dos cosas distintas; cuando los dos salian del mismo
        # campo la fila quedaba diciendo "Casa FOA Casa FOA", que es lo que se
        # ve en el video del 16/10/2026.
        logo_html = '<div class="award-row__logo award-row__logo--vacio"></div>'

    descripcion = premio.get('descripcion') or ''
    obra_html = ''
    if obra and obra in slugs_publicados:
        obra_html = ('\n                  <span class="award-row__obra">'
                     '<a href="/proyectos/%s/">%s</a></span>'
                     % (e(obra), e(titulo_de_obra(obra))))
    return ('%s\n'
            '            <div class="award-row%s">\n'
            '              <div class="award-row__left">\n'
            '                %s\n'
            '                <div class="award-row__content">\n'
            '                  <div class="award-row__name">%s</div>\n'
            '                  <span class="award-row__desc">%s</span>%s\n'
            '                </div>\n'
            '              </div>\n'
            '              <div class="award-row__res">%s</div>\n'
            '              <div class="award-row__city">%s</div>\n'
            '            </div>\n'
            '            %s' % (FILA_INICIO % e(premio.get('id') or premio.get('nombre')),
                                clase_fila, logo_html, nombre, e(descripcion), obra_html,
                                e(premio.get('resultado')), e(premio.get('ciudad')),
                                FILA_FIN))


def bloque(premios, slugs_publicados):
    """Todo el listado: un bloque por año, del mas nuevo al mas viejo.

    Dentro de cada año manda el campo orden, que es el que el estudio mueve
    desde el panel con las flechas. Antes los premios del panel se agregaban
    sueltos a una pagina escrita a mano, asi que su orden no podia ganarle a
    ninguna fila historica: siempre salian ultimos.
    """
    grupos = {}
    for premio in premios:
        grupos.setdefault(int(premio.get('anio') or 0), []).append(premio)
    partes = []
    for anio in sorted(grupos, reverse=True):
        filas = sorted(grupos[anio],
                       key=lambda p: (int(p.get('orden') or 0),
                                      p.get('created_at') or ''))
        partes.append('          <div class="award-year-block" data-year="%d">\n'
                      '            <div class="press-year-head">%d</div>\n'
                      '%s\n'
                      '          </div>'
                      % (anio, anio,
                         '\n'.join(fila(p, slugs_publicados) for p in filas)))
    return '\n'.join(partes)


def filtros(premios):
    """Los botones de año, que salen del contenido y no de una lista a mano."""
    anios = sorted({int(p.get('anio') or 0) for p in premios}, reverse=True)
    return '\n'.join(
        '          <button class="filter-btn" data-year="%d">%d</button>' % (a, a)
        for a in anios if a)


_sembrados = None


def es_historico(premio):
    """Si este premio es uno de los que vivian escritos en premios/index.html.

    Su sello ya esta en la banda de la ficha desde siempre, puesto por el campo
    obras.premios y su catalogo de logos. Al pasarlos a la base, el paso que
    arma las bandas empezo a agregarlos otra vez, y como en la ficha figuran con
    otro nombre -"Architizer A+" contra "A+ Awards — Architizer", "SBID" contra
    "Society of British and International Interior Design (SBID)"- ninguna
    comparacion de texto los emparejaba: Movistar Arena, Manduca y Osten
    salieron publicadas con el mismo premio dos veces.

    Compararlos contra la lista de los que se sembraron es exacto y no depende
    de como este escrito el nombre en cada lado.
    """
    global _sembrados
    if _sembrados is None:
        _sembrados = set()
        if os.path.isfile(HISTORICOS):
            for viejo in json.load(io.open(HISTORICOS, encoding='utf-8')):
                _sembrados.add((int(viejo['anio']), normalizar(viejo['nombre'])))
    return (int(premio.get('anio') or 0),
            normalizar(premio.get('nombre'))) in _sembrados


def bloque_obras(premios, slugs_publicados):
    """Prepara los reconocimientos vinculados para la banda de cada ficha."""
    por_obra = {}
    for premio in premios:
        slug = (premio.get('obra_slug') or '').strip()
        if slug and slug in slugs_publicados and not es_historico(premio):
            por_obra.setdefault(slug, []).append(premio)
    return por_obra


def normalizar(texto):
    """Para comparar nombres de premio: sin acentos, sin signos, sin dobles espacios."""
    plano = unicodedata.normalize('NFD', (texto or '').strip().casefold())
    plano = ''.join(c for c in plano if unicodedata.category(c) != 'Mn')
    return ' '.join(re.sub(r'[^a-z0-9]+', ' ', plano).split())


def item_barra(premio, con_anio=False):
    """Una entrada de la banda de la ficha.

    El año se agrega solo cuando hace falta para distinguir: una obra que gano
    el mismo premio dos veces mostraba dos sellos identicos sin manera de saber
    cual es cual.
    """
    nombre = e(premio.get('nombre'))
    etiqueta = nombre
    if con_anio and premio.get('anio'):
        etiqueta = '%s %s' % (nombre, e(premio.get('anio')))
    logo = (premio.get('logo') or '').strip()
    if logo:
        visual = ('<img src="%s" alt="%s" loading="lazy" decoding="async">'
                  '<span>%s</span>' % (e(logo), etiqueta, etiqueta))
    else:
        visual = '<span>%s</span>' % etiqueta
    return ('          <a class="award-bar__item" href="/premios/" aria-label="Ver %s">'
            '%s</a>' % (etiqueta, visual))


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
            #
            # La comparacion es por igualdad del nombre normalizado y no por
            # subcadena. Con subcadena, "Casa FOA" tapaba a "Casa FOA — Jurado"
            # y cualquier premio cuyo nombre estuviera contenido en un sello
            # historico desaparecia de la ficha sin aviso.
            historicos = {normalizar(html.unescape(x)) for x in re.findall(
                r'<a class="award-bar__item[^>]*>.*?<span>(.*?)</span>.*?</a>',
                pagina, flags=re.S)}

            # Una obra puede tener varios premios, y puede tener el mismo premio
            # en años distintos: la clave lleva el año. Antes la clave era solo
            # el nombre, asi que una obra premiada dos veces por el mismo
            # concurso mostraba una sola entrada y perdia la otra.
            repetidos = {}
            for premio in relacionados:
                repetidos[normalizar(premio.get('nombre'))] = \
                    repetidos.get(normalizar(premio.get('nombre')), 0) + 1

            nuevos, puestos = [], set()
            for premio in relacionados:
                normalizado = normalizar(premio.get('nombre'))
                if not normalizado:
                    continue
                clave = (normalizado, str(premio.get('anio') or ''))
                if clave in puestos or normalizado in historicos:
                    continue
                nuevos.append(item_barra(premio, con_anio=repetidos[normalizado] > 1))
                puestos.add(clave)
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
        premios = sembrar_historicos(url, clave, premios)
        reponer_logos(url, clave, premios)
        bajar_logos(premios)
        normalizar_orden(url, clave, premios)
    except urllib.error.HTTPError as error:
        texto = error.read().decode('utf-8', 'replace')
        if error.code in (400, 404) and 'premios_panel' in texto:
            print('premios: migracion 0020 pendiente; se conserva el contenido actual')
            return 0
        raise

    # Desde que los premios viven en la base, premios/index.html llega al build
    # con el listado vacio. Entonces publicar sin filas no deja la pagina "como
    # estaba": la deja sin un solo premio. Mejor cortar el build y que siga en
    # linea la version anterior del sitio.
    if not premios:
        raise RuntimeError('la base no devolvio ningun premio publicado; '
                           'no se publica una pagina de premios vacia')
    # El listado entero y la barra de años se generan desde la base. Antes la
    # pagina traia los premios escritos a mano y el paso solo agregaba los del
    # panel, que es por lo que su orden nunca podia ganarles.
    pagina = re.sub(re.escape(INICIO) + r'.*?' + re.escape(FIN),
                    lambda _: INICIO + '\n' + bloque(premios, slugs_publicados)
                    + '\n          ' + FIN, pagina, count=1, flags=re.S)
    pagina = re.sub(re.escape(FILTROS_INICIO) + r'.*?' + re.escape(FILTROS_FIN),
                    lambda _: FILTROS_INICIO + '\n' + filtros(premios)
                    + '\n          ' + FILTROS_FIN, pagina, count=1, flags=re.S)
    io.open(PAGINA, 'w', encoding='utf-8', newline='\n').write(pagina)
    sincronizar_bandas(premios, slugs_publicados)
    print('premios: %d premios publicados en %d años'
          % (len(premios), len({p.get('anio') for p in premios})))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print('ERROR al sincronizar premios: %s' % error)
        sys.exit(1)
