# -*- coding: utf-8 -*-
"""Enlaza cada premio con la obra premiada.

La pagina de premios listaba el galardon pero no decia por que obra se
gano, que es lo primero que quiere saber quien la mira. El dato estaba en
la pagina "Premios & News" del WordPress viejo.

Solo entran los premios donde el texto original nombra la obra sin lugar a
dudas. Los demas quedan como estan: es preferible un premio sin obra que
un premio atribuido a la obra equivocada.

    python docs/premios_obras.py
"""
import io, re

# (año, fragmento del nombre del premio) -> [(slug, titulo visible), ...]
# El slug puede ser None: son obras que el estudio premio pero que todavia
# no estan en el sitio (les faltan fotos), asi que se nombran sin enlazar.
MAPA = {
    ('2025', 'LIV Hospitality'):      [('movistar-arena', 'Movistar Arena')],
    ('2024', 'Hospitality Design'):   [('manduca', 'Mercado Manduca')],
    ('2024', 'ARCH FADEA'):           [('manduca', 'Mercado Manduca')],
    ('2023', 'Surface Design'):       [('moshu', 'Moshu'), ('cien', 'Cien'),
                                       ('manduca', 'Mercado Manduca')],
    ('2022', 'Bienal Internacional'): [('kavak-hub', 'Kavak Hub'), ('fogon', 'Fogón')],
    ('2022', 'Prix Versailles'):      [('moshu', 'Moshu')],
    ('2018', 'Accor Hotels'):         [('novotel', 'Novotel')],
    ('2018', 'Next Landmark'):        [('goodsten', 'Goodsten')],
    ('2014', 'Next Landmark'):        [('dos-casas-conde', 'Dos casas Conde'),
                                       (None, 'PH Loft Arias')],
    ('2014', 'Restaurant & Bar'):     [('victoria-brown', 'Victoria Brown')],
    ('2023', 'German Design'):        [('osten', 'Osten')],
    ('2023', 'Restaurant & Bar'):     [('benedetta', 'Benedetta')],

    # Del CV extendido que mando el estudio, que nombra la obra de cada uno.
    ('2026', 'A+ Awards'):            [('movistar-arena', 'Movistar Arena')],
    ('2025', 'ARCH FADEA'):           [('manduca', 'Mercado Manduca')],
    ('2023', 'A+ Awards'):            [('manduca', 'Mercado Manduca')],
    ('2022', 'Bienal SCA'):           [('fogon', 'Fogón'), ('mamba-bar', 'Mamba Bar')],
    ('2021', 'Restaurant & Bar'):     [('osten', 'Osten')],
    ('2020', 'IIDA'):                 [('goodsten', 'Goodsten')],
    ('2020', 'Restaurant & Bar'):     [('fogon', 'Fogón')],
    ('2020', 'Society of British'):   [('mamba-bar', 'Mamba Bar')],
    ('2019', 'Prix Versailles'):      [('nim-bar', 'The Nim Bar')],
    # Ese año hay dos filas del mismo premio y el CV las distingue: Mamba
    # gano mejor bar de America y Nim quedo finalista.
    ('2019', 'Restaurant & Bar', 'Ganador'):   [('mamba-bar', 'Mamba Bar')],
    ('2019', 'Restaurant & Bar', 'Finalista'): [('nim-bar', 'The Nim Bar')],
    ('2014', 'Premios BIAR'):         [('atelier-vilela', 'Atelier Vilela')],
    ('2010', 'Bienal SCA'):           [(None, 'PH El Salvador')],
    ('2008', 'Bienal SCA'):           [(None, 'Galería de arte Objeto A')],
}

# Que se premio, en una linea. Sale del texto que el estudio publico en la
# pagina "Premios & News" del sitio anterior, resumido.
DESCRIPCION = {
    ('2025', 'LIV Hospitality'):
        'Diseño arquitectónico en espacios para eventos.',
    ('2024', 'Hospitality Design'):
        'Finalista entre 925 candidaturas.',
    ('2024', 'ARCH FADEA'):
        '3er puesto en la etapa regional CABA, categoría obra privada de escala media.',
    ('2024', 'Clarín ARQ'):
        '2do puesto en la categoría diseño interior.',
    ('2023', 'Surface Design'):
        'Ganadores en edificio comercial interior, estructura temporal y paisaje y espacio público.',
    ('2023', 'German Design'):
        'Mención especial en excelencia de arquitectura y diseño interior.',
    ('2023', 'Restaurant & Bar'):
        'Finalista en la categoría Américas.',
    ('2022', 'Bienal Internacional'):
        'Seleccionados en la categoría interiorismo.',
    ('2022', 'Prix Versailles'):
        'Mención en la categoría restaurante, premio especial exterior de Centroamérica y Sudamérica.',
    ('2020', 'IIDA'):
        'Mejor firma en la especialidad comercial e industrial de diseño interior.',
    ('2018', 'Accor Hotels'):
        'Primer premio del concurso internacional, entre más de 50 estudios de América Latina.',
    ('2018', 'Next Landmark'):
        'Mención en interiorismo de hotelería y en Landmark of the Year.',
    ('2014', 'Next Landmark'):
        'Mención en Landmark of the Year.',
    ('2014', 'Restaurant & Bar'):
        'Preseleccionada como mejor bar de América.',
}

FILA = re.compile(r'(?s)(<div class="award-year-block" data-year="(\d+)">.*?)'
                  r'(?=<div class="award-year-block"|</div>\s*</div>\s*</section>)')
NOMBRE = re.compile(r'(<div class="award-row__name">)(.*?)(</div>)')


def main():
    p = 'premios/index.html'
    h = io.open(p, encoding='utf-8').read()
    if 'award-row__obra' in h:
        print('los premios ya tienen la obra enlazada')
        return

    puestos = []

    def por_anio(mb):
        anio = mb.group(2)

        def por_nombre(mn):
            nom = mn.group(2)
            # El resultado (Ganador / Finalista) desempata cuando el mismo
            # premio aparece dos veces en el mismo año.
            mres = re.search(r'award-row__res">(.*?)</div>',
                             mb.group(1)[mn.end(3):])
            res = mres.group(1).strip() if mres else ''
            if 'award-row__obra' in nom or 'award-row__desc' in nom:
                return mn.group(0)
            extra = ''
            for (a, frag), texto in DESCRIPCION.items():
                if a == anio and frag.lower() in nom.lower():
                    extra += '<span class="award-row__desc">%s</span>' % texto
                    break
            for clave, obras in MAPA.items():
                a, frag = clave[0], clave[1]
                if a != anio or frag.lower() not in nom.lower():
                    continue
                if len(clave) == 3 and clave[2].lower() not in res.lower():
                    continue
                enlaces = ' · '.join(
                    ('<a href="/proyectos/%s/">%s</a>' % (s, t) if s else t)
                    for s, t in obras)
                extra += '<span class="award-row__obra">%s</span>' % enlaces
                puestos.append((anio, nom[:34], ', '.join(t for _, t in obras)))
                break
            if not extra:
                return mn.group(0)
            return mn.group(1) + nom + extra + mn.group(3)

        return NOMBRE.sub(por_nombre, mb.group(1))

    h2 = FILA.sub(por_anio, h)
    if h2 == h:
        print('no se modifico nada: revisar los selectores')
        return
    io.open(p, 'w', encoding='utf-8').write(h2)
    for a, nom, obras in puestos:
        print('  %-6s %-36s -> %s' % (a, nom, obras))
    print('\npremios enlazados: %d de 31' % len(puestos))


if __name__ == '__main__':
    main()
