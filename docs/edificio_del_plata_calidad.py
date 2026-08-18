# -*- coding: utf-8 -*-
"""Sincroniza la seleccion de fotos de Edificio del Plata con el Drive."""
import io
import json
import os
import re

from PIL import Image


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = 'edificio-del-plata'
VERSION = '20260818'
TOTAL = 18
PORTADA = '/assets/covers/%s.webp' % SLUG
DATOS = os.path.join(RAIZ, 'docs', 'panel_datos.json')
FICHA = os.path.join(RAIZ, 'proyectos', SLUG, 'index.html')
GALERIA = os.path.join(RAIZ, 'assets', 'gallery', SLUG)


def medidas(numero):
    ruta = os.path.join(GALERIA, '%d.webp' % numero)
    if not os.path.isfile(ruta):
        raise SystemExit('falta %s' % ruta)
    with Image.open(ruta) as imagen:
        return imagen.size


def actualizar_datos():
    obras = json.load(io.open(DATOS, encoding='utf-8'))
    obra = next((item for item in obras if item['slug'] == SLUG), None)
    if not obra:
        raise SystemExit('%s no figura en panel_datos.json' % SLUG)
    obra['portada'] = PORTADA
    obra['galeria'] = ['%d.webp' % numero for numero in range(1, TOTAL + 1)]
    io.open(DATOS, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(obras, ensure_ascii=False, indent=1) + '\n')


def actualizar_etiqueta(match):
    numero = int(match.group(1))
    ancho, alto = medidas(numero)
    etiqueta = match.group(0)
    etiqueta = re.sub(
        r'(src="/assets/gallery/%s/%d\.webp)(?:\?[^\"]*)?(\")' % (SLUG, numero),
        r'\g<1>?v=%s\2' % VERSION,
        etiqueta,
        count=1,
    )
    etiqueta = re.sub(r'\bwidth="\d+"', 'width="%d"' % ancho, etiqueta, count=1)
    etiqueta = re.sub(r'\bheight="\d+"', 'height="%d"' % alto, etiqueta, count=1)
    return etiqueta


def actualizar_ficha():
    html = io.open(FICHA, encoding='utf-8').read()
    html = re.sub(
        r'\s*<figure class="gallery-grid__item[^\"]*"><img '
        r'src="/assets/gallery/%s/(?:19|20)\.webp[^>]*></figure>' % SLUG,
        '',
        html,
    )
    html = re.sub(
        r'<img\b[^>]*src="/assets/gallery/%s/(\d+)\.webp(?:\?[^\"]*)?"[^>]*>' % SLUG,
        actualizar_etiqueta,
        html,
    )
    html = html.replace('data-total="20"', 'data-total="18"')
    html = html.replace('Ver las 20 fotos', 'Ver las 18 fotos')
    io.open(FICHA, 'w', encoding='utf-8', newline='\n').write(html)


def main():
    dimensiones = [medidas(numero) for numero in range(1, TOTAL + 1)]
    actualizar_datos()
    actualizar_ficha()
    altas = sum(1 for ancho, alto in dimensiones if ancho > 800)
    print('%s: %d fotos, %d en alta resolucion' % (SLUG, TOTAL, altas))


if __name__ == '__main__':
    main()
