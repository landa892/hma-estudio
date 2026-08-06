# -*- coding: utf-8 -*-
"""Da de alta la memoria descriptiva de una obra, en castellano y en ingles.

El castellano entra al HTML de la obra como <section class="project-memoria">
justo antes de la galeria. El ingles no se traduce: el estudio lo escribe
aparte, asi que se guarda en docs/en_memorias.json y en_gen lo inyecta al
regenerar el espejo.

Los textos se leen de docs/memorias_drive/<slug>.txt, con este formato:

    <parrafos en castellano, uno por linea, lineas vacias ignoradas>
    ---EN---
    <parrafos en ingles, idem; el bloque entero es opcional>

Uso:  python docs/memorias_alta.py [slug ...]     (sin slugs: todos los .txt)
"""
import io, os, re, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUENTE = os.path.join(ROOT, 'docs', 'memorias_drive')
JSON_EN = os.path.join(ROOT, 'docs', 'en_memorias.json')

ANCLA = '    <section class="project-gallery">'
YA_ESTA = '<section class="project-memoria">'


def escapar(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def bloque_es(parrafos):
    """Mismo molde que en_gen.poner_memoria_en, pero en castellano.

    Con dos parrafos o menos no vale la pena plegar el texto: se muestra
    entero y el boton no aparece.
    """
    plegable = len(parrafos) > 2
    cuerpo = '\n'.join('          <p>%s</p>' % escapar(p) for p in parrafos)
    boton = ''
    if plegable:
        boton = ('\n        <button class="memoria-more gallery-more" type="button"\n'
                 '          data-mas="Seguir leyendo" data-menos="Leer menos"\n'
                 '          aria-expanded="false">Seguir leyendo</button>')
    return ('    <section class="project-memoria">\n'
            '      <div class="container">\n'
            '        <div class="memoria-cuerpo%s reveal">\n%s\n        </div>%s\n'
            '      </div>\n'
            '    </section>\n\n' % ('' if plegable else ' is-open', cuerpo, boton))


def leer_fuente(slug):
    ruta = os.path.join(FUENTE, slug + '.txt')
    texto = io.open(ruta, encoding='utf-8').read()
    partes = re.split(r'^---EN---\s*$', texto, maxsplit=1, flags=re.M)
    def parrafos(t):
        return [p.strip() for p in t.strip().split('\n') if p.strip()]
    return parrafos(partes[0]), parrafos(partes[1]) if len(partes) > 1 else []


def main(slugs):
    if not slugs:
        slugs = sorted(f[:-4] for f in os.listdir(FUENTE) if f.endswith('.txt'))

    en_todas = {}
    if os.path.isfile(JSON_EN):
        en_todas = json.load(io.open(JSON_EN, encoding='utf-8'))

    for slug in slugs:
        pagina = os.path.join(ROOT, 'proyectos', slug, 'index.html')
        if not os.path.isfile(pagina):
            print('  [!] no existe la pagina de %s' % slug)
            continue
        es, en = leer_fuente(slug)
        if not es:
            print('  [!] %s: la memoria en castellano vino vacia' % slug)
            continue

        html = io.open(pagina, encoding='utf-8').read()
        if YA_ESTA in html:
            print('  [=] %s ya tenia memoria, se deja como estaba' % slug)
        elif ANCLA not in html:
            print('  [!] %s: no aparece la galeria, no se donde insertarla' % slug)
            continue
        else:
            io.open(pagina, 'w', encoding='utf-8').write(
                html.replace(ANCLA, bloque_es(es) + ANCLA, 1))
            print('  [+] %s: %d parrafos en castellano' % (slug, len(es)))

        if en:
            en_todas[slug] = en
            print('      + %d parrafos en ingles' % len(en))

    json.dump(en_todas, io.open(JSON_EN, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1, sort_keys=True)
    print('en_memorias.json: %d obras' % len(en_todas))


if __name__ == '__main__':
    main(sys.argv[1:])
