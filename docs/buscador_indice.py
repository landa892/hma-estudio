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
          # segunda tanda: las tres que esperaban las fotos del Drive
          'oficina-casa-luna', 'ph-el-salvador', 'ph-loft-arias']
ARCHIVO = 'scripts/search-index.js'
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


def main():
    crudo = io.open(ARCHIVO, encoding='utf-8').read()
    cuerpo = crudo[crudo.index('['):crudo.rindex(']') + 1]
    indice = json.loads(cuerpo)
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
    proy = sorted([e for e in indice if e['tipo'] == 'Proyecto'],
                  key=lambda e: e['titulo'].lower())
    otras = [e for e in indice if e['tipo'] != 'Proyecto']
    salida = proy + otras
    io.open(ARCHIVO, 'w', encoding='utf-8').write(
        CABEZA + json.dumps(salida, ensure_ascii=False, indent=1) + ';\n')
    print('sumadas: %s' % (', '.join(puestas) or '—'))
    print('entradas totales: %d  (proyectos: %d)' % (len(salida), len(proy)))


if __name__ == '__main__':
    main()
