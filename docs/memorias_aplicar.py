# -*- coding: utf-8 -*-
"""Mete la memoria descriptiva de cada obra en su pagina.

El texto lo escribio el estudio y estaba en el WordPress viejo. El mapa de
abajo es explicito a proposito: se armo obra por obra confirmando la
direccion, porque emparejar por nombre cruza mal ("Malita" con "Edificio
Malabia", "Lucciano's Olivos" con el de Caballito).

Las obras que no figuran en el mapa quedan como estan.
"""
import io, json, os, re, html

RAIZ = os.environ['HMA_RAIZ']

# slug del sitio -> titulo en el WordPress. Cada linea se confirmo cotejando
# la direccion de la obra contra la del WordPress.
MAPA = {
    'aire-libre': 'Aire Libre',
    'araoz': 'Edificio Araoz',
    'atelier-vilela': 'Atelier Vilela',
    'benedetta': 'Benedetta',
    'bienal-venecia': 'Sinapsis - Pabellón Argentino para Venecia',
    'bolivar': 'Edificio Bolivar',
    'cafe-artois': 'Cafe Artois',
    'cien': 'Cien',
    'dos-casas-conde': 'Dos casas conde',
    'edificio-del-plata': 'Edificio Del Plata',
    'fehgra': 'Fehgra',
    'fogon': 'Fogon',
    'fresco': 'Fresco',
    'goodsten': 'Goodsten',
    'hausscape': 'Hausscape',
    'juan-valdez': 'Juan Valdez',
    'kavak-hub': 'Kavak Hub',
    'kavak-oficinas': 'Kavak',
    'malabia': 'Edificio Malabia',
    'mamba-bar': 'Mamba Bar',
    'manduca': 'Mercado Manduca',
    'moshu': 'Moshu Treehouse',
    'movistar-arena': 'Movistar Arena VIP Lounges',
    'nim-bar': 'The Nim Bar',
    'osten': 'Osten',
    'osten-tower': 'Osten Tower',
    'people': 'People',
    'plaza-mateo': 'Plaza Mateo',
    'uala-office': 'Ualá',
    'victoria-brown': 'Victoria Brown',
    'williamsburg': 'Willamsburg',
}

# Erratas del texto original. Lista corta y explicita: no se toca nada que
# no este aca, para no "corregir" decisiones de estilo del estudio.
ERRATAS = [
    ('somo símbolo', 'como símbolo'),
    ('la primer gran', 'la primera gran'),
    ('El proyecto esta desarrollado', 'El proyecto está desarrollado'),
    ('recurrir materiales', 'recurrir a materiales'),
    ('la atmosfera', 'la atmósfera'),
    ('los ladrillos muto', 'los ladrillos mutó'),
    ('nos conformo', 'nos conformó'),
    ('para al modelo', 'para el modelo'),
    ('Se realizo una', 'Se realizó una'),
    ('se logro una', 'se logró una'),
    ('resulto un complejo', 'resultó un complejo'),
    ('  ', ' '),
]

ES = re.compile(r'(?i)(?<![a-z])(que|para|como|espacio|desde|del|los|las|una|'
                r'con|fue|por)(?![a-z])')
EN = re.compile(r'(?i)(?<![a-z])(the|and|with|from|which|space|our|this|was|'
                r'were)(?![a-z])')


def castellano(o):
    t = ' '.join(o['memoria'])
    return len(ES.findall(t)) > len(EN.findall(t))


def limpiar(p):
    p = ' '.join(p.split())
    for mal, bien in ERRATAS:
        p = p.replace(mal, bien)
    return p.strip()


def bloque(parrafos):
    ps = [limpiar(p) for p in parrafos]
    ps = [p for p in ps if len(p) > 40]
    if not ps:
        return None
    cuerpo = '\n'.join(
        '          <p>%s</p>' % html.escape(p, quote=False) for p in ps)
    # Con dos parrafos o menos no hay nada que plegar.
    plegable = len(ps) > 2
    abierta = '' if plegable else ' is-open'
    boton = ''
    if plegable:
        boton = ('\n        <button class="memoria-more gallery-more" type="button"\n'
                 '          data-mas="Seguir leyendo" data-menos="Leer menos"\n'
                 '          aria-expanded="false">Seguir leyendo</button>')
    return ('\n    <section class="project-memoria">\n'
            '      <div class="container">\n'
            '        <div class="memoria-cuerpo%s reveal">\n%s\n        </div>%s\n'
            '      </div>\n'
            '    </section>\n' % (abierta, cuerpo, boton))


def main():
    wp = json.load(io.open('wp_obras.json', encoding='utf-8'))
    porti = {}
    for o in wp:
        if o['estado'] in ('publish', 'private') and o['n_parrafos'] >= 2 and castellano(o):
            t = o['titulo'].strip()
            if t not in porti or o['n_parrafos'] > porti[t]['n_parrafos']:
                porti[t] = o

    puestas = faltan = 0
    for slug, titulo in sorted(MAPA.items()):
        o = porti.get(titulo)
        if not o:
            print('  %-22s NO ESTA "%s" en el WordPress' % (slug, titulo))
            faltan += 1
            continue
        p = os.path.join(RAIZ, 'proyectos', slug, 'index.html')
        h = io.open(p, encoding='utf-8').read()
        if 'project-memoria' in h:
            print('  %-22s ya tenia memoria' % slug)
            continue
        b = bloque(o['memoria'])
        if not b:
            print('  %-22s memoria vacia' % slug)
            faltan += 1
            continue
        ancla = '\n    <section class="project-gallery">'
        if ancla not in h:
            print('  %-22s SIN galeria donde anclar' % slug)
            faltan += 1
            continue
        h = h.replace(ancla, b + ancla, 1)
        io.open(p, 'w', encoding='utf-8').write(h)
        n = len([x for x in o['memoria'] if len(limpiar(x)) > 40])
        print('  %-22s %2d parrafos  <- %s' % (slug, n, titulo))
        puestas += 1
    print('\nmemorias puestas: %d   sin poner: %d' % (puestas, faltan))


if __name__ == '__main__':
    main()
