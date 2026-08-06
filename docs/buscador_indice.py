# -*- coding: utf-8 -*-
"""Suma las obras nuevas al indice del buscador.

El buscador de /buscar/ trabaja contra scripts/search-index.js, que es un
arreglo plano en el propio archivo. Las entradas nuevas se arman leyendo la
ficha ya generada, para que digan lo mismo que la pagina.

    python docs/buscador_indice.py
"""
import io, json, os, re, html

NUEVAS = ['abasto-patio-comidas', 'burger-7167', 'casa-olmo', 'clasico-quilmes',
          'elyaki', 'luccianos-olivos', 'malita', 'stella-artois-mercat',
          'the-birra',
          # segunda tanda: las cuatro que esperaban las fotos del Drive
          'oficina-casa-luna', 'ph-el-salvador', 'ph-loft-arias',
          'galeria-objeto-a']
ARCHIVO = 'scripts/search-index.js'
ARCHIVO_EN = 'scripts/search-index-en.js'
CABEZA = 'window.HMA_SEARCH_INDEX = '


def de_la_ficha(slug):
    h = io.open(os.path.join('proyectos', slug, 'index.html'), encoding='utf-8').read()
    g = lambda p: html.unescape((re.search(p, h, re.S) or [None, ''])[1]).strip()
    esp = dict(re.findall(r'<dt>(.*?)</dt><dd>(.*?)</dd>', h))
    esp = {html.unescape(k): html.unescape(v) for k, v in esp.items()}
    partes = [esp.get('Tipo', ''), esp.get('Ubicación', ''), esp.get('Superficie', ''),
              esp.get('Año', '')]
    return {
        'tipo': 'Proyecto',
        'titulo': g(r'<h1 class="display-2 mt-14">(.*?)</h1>'),
        'sub': g(r'<span class="eyebrow">(.*?)</span>'),
        'desc': ' · '.join(p for p in partes if p),
        'url': '/proyectos/%s/' % slug,
        'img': '/assets/gallery/%s/1.webp' % slug,
    }


def de_la_ficha_en(slug):
    p = os.path.join('en', 'projects', slug, 'index.html')
    if not os.path.isfile(p):
        return None
    h = io.open(p, encoding='utf-8').read()
    g = lambda patron: html.unescape((re.search(patron, h, re.S) or [None, ''])[1]).strip()
    esp = dict(re.findall(r'<dt>(.*?)</dt><dd>(.*?)</dd>', h))
    esp = {html.unescape(k): html.unescape(v) for k, v in esp.items()}
    partes = [esp.get('Type', ''), esp.get('Location', ''), esp.get('Area', ''),
              esp.get('Year', '')]
    return {
        'tipo': 'Project',
        'titulo': g(r'<h1 class="display-2 mt-14">(.*?)</h1>'),
        'sub': g(r'<span class="eyebrow">(.*?)</span>'),
        'desc': ' · '.join(p for p in partes if p),
        'url': '/en/projects/%s/' % slug,
        'img': '/assets/gallery/%s/1.webp' % slug,
    }


def leer_indice(archivo):
    crudo = io.open(archivo, encoding='utf-8').read()
    return json.loads(crudo[crudo.index('['):crudo.rindex(']') + 1])


def escribir_indice(archivo, indice, tipo):
    proy = sorted([e for e in indice if e['tipo'] == tipo],
                  key=lambda e: e['titulo'].lower())
    otras = [e for e in indice if e['tipo'] != tipo]
    salida = proy + otras
    io.open(archivo, 'w', encoding='utf-8').write(
        CABEZA + json.dumps(salida, ensure_ascii=False, indent=1) + ';\n')
    return salida


def main():
    indice = leer_indice(ARCHIVO)
    hay = {e['url'] for e in indice}
    puestas = []
    for slug in NUEVAS:
        u = '/proyectos/%s/' % slug
        if u in hay:
            continue
        e = de_la_ficha(slug)
        indice.append(e)
        puestas.append(e['titulo'])
    # Los proyectos van ordenados por titulo; el resto de las entradas
    # (paginas del sitio) se deja donde estaba.
    salida = escribir_indice(ARCHIVO, indice, 'Proyecto')
    print('sumadas: %s' % (', '.join(puestas) or '—'))
    print('entradas totales: %d  (proyectos: %d)' %
          (len(salida), sum(e['tipo'] == 'Proyecto' for e in salida)))


def main_en():
    """Completa el indice ingles una vez que en_gen creo las fichas espejo."""
    indice = leer_indice(ARCHIVO_EN)
    hay = {e['url'] for e in indice}
    puestas = []
    for slug in NUEVAS:
        u = '/en/projects/%s/' % slug
        if u in hay:
            continue
        e = de_la_ficha_en(slug)
        if not e:
            continue
        indice.append(e)
        hay.add(u)
        puestas.append(e['titulo'])
    salida = escribir_indice(ARCHIVO_EN, indice, 'Project')
    print('indice ingles: %s' % (', '.join(puestas) or '—'))
    print('entradas ingles: %d  (proyectos: %d)' %
          (len(salida), sum(e['tipo'] == 'Project' for e in salida)))


if __name__ == '__main__':
    main()
