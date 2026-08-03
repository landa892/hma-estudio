# -*- coding: utf-8 -*-
"""Control del espejo en ingles: busca castellano que haya quedado colado.

El reporte de faltantes de en_gen.py solo ve las frases que ninguna regla
cubre. Las que una regla generica traduce a medias ("See la prensa") pasan
sin aviso, porque la funcion devuelve texto igual. Esto revisa el resultado
final y marca el texto visible que todavia tiene palabras castellanas.

    python docs/en_control.py
"""
import io, re, glob, collections

PISTAS = re.compile(
    r'(?<![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])('
    r'el|la|los|las|del|una|unos|unas|con|para|por|desde|hasta|entre|sobre|'
    r'más|menos|obra|obras|proyecto|proyectos|notas|prensa|premios|año|años|'
    r'todas|todos|nuestro|nuestra|sus|este|esta|como|cuando|donde|'
    r'Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|'
    r'Noviembre|Diciembre'
    r')(?![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])')

# Palabras castellanas que en ingles son nombres propios o texto legitimo.
PERDONADOS = re.compile(r'^(Casa FOA|Plaza Mateo|Mercado Manduca|La Rural)$')


def main():
    hallazgos = collections.Counter()
    for f in sorted(glob.glob('en/**/*.html', recursive=True)):
        h = io.open(f, encoding='utf-8').read()
        # Fuera scripts, estilos, comentarios y el interior de los href.
        h = re.sub(r'(?s)<(script|style)\b.*?</\1>', ' ', h)
        h = re.sub(r'(?s)<!--.*?-->', ' ', h)
        h = re.sub(r'href="[^"]*"', ' ', h)
        for m in re.finditer(r'>([^<>]{3,240})<', h):
            t = ' '.join(m.group(1).split())
            if t and PISTAS.search(t) and not PERDONADOS.match(t):
                hallazgos[(f.replace(chr(92), '/'), t[:96])] += 1
    if not hallazgos:
        print('espejo limpio: no quedo castellano en el texto visible')
        return
    print('SOSPECHOSOS (%d):' % len(hallazgos))
    for (f, t), n in hallazgos.most_common():
        print('  %-34s %s' % (f[:34], t))


if __name__ == '__main__':
    main()
