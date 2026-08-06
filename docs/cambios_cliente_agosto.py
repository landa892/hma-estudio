# -*- coding: utf-8 -*-
"""Applies the August project-list corrections requested by the studio.

The project list exists in Spanish and English and every related-project card
repeats part of that data. This script keeps categories, status badges, years,
compact measurements, awards and project teams consistent across the site.

    python docs/cambios_cliente_agosto.py
"""
import glob
import html
import io
import json
import os
import re


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CATEGORY_LABELS = {
    'hoteleria': ('Hoteler\u00eda', 'Hospitality'),
    'comercial': ('Comercial', 'Commercial'),
    'gastronomico': ('Gastron\u00f3mico', 'Food & Beverage'),
    'residencial': ('Residencial', 'Residential'),
    'oficinas': ('Oficinas', 'Offices'),
    'cultural': ('Cultural & Institucional', 'Cultural & Institutional'),
}

# Corrections explicitly sent by the studio, plus the split between hospitality
# and commercial work that was requested in the same document.
PROJECTS = {
    'uala-ii': {
        'category': 'oficinas',
        'state': 'obra',
        'year': '2019–2020',
        'surface': ('757 m²', '757 m²'),
    },
    'aire-libre': {'state': 'obra', 'year': '2024'},
    'bienal-venecia': {'state': 'proyecto', 'year': '2024'},
    'hyatt-ziva': {'category': 'hoteleria', 'year': '2024'},
    'iol': {'state': 'obra'},
    'roket': {'category': 'comercial', 'year': '2024'},
    'movistar-arena': {'category': 'comercial'},
    'parfumerie': {'category': 'comercial'},
    'hausscape': {'category': 'comercial'},
    'indusparquet': {'category': 'comercial'},
    'cien': {'category': 'comercial', 'surface': ('300 m\u00b2', '300 m\u00b2')},
    'manduca': {'category': 'gastronomico'},
    'kavak-hub': {'category': 'oficinas', 'surface': ('15.300 m\u00b2', '15,300 m\u00b2')},
    'kavak-oficinas': {'category': 'oficinas'},
    'plaza-mateo': {'category': 'comercial'},
    'osten-tower': {'surface': ('950 m\u00b2', '950 m\u00b2')},
    'cafe-artois': {'surface': ('354 m\u00b2', '354 m\u00b2')},
    'atelier-vilela': {'surface': ('115 m\u00b2', '115 m\u00b2')},
    'victoria-brown': {'surface': ('385 m\u00b2', '385 m\u00b2')},
}

AWARDS = {
    'atelier-vilela': 'BIAR',
    'benedetta': 'Restaurant & Bar Design Awards',
    'cien': 'Surface Design Awards',
    'dos-casas-conde': 'Next Landmark Awards',
    'fogon': 'Bienal SCA-CPAU \u00b7 Restaurant & Bar Design Awards',
    'goodsten': 'IIDA \u00b7 Next Landmark Awards',
    'kavak-hub': 'Bienal Internacional de Arquitectura',
    'mamba-bar': 'SBID \u00b7 Restaurant & Bar Design Awards',
    'manduca': 'Architizer A+ \u00b7 Surface Design \u00b7 Hospitality Design \u00b7 ARQ-FADEA',
    'moshu': 'Prix Versailles \u00b7 Surface Design Awards',
    'movistar-arena': 'Architizer A+ \u00b7 LIV Hospitality Design Awards',
    'nim-bar': 'Prix Versailles \u00b7 Restaurant & Bar Design Awards',
    'novotel': 'Accor Hotels Design & Technical Summit',
    'osten': 'German Design Awards \u00b7 SBID \u00b7 Restaurant & Bar Design Awards',
    'victoria-brown': 'Restaurant & Bar Design Awards',
}

WORDPRESS_SLUG = {
    'abasto-patio-comidas': 'patio-comidas-abasto-shopping',
    'araoz': 'a757',
    'atelier-vilela': '24',
    'bienal-venecia': 'sinapsis',
    'bolivar': '21',
    'burger-7167': '7167-burger',
    'cafe-artois': '55',
    'casa-olmo': '37',
    'clasico-quilmes': 'el-clasico-de-quilmes',
    'dos-casas-conde': '8',
    'elyaki': '50',
    'galeria-objeto-a': '9',
    'goodsten': '35',
    'hyatt-ziva': 'hyatt-ziva-barbados',
    'iguanafix': '54',
    'kavak-oficinas': 'kavak-oficina',
    'luccianos-caballito': '32',
    'luccianos-olivos': '33',
    'malabia': 'edificio-malabia',
    'malita': 'malita-bar',
    'mamba-bar': '48',
    'manduca': 'mercado-manduca',
    'moshu': 'moshu-treehouse',
    'nim-bar': '46',
    'novotel': '59',
    'oficina-casa-luna': '22',
    'osten-foa': 'cafeteria-osten-casa-foa',
    'ph-el-salvador': 'es4633',
    'ph-loft-arias': '10',
    'stella-artois-mercat': 'stella-artois-mercat',
    'the-birra': '36',
    'tostado': 'tostado',
    'uala-office': '51',
    'victoria-brown': '25',
    'williamsburg': 'williamsburg',
}


