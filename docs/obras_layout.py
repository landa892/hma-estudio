# -*- coding: utf-8 -*-
"""Mantiene la caratula como primera imagen editorial de cada ficha.

El listado es la fuente definitiva de la portada: el panel lo actualiza cuando
el estudio elige otra foto. Este paso corre despues de los generadores del
panel y replica esa decision en la primera fila de la ficha, en Open Graph y,
por extension, en la composicion de memoria que arma ``scripts/main.js``.
"""
import io
import os
import re
import sys


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LISTADO = os.path.join(RAIZ, 'proyectos', 'index.html')


def atributo(etiqueta, nombre):
    m = re.search(r'\b%s="([^"]*)"' % re.escape(nombre), etiqueta)
    return m.group(1) if m else ''


def poner_atributo(etiqueta, nombre, valor):
    patron = r'(\b%s=")[^"]*(")' % re.escape(nombre)
    if re.search(patron, etiqueta):
        return re.sub(patron, r'\g<1>%s\2' % valor, etiqueta, count=1)
    return etiqueta[:-1] + ' %s="%s">' % (nombre, valor)


def ruta_sin_version(src):
    return re.split(r'[?#]', src, maxsplit=1)[0]


def portadas_del_listado():
    html = io.open(LISTADO, encoding='utf-8').read()
    portadas = {}
    patron = re.compile(
        r'<a href="/proyectos/([^/]+)/" class="project-card".*?</a>', re.S)
    for tarjeta in patron.finditer(html):
        img = re.search(r'<img\b[^>]*>', tarjeta.group(0))
        if img:
            portadas[tarjeta.group(1)] = img.group(0)
    return portadas


def preparar_portada(etiqueta):
    etiqueta = poner_atributo(etiqueta, 'loading', 'eager')
    etiqueta = poner_atributo(etiqueta, 'decoding', 'async')
    return poner_atributo(etiqueta, 'fetchpriority', 'high')


def preparar_secundaria(etiqueta):
    etiqueta = poner_atributo(etiqueta, 'loading', 'lazy')
    etiqueta = poner_atributo(etiqueta, 'decoding', 'async')
    return re.sub(r'\s+fetchpriority="[^"]*"', '', etiqueta)


def actualizar_ficha(slug, portada):
    ruta = os.path.join(RAIZ, 'proyectos', slug, 'index.html')
    if not os.path.isfile(ruta):
        return False
    html = io.open(ruta, encoding='utf-8').read()
    seccion = re.search(
        r'(?s)(\n    <section class="project-gallery">)(.*?)(\n    </section>)',
        html)
    if not seccion:
        return False

    cuerpo = seccion.group(2)
    imagenes = re.findall(r'<img\b[^>]*>', cuerpo)
    if not imagenes:
        return False

    src_portada = ruta_sin_version(atributo(portada, 'src'))
    secundarias = [img for img in imagenes
                   if ruta_sin_version(atributo(img, 'src')) != src_portada]
    ordenadas = [preparar_portada(portada)]
    ordenadas.extend(preparar_secundaria(img) for img in secundarias)
    ordenadas = ordenadas[:len(imagenes)]

    it = iter(ordenadas)
    cuerpo_nuevo = re.sub(r'<img\b[^>]*>', lambda _: next(it), cuerpo,
                          count=len(ordenadas))
    nuevo = html[:seccion.start(2)] + cuerpo_nuevo + html[seccion.end(2):]

    absoluta = 'https://estudiohma.com' + atributo(portada, 'src')
    nuevo = re.sub(r'(<meta property="og:image" content=")[^"]+',
                   r'\g<1>' + absoluta, nuevo, count=1)

    if nuevo == html:
        return False
    io.open(ruta, 'w', encoding='utf-8', newline='\n').write(nuevo)
    return True


def main():
    portadas = portadas_del_listado()
    cambiadas = sum(actualizar_ficha(slug, portada)
                    for slug, portada in portadas.items())
    print('fichas con portada editorial sincronizada: %d de %d' %
          (cambiadas, len(portadas)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
