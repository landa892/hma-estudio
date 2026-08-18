# -*- coding: utf-8 -*-
"""Genera datos estructurados SEO para todas las paginas publicas.

Se ejecuta despues de regenerar el espejo en ingles y de ordenar Trabajos. De
este modo el schema siempre describe el HTML final, incluso cuando el panel
crea o modifica una obra.

    python docs/seo_gen.py
"""
from __future__ import print_function

import glob
import html
import io
import json
import os
import re
import tempfile
from urllib.parse import urlparse


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://estudiohma.com'
ORG_ID = SITE + '/#organization'
SITE_ID = SITE + '/#website'
START = '<!-- SEO-JSON-LD:START -->'
END = '<!-- SEO-JSON-LD:END -->'

SOCIAL = [
    'https://www.instagram.com/hitzig.militello.arquitectos/',
    'https://www.linkedin.com/company/hitzig-militello-arquitectos/',
    'https://www.facebook.com/estudiohma',
    'https://www.youtube.com/@HMAEstudio',
    'https://www.behance.net/hitzigmilitello',
    'https://www.pinterest.co.uk/leomil78/hitzig-militello-arquitectos/',
]


def read(path):
    with io.open(path, encoding='utf-8') as source:
        return source.read()


def write(path, content):
    # Reemplazo atomico: evita que el listado grande quede a medio escribir si
    # el antivirus o el servidor local lo estan leyendo durante el build.
    folder = os.path.dirname(path)
    handle, temporary = tempfile.mkstemp(prefix='.seo-', suffix='.html', dir=folder)
    try:
        with io.open(handle, 'w', encoding='utf-8', newline='', closefd=True) as target:
            target.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def one(pattern, source, default=''):
    match = re.search(pattern, source, re.I | re.S)
    return html.unescape(match.group(1)).strip() if match else default


def plain(fragment):
    fragment = re.sub(r'<br\s*/?>', ' ', fragment, flags=re.I)
    fragment = re.sub(r'<[^>]+>', ' ', fragment)
    return ' '.join(html.unescape(fragment).split())


def page_data(source):
    canonical = one(r'<link\s+rel="canonical"\s+href="([^"]+)"', source)
    title = plain(one(r'<title>(.*?)</title>', source))
    description = one(r'<meta\s+name="description"\s+content="([^"]*)"', source)
    image = one(r'<meta\s+property="og:image"\s+content="([^"]*)"', source)
    heading = plain(one(r'<h1[^>]*>(.*?)</h1>', source, title.split('|')[0]))
    language = one(r'<html\s+lang="([^"]+)"', source, 'es')
    return {
        'canonical': canonical,
        'title': title,
        'description': description,
        'image': image,
        'heading': heading,
        'language': language,
        'path': urlparse(canonical).path if canonical else '/',
    }


def organization(language):
    english = language.startswith('en')
    return {
        '@type': ['ProfessionalService', 'Organization'],
        '@id': ORG_ID,
        'name': 'Hitzig Militello Arquitectos',
        'alternateName': ['HMA', 'Hitzig Militello Architects'],
        'description': (
            'Architecture and interior design studio founded in Buenos Aires '
            'in 2006, specialising in hospitality, restaurants, workplaces '
            'and residential projects.' if english else
            'Estudio de arquitectura e interiorismo fundado en Buenos Aires '
            'en 2006, especializado en hoteler\u00eda, gastronom\u00eda, oficinas y '
            'proyectos residenciales.'
        ),
        'url': SITE + '/',
        'logo': {
            '@type': 'ImageObject',
            'url': SITE + '/favicon-512x512.png',
            'width': 512,
            'height': 512,
        },
        'image': SITE + '/assets/og-hma-estudio-video-2026.jpg',
        'email': 'hma@estudiohma.com',
        'telephone': ['+54 11 4773 8658', '+1 305 851 3565'],
        'foundingDate': '2006',
        'founder': [
            {'@type': 'Person', 'name': 'Fernando Hitzig'},
            {'@type': 'Person', 'name': 'Leonardo Militello'},
        ],
        'address': {
            '@type': 'PostalAddress',
            'streetAddress': 'Soler 5130, 1 B, Palermo',
            'addressLocality': 'Buenos Aires',
            'addressRegion': 'Ciudad Aut\u00f3noma de Buenos Aires',
            'postalCode': 'C1425',
            'addressCountry': 'AR',
        },
        'areaServed': [
            {'@type': 'Country', 'name': 'Argentina'},
            {'@type': 'Place', 'name': 'Latin America' if english else 'Am\u00e9rica Latina'},
            {'@type': 'Place', 'name': 'Europe' if english else 'Europa'},
            {'@type': 'Place', 'name': 'Middle East' if english else 'Medio Oriente'},
            {'@type': 'Country', 'name': 'United States' if english else 'Estados Unidos'},
        ],
        'knowsAbout': (
            ['Architecture', 'Interior design', 'Hospitality design',
             'Restaurant design', 'Workplace design', 'Residential architecture']
            if english else
            ['Arquitectura', 'Dise\u00f1o de interiores', 'Hoteler\u00eda',
             'Dise\u00f1o gastron\u00f3mico', 'Dise\u00f1o de oficinas', 'Arquitectura residencial']
        ),
        'sameAs': SOCIAL,
    }


