# -*- coding: utf-8 -*-
"""Encuentra las fotos repetidas de cada galeria y deja la lista en un JSON.

El cliente marco doce obras con "foto repetida". Revisadas las 61 aparecieron
dos causas distintas:

  1. La portada vuelve a aparecer dentro de la galeria. Pasa en 45 de 56 obras
     con portada, y explica once de las doce que marco: la ficha abre con la
     portada a lo ancho y la misma imagen reaparece mas abajo en la grilla.
     "Esta foto esta repetida, al principio y al final", dijo de IOL.

  2. La misma foto cargada dos veces dentro de la galeria, con distinto peso.

  3. Un plano que esta en assets/planos/ y ademas suelto en la galeria, con lo
     cual la ficha lo muestra dos veces: en la grilla y en el bloque de planos.

Las dos se le escapaban al deduplicador de panel_galerias.py, que compara por
SHA1: son la misma imagen guardada dos veces, asi que los bytes no coinciden.
Aca se comparan las imagenes, no los archivos.

Corre en la maquina del desarrollador, no en el build: necesita Pillow para
abrir los .webp, y el build de Vercel no lo tiene. Por eso el resultado viaja
como dato -docs/galeria_repetidas.json- y panel_galerias.py solo lo lee.

    python docs/galeria_repetidas.py             # reescribe el JSON
    python docs/galeria_repetidas.py --verificar # no escribe, solo informa
"""
import io
import json
import os
import re
import sys

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GALERIAS = os.path.join(RAIZ, 'assets', 'gallery')
PORTADAS = os.path.join(RAIZ, 'assets', 'covers')
SALIDA = os.path.join(RAIZ, 'docs', 'galeria_repetidas.json')

# Dos imagenes distintas de una misma obra comparten encuadre, luz y paleta, y
# rondan 0.6-0.9. Recien arriba de 0.99 es la misma toma reguardada.
UMBRAL = 0.99
# Contra un plano el listón baja: es el mismo dibujo reguardado en otra medida
# y da 0.977, pero dos planos distintos de una misma obra -planta y corte- no
# pasan de 0.32, asi que no hay riesgo de confundirlos.
UMBRAL_PLANO = 0.95
LADO = 16


def firma(ruta):
    """Version chica y normalizada de la imagen, para comparar contenido."""
    try:
        imagen = Image.open(ruta).convert('L').resize((LADO, LADO), Image.LANCZOS)
    except Exception:
        return None
    puntos = list(imagen.getdata())
    media = sum(puntos) / len(puntos)
    desvio = (sum((v - media) ** 2 for v in puntos) / len(puntos)) ** 0.5 or 1.0
    return [(v - media) / desvio for v in puntos]


def parecido(a, b):
    return sum(x * y for x, y in zip(a, b)) / len(a)


def orden_natural(nombre):
    m = re.match(r'^(\d+)', nombre)
    return (0, int(m.group(1))) if m else (1, nombre)


def repetidas_de(slug):
    """Nombres de archivo que repiten la portada o una foto anterior."""
    carpeta = os.path.join(GALERIAS, slug)
    if not os.path.isdir(carpeta):
        return []

    nombres = sorted((n for n in os.listdir(carpeta) if n.endswith('.webp')),
                     key=orden_natural)

    # Entran primero la portada y los planos: son los que la ficha muestra
    # aparte, asi que si una foto de la galeria repite alguno, la que sobra es
    # la de la galeria. Los planos duplicados adentro de la galeria hacian que
    # el mismo plano saliera dos veces en la misma pagina.
    vistas = []
    portada = os.path.join(PORTADAS, slug + '.webp')
    if os.path.isfile(portada):
        f = firma(portada)
        if f:
            vistas.append((f, UMBRAL))
    planos = os.path.join(RAIZ, 'assets', 'planos', slug)
    if os.path.isdir(planos):
        for nombre in sorted(os.listdir(planos)):
            if not nombre.endswith('.webp'):
                continue
            f = firma(os.path.join(planos, nombre))
            if f:
                vistas.append((f, UMBRAL_PLANO))

    sobran = []
    for nombre in nombres:
        actual = firma(os.path.join(carpeta, nombre))
        if actual is None:
            continue
        if any(parecido(actual, vista) > tope for vista, tope in vistas):
            sobran.append(nombre)
        else:
            vistas.append((actual, UMBRAL))
    return sobran


def main(verificar):
    mapa = {}
    for slug in sorted(os.listdir(GALERIAS)):
        if not os.path.isdir(os.path.join(GALERIAS, slug)):
            continue
        sobran = repetidas_de(slug)
        if sobran:
            mapa[slug] = sobran

    total = sum(len(v) for v in mapa.values())
    print('obras con fotos repetidas: %d' % len(mapa))
    print('fotos que se dejan de mostrar: %d' % total)
    for slug, sobran in sorted(mapa.items()):
        print('  %-24s %s' % (slug, ', '.join(sobran)))

    if verificar:
        anterior = {}
        if os.path.isfile(SALIDA):
            anterior = json.load(io.open(SALIDA, encoding='utf-8'))
        print('\n(--verificar: no se escribio nada)')
        return 0 if anterior == mapa else 1

    io.open(SALIDA, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(mapa, ensure_ascii=False, indent=1, sort_keys=True) + '\n')
    print('\nescrito %s' % os.path.relpath(SALIDA, RAIZ))
    return 0


if __name__ == '__main__':
    sys.exit(main('--verificar' in sys.argv))
