# -*- coding: utf-8 -*-
"""Completa descripciones recuperadas del WordPress y los CV del estudio.

La Bienal SCA-CPAU 2014 queda sin descripcion porque las fuentes solo la
enumeran como finalista y no identifican una obra ni una categoria.

    python docs/premios_descripciones.py
"""

import io


ES = [
    ('2026', 'A+ Awards', 'Mención especial',
     'Mención especial para Movistar Arena en la categoría Commercial Interiors.', None),
    ('2025', 'Premios Nacionales ARCH FADEA', 'Finalista',
     'Mercado Manduca obtuvo el 3er puesto en la etapa regional CABA, categoría obra privada de escala media.', None),
    ('2023', 'A+ Awards', 'Mención especial',
     'Mención especial para Mercado Manduca en la categoría Commercial Renovations & Additions.', None),
    ('2022', 'Bienal SCA-CPAU', 'Finalista',
     'Fogón fue reconocido en arquitectura construida en el extranjero y Mamba Bar en arquitectura comercial e interiorismo.', None),
    ('2022', 'Society of British', 'Finalista',
     'Osten fue finalista en los SBID International Design Awards.',
     '<a href="/proyectos/osten/">Osten</a>'),
    ('2021', 'A+Firms', 'Finalista',
     'El estudio fue finalista en la categoría Interior Design — Commercial.', None),
    ('2021', 'Restaurant & Bar', 'Ganador',
     'Osten fue reconocido en la categoría mejor restaurante y bar independiente de América.', None),
    ('2020', 'Restaurant & Bar', 'Finalista',
     'Fogón fue finalista como mejor restaurante de Medio Oriente y África.', None),
    ('2020', 'Society of British', 'Finalista',
     'Mamba Bar fue finalista en la categoría mejor restaurante de diseño del mundo.', None),
    ('2019', 'Prix Versailles', 'Finalista',
     'The Nim Bar fue finalista del premio especial de diseño interior para restaurantes de Centroamérica, Sudamérica y el Caribe.', None),
    ('2019', 'Restaurant & Bar', 'Ganador',
     'Mamba Bar fue ganador como mejor bar de América.', None),
    ('2019', 'Restaurant & Bar', 'Finalista',
     'The Nim Bar fue finalista como mejor bar de América.', None),
    ('2014', 'Premios BIAR', 'Finalista',
     'Atelier Vilela fue seleccionada como finalista de la Bienal Argentina de Arquitectura.', None),
    ('2010', 'Bienal SCA-CPAU', 'Finalista',
     'Casa PH El Salvador fue seleccionada como obra finalista.', None),
    ('2008', 'Bienal SCA-CPAU', 'Finalista',
     'Galería de arte Objeto A fue seleccionada como obra finalista.', None),
]

EN = [
    ('2026', 'A+ Awards', 'Special mention',
     'Special Mention for Movistar Arena in the Commercial Interiors category.', None),
    ('2025', 'ARCH FADEA National Awards', 'Finalist',
     'Mercado Manduca received third place in the CABA regional stage, medium-scale private project category.', None),
    ('2023', 'A+ Awards', 'Special mention',
     'Special Mention for Mercado Manduca in the Commercial Renovations & Additions category.', None),
    ('2022', 'Bienal SCA-CPAU', 'Finalist',
     'Fogón was recognised in architecture built abroad and Mamba Bar in commercial architecture and interior design.', None),
    ('2022', 'Society of British', 'Finalist',
     'Osten was a finalist at the SBID International Design Awards.',
     '<a href="/en/projects/osten/">Osten</a>'),
    ('2021', 'A+Firms', 'Finalist',
     'The studio was a finalist in the Interior Design — Commercial category.', None),
    ('2021', 'Restaurant & Bar', 'Winner',
     'Osten was recognised in the Best Independent Restaurant and Bar in the Americas category.', None),
    ('2020', 'Restaurant & Bar', 'Finalist',
     'Fogón was a finalist for Best Restaurant in the Middle East and Africa.', None),
    ('2020', 'Society of British', 'Finalist',
     'Mamba Bar was a finalist in the World’s Best Designed Restaurant category.', None),
    ('2019', 'Prix Versailles', 'Finalist',
     'The Nim Bar was a finalist for the Special Prize for Restaurant Interior Design in Central America, South America and the Caribbean.', None),
    ('2019', 'Restaurant & Bar', 'Winner',
     'Mamba Bar won Best Bar in the Americas.', None),
    ('2019', 'Restaurant & Bar', 'Finalist',
     'The Nim Bar was a finalist for Best Bar in the Americas.', None),
    ('2014', 'Premios BIAR', 'Finalist',
     'Atelier Vilela was selected as a finalist at the Argentine Architecture Biennial.', None),
    ('2010', 'Bienal SCA-CPAU', 'Finalist',
     'Casa PH El Salvador was selected as a finalist.', None),
    ('2008', 'Bienal SCA-CPAU', 'Finalist',
     'Galería de arte Objeto A was selected as a finalist.', None),
]


def read(path):
    return io.open(path, encoding='utf-8').read()


def write(path, content):
    io.open(path, 'w', encoding='utf-8', newline='').write(content)


def find_row(content, year, name, result):
    marker = '<div class="award-year-block" data-year="%s"' % year
    year_start = content.index(marker)
    year_end = content.find('<div class="award-year-block" data-year="',
                            year_start + len(marker))
    if year_end < 0:
        year_end = len(content)

    cursor = year_start
    while True:
        name_pos = content.find('<div class="award-row__name">', cursor, year_end)
        if name_pos < 0:
            raise ValueError('No se encontro %s %s %s' % (year, name, result))
        name_end = content.find('</div>', name_pos) + len('</div>')
        visible_name = content[name_pos:name_end]
        row_end = content.find('<div class="award-row">', name_end, year_end)
        if row_end < 0:
            row_end = year_end
        row = content[name_pos:row_end]
        if name in visible_name and ('award-row__res">%s</div>' % result) in row:
            return name_end, row_end
        cursor = name_end


def update(path, entries):
    content = read(path)
    changed = 0
    for year, name, result, description, work in entries:
        name_end, row_end = find_row(content, year, name, result)
        row = content[name_end:row_end]
        if 'award-row__desc' not in row:
            addition = '\n                  <span class="award-row__desc">%s</span>' % description
            if work and 'award-row__obra' not in row:
                addition += '\n                  <span class="award-row__obra">%s</span>' % work
            content = content[:name_end] + addition + content[name_end:]
            changed += 1
    if changed:
        write(path, content)
    return changed


def main():
    es = update('premios/index.html', ES)
    en = update('en/awards/index.html', EN)
    print('descripciones agregadas: ES=%d EN=%d' % (es, en))


if __name__ == '__main__':
    main()