def website(language):
    return {
        '@type': 'WebSite',
        '@id': SITE_ID,
        'url': SITE + '/',
        'name': 'Hitzig Militello Arquitectos',
        'alternateName': ['HMA', 'Hitzig Militello Architects'],
        'inLanguage': ['es-AR', 'en'],
        'publisher': {'@id': ORG_ID},
    }


def section_info(path, english):
    sections = {
        'estudio': ('Studio' if english else 'Estudio', '/en/studio/' if english else '/estudio/'),
        'studio': ('Studio', '/en/studio/'),
        'proyectos': ('Projects' if english else 'Trabajos', '/en/projects/' if english else '/proyectos/'),
        'projects': ('Projects', '/en/projects/'),
        'premios': ('Awards' if english else 'Premios', '/en/awards/' if english else '/premios/'),
        'awards': ('Awards', '/en/awards/'),
        'prensa': ('Press' if english else 'Prensa', '/en/press/' if english else '/prensa/'),
        'press': ('Press', '/en/press/'),
        'contacto': ('Contact' if english else 'Contacto', '/en/contact/' if english else '/contacto/'),
        'contact': ('Contact', '/en/contact/'),
        'buscar': ('Search' if english else 'Buscar', '/en/search/' if english else '/buscar/'),
        'search': ('Search', '/en/search/'),
    }
    parts = [part for part in path.split('/') if part]
    for part in parts:
        if part in sections:
            return sections[part]
    return None


def breadcrumbs(data):
    path = data['path']
    english = data['language'].startswith('en')
    if path in ('/', '/en/'):
        return None
    items = [{
        '@type': 'ListItem',
        'position': 1,
        'name': 'Home' if english else 'Inicio',
        'item': SITE + ('/en/' if english else '/'),
    }]
    section = section_info(path, english)
    if section:
        items.append({
            '@type': 'ListItem',
            'position': 2,
            'name': section[0],
            'item': SITE + section[1],
        })
    is_project = '/proyectos/' in path or '/en/projects/' in path
    listing = path in ('/proyectos/', '/en/projects/')
    if is_project and not listing:
        items.append({
            '@type': 'ListItem',
            'position': len(items) + 1,
            'name': data['heading'],
            'item': data['canonical'],
        })
    if len(items) == 1:
        items[-1]['name'] = data['heading'] or (section[0] if section else data['title'])
        items[-1]['item'] = data['canonical']
    return {
        '@type': 'BreadcrumbList',
        '@id': data['canonical'] + '#breadcrumb',
        'itemListElement': items,
    }


def specs(source):
    result = {}
    for label, value in re.findall(
            r'<div[^>]*class="[^"]*\bspec-row\b[^"]*"[^>]*>\s*'
            r'<dt[^>]*>(.*?)</dt>\s*<dd[^>]*>(.*?)</dd>\s*</div>',
            source, re.I | re.S):
        result[plain(label).lower()] = plain(value)
    return result


def project_work(source, data):
    fields = specs(source)
    english = data['language'].startswith('en')

    def field(*names):
        for name in names:
            if name in fields:
                return fields[name]
        return ''

    year = field('ano', 'año', 'year')
    location = field('ubicacion', 'ubicación', 'location')
    country = field('pais', 'país', 'country')
    genre = field('tipo', 'type')
    state = field('estado', 'status')
    place_parts = [location] if location else []
    if country and country.lower() not in location.lower():
        place_parts.append(country)
    place_name = ', '.join(place_parts)
    work = {
        '@type': 'CreativeWork',
        '@id': data['canonical'] + '#project',
        'name': data['heading'],
        'headline': data['heading'],
        'description': data['description'],
        'url': data['canonical'],
        'inLanguage': 'en' if english else 'es-AR',
        'creator': {'@id': ORG_ID},
        'copyrightHolder': {'@id': ORG_ID},
    }
    if data['image']:
        work['image'] = data['image']
    if year:
        work['temporalCoverage'] = year
    if genre:
        work['genre'] = genre
    if state:
        work['creativeWorkStatus'] = state
    if place_name:
        work['spatialCoverage'] = {'@type': 'Place', 'name': place_name}
    return work


