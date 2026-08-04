# -*- coding: utf-8 -*-
"""Saca el texto repetido de las filas de foto.

Al entrar la memoria descriptiva, seis fichas quedaron diciendo dos veces
lo mismo: la memoria arriba, completa, y los mismos parrafos otra vez al
costado de cada foto. Aca se saca el texto de la fila y la foto pasa a
ocupar el ancho completo (.project-row--sola).

Solo se toca la fila cuyo texto coincide con un parrafo de la memoria. Las
filas con texto propio quedan como estan.

    python docs/memorias_dedup.py
"""
import io, os, re, glob, html, difflib

FILA = re.compile(
    r'(?s)<div class="project-row([^"]*)">\s*'
    r'(<div class="project-row__text">.*?</div>\s*<div class="project-row__photo">.*?</div>'
    r'|<div class="project-row__photo">.*?</div>\s*<div class="project-row__text">.*?</div>)'
    r'\s*</div>')
TEXTO = re.compile(r'(?s)<div class="project-row__text">.*?</div>')
FOTO = re.compile(r'(?s)<div class="project-row__photo">.*?</div>')
PARRAFO = re.compile(r'(?s)<p[^>]*>(.*?)</p>')


def plano(h):
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', '', h)).split())


def main():
    tocadas = total = 0
    for f in sorted(glob.glob(os.path.join('proyectos', '*', 'index.html'))):
        slug = f.replace(os.sep, '/').split('/')[1]
        h = io.open(f, encoding='utf-8').read()
        m = re.search(r'(?s)<div class="memoria-cuerpo.*?</div>\s*(?:<button|</div>)', h)
        if not m:
            continue
        mem = [plano(p) for p in PARRAFO.findall(m.group(0))]
        if not mem:
            continue
        sacadas = [0]

        def cambiar(mf):
            clases, cuerpo = mf.group(1), mf.group(2)
            if '--sola' in clases:
                return mf.group(0)
            mt = TEXTO.search(cuerpo)
            if not mt:
                return mf.group(0)
            t = plano(mt.group(0))
            if len(t) < 60:
                return mf.group(0)
            if not any(difflib.SequenceMatcher(None, t[:180], p[:180]).ratio() > .8
                       for p in mem):
                return mf.group(0)
            foto = FOTO.search(cuerpo)
            if not foto:
                return mf.group(0)
            sacadas[0] += 1
            # Se pierde --reverse: sin texto al lado, invertir no significa nada.
            return ('<div class="project-row project-row--sola reveal">\n'
                    '        %s\n      </div>' % foto.group(0))

        h2 = FILA.sub(cambiar, h)
        if sacadas[0]:
            io.open(f, 'w', encoding='utf-8').write(h2)
            print('  %-22s %d filas sin texto propio' % (slug, sacadas[0]))
            tocadas += 1
            total += sacadas[0]
    print('\nfichas tocadas: %d   filas convertidas: %d' % (tocadas, total))


if __name__ == '__main__':
    main()
