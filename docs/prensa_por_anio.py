# -*- coding: utf-8 -*-
"""Agrupa las notas online por año, con un rotulo por grupo.

El estudio las queria "por carpeta segun los años": la lista era plana y con
catorce entradas costaba ver donde terminaba un año y empezaba el siguiente.
El orden ya venia de mas nuevo a mas viejo y no se toca.

    python docs/prensa_por_anio.py
"""
import io, os, re

RUTA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'prensa', 'index.html')

FEED = re.compile(r'<div class="press-feed[^"]*"[^>]*>')
# Cada fila abre y cierra varios <div> anidados, asi que no sirve cortar en el
# primer </div>: hay que contar la profundidad. Con un .*? no perezoso se
# perdia una fila por corrida.
ETIQUETA = re.compile(r'<(/?)div\b[^>]*>')


def filas_de(cuerpo):
    """Parte el cuerpo del feed en filas completas, respetando el anidamiento."""
    filas, inicio, nivel = [], None, 0
    for m in ETIQUETA.finditer(cuerpo):
        cierra = bool(m.group(1))
        if inicio is None:
            if not cierra and 'class="press-row"' in m.group(0):
                inicio, nivel = m.start(), 1
            continue
        nivel += -1 if cierra else 1
        if nivel == 0:
            filas.append(cuerpo[inicio:m.end()])
            inicio = None
    return filas


def cuerpo_del_feed(h):
    """Devuelve (desde, hasta) del contenido del contenedor de notas.

    Se cuenta la profundidad en vez de buscar el primer </div>: el feed tiene
    catorce filas anidadas y cortar en el primer cierre se comia la ultima.
    """
    m = FEED.search(h)
    if not m:
        raise SystemExit('no encuentro la lista de notas online')
    nivel = 1
    for t in ETIQUETA.finditer(h, m.end()):
        nivel += -1 if t.group(1) else 1
        if nivel == 0:
            return m.end(), t.start()
    raise SystemExit('el contenedor de notas no cierra')


def main():
    h = io.open(RUTA, encoding='utf-8').read()
    desde, hasta = cuerpo_del_feed(h)
    cuerpo = h[desde:hasta]
    if 'pr-anio' in cuerpo:
        print('ya estaba agrupada')
        return

    filas = filas_de(cuerpo)
    if len(filas) != cuerpo.count('class="press-row"'):
        raise SystemExit('lei %d filas de %d: no las toco'
                         % (len(filas), cuerpo.count('class="press-row"')))

    salida, anio_actual = [], None
    for fila in filas:
        fecha = re.search(r'class="pr-date">(.*?)</div>', fila, re.S)
        anio = re.search(r'(?:19|20)\d{2}', fecha.group(1) if fecha else '')
        anio = anio.group(0) if anio else 'Sin año'
        if anio != anio_actual:
            anio_actual = anio
            salida.append('            <div class="pr-anio">%s</div>' % anio)
        salida.append('            ' + fila.strip())

    nuevo = '\n' + '\n'.join(salida) + '\n          '
    io.open(RUTA, 'w', encoding='utf-8').write(h[:desde] + nuevo + h[hasta:])
    print('notas: %d   años: %d'
          % (len(filas), sum(1 for x in salida if 'pr-anio' in x)))


if __name__ == '__main__':
    main()