def project_items(source, data):
    english = data['language'].startswith('en')
    prefix = '/en/projects/' if english else '/proyectos/'
    found = []
    seen = set()
    for href in re.findall(r'href="(' + re.escape(prefix) + r'[^"#?]+/?)"', source):
        href = href if href.endswith('/') else href + '/'
        if href == prefix or href in seen:
            continue
        seen.add(href)
        slug = href.rstrip('/').split('/')[-1]
        project_file = os.path.join(ROOT, 'en', 'projects', slug, 'index.html') if english else os.path.join(ROOT, 'proyectos', slug, 'index.html')
        name = slug.replace('-', ' ').title()
        if os.path.exists(project_file):
            project_source = read(project_file)
            name = plain(one(r'<h1[^>]*>(.*?)</h1>', project_source, name))
        found.append({
            '@type': 'ListItem',
            'position': len(found) + 1,
            'name': name,
            'url': SITE + href,
        })
    return found


def page_type(path):
    if path in ('/estudio/', '/en/studio/'):
        return 'AboutPage'
    if path in ('/contacto/', '/en/contact/'):
        return 'ContactPage'
    if path in ('/proyectos/', '/en/projects/', '/premios/', '/en/awards/',
                '/prensa/', '/en/press/'):
        return 'CollectionPage'
    if path in ('/buscar/', '/en/search/'):
        return 'SearchResultsPage'
    return 'WebPage'


def graph_for(source):
    data = page_data(source)
    # La entidad completa vive una sola vez, en la portada canonica. El resto
    # de las paginas la referencia por @id; asi no hay 140 copias que puedan
    # divergir cuando cambia un telefono, una direccion o una red social.
    graph = []
    if data['path'] == '/':
        graph.extend([organization('es'), website('es')])
    crumb = breadcrumbs(data)
    if crumb:
        graph.append(crumb)

    page = {
        '@type': page_type(data['path']),
        '@id': data['canonical'] + '#webpage',
        'url': data['canonical'],
        'name': data['title'],
        'headline': data['heading'],
        'description': data['description'],
        'inLanguage': 'en' if data['language'].startswith('en') else 'es-AR',
        'isPartOf': {'@id': SITE_ID},
        'about': {'@id': ORG_ID},
    }
    if data['image']:
        page['primaryImageOfPage'] = {'@type': 'ImageObject', 'url': data['image']}
    if crumb:
        page['breadcrumb'] = {'@id': crumb['@id']}

    is_project = ('/proyectos/' in data['path'] or '/en/projects/' in data['path'])
    listing = data['path'] in ('/proyectos/', '/en/projects/')
    if is_project and not listing:
        project = project_work(source, data)
        page['mainEntity'] = {'@id': project['@id']}
        graph.extend([page, project])
    else:
        if listing:
            items = project_items(source, data)
            page['mainEntity'] = {
                '@type': 'ItemList',
                '@id': data['canonical'] + '#projects',
                'numberOfItems': len(items),
                'itemListElement': items,
            }
        graph.append(page)
    return {'@context': 'https://schema.org', '@graph': graph}


def strip_schema(source):
    source = re.sub(
        r'(?ms)^[ \t]*' + re.escape(START) + r'.*?'
        r'^[ \t]*' + re.escape(END) + r'[ \t]*\r?\n?',
        '', source)
    # La portada tenia un schema manual anterior al generador. Una vez que esta
    # herramienta existe, hay una sola fuente para evitar entidades duplicadas.
    source = re.sub(
        r'(?ims)^[ \t]*<script\s+type="application/ld\+json"[^>]*>.*?'
        r'</script>[ \t]*\r?\n?',
        '', source)
    return source


def inject(path):
    source = strip_schema(read(path))
    data = page_data(source)
    if not data['canonical']:
        return False
    # El JSON va compacto: son datos para maquinas y aparece en 140 paginas.
    # Mantenerlo en una linea reduce mucho el peso del repo y de cada respuesta.
    payload = json.dumps(graph_for(source), ensure_ascii=False,
                         separators=(',', ':'))
    block = '  %s\n  <script type="application/ld+json">%s</script>\n  %s\n' % (
        START,
        payload,
        END,
    )
    updated = source.replace('</head>', block + '</head>', 1)
    write(path, updated)
    return True


def main():
    paths = sorted(
        path for path in glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True)
        if not any(part in ('admin', 'docs', 'node_modules')
                   for part in os.path.relpath(path, ROOT).split(os.sep))
    )
    changed = sum(1 for path in paths if inject(path))
    print('schema SEO generado en %d paginas publicas' % changed)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
