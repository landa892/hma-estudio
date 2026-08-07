# -*- coding: utf-8 -*-
"""Aplica las tapas elegidas en el WordPress anterior y el Drive.

Las tarjetas, las filas, el buscador y el Open Graph de cada ficha usan la
misma portada. El orden de las fotos dentro de las galerias no se modifica.

Las que salen de assets/covers vienen de las carpetas "03 - Carátula" del
Drive del estudio: ahi el estudio marca que foto es la portada de cada obra.
Se guardan aparte en vez de reordenar la galeria porque la foto elegida no
siempre esta entre las que publica el sitio.  Ver docs/caratulas.py.

    python docs/tapas_wordpress.py
"""

import io
import os
import re


# slug: (ruta de portada, ancho, alto)
PORTADAS = {
    'accor-hotels': ('/assets/covers/accor-hotels.webp', 800, 450),
    'aire-libre': ('/assets/covers/aire-libre.webp', 800, 533),
    'antiche': ('/assets/covers/antiche.webp', 1000, 849),
    'araoz': ('/assets/covers/araoz.webp', 533, 800),
    'atelier-vilela': ('/assets/covers/atelier-vilela.webp', 1200, 788),
    'benedetta': ('/assets/covers/benedetta.webp', 1200, 694),
    'bienal-venecia': ('/assets/covers/bienal-venecia.webp', 1200, 849),
    'bolivar': ('/assets/covers/bolivar.webp', 1200, 800),
    'burger-7167': ('/assets/covers/burger-7167.webp', 800, 533),
    'cafe-artois': ('/assets/covers/cafe-artois.webp', 1200, 375),
    'casa-olmo': ('/assets/covers/casa-olmo.webp', 1024, 684),
    'cceba': ('/assets/covers/cceba.webp', 1200, 798),
    'cerveceria-austral': ('/assets/covers/cerveceria-austral.webp', 1200, 800),
    'cien': ('/assets/covers/cien.webp', 1200, 800),
    'clasico-quilmes': ('/assets/covers/clasico-quilmes.webp', 1200, 800),
    'dos-casas-conde': ('/assets/covers/dos-casas-conde.webp', 800, 1200),
    'elyaki': ('/assets/covers/elyaki.webp', 1200, 800),
    'fehgra': ('/assets/covers/fehgra.webp', 800, 520),
    'fogon': ('/assets/covers/fogon.webp', 1024, 683),
    'fresco': ('/assets/covers/fresco.webp', 1200, 800),
    'goodsten': ('/assets/covers/goodsten.webp', 1200, 800),
    'hausscape': ('/assets/covers/hausscape.webp', 818, 545),
    'hyatt-ziva': ('/assets/covers/hyatt-ziva.webp', 800, 450),
    'iguanafix': ('/assets/covers/iguanafix.webp', 900, 600),
    'indusparquet': ('/assets/covers/indusparquet.webp', 1200, 800),
    'iol': ('/assets/covers/iol.webp', 1200, 803),
    'juan-valdez': ('/assets/covers/juan-valdez.webp', 800, 533),
    'kavak-hub': ('/assets/covers/kavak-hub.webp', 1200, 800),
    'kavak-oficinas': ('/assets/covers/kavak-oficinas.webp', 1200, 800),
    'luccianos-caballito': ('/assets/covers/luccianos-caballito.webp', 1024, 576),
    'luccianos-olivos': ('/assets/covers/luccianos-olivos.webp', 1200, 800),
    'malabia': ('/assets/covers/malabia.webp', 800, 1200),
    'malita': ('/assets/covers/malita.webp', 1200, 800),
    'mamba-bar': ('/assets/covers/mamba-bar.webp', 1200, 800),
    'manduca': ('/assets/covers/manduca.webp', 800, 774),
    'moshu': ('/assets/covers/moshu.webp', 533, 800),
    'movistar-arena': ('/assets/covers/movistar-arena.webp', 1010, 616),
    'nim-bar': ('/assets/covers/nim-bar.webp', 1200, 1100),
    'osten': ('/assets/covers/osten.webp', 533, 800),
    'osten-foa': ('/assets/covers/osten-foa.webp', 800, 533),
    'osten-tower': ('/assets/covers/osten-tower.webp', 1024, 682),
    'parfumerie': ('/assets/covers/parfumerie.webp', 643, 428),
    'people': ('/assets/covers/people.webp', 801, 1000),
    'plaza-mateo': ('/assets/covers/plaza-mateo.webp', 800, 470),
    'stella-artois-mercat': ('/assets/covers/stella-artois-mercat.webp', 1200, 800),
    'the-birra': ('/assets/covers/the-birra.webp', 1200, 801),
    # La carpeta de caratula del Drive contiene una foto de Tribunales, pero
    # esta ficha corresponde a Miami. La primera foto esta identificada en el
    # Drive como Tostado-Miami-1.
    'tostado': ('/assets/gallery/tostado/1.webp', 1024, 768),
    'uala-office': ('/assets/covers/uala-office.webp', 1200, 800),
    'victoria-brown': ('/assets/covers/victoria-brown.webp', 1200, 800),
    'williamsburg': ('/assets/covers/williamsburg.webp', 1200, 499),
}

