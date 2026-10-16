# -*- coding: utf-8 -*-
"""Saca de premios/index.html los premios historicos, para que los administre el panel.

El estudio lo pidio el 16/10/2026 en audio: "estaria bueno si nosotros tambien
podemos editar eso... si yo quiero poner otro arriba pueda hacerlo". Hoy los
premios viejos viven escritos en el HTML y solo se pueden tocar a mano, asi que
el orden del panel nunca puede ganarles: siempre salen primero dentro de su año.

Este script los pasa a docs/premios_historicos.json, con los mismos campos que
la tabla premios_panel. De ahi los siembra el build -como ya se hace con las
galerias y con las notas de prensa- y desde ese momento la pagina entera se
arma desde la base y todo es editable.

Corre una sola vez, en la maquina del desarrollador, y su salida va al
repositorio.

    python docs/premios_extraer.py
"""
import io
import json
import os
import re
import sys
from html import unescape

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINA = os.path.join(RAIZ, 'premios', 'index.html')
DESTINO = os.path.join(RAIZ, 'docs', 'premios_historicos.json')

# Los premios cuyo sello es una palabra y no una imagen -"Architizer", "ARQ"-
# se guardan con este prefijo en el campo logo. Es la misma idea que los
# @site: y @seed: que ya usan las galerias: el campo lleva una marca en vez de
# una ruta, y quien arma el HTML decide que hacer con ella. Evita agregar una
# columna a la tabla solo para seis filas.
TEXTO = '@texto:'


def limpiar(html_crudo):
    """El texto visible de un trozo de HTML."""
    return unescape(re.sub(r'<[^>]+>', '', html_crudo or '')).strip()


def cierre_de(texto, desde):
    """Indice del </div> que cierra el <div> que abre en `desde`."""
    nivel = 0
    for marca in re.finditer(r'<(/?)div\b[^>]*>', texto[desde:]):
        if marca.group(1):
            nivel -= 1
            if nivel == 0:
                return desde + marca.end()
        else:
            nivel += 1
    raise SystemExit('no encuentro el cierre de una fila')


def main():
    pagina = io.open(PAGINA, encoding='utf-8').read()
    salida = []

    for bloque in re.finditer(
            r'<div class="award-year-block" data-year="(\d{4})">', pagina):
        anio = int(bloque.group(1))
        fin = cierre_de(pagina, bloque.start())
        cuerpo = pagina[bloque.start():fin]

        # Tras "award-row" tiene que venir la comilla o un espacio: sin eso el
        # patron tambien agarraba los div de adentro -award-row__left,
        # award-row__content- y salian 117 filas en vez de 39.
        for fila in re.finditer(r'[ \t]*<div class="award-row(?: ([^"]*))?">', cuerpo):
            trozo = cuerpo[fila.start():cierre_de(cuerpo, fila.start())]
            clases = fila.group(1) or ''

            logo = ''
            imagen = re.search(r'award-row__logo"><img src="([^"]+)"', trozo)
            if imagen:
                logo = imagen.group(1)
            else:
                plano = re.search(r'<span class="award-platform">(.*?)</span>', trozo)
                if plano:
                    logo = TEXTO + limpiar(plano.group(1))

            nombre = re.search(r'<div class="award-row__name">(.*?)</div>', trozo, re.S)
            enlace = re.search(r'<div class="award-row__name"><a href="([^"]+)"', trozo)
            desc = re.search(r'<span class="award-row__desc">(.*?)</span>', trozo, re.S)
            obra = re.search(r'award-row__obra"[^>]*href="/proyectos/([^/"]+)/', trozo)
            if not obra:
                obra = re.search(r'<span class="award-row__obra">'
                                 r'<a href="/proyectos/([^/"]+)/', trozo)
            resultado = re.search(r'<div class="award-row__res">(.*?)</div>', trozo, re.S)
            ciudad = re.search(r'<div class="award-row__city">(.*?)</div>', trozo, re.S)

            salida.append({
                'anio': anio,
                'orden': len([x for x in salida if x['anio'] == anio]),
                'nombre': limpiar(nombre.group(1)) if nombre else '',
                'resultado': limpiar(resultado.group(1)) if resultado else '',
                'ciudad': limpiar(ciudad.group(1)) if ciudad else '',
                'descripcion': limpiar(desc.group(1)) if desc else '',
                'enlace': enlace.group(1) if enlace else '',
                'obra_slug': obra.group(1) if obra else '',
                'logo': logo,
                'reconocimiento': 'award-row--recognition' in clases,
            })

    sin_nombre = [p for p in salida if not p['nombre']]
    if sin_nombre:
        raise SystemExit('hay %d filas sin nombre; revisar el parseo'
                         % len(sin_nombre))

    io.open(DESTINO, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(salida, ensure_ascii=False, indent=1) + '\n')

    print('premios historicos extraidos: %d' % len(salida))
    print('  con sello de imagen   : %d'
          % sum(1 for p in salida if p['logo'] and not p['logo'].startswith(TEXTO)))
    print('  con sello de texto    : %d'
          % sum(1 for p in salida if p['logo'].startswith(TEXTO)))
    print('  sin sello             : %d' % sum(1 for p in salida if not p['logo']))
    print('  con obra vinculada    : %d' % sum(1 for p in salida if p['obra_slug']))
    print('  con enlace            : %d' % sum(1 for p in salida if p['enlace']))
    print('  marcados reconocimiento: %d' % sum(1 for p in salida if p['reconocimiento']))
    print('  años                  : %s'
          % ' '.join(str(a) for a in sorted({p['anio'] for p in salida}, reverse=True)))
    print('\nescrito en docs/premios_historicos.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