def read(path):
    with io.open(path, encoding='utf-8') as source:
        return source.read()


def write(path, content):
    with io.open(path, 'w', encoding='utf-8', newline='') as target:
        target.write(content)


def text_content(fragment):
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', '', fragment)).split())


def replace_class_text(body, class_name, value):
    return re.sub(
        r'(<[^>]+class="[^"]*\b%s\b[^"]*"[^>]*>).*?(</[^>]+>)'
        % re.escape(class_name),
        lambda match: match.group(1) + html.escape(value, quote=False) + match.group(2),
        body,
        count=1,
        flags=re.S,
    )


def compact_meta(body, config, english=False):
    index = 1 if english else 0

    def replace(match):
        spans = re.findall(r'<span>(.*?)</span>', match.group(1), re.S)
        values = [text_content(span) for span in spans]
        if not values:
            return match.group(0)
        program = values[0].replace(' - en proceso', '').replace(' - in progress', '')
        program = program.replace(' \u2014 en proceso', '').replace(' \u2014 in progress', '')
        location = values[1] if len(values) > 1 else ''
        current_year = next((value for value in reversed(values)
                             if re.search(r'(?:19|20)\d{2}', value)), '')
        current_surface = next((value for value in values if 'm\u00b2' in value), '')
        surface = config.get('surface', (current_surface, current_surface))[index]
        year = config.get('year', current_year)
        ordered = [program, location, surface, year]
        inner = ''.join('<span>%s</span>' % html.escape(value, quote=False)
                        for value in ordered if value)
        return match.group(0).replace(match.group(1), inner, 1)

    for class_name in ('p-meta', 'plr-meta'):
        body = re.sub(
            r'(?s)<div class="%s">(.*?)</div>' % class_name,
            replace,
            body,
            count=1,
        )
    if config.get('year'):
        body = replace_class_text(body, 'plr-loc', config['year'])
    return body


def update_anchor(content, slug, config, english=False, listing=False):
    pattern = re.compile(
        r'(<a\b(?=[^>]*\bdata-slug="%s")[^>]*>)(.*?)(</a>)'
        % re.escape(slug),
        re.S,
    )
    category = config.get('category')
    state = config.get('state')

    def replace(match):
        opening, body = match.group(1), match.group(2)
        if category:
            opening = re.sub(r'data-cat="[^"]*"', 'data-cat="%s"' % category,
                             opening, count=1)
            label = CATEGORY_LABELS[category][1 if english else 0]
            body = replace_class_text(body, 'card-cat', label)
            body = replace_class_text(body, 'plr-cat', label)
        if state:
            opening = re.sub(r'data-estado="[^"]*"', 'data-estado="%s"' % state,
                             opening, count=1)
            label = ('Project' if english else 'Proyecto') if state == 'proyecto' \
                else ('Built' if english else 'Obra')
            body = re.sub(
                r'<span class="card-estado[^>]*>.*?</span>',
                '<span class="card-estado card-estado--%s">%s</span>' % (state, label),
                body,
                count=1,
                flags=re.S,
            )
        if listing:
            body = compact_meta(body, config, english)
            award = AWARDS.get(slug)
            if award and 'class="p-name"' in body:
                award_html = '<div class="p-awards">\u2605 %s</div>' % award
                if re.search(r'<div class="p-awards">.*?</div>', body, re.S):
                    body = re.sub(r'<div class="p-awards">.*?</div>', award_html,
                                  body, count=1, flags=re.S)
                else:
                    body = body.replace('</div>\n            </div>',
                                        '</div>\n              %s\n            </div>' % award_html,
                                        1)
        return opening + body + match.group(3)

    return pattern.sub(replace, content)


