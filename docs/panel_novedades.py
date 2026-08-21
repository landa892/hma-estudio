# -*- coding: utf-8 -*-
"""Escribe en el Inicio los respaldos editables de Instagram, LinkedIn y YouTube.

LinkedIn y YouTube intentan actualizarse en el navegador desde sus APIs. Estos
datos siguen siendo necesarios: si una credencial vence o un servicio falla, la
pagina conserva una publicacion valida. Instagram no expone un feed publico sin
una aplicacion de Meta, asi que se actualiza desde el panel.
"""
import html
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
    },
    'linkedin': {
        'titulo': ('El estudio detrás del Movistar Arena',
                   'The studio behind Movistar Arena'),
        'texto': (
            'Leonardo Militello y Fernando Hitzig repasan dos décadas de '
            'trayectoria y el proceso creativo del espacio VIP gastronómico del '
            'Movistar Arena.',
            'Leonardo Militello and Fernando Hitzig look back on two decades of '
            'work and the creative process behind the Movistar Arena VIP '
            'hospitality space.'),
        'url': (
            'https://www.linkedin.com/posts/hitzig-militello-arquitectos_'
            'dise%C3%B1amos-el-vip-del-movistar-arena-para-activity-'
            '7474580879424671744--V-b',) * 2,
        'imagen': ('@site:/assets/covers/movistar-arena.webp',) * 2,
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
        for campo in ('titulo', 'texto', 'url', 'imagen'):
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


def imagen_local(red, ruta, supabase_url=None, clave=None):
    if ruta.startswith('@site:'):
        return ruta[len('@site:'):]
    if not supabase_url or not ruta:
        return None
    os.makedirs(CARPETA, exist_ok=True)
    destino = os.path.join(CARPETA, '%s-panel.webp' % red)
    remoto = (supabase_url + '/storage/v1/object/public/obras/'
              + urllib.parse.quote(ruta, safe='/'))
    pedido = urllib.request.Request(remoto, headers={'apikey': clave})
    with urllib.request.urlopen(pedido, timeout=45) as r:
        contenido = r.read()
    if not contenido:
        raise RuntimeError('la imagen guardada esta vacia')
    io.open(destino, 'wb').write(contenido)
    return '/assets/home/%s-panel.webp' % red


def main(supabase):
    if supabase:
        filas, url, clave = desde_supabase()
    else:
        filas, url, clave = filas_default(), None, None

    codigo = io.open(INICIO, encoding='utf-8').read()
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
            local = None
            print('aviso: no se bajo la imagen de %s: %s' % (red, exc))
        if local:
            codigo = reemplazar_atributo(
                codigo, 'src', 'data-%s-image' % red, local)

    io.open(INICIO, 'w', encoding='utf-8', newline='\n').write(codigo)
    print('respaldos del Inicio: 3 redes')
    return 0


if __name__ == '__main__':
    sys.exit(main('--supabase' in sys.argv))
