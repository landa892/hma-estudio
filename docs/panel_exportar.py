# -*- coding: utf-8 -*-
"""Saca las 61 obras del sitio a datos, para poder cargarlas en el panel.

Es el paso previo a que el sitio se genere desde la base: primero hay que
llevar a la base lo que hoy vive escrito en el HTML. Se lee de las paginas
mismas y no del WordPress viejo ni del Drive, porque el sitio es lo unico que
tiene todas las correcciones acumuladas.

Escribe docs/panel_datos.json. De ahi salen despues el SQL de carga y la
comparacion contra las paginas actuales.

    python docs/panel_exportar.py
"""
import io, json, os, re, glob

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ESTADOS = {
    'Obra concluida': 'concluida',
    'Obra recientemente inaugurada': 'concluida',
    'Proyecto en proceso': 'en_progreso',
    'Proyecto': 'en_proyecto',
    'Obra': 'concluida',
}


def limpiar(t):
    t = re.sub(r'<br\s*/?>', '\n', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = (t.replace('&amp;', '&').replace('&nbsp;', ' ')
          .replace('&lt;', '<').replace('&gt;', '>'))
    lineas = [re.sub(r'[ \t]+', ' ', x).strip() for x in t.split('\n')]
    return '\n'.join(x for x in lineas if x).strip()


def ficha(html):
    """Los pares <dt>rotulo</dt><dd>valor</dd> de la ficha tecnica."""
    datos = {}
    for m in re.finditer(r'<dt>(.*?)</dt>\s*<dd>(.*?)</dd>', html, re.S):
        datos[limpiar(m.group(1))] = limpiar(m.group(2))
    return datos


def memoria(html):
    """Los parrafos del bloque de memoria, en orden."""
    m = re.search(r'(?s)<div class="memoria-cuerpo[^"]*"[^>]*>(.*?)</div>', html)
    if not m:
        return None
    parrafos = [limpiar(p) for p in re.findall(r'<p>(.*?)</p>', m.group(1), re.S)]
    parrafos = [p for p in parrafos if p]
    return '\n\n'.join(parrafos) or None


def tarjetas():
    """Categoria, estado, bajada y orden salen del listado, no de la ficha.

    La ficha de la obra no dice a que filtro pertenece: eso vive como atributo
    de la tarjeta del listado, y el orden en que aparecen ahi es el orden que
    el estudio eligio.
    """
    h = io.open(os.path.join(RAIZ, 'proyectos', 'index.html'), encoding='utf-8').read()
    fuera = {}
    patron = re.compile(
        r'<a href="/proyectos/(?P<slug>[a-z0-9-]+)/"[^>]*class="project-card"'
        r'(?P<attrs>[^>]*)>(?P<cuerpo>.*?)</a>', re.S)
    for i, m in enumerate(patron.finditer(h)):
        attrs = m.group('attrs')
        cuerpo = m.group('cuerpo')
        cat = re.search(r'data-cat="([^"]*)"', attrs)
        est = re.search(r'data-estado="([^"]*)"', attrs)
        premio = re.search(r'class="p-awards">(.*?)</div>', cuerpo, re.S)
        fuera[m.group('slug')] = {
            'categoria': cat.group(1) if cat else None,
            'estado_tarjeta': est.group(1) if est else None,
            'premios': limpiar(premio.group(1)).lstrip('★ ').strip() if premio else None,
            'orden': i,
        }
    return fuera


def galeria(slug):
    """Las fotos publicadas de la obra, en el orden en que estan numeradas."""
    carpeta = os.path.join(RAIZ, 'assets', 'gallery', slug)
    if not os.path.isdir(carpeta):
        return []
    archivos = []
    for f in os.listdir(carpeta):
        m = re.match(r'^(\d+)\.webp$', f)
        if m:
            archivos.append((int(m.group(1)), f))
    return [f for _, f in sorted(archivos)]


def portada(slug, html):
    """La foto que hoy se ve en la tarjeta del listado."""
    m = re.search(r'<a href="/proyectos/%s/"[^>]*class="project-card".*?'
                  r'<img src="([^"]*)"' % re.escape(slug), html, re.S)
    return m.group(1) if m else None


def main():
    listado = io.open(os.path.join(RAIZ, 'proyectos', 'index.html'),
                      encoding='utf-8').read()
    extra = tarjetas()

    memorias_en = {}
    ruta_en = os.path.join(RAIZ, 'docs', 'en_memorias.json')
    if os.path.isfile(ruta_en):
        memorias_en = json.load(io.open(ruta_en, encoding='utf-8'))

    obras = []
    for p in sorted(glob.glob(os.path.join(RAIZ, 'proyectos', '*', 'index.html'))):
        slug = os.path.basename(os.path.dirname(p))
        h = io.open(p, encoding='utf-8').read()
        f = ficha(h)
        e = extra.get(slug, {})

        titulo = limpiar(re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S).group(1))
        lede = re.search(r'class="lede[^"]*"[^>]*>(.*?)</p>', h, re.S)

        obras.append({
            'slug': slug,
            'titulo': titulo,
            'ubicacion': f.get('Ubicación'),
            'pais': f.get('País'),
            'anio': f.get('Año'),
            'superficie': f.get('Superficie'),
            'comitente': f.get('Comitente'),
            'tipologia': f.get('Tipo'),
            'fotografia': f.get('Fotógrafo') or f.get('Fotografía'),
            'categoria': e.get('categoria'),
            'equipo': [x for x in (f.get('Equipo') or '').split('\n') if x],
            'bajada': limpiar(lede.group(1)) if lede else None,
            'memoria': memoria(h),
            'memoria_en': ('\n\n'.join(memorias_en[slug])
                           if slug in memorias_en else None),
            'estado': ESTADOS.get(f.get('Estado'), 'en_proyecto'),
            'publicada': True,       # las 61 estan en el sitio
            'destacada': False,      # el home usa sus propios banners
            'orden': e.get('orden'),
            'premios': e.get('premios'),
            'portada': portada(slug, listado),
            'galeria': galeria(slug),
        })

    destino = os.path.join(RAIZ, 'docs', 'panel_datos.json')
    io.open(destino, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(obras, ensure_ascii=False, indent=1))

    # --- que quedo incompleto -------------------------------------------
    faltan = {}
    for campo in ('ubicacion', 'pais', 'anio', 'superficie', 'tipologia',
                  'categoria', 'bajada', 'memoria', 'memoria_en', 'comitente',
                  'fotografia'):
        cuantas = [o['slug'] for o in obras if not o.get(campo)]
        if cuantas:
            faltan[campo] = cuantas

    print('obras exportadas: %d  ->  docs/panel_datos.json' % len(obras))
    print('fotos en total:   %d' % sum(len(o['galeria']) for o in obras))
    print('con memoria:      %d' % sum(1 for o in obras if o['memoria']))
    print('\ncampos vacios:')
    for campo, lista in sorted(faltan.items(), key=lambda x: -len(x[1])):
        print('  %-12s %2d  %s' % (campo, len(lista), ', '.join(lista[:5])
                                   + ('…' if len(lista) > 5 else '')))


if __name__ == '__main__':
    main()