def update_filters(content, english=False):
    hospitality = 'Hospitality' if english else 'Hoteler\u00eda'
    commercial = 'Commercial' if english else 'Comercial'
    replacement = (
        '<button class="filter-btn" data-filter="hoteleria">%s</button>\n'
        '            <button class="filter-btn" data-filter="comercial">%s</button>'
        % (hospitality, commercial)
    )
    content = re.sub(
        r'\s*<button class="filter-btn" data-filter="comercial">.*?</button>',
        '',
        content,
        flags=re.S,
    )
    return re.sub(
        r'<button class="filter-btn" data-filter="hoteleria">.*?</button>',
        replacement,
        content,
        count=1,
        flags=re.S,
    )


def names_from_team(value):
    names = []
    for line in value.splitlines():
        line = ' '.join(line.split()).strip(' -:')
        if re.match(r'^(?:Arq\.|Arch\.)', line, re.I):
            line = re.sub(r'^Arch\.', 'Arq.', line, flags=re.I)
            if line not in names:
                names.append(line)
    return names[:8]


def teams():
    data = json.loads(read(os.path.join(ROOT, 'docs', 'wordpress_proyectos.json')))
    result = {}
    for slug in os.listdir(os.path.join(ROOT, 'proyectos')):
        if slug == 'index.html':
            continue
        source_slug = WORDPRESS_SLUG.get(slug, slug)
        names = names_from_team(data.get(source_slug, {}).get('equipo', ''))
        result[slug] = names or ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello']
    return result


def update_team(content, names, english=False):
    label = 'Team' if english else 'Equipo'
    shown = [re.sub(r'^Arq\.', 'Arch.', name) if english else name for name in names]
    row = ('          <div class="spec-row spec-row--team"><dt>%s</dt><dd>%s</dd></div>'
           % (label, '<br>'.join(html.escape(name, quote=False) for name in shown)))
    if 'class="spec-row spec-row--team"' in content:
        return re.sub(r'\s*<div class="spec-row spec-row--team">.*?</div>',
                      '\n' + row, content, count=1, flags=re.S)
    return re.sub(r'(\s*</dl>)', '\n' + row + r'\1', content, count=1)


def update_detail(content, config, english=False):
    """Keep the technical sheet aligned with its listing-card corrections."""
    content = content.replace('Proyecto en proceso', 'Proyecto')
    content = content.replace('Project in progress', 'Project')

    values = {}
    if config.get('state'):
        values['Status' if english else 'Estado'] = (
            ('Project' if english else 'Proyecto')
            if config['state'] == 'proyecto'
            else ('Built' if english else 'Obra concluida')
        )
    if config.get('year'):
        values['Year' if english else 'Año'] = config['year']
    if config.get('surface'):
        values['Area' if english else 'Superficie'] = config['surface'][1 if english else 0]

    for label, value in values.items():
        content = re.sub(
            r'(<div class="spec-row"><dt>%s</dt><dd>).*?(</dd></div>)'
            % re.escape(label),
            lambda match: match.group(1) + html.escape(value, quote=False) + match.group(2),
            content,
            count=1,
            flags=re.S,
        )
    return content


def update_listing(path, english=False):
    content = update_filters(read(path), english)
    for slug in set(PROJECTS) | set(AWARDS):
        content = update_anchor(content, slug, PROJECTS.get(slug, {}),
                                english, listing=True)
    write(path, content)


def update_all_pages(team_map):
    changed = 0
    for path in sorted(glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)):
        if 'node_modules' in path:
            continue
        relative = os.path.relpath(path, ROOT).replace('\\', '/')
        english = relative.startswith('en/')
        content = read(path)
        updated = re.sub(r'/styles/main\.css\?v=\d+', '/styles/main.css?v=79', content)
        for slug, config in PROJECTS.items():
            updated = update_anchor(updated, slug, config, english)
        match = re.match(r'(?:en/projects|proyectos)/([^/]+)/index\.html$', relative)
        if match:
            slug = match.group(1)
            config = PROJECTS.get(slug, {})
            if config.get('category'):
                label = CATEGORY_LABELS[config['category']][1 if english else 0]
                updated = re.sub(r'(<span class="eyebrow">).*?(</span>)',
                                 lambda item: item.group(1) + label + item.group(2),
                                 updated, count=1, flags=re.S)
            updated = update_detail(updated, config, english)
            updated = update_team(updated, team_map.get(slug, []), english)
        if updated != content:
            write(path, updated)
            changed += 1
    return changed


def main():
    team_map = teams()
    changed = update_all_pages(team_map)
    update_listing(os.path.join(ROOT, 'proyectos', 'index.html'))
    update_listing(os.path.join(ROOT, 'en', 'projects', 'index.html'), True)
    print('paginas sincronizadas: %d' % changed)
    print('equipos disponibles: %d' % len(team_map))


if __name__ == '__main__':
    main()
