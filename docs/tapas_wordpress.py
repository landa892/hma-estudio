# -*- coding: utf-8 -*-
"""Aplica las tapas elegidas en el WordPress anterior y el Drive.

Las tarjetas, las filas, el buscador y el Open Graph de cada ficha usan la
misma portada. El orden de las fotos dentro de las galerias no se modifica.

    python docs/tapas_wordpress.py
"""

import io
import os
import re


# slug: (ruta de portada, ancho, alto)
PORTADAS = {
    'antiche': ('/assets/gallery/antiche/33.webp', 1000, 868),
    'araoz': ('/assets/gallery/araoz/11.webp', 533, 800),
    'atelier-vilela': ('/assets/gallery/atelier-vilela/2.webp', 1200, 788),
    'bolivar': ('/assets/gallery/bolivar/19.webp', 1348, 899),
    'fehgra': ('/assets/gallery/fehgra/3.webp', 800, 520),
    'fogon': ('/assets/gallery/fogon/25.webp', 1024, 683),
    'fresco': ('/assets/gallery/fresco/34.webp', 2000, 1333),
    'goodsten': ('/assets/gallery/goodsten/15.webp', 1800, 1200),
    'hausscape': ('/assets/gallery/hausscape/2.webp', 818, 545),
    'hyatt-ziva': ('/assets/covers/hyatt-ziva.webp', 800, 450),
    'juan-valdez': ('/assets/gallery/juan-valdez/21.webp', 800, 533),
    'kavak-hub': ('/assets/gallery/kavak-hub/2.webp', 2000, 1125),
    'kavak-oficinas': ('/assets/gallery/kavak-oficinas/14.webp', 2000, 1333),
    'luccianos-caballito': ('/assets/gallery/luccianos-caballito/12.webp', 1024, 682),
    'mamba-bar': ('/assets/gallery/mamba-bar/12.webp', 1800, 1200),
    'movistar-arena': ('/assets/covers/movistar-arena.webp', 800, 533),
    'nim-bar': ('/assets/gallery/nim-bar/27.webp', 1800, 1200),
    'people': ('/assets/gallery/people/13.webp', 801, 1000),
    'tostado': ('/assets/gallery/tostado/28.webp', 1000, 667),
    'uala-office': ('/assets/gallery/uala-office/34.webp', 2000, 1333),
    'victoria-brown': ('/assets/gallery/victoria-brown/14.webp', 1800, 1200),
    'williamsburg': ('/assets/gallery/williamsburg/17.webp', 2000, 1333),
}

PUBLIC_BASE = 'https://estudiohma.com'


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
