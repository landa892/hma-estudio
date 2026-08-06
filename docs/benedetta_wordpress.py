# -*- coding: utf-8 -*-
"""Restores Benedetta's editorial order from the previous WordPress site.

The old project page defines both the cover and the gallery sequence. The
assets are already stored in that order; this script keeps the Spanish and
English pages, dimensions and visible plans in sync.

    python docs/benedetta_wordpress.py
"""
import io
import json
import os
import re

from PIL import Image


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = 'benedetta'
FEATURED = (1, 7, 12)
VISIBLE = 6


def dimensions(path):
    with Image.open(path) as image:
        return image.size


def photo_data():
    folder = os.path.join(ROOT, 'assets', 'gallery', SLUG)
    photos = []
    for name in os.listdir(folder):
        match = re.fullmatch(r'(\d+)\.webp', name)
        if match:
            number = int(match.group(1))
            width, height = dimensions(os.path.join(folder, name))
            photos.append({'n': number, 'w': width, 'h': height})
    return sorted(photos, key=lambda photo: photo['n'])


def plan_data():
    folder = os.path.join(ROOT, 'assets', 'planos', SLUG)
    plans = []
    for name in os.listdir(folder):
        match = re.fullmatch(r'(\d+)\.webp', name)
        if match:
            number = int(match.group(1))
            width, height = dimensions(os.path.join(folder, name))
            plans.append({'n': number, 'w': width, 'h': height})
    return sorted(plans, key=lambda plan: plan['n'])


def project_gallery(photos, title, photo_word):
    by_number = {photo['n']: photo for photo in photos}
    rows = []
    for position, number in enumerate(FEATURED):
        photo = by_number[number]
        loading = (' loading="eager" decoding="async" fetchpriority="high"'
                   if position == 0 else ' loading="lazy" decoding="async"')
        rows.append(
            '      <div class="project-row project-row--sola reveal">\n'
            '        <div class="project-row__photo"><img '
            'src="/assets/gallery/%s/%d.webp" width="%d" height="%d" '
            'alt="%s - %s %d"%s></div>\n'
            '      </div>'
            % (SLUG, number, photo['w'], photo['h'], title, photo_word,
               number, loading)
        )
    return ('    <section class="project-gallery">\n%s\n    </section>'
            % '\n\n'.join(rows))


def gallery_section(photos, plans, title, english=False):
    items = []
    for photo in photos[:VISIBLE]:
        items.append(
            '          <figure class="gallery-grid__item"><img '
            'src="/assets/gallery/%s/%d.webp" width="%d" height="%d" '
            'alt="%s - %s %d" loading="lazy" decoding="async"></figure>'
            % (SLUG, photo['n'], photo['w'], photo['h'], title,
               'photo' if english else 'foto', photo['n'])
        )
    for plan in plans:
        items.append(
            '          <figure class="gallery-grid__item gallery-grid__item--plano"><img '
            'src="/assets/planos/%s/%d.webp" width="%d" height="%d" '
            'alt="%s - %s %d" loading="lazy" decoding="async"></figure>'
            % (SLUG, plan['n'], plan['w'], plan['h'], title,
               'plan' if english else 'plano', plan['n'])
        )
    for photo in photos[VISIBLE:]:
        items.append(
            '          <figure class="gallery-grid__item is-extra"><img '
            'src="/assets/gallery/%s/%d.webp" width="%d" height="%d" '
            'alt="%s - %s %d" loading="lazy" decoding="async"></figure>'
            % (SLUG, photo['n'], photo['w'], photo['h'], title,
               'photo' if english else 'foto', photo['n'])
        )
    total = len(photos)
    if english:
        eyebrow, heading = 'Gallery', 'All photos'
        more, less = 'See all %d photos' % total, 'See fewer photos'
    else:
        eyebrow, heading = 'Galer\u00eda', 'Todas las fotos'
        more, less = 'Ver las %d fotos' % total, 'Ver menos fotos'
    return (
        '    <section class="section no-border" id="galeria">\n'
        '      <div class="container">\n'
        '        <div class="section-head"><div><span class="eyebrow">%s</span>'
        '<h2 class="display-3 mt-10">%s</h2></div></div>\n'
        '        <div class="gallery-grid reveal">\n%s\n        </div>\n'
        '        <button type="button" class="btn gallery-more" data-total="%d" '
        'data-mas="%s" data-menos="%s" aria-expanded="false">%s</button>\n'
        '      </div>\n'
        '    </section>'
        % (eyebrow, heading, '\n'.join(items), total, more, less, more)
    )


def update_page(path, photos, plans, english=False):
    with io.open(path, encoding='utf-8') as source:
        html = source.read()
    title = 'Benedetta'
    html = re.sub(
        r'(?s)    <section class="project-gallery">.*?    </section>',
        project_gallery(photos, title, 'photo' if english else 'foto'),
        html,
        count=1,
    )
    html = re.sub(
        r'(?s)    <section class="section no-border" id="galeria">.*?    </section>',
        gallery_section(photos, plans, title, english),
        html,
        count=1,
    )
    html = re.sub(
        r'(<meta property="og:image" content=")[^"]+("\s*/?>)',
        r'\1https://estudiohma.com/assets/covers/benedetta.webp\2',
        html,
        count=1,
    )
    html = html.replace('/styles/main.css?v=77', '/styles/main.css?v=78')
    with io.open(path, 'w', encoding='utf-8', newline='') as target:
        target.write(html)


def update_data(photos):
    path = os.path.join(ROOT, 'docs', 'obras_alta.json')
    with io.open(path, encoding='utf-8') as source:
        data = json.load(source)
    if SLUG not in data:
        return
    data[SLUG]['galeria'] = photos
    with io.open(path, 'w', encoding='utf-8', newline='') as target:
        json.dump(data, target, ensure_ascii=False, indent=1)


def main():
    photos = photo_data()
    plans = plan_data()
    if [photo['n'] for photo in photos] != list(range(1, 32)):
        raise SystemExit('Benedetta must contain photos 1 through 31')
    update_page(os.path.join(ROOT, 'proyectos', SLUG, 'index.html'),
                photos, plans)
    update_page(os.path.join(ROOT, 'en', 'projects', SLUG, 'index.html'),
                photos, plans, english=True)
    update_data(photos)
    print('Benedetta: %d ordered photos, %d visible plans' %
          (len(photos), len(plans)))


if __name__ == '__main__':
    main()
