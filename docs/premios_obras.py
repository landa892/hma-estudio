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
    ('2014', 'Next Landmark'):        [('dos-casas-conde', 'Dos casas Conde')],
    ('2014', 'Restaurant & Bar'):     [('victoria-brown', 'Victoria Brown')],
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
            for (a, frag), obras in MAPA.items():
                if a != anio or frag.lower() not in nom.lower():
                    continue
                if 'award-row__obra' in nom:
                    continue
                enlaces = ' · '.join(
                    '<a href="/proyectos/%s/">%s</a>' % (s, t) for s, t in obras)
                puestos.append((anio, nom[:34], ', '.join(t for _, t in obras)))
                return (mn.group(1) + nom +
                        '<span class="award-row__obra">%s</span>' % enlaces +
                        mn.group(3))
            return mn.group(0)

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