PUBLIC_BASE = 'https://hma-estudio.vercel.app'


def leer(path):
    return io.open(path, encoding='utf-8').read()


def escribir(path, content):
    io.open(path, 'w', encoding='utf-8', newline='').write(content)


def actualizar_tarjetas(content, slug, cover_path, width, height):
    card = re.compile(
        r'(<a\b(?=[^>]*\bdata-slug="%s")[^>]*>)(.*?)(</a>)'
        % re.escape(slug),
        re.S,
    )
    image = re.compile(
        r'(<img\s+src=")[^"]+("\s+width=")\d+("\s+height=")\d+("[^>]*>)'
    )
    replacement = r'\g<1>%s\g<2>%d\g<3>%d\g<4>' % (
        cover_path,
        width,
        height,
    )

    def replace_card(match):
        body, count = image.subn(replacement, match.group(2), count=1)
        return match.group(1) + body + match.group(3) if count else match.group(0)

    return card.sub(replace_card, content)


def actualizar_og(content, cover_path):
    return re.sub(
        r'(<meta property="og:image" content=")[^"]+(">)',
        r'\1%s%s\2' % (PUBLIC_BASE, cover_path),
        content,
        count=1,
    )


def actualizar_social(content, normalized_path):
    """Hace que las previews apunten al despliegue que sirve los assets."""
    public_path = '/' + normalized_path
    if public_path.endswith('/index.html'):
        public_path = public_path[:-len('index.html')]

    content = re.sub(
        r'(<meta property="og:image" content=")'
        r'(?:https://(?:www\.)?estudiohma\.com|'
        r'https://hma-estudio\.vercel\.app)?(/assets/[^"]+)(">)',
        r'\1%s\2\3' % PUBLIC_BASE,
        content,
        count=1,
    )
    return re.sub(
        r'(<meta property="og:url" content=")[^"]+(">)',
        r'\1%s%s\2' % (PUBLIC_BASE, public_path),
        content,
        count=1,
    )


def actualizar_buscador(content, slug, cover_path):
    item = re.compile(
        r'("url":\s*"/(?:en/projects|proyectos)/%s/",\s*"img":\s*")[^"]+("\s*\})'
        % re.escape(slug),
        re.S,
    )
    return item.sub(r'\1%s\2' % cover_path, content)


def html_paths():
    paths = ['proyectos/index.html', 'en/projects/index.html']
    for root in ('proyectos', os.path.join('en', 'projects')):
        for folder in os.listdir(root):
            path = os.path.join(root, folder, 'index.html')
            if os.path.isfile(path):
                paths.append(path)
    return sorted(set(paths))


def main():
    changed = []
    for path in html_paths():
        original = leer(path)
        updated = original
        normalized_path = path.replace('\\', '/')
        for slug, (cover_path, width, height) in PORTADAS.items():
            updated = actualizar_tarjetas(
                updated, slug, cover_path, width, height
            )
            if normalized_path in (
                'proyectos/%s/index.html' % slug,
                'en/projects/%s/index.html' % slug,
            ):
                updated = actualizar_og(updated, cover_path)
        updated = actualizar_social(updated, normalized_path)
        if updated != original:
            escribir(path, updated)
            changed.append(path)

    for path in ('scripts/search-index.js', 'scripts/search-index-en.js'):
        original = leer(path)
        updated = original
        for slug, (cover_path, _, __) in PORTADAS.items():
            updated = actualizar_buscador(updated, slug, cover_path)
        if updated != original:
            escribir(path, updated)
            changed.append(path)

    print('tapas actualizadas: %d' % len(PORTADAS))
    print('archivos modificados: %d' % len(changed))
    for path in changed:
        print('  ' + path)


if __name__ == '__main__':
    main()
