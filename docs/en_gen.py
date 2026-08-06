# -*- coding: utf-8 -*-
"""Genera el espejo en ingles del sitio bajo /en/.

   El castellano sigue siendo la fuente: se toca solo para agregarle el boton
   de idioma y el hreflang. Todo /en/ se regenera de cero cada vez, asi que
   nunca hay que mantener dos sitios a mano: se edita el castellano y se
   vuelve a correr esto.
"""
import io, os, re, glob, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import en_dic3
import en_dic4
import en_dic5
import en_dic6
from en_rutas import a_ingles, a_castellano, reescribir_enlaces

ROOT = r'C:\Users\El Niño\Desktop\Trabajo para naza\hma-estudio'
SITIO = 'https://estudiohma.com'
tr = en_dic6.traducir

sin_traducir = []


def T(t):
    """Traduce respetando los espacios de los bordes."""
    izq = re.match(r'^\s*', t).group(0)
    der = re.search(r'\s*$', t).group(0)
    nucleo = t.strip()
    if not nucleo or not re.search(r'[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]', nucleo):
        return t
    r = tr(re.sub(r'\s+', ' ', nucleo))
    if r is None:
        sin_traducir.append(nucleo)
        return t
    return izq + r + der


# --- lo que no se toca: el contenido de <style> y <script> -------------------
INTOCABLE = re.compile(r'(<(style|script)\b[^>]*>.*?</\2>)', re.S)


def traducir_html(html):
    """El patron tiene dos grupos, asi que re.split devuelve, en ciclos de tres:
       texto, el bloque entero, el nombre de la etiqueta. Se traduce el texto,
       se copia el bloque tal cual y se descarta el nombre, que ya viene dentro
       del bloque. Contar mal este ciclo se come parrafos enteros sin avisar."""
    salida = []
    for i, parte in enumerate(INTOCABLE.split(html)):
        if i % 3 == 0:
            salida.append(_traducir_trozo(parte))
        elif i % 3 == 1:
            salida.append(parte)
    return ''.join(salida)


# data-mas y data-menos son los rotulos del boton "ver mas": el script los lee
# de aca, asi que si no se traducen el boton vuelve al castellano al tocarlo.
ATRIBUTOS = ('alt', 'aria-label', 'placeholder', 'data-mas', 'data-menos')

# el content de un meta solo se traduce si el meta es de texto para humanos:
# la politica de seguridad, robots o twitter:card no se tocan.
META_DE_TEXTO = re.compile(
    r'<meta\s+(?:name|property)="(description|keywords|og:title|og:description|'
    r'og:site_name|og:image:alt|twitter:title|twitter:description|twitter:image:alt)"'
    r'\s+content="([^"]*)"', re.I | re.S)


def _traducir_trozo(h):
    # nodos de texto: esto ya cubre <title>, porque su contenido es un nodo mas
    h = re.sub(r'>([^<>]+)<', lambda m: '>' + T(m.group(1)) + '<', h)
    # atributos visibles
    h = re.sub(r'\b(%s)="([^"]*)"' % '|'.join(ATRIBUTOS),
               lambda m: '%s="%s"' % (m.group(1), T(m.group(2))), h)
    # meta de texto
    h = META_DE_TEXTO.sub(
        lambda m: m.group(0).replace('content="%s"' % m.group(2),
                                     'content="%s"' % T(m.group(2))), h)
    return h


# --- boton de idioma ---------------------------------------------------------
def boton_idioma(destino, rotulo, titulo):
    return ('<a class="site-menu__icon-btn site-menu__lang" href="%s" '
            'hreflang="%s" aria-label="%s"><span>%s</span></a>'
            % (destino, 'en' if rotulo == 'EN' else 'es', titulo, rotulo))


ANCLA_CONTROLES = '<div class="site-menu__controls">'


def sacar_boton(html):
    """Se saca antes de traducir para que el generador sea repetible: si no, en
       la segunda corrida el boton "EN" de la pagina en castellano entraba al
       traductor como si fuera contenido."""
    return re.sub(r'\n?\s*<a class="site-menu__icon-btn site-menu__lang".*?</a>', '',
                  html, flags=re.S)


def poner_boton(html, destino, rotulo, titulo):
    html = sacar_boton(html)
    if ANCLA_CONTROLES not in html:
        return html
    return html.replace(
        ANCLA_CONTROLES,
        ANCLA_CONTROLES + '\n      ' + boton_idioma(destino, rotulo, titulo), 1)


def poner_hreflang(html, ruta_es, ruta_en):
    html = re.sub(r'\n?\s*<link rel="alternate" hreflang="[^"]*"[^>]*>', '', html)
    bloque = ('\n  <link rel="alternate" hreflang="es" href="%s%s">'
              '\n  <link rel="alternate" hreflang="en" href="%s%s">'
              '\n  <link rel="alternate" hreflang="x-default" href="%s%s">'
              % (SITIO, ruta_es, SITIO, ruta_en, SITIO, ruta_es))
    return html.replace('</head>', bloque + '\n</head>', 1)


# --- paginas -----------------------------------------------------------------
def ruta_de(p):
    r = '/' + p.replace(os.sep, '/')
    return r.replace('/index.html', '/') if r.endswith('index.html') else r


