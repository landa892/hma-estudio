# -*- coding: utf-8 -*-
"""Pone en cada ficha de obra los premios que la pagina /premios/ le atribuye.

   El cliente reviso el sitio y marco que las fichas se quedan cortas: "Osten
   tiene 3 premios, revisar", "Fogon tiene 3", "Mamba tiene 3", "Goodsten dos",
   "Movistar dos". Tenia razon en todos: la pagina de premios ya lo decia y las
   fichas mostraban menos o directamente ninguno.

   Pasaba porque las dos cosas se cargaron a mano y por separado. Aca la fuente
   pasa a ser una sola: /premios/ es la lista completa, y de ahi sale la barra
   de premios de cada ficha. Si manana se suma un premio a esa pagina y se
   vuelve a correr esto, la ficha se entera.

   Lo que NO decide este script: que premio gano cada obra. Eso vive en
   /premios/ y se edita ahi. Si una obra no figura, aca no aparece: es
   preferible una ficha sin premio que un premio atribuido a la obra
   equivocada.

       python docs/premios_en_fichas.py --verificar   # no escribe, compara
       python docs/premios_en_fichas.py
"""
import io
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREMIOS = os.path.join(RAIZ, 'premios', 'index.html')

# La barra va entre las fotos a lo ancho y la grilla "Todas las fotos", que es
# donde ya esta en las fichas que la tienen.
ANCLA = '\n    <section class="section no-border" id="galeria">'
BLOQUE = re.compile(r'(?s)\n    <section class="award-bar">.*?\n    </section>\n')


def premios_por_obra():
    """{slug: [(nombre, logo)]} leyendo la pagina de premios."""
    h = io.open(PREMIOS, encoding='utf-8').read()
    fuera = {}
    for fila in re.findall(
            r'(?s)<div class="award-row">.*?'
            r'(?=<div class="award-row">|</div>\s*</div>\s*</div>)', h):
        nom = re.search(r'award-row__name"><a[^>]*>(.*?)</a>', fila)
        logo = re.search(r'award-row__logo"><img src="([^"]+)"', fila)
        if not nom:
            continue
        nombre = re.sub(r'<[^>]+>', '', nom.group(1)).strip()
        for slug in set(re.findall(r'href="/proyectos/([^/]+)/"', fila)):
            lista = fuera.setdefault(slug, [])
            # La pagina tiene alguna fila repetida —Manduca aparece dos veces
            # con el mismo premio—; en la ficha se veria como dos logos iguales.
            if not any(n == nombre for n, _ in lista):
                lista.append((nombre, logo.group(1) if logo else ''))
    return fuera


def barra(premios):
    items = []
    for nombre, logo in premios:
        items.append(
            '          <a class="award-bar__item" href="/premios/" '
            'aria-label="Ver %s"><img src="%s" width="400" height="300" '
            'alt="%s" loading="lazy" decoding="async"><span>%s</span></a>'
            % (nombre, logo, nombre, nombre))
    return ('\n    <section class="award-bar">\n'
            '      <div class="container award-bar__inner">\n'
            '        <h2 class="award-bar__title">Premios y distinciones</h2>\n'
            '        <div class="award-bar__logos">\n%s\n        </div>\n'
            '      </div>\n'
            '    </section>\n' % '\n'.join(items))


def main(verificar):
    mapa = premios_por_obra()
    if not mapa:
        print('ERROR: no pude leer ningun premio de /premios/. No se toca nada.')
        return 1

    print('obras premiadas segun /premios/: %d' % len(mapa))

    cambiadas, avisos = [], []
    for slug, premios in sorted(mapa.items()):
        ruta = os.path.join(RAIZ, 'proyectos', slug, 'index.html')
        if not os.path.isfile(ruta):
            avisos.append('%s: la pagina no existe' % slug)
            continue

        antes = io.open(ruta, encoding='utf-8').read()
        nueva = barra(premios)

        if BLOQUE.search(antes):
            despues = BLOQUE.sub(lambda _: nueva, antes, count=1)
        elif ANCLA in antes:
            despues = antes.replace(ANCLA, nueva + ANCLA, 1)
        else:
            avisos.append('%s: no encuentro donde poner la barra' % slug)
            continue

        if despues == antes:
            continue
        cuantos = len(re.findall(r'award-bar__item', antes))
        cambiadas.append('%s (%d -> %d)' % (slug, cuantos, len(premios)))
        if not verificar:
            io.open(ruta, 'w', encoding='utf-8', newline='\n').write(despues)

    # Una ficha con barra de premios que la pagina de premios no respalda.
    sobran = []
    for slug in os.listdir(os.path.join(RAIZ, 'proyectos')):
        ruta = os.path.join(RAIZ, 'proyectos', slug, 'index.html')
        if os.path.isfile(ruta) and slug not in mapa:
            if BLOQUE.search(io.open(ruta, encoding='utf-8').read()):
                sobran.append(slug)

    print('fichas actualizadas: %d' % len(cambiadas))
    for c in cambiadas:
        print('  ' + c)
    if sobran:
        print('\nOJO — tienen barra de premios y /premios/ no les atribuye '
              'ninguno: %s' % ', '.join(sobran))
    if avisos:
        print('\navisos:')
        for a in avisos:
            print('  ' + a)
    if verificar:
        print('\n(--verificar: no se toco nada)')
    return 0


if __name__ == '__main__':
    sys.exit(main('--verificar' in sys.argv))
