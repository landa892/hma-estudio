# -*- coding: utf-8 -*-
"""Escribe en el Inicio los respaldos editables de Instagram, LinkedIn y YouTube.

Instagram y YouTube intentan actualizarse en el navegador desde sus APIs.
Estos datos siguen siendo necesarios: si una credencial vence, una publicacion
es una colaboracion o un servicio falla, la pagina conserva lo elegido en el
panel. LinkedIn se administra desde ese mismo panel.
"""
import html
import hashlib
import io
import json
import os
import re
import sys
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INICIO = os.path.join(RAIZ, 'index.html')
CARPETA = os.path.join(RAIZ, 'assets', 'home')

DEFAULTS = {
    'instagram': {
        'titulo': ('Movistar Arena', 'Movistar Arena'),
        'texto': (
            'Nuestro proyecto VIP Lounge Movistar Arena fue distinguido con una '
            'Mención Especial en la categoría Commercial Interiors de los '
            'Architizer A+ Awards 2026.',
            'Our VIP Lounge Movistar Arena project received a Special Mention in '
            'the Commercial Interiors category of the 2026 Architizer A+ Awards.'),
        'url': ('https://www.instagram.com/p/DYANnd0CXnT/',) * 2,
        'imagen': ('@site:/assets/covers/movistar-arena.webp',) * 2,
        'modo': ('automatico',) * 2,
    },
    'linkedin': {
        'titulo': ('Aire Libre: arquitectura y naturaleza',
                   'Aire Libre: architecture and nature'),
        'texto': (
            'Inspirado en los antiguos invernaderos ingleses, Aire Libre combina '
            'recursos industriales, vegetación y coctelería en más de 900 m².',
            'Inspired by historic English greenhouses, Aire Libre combines '
            'industrial materials, vegetation and cocktail culture across more '
            'than 900 m².'),
        'url': (
            'https://www.linkedin.com/posts/hitzig-militello-arquitectos_'
            'interiordesign-dise%C3%B1odeinteriores-architecture-activity-'
            '7311051799749128194-7TTX',) * 2,
        'imagen': ('@site:/assets/covers/aire-libre.webp',) * 2,
    },
    'youtube': {
        'titulo': ('Entrevista con @LadrilloInfo', 'Interview with @LadrilloInfo'),
        'texto': (
            'Leonardo Militello y Fernando Hitzig cuentan cómo diseñan espacios '
            'que generan experiencia.',
            'Leonardo Militello and Fernando Hitzig explain how they design '
            'experience-led spaces.'),
        'url': ('https://www.youtube.com/watch?v=EalBF9mvgRI',) * 2,
        'imagen': ('@site:/assets/video/podcast-ladrillo.webp',) * 2,
    },
}


def filas_default():
    filas = []
    orden = 40
    for red in ('instagram', 'linkedin', 'youtube'):
        campos = ('titulo', 'texto', 'url', 'imagen', 'modo') if red == 'instagram' else (
            'titulo', 'texto', 'url', 'imagen')
        for campo in campos:
            es, en = DEFAULTS[red][campo]
            filas.append({
                'clave': 'home.%s_%s' % (red, campo),
                'seccion': 'novedades',
                'rotulo': '%s — %s' % (red.capitalize(), campo),
                'es': es,
                'en': en,
                'multilinea': campo == 'texto',
                'orden': orden,
            })
            orden += 1
    return filas


def desde_supabase():
    url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY', '')
    if not url or not clave:
        raise SystemExit('Faltan SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno.')
    headers = {'apikey': clave, 'Authorization': 'Bearer ' + clave}
    pedido = urllib.request.Request(
        url + '/rest/v1/textos?select=*&seccion=eq.novedades&order=orden.asc',
        headers=headers)
    with urllib.request.urlopen(pedido, timeout=30) as r:
        filas = json.loads(r.read().decode('utf-8'))

    existentes = set(f['clave'] for f in filas)
    faltantes = [f for f in filas_default() if f['clave'] not in existentes]
    if faltantes:
        alta = urllib.request.Request(
            url + '/rest/v1/textos?on_conflict=clave',
            data=json.dumps(faltantes, ensure_ascii=False).encode('utf-8'),
            method='POST',
            headers=dict(headers, **{
                'Content-Type': 'application/json',
                'Prefer': 'resolution=ignore-duplicates,return=representation',
            }))
        with urllib.request.urlopen(alta, timeout=30) as r:
            filas.extend(json.loads(r.read().decode('utf-8')))
        print('novedades sembradas: %d' % len(faltantes))
    return filas, url, clave


def valor(filas, red, campo, idioma='es'):
    clave = 'home.%s_%s' % (red, campo)
    fila = next((f for f in filas if f.get('clave') == clave), None)
    return ((fila or {}).get(idioma) or DEFAULTS[red][campo][0]).strip()