# La memoria descriptiva no se traduce palabra por palabra: el estudio la
# escribio en los dos idiomas por separado, y los parrafos no se
# corresponden uno a uno. Asi que el bloque entero se reemplaza por la
# version inglesa cuando existe. Las obras que no tienen memoria inglesa
# pierden el bloque en el espejo: es preferible a dejar castellano en una
# pagina en ingles, y quedan listadas al final para que el estudio las mande.
MEMORIAS_EN = {}
_ruta_mem = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'en_memorias.json')
if os.path.isfile(_ruta_mem):
    import json as _json
    MEMORIAS_EN = _json.load(io.open(_ruta_mem, encoding='utf-8'))

sin_memoria_en = []
BLOQUE_MEM = re.compile(
    r'(?s)\n    <section class="project-memoria">.*?\n    </section>\n')


MARCA_MEM = '<!--MEMORIA-EN-->'


def sacar_memoria(html_es):
    """Deja un marcador en lugar de la memoria, antes de traducir.

    Si el bloque llegara al traductor, sus parrafos apareceerian en el
    reporte de faltantes aunque despues se descarten.
    """
    return BLOQUE_MEM.sub('\n' + MARCA_MEM + '\n', html_es, count=1)


def poner_memoria_en(html_en, ruta_archivo):
    if MARCA_MEM not in html_en:
        return html_en
    partes = ruta_archivo.replace(chr(92), '/').split('/')
    slug = partes[1] if len(partes) > 2 and partes[0] == 'proyectos' else ''
    parrafos = MEMORIAS_EN.get(slug)
    if not parrafos:
        sin_memoria_en.append(slug or ruta_archivo)
        return html_en.replace('\n' + MARCA_MEM + '\n', '\n', 1)
    plegable = len(parrafos) > 2
    cuerpo = '\n'.join('          <p>%s</p>' % p.replace('&', '&amp;').replace('<', '&lt;')
                       for p in parrafos)
    boton = ''
    if plegable:
        boton = ('\n        <button class="memoria-more gallery-more" type="button"\n'
                 '          data-mas="Keep reading" data-menos="Read less"\n'
                 '          aria-expanded="false">Keep reading</button>')
    nuevo = ('\n    <section class="project-memoria">\n'
             '      <div class="container">\n'
             '        <div class="memoria-cuerpo%s reveal">\n%s\n        </div>%s\n'
             '      </div>\n'
             '    </section>\n' % ('' if plegable else ' is-open', cuerpo, boton))
    return html_en.replace('\n' + MARCA_MEM + '\n', nuevo, 1)


def main():
    os.chdir(ROOT)
    if os.path.isdir('en'):
        shutil.rmtree('en')

    paginas = sorted([p for p in glob.glob('**/index.html', recursive=True)
                      if 'node_modules' not in p and not p.startswith(('docs', 'en'))]
                     + ['404.html'])

    hechas = []
    for p in paginas:
        s = io.open(p, encoding='utf-8').read()
        ruta_es = ruta_de(p)
        ruta_en = a_ingles(ruta_es)

        # --- version en ingles ---
        en = poner_memoria_en(traducir_html(sacar_memoria(sacar_boton(s))), p)
        en = reescribir_enlaces(en)
        en = en.replace('<html lang="es"', '<html lang="en"', 1)
        en = re.sub(r'(<meta property="og:locale" content=")[^"]*(")', r'\1en_US\2', en)
        en = re.sub(r'(<link rel="canonical" href="[^"]*?)(")',
                    lambda m: '<link rel="canonical" href="%s%s"' % (SITIO, ruta_en), en)
        en = poner_hreflang(en, ruta_es, ruta_en)
        en = poner_boton(en, ruta_es, 'ES', 'Ver esta página en español')
        # el buscador tiene su propio indice traducido, con las urls de /en/
        en = en.replace('/scripts/search-index.js', '/scripts/search-index-en.js')

        destino = os.path.join('en', ruta_en[4:].lstrip('/'))
        if ruta_en.endswith('/'):
            destino = os.path.join(destino, 'index.html')
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        io.open(destino, 'w', encoding='utf-8').write(en)

        # --- el castellano solo suma boton y hreflang ---
        es = poner_hreflang(s, ruta_es, ruta_en)
        es = poner_boton(es, ruta_en, 'EN', 'View this page in English')
        if es != s:
            io.open(p, 'w', encoding='utf-8').write(es)

        hechas.append((ruta_es, ruta_en))

    print('paginas espejadas: %d' % len(hechas))
    if sin_traducir:
        from collections import Counter
        c = Counter(sin_traducir)
        print('\nSIN TRADUCIR (%d distintas):' % len(c))
        for t, n in c.most_common():
            print('  %3d x %s' % (n, t[:160]))
        # Lista completa y sin recortar, para poder pasarla al diccionario.
        import json
        io.open('docs/en_faltantes.json', 'w', encoding='utf-8').write(
            json.dumps([t for t, _ in c.most_common()], ensure_ascii=False, indent=1))
    else:
        print('sin faltantes: todo el texto visible quedo traducido')
    if sin_memoria_en:
        print('\nOBRAS SIN MEMORIA EN INGLES (%d) — el espejo va sin ese bloque:'
              % len(sin_memoria_en))
        print('  ' + ', '.join(sorted(sin_memoria_en)))
    # Las fichas en ingles ya existen en este punto, asi que tambien se puede
    # completar su indice de busqueda con las obras dadas de alta.
    import buscador_indice
    buscador_indice.main_en()
    return hechas


if __name__ == '__main__':
    main()
