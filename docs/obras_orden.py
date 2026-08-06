# -*- coding: utf-8 -*-
"""Ordena el listado de proyectos por año, del mas nuevo al mas viejo.

Estaba alfabetico, que no dice nada: quien entra quiere ver primero lo
ultimo. El año sale del propio listado, del ultimo dato de cada tarjeta.

Los rangos ("2018-2022", "2015-2023") se ordenan por su año final, que es
cuando el trabajo se termino. A igual año se desempata por nombre, para que
el orden sea siempre el mismo y el archivo no cambie sin motivo.

    python docs/obras_orden.py
"""
import io, re, html

# La sangria del listado es despareja: parte de las tarjetas arranca en la
# columna cero y parte con diez espacios. El patron la acepta como venga y
# la salida se normaliza a diez.
def patrones_de(route):
    return {
        'project-card': re.compile(
            r'(?s)[ \t]*<a href="/%s/[^"]+/" class="project-card".*?</a>\n'
            % route),
        'project-list-row': re.compile(
            r'(?s)[ \t]*<a href="/%s/[^"]+/" class="project-list-row".*?</a>\n'
            % route),
    }


def sangrar(bloque):
    lineas = [l.strip() for l in bloque.rstrip('\n').split('\n')]
    salida = []
    for i, l in enumerate(lineas):
        salida.append(('          ' if i == 0 or i == len(lineas) - 1
                       else '            ') + l)
    return '\n'.join(salida) + '\n'


def anio_de(bloque):
    """El año es el ultimo <span> de la fila de datos."""
    spans = re.findall(r'<span>(.*?)</span>', bloque)
    for s in reversed(spans):
        m = re.findall(r'(19|20)(\d{2})', html.unescape(s))
        if m:
            return max(int(a + b) for a, b in m)
    return 0


def nombre_de(bloque):
    m = re.search(r'class="(?:p-name|plr-name)">(.*?)<', bloque)
    return html.unescape(m.group(1)).lower() if m else ''


def ordenar(p, route):
    h = io.open(p, encoding='utf-8').read()
    patterns = patrones_de(route)
    resumen = []
    for clase, patron in patterns.items():
        bloques = patron.findall(h)
        if not bloques:
            raise SystemExit('no se encontraron bloques de %s' % clase)
        ordenados = [sangrar(b) for b in
                     sorted(bloques, key=lambda b: (-anio_de(b), nombre_de(b)))]
        # Se reemplaza cada bloque por el que corresponde en el orden nuevo.
        it = iter(ordenados)
        h = patron.sub(lambda _: next(it), h)
        resumen.append('%s: %d ordenados' % (clase, len(bloques)))
    io.open(p, 'w', encoding='utf-8').write(h)
    for r in resumen:
        print('  ' + r)
    primeros = patterns['project-card'].findall(h)[:6]
    print('\nprimeros de %s:' % p)
    for b in primeros:
        print('   %-28s %d' % (nombre_de(b), anio_de(b)))


def main():
    ordenar('proyectos/index.html', 'proyectos')
    ordenar('en/projects/index.html', 'en/projects')


if __name__ == '__main__':
    main()