def reemplazar_atributo(codigo, atributo, dato, nuevo):
    patron = r'<[^>]+\b%s\b[^>]*>' % dato
    valor_nuevo = html.escape(nuevo, quote=True)

    def tocar(m):
        etiqueta = m.group(0)
        if not re.search(r'\b%s="[^"]*"' % atributo, etiqueta):
            raise SystemExit('Falta %s en la etiqueta %s' % (atributo, dato))
        return re.sub(r'\b%s="[^"]*"' % atributo,
                      '%s="%s"' % (atributo, valor_nuevo), etiqueta, count=1)

    actualizado, n = re.subn(patron, tocar, codigo)
    if not n:
        raise SystemExit('No encuentro %s para %s en index.html' % (atributo, dato))
    return actualizado


def reemplazar_texto(codigo, dato, nuevo):
    patron = r'(<(?P<tag>h2|p)\b[^>]*\b%s\b[^>]*>).*?(</(?P=tag)>)' % dato
    actualizado, n = re.subn(
        patron, lambda m: m.group(1) + html.escape(nuevo) + m.group(3),
        codigo, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('No encuentro un unico %s en index.html' % dato)
    return actualizado


def ruta_imagen_salida(red, ruta):
    """Devuelve la direccion que debe quedar escrita en el Inicio.

    La base conserva la ruta estable de Storage, pero el sitio publicado usa
    una copia local versionada por la ruta de Storage. Centralizar evita que el
    verificador compare la ruta de origen con la ruta de salida y rechace una
    imagen que el build descargo correctamente.
    """
    if ruta.startswith('@site:') or ruta.startswith('@seed:'):
        return ruta.split(':', 1)[1]
    if ruta:
        # El panel genera otra ruta en cada carga. Con un nombre fijo el
        # navegador seguia mostrando IOL aunque ARQ ya estuviera publicado.
        version = hashlib.sha256(ruta.encode('utf-8')).hexdigest()[:12]
        return '/assets/home/%s-panel-%s.webp' % (red, version)
    return None


def imagen_local(red, ruta, supabase_url=None, clave=None):
    # Igual que en el resto del build: una ruta con @ es del repositorio y
    # pedirsela al Storage devuelve 400. Se cubren los dos prefijos aunque hoy
    # las novedades solo usen @site:, para que no dependa de eso.
    salida = ruta_imagen_salida(red, ruta)
    if ruta.startswith('@site:') or ruta.startswith('@seed:'):
        return salida
    if not supabase_url or not ruta:
        return None
    os.makedirs(CARPETA, exist_ok=True)
    destino = os.path.join(CARPETA, os.path.basename(salida))
    remoto = (supabase_url + '/storage/v1/object/public/obras/'
              + urllib.parse.quote(ruta, safe='/'))
    pedido = urllib.request.Request(remoto, headers={'apikey': clave})
    with urllib.request.urlopen(pedido, timeout=45) as r:
        contenido = r.read()
    if not contenido:
        raise RuntimeError('la imagen guardada esta vacia')
    with io.open(destino, 'wb') as archivo:
        archivo.write(contenido)
    return salida


def main(supabase):
    if supabase:
        filas, url, clave = desde_supabase()
    else:
        filas, url, clave = filas_default(), None, None

    codigo = io.open(INICIO, encoding='utf-8').read()
    codigo = reemplazar_atributo(
        codigo, 'data-instagram-mode', 'data-instagram-mode',
        valor(filas, 'instagram', 'modo'))
    for red in ('instagram', 'linkedin', 'youtube'):
        codigo = reemplazar_atributo(
            codigo, 'href', 'data-%s-link' % red, valor(filas, red, 'url'))
        codigo = reemplazar_texto(
            codigo, 'data-%s-title' % red, valor(filas, red, 'titulo'))
        codigo = reemplazar_texto(
            codigo, 'data-%s-text' % red, valor(filas, red, 'texto'))
        try:
            local = imagen_local(red, valor(filas, red, 'imagen'), url, clave)
        except Exception as exc:
            # Dejar la copia anterior seria especialmente enganoso: el build
            # terminaria en verde aunque el estudio acabara de elegir otra
            # imagen. La publicacion se conserva anterior y el log explica la
            # causa concreta para poder reintentar.
            raise RuntimeError('no se pudo bajar la imagen de %s: %s' % (red, exc))
        if local:
            codigo = reemplazar_atributo(
                codigo, 'src', 'data-%s-image' % red, local)

    io.open(INICIO, 'w', encoding='utf-8', newline='\n').write(codigo)
    print('respaldos del Inicio: 3 redes')
    return 0


if __name__ == '__main__':
    sys.exit(main('--supabase' in sys.argv))
