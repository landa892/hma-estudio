# -*- coding: utf-8 -*-
"""Da de alta las obras que estaban en el sitio anterior y no en el nuevo.

Los datos salen de la exportacion del WordPress del estudio. La tabla de
abajo es explicita porque la categoria, el titulo que se muestra y la
bajada son decisiones y no se deducen del archivo: el campo "programa"
dice "food & fun" o "Icecream & coffee shop", que sirve como dato pero no
como texto de la pagina.

Solo entran obras que en el WordPress figuraban como publicadas. Las que
estaban privadas o en borrador no se tocan: que esten en el archivo no
significa que el estudio quiera mostrarlas.

    python docs/obras_alta.py
"""
import io, json, os, re, html

DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'obras_alta.json')

# slug -> lo que se muestra
FICHAS = {
    'abasto-patio-comidas': dict(
        titulo='Patio de Comidas Abasto', cat='gastronomico',
        tipo='Patio de comidas', pais='Argentina',
        lede='Los dos patios de comidas del Abasto Shopping, 1.594 m² de reforma integral en Buenos Aires.',
        sup='294 m² (Patio Zorzal) · 1.300 m² (Patio Central)'),
    'burger-7167': dict(
        titulo='7167 Burger', cat='gastronomico',
        tipo='Hamburguesería', pais='Argentina',
        lede='Una hamburguesería de 70 m² en Scalabrini Ortiz, Buenos Aires.',
        sup='70 m²'),
    'casa-olmo': dict(
        titulo='Casa Olmo', cat='gastronomico',
        tipo='Bar', pais='Argentina',
        lede='Un bar de 75 m² con patio en el centro de Ushuaia.',
        sup='75 m² cubiertos · 87 m² descubiertos'),
    'clasico-quilmes': dict(
        titulo='El Clásico de Quilmes', cat='gastronomico',
        tipo='Bar', pais='Argentina',
        lede='Un bar en dos niveles sobre Esmeralda, en el centro de Buenos Aires.',
        sup='60 m² planta baja · 71 m² subsuelo'),
    'elyaki': dict(
        titulo='Elyaki', cat='gastronomico',
        tipo='Parrilla y bar', pais='Argentina',
        lede='Una parrilla japonesa de 57 m² en Palermo, Buenos Aires.',
        sup='57 m²'),
    'galeria-objeto-a': dict(
        titulo='Galería de arte Objeto A', cat='cultural',
        tipo='Galería de arte', pais='Argentina',
        lede='Una galería de arte de 253 m² en Palermo, Buenos Aires.',
        sup='253,3 m² cubiertos · 52,1 m² descubiertos'),
    'hill-of-arts': dict(
        titulo='Hill of Arts', cat='hoteleria',
        tipo='Hotel', pais='Italia',
        lede='Un hotel en Villa Altissimo, sobre las colinas de Turín.',
        sup='283 m² de obra nueva · 1.490 m² de renovación · 386 m² descubiertos'),
    'luccianos-olivos': dict(
        titulo="Lucciano's Olivos", cat='gastronomico',
        tipo='Heladería y cafetería', pais='Argentina',
        lede='Una heladería y cafetería de 100 m² sobre Libertador, en Olivos.',
        sup='100 m²'),
    'malita': dict(
        titulo='Malita', cat='gastronomico',
        tipo='Bar', pais='Argentina',
        lede='Un bar con patio en el Paseo de la Buena Vista, sobre Libertador.',
        sup='90 m² planta baja · 136 m² exterior'),
    'oficina-casa-luna': dict(
        titulo='Oficina + casa Luna', cat='oficinas',
        tipo='Oficina y vivienda', pais='Argentina',
        lede='Una oficina y una casa en un mismo edificio, sobre la calle Luna.',
        sup='250 m² cubiertos · 100 m² descubiertos'),
    'ph-el-salvador': dict(
        titulo='PH El Salvador', cat='residencial',
        tipo='Vivienda', pais='Argentina',
        lede='Un PH de cuatro ambientes con piscina en Palermo, Buenos Aires.',
        sup='126 m² cubiertos · 63 m² descubiertos'),
    'ph-loft-arias': dict(
        titulo='PH Loft Arias', cat='residencial',
        tipo='Vivienda', pais='Argentina',
        lede='Un loft con quincho de 150 m² en Buenos Aires.',
        sup='150 m² cubiertos · 100 m² descubiertos'),
    'stella-artois-mercat': dict(
        titulo='Stella Artois Mercat', cat='gastronomico',
        tipo='Barra', pais='Argentina',
        lede='Una barra de 15 m² para Stella Artois en el Mercat de Villa Crespo.',
        sup='15 m²'),
    'the-birra': dict(
        titulo='The Birra', cat='gastronomico',
        tipo='Almacén de bebidas', pais='Argentina',
        lede='Un almacén de bebidas en dos niveles en el centro de Ushuaia.',
        sup='38 m² planta baja · 53 m² primer piso'),
}

E = lambda s: html.escape(str(s or ''), quote=False)


# El campo del WordPress no siempre trae la direccion separada por comas
# ("Avenida del Libertador 3883 - Paseo de la Infanta -Buenos Aires"), asi
# que donde no se puede partir bien se escribe a mano.
A_MANO = {
    'malita': ('Av. del Libertador 3883, Paseo de la Infanta, Buenos Aires', 'Buenos Aires'),
    'luccianos-olivos': ('Av. del Libertador, Olivos, Buenos Aires', 'Olivos'),
    'the-birra': ('Roca 63, Ushuaia', 'Ushuaia'),
    'casa-olmo': ('Av. San Martín 86, Ushuaia', 'Ushuaia'),
    'hill-of-arts': ('Villa Altissimo, Turín', 'Turín'),
}


def ciudad(direccion):
    p = [x.strip() for x in (direccion or '').replace('.', '').split(',') if x.strip()]
    return p[-1] if p else ''


def bloque_memoria(parrafos):
    if not parrafos:
        return ''
    cuerpo = '\n'.join('          <p>%s</p>' % E(p) for p in parrafos)
    plegable = len(parrafos) > 2
    boton = ''
    if plegable:
        boton = ('\n        <button class="memoria-more gallery-more" type="button"\n'
                 '          data-mas="Seguir leyendo" data-menos="Leer menos"\n'
                 '          aria-expanded="false">Seguir leyendo</button>')
    return ('\n    <section class="project-memoria">\n'
            '      <div class="container">\n'
            '        <div class="memoria-cuerpo%s reveal">\n%s\n        </div>%s\n'
            '      </div>\n'
            '    </section>\n' % ('' if plegable else ' is-open', cuerpo, boton))


VISIBLES_GRILLA = 6   # las demas entran con el boton, igual que el resto del sitio


def bloque_filas(slug, titulo, fotos):
    """Las primeras fotos a lo ancho, antes de la grilla."""
    if not fotos:
        return '\n'
    trozos = []
    for f in fotos[:3]:
        eager = (' loading="eager" decoding="async" fetchpriority="high"'
                 if f['n'] == 1 else ' loading="lazy" decoding="async"')
        trozos.append(
            '      <div class="project-row project-row--sola reveal">\n'
            '        <div class="project-row__photo"><img src="/assets/gallery/%s/%d.webp" '
            'width="%d" height="%d" alt="%s — foto %d"%s></div>\n      </div>\n'
            % (slug, f['n'], f['w'], f['h'], E(titulo), f['n'], eager))
    return ('\n    <section class="project-gallery">\n%s    </section>\n'
            % '\n'.join(trozos))


def bloque_grilla(slug, titulo, fotos):
    """La seccion "Todas las fotos", con el boton que despliega el resto."""
    if not fotos:
        return '\n'
    items = '\n'.join(
        '          <figure class="gallery-grid__item%s"><img src="/assets/gallery/%s/%d.webp" '
        'alt="%s — foto %d" loading="lazy" decoding="async"></figure>'
        % ('' if i < VISIBLES_GRILLA else ' is-extra', slug, f['n'], E(titulo), f['n'])
        for i, f in enumerate(fotos))
    boton = ''
    if len(fotos) > VISIBLES_GRILLA:
        boton = ('\n        <button type="button" class="btn gallery-more" data-total="%d" '
                 'data-mas="Ver las %d fotos" data-menos="Ver menos fotos" '
                 'aria-expanded="false">Ver las %d fotos</button>'
                 % (len(fotos), len(fotos), len(fotos)))
    return ('\n    <section class="section no-border" id="galeria">\n'
            '      <div class="container">\n'
            '        <div class="section-head"><div><span class="eyebrow">Galería</span>'
            '<h2 class="display-3 mt-10">Todas las fotos</h2></div></div>\n'
            '        <div class="gallery-grid reveal">\n%s\n        </div>%s\n'
            '      </div>\n    </section>\n' % (items, boton))


def pagina(molde, slug, f, campos, parrafos, fotos):
    """Parte del molde de una ficha existente y le cambia lo propio."""
    t, lede = f['titulo'], f['lede']
    dir_ = html.unescape(campos.get('direccion', '') or '').replace('\n', ' ').strip(' .')
    ciu = ciudad(dir_)
    if slug in A_MANO:
        dir_, ciu = A_MANO[slug]
    anio = (campos.get('fecha', '') or '').replace('-', '–')
    meta = ('<div class="project-meta-row"><span>%s</span><span>%s</span>'
            '<span>%s</span><span>%s</span></div>'
            % (E(f['tipo']), E(ciu), E(f['sup'].split(' · ')[0]), E(anio)))
    especs = '\n'.join([
        '          <div class="spec-row"><dt>Tipo</dt><dd>%s</dd></div>' % E(f['tipo']),
        '          <div class="spec-row"><dt>Ubicación</dt><dd>%s</dd></div>' % E(dir_),
        '          <div class="spec-row"><dt>País</dt><dd>%s</dd></div>' % E(f['pais']),
        '          <div class="spec-row"><dt>Superficie</dt><dd>%s</dd></div>' % E(f['sup']),
        '          <div class="spec-row"><dt>Año</dt><dd>%s</dd></div>' % E(anio)])

    h = molde
    # cabecera
    h = re.sub(r'<title>.*?</title>', '<title>%s | Hitzig Militello Arquitectos</title>' % E(t), h)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + E(lede) + m.group(2), h)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
               lambda m: m.group(1) + E(t) + ' | Hitzig Militello Arquitectos' + m.group(2), h)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1) + E(lede) + m.group(2), h)
    h = h.replace('/assets/gallery/benedetta/1.webp', '/assets/gallery/%s/1.webp' % slug)
    h = h.replace('/proyectos/benedetta/', '/proyectos/%s/' % slug)
    h = h.replace('/en/projects/benedetta/', '/en/projects/%s/' % slug)
    # cabecera de la ficha
    h = re.sub(r'<span class="eyebrow">.*?</span>', '<span class="eyebrow">%s</span>' % E(NOMBRE_CAT[f['cat']]), h, count=1)
    h = re.sub(r'<h1 class="display-2 mt-14">.*?</h1>', '<h1 class="display-2 mt-14">%s</h1>' % E(t), h, count=1)
    h = re.sub(r'<p class="lede">.*?</p>', '<p class="lede">%s</p>' % E(lede), h, count=1)
    h = re.sub(r'(?s)<div class="project-meta-row">.*?</div>', meta, h, count=1)
    h = re.sub(r'(?s)(<dl class="project-specs">).*?(\n\s*</dl>)',
               lambda m: m.group(1) + '\n' + especs + m.group(2), h, count=1)
    # cuerpo
    h = re.sub(r'(?s)\n    <section class="project-memoria">.*?\n    </section>\n',
               bloque_memoria(parrafos) or '\n', h, count=1)
    h = re.sub(r'(?s)\n    <section class="project-gallery">.*?\n    </section>\n',
               lambda _: bloque_filas(slug, t, fotos), h, count=1)
    h = re.sub(r'(?s)\n    <section class="section no-border" id="galeria">.*?\n    </section>\n',
               lambda _: bloque_grilla(slug, t, fotos), h, count=1)
    if 'benedetta' in h:
        raise SystemExit('%s: quedo una referencia al molde' % slug)
    return h


NOMBRE_CAT = {'gastronomico': 'Gastronómico', 'hoteleria': 'Hotelería & Comercial',
              'residencial': 'Residencial', 'oficinas': 'Oficinas',
              'cultural': 'Cultural & Institucional'}


def main():
    d = json.load(io.open(DATOS, encoding='utf-8'))
    molde = io.open('proyectos/benedetta/index.html', encoding='utf-8').read()
    hechas, sin_foto = [], []
    for slug in sorted(FICHAS):
        o = d.get(slug)
        if not o:
            print('  %-22s sin datos' % slug); continue
        fotos = o.get('galeria') or []
        if not fotos:
            sin_foto.append(slug)
            print('  %-22s SIN FOTOS, no se crea' % slug)
            continue
        dest = os.path.join('proyectos', slug)
        # Una obra ya publicada no se vuelve a generar: despues del alta la
        # pagina recibe planos, portada del Drive y correcciones de ficha que
        # el molde no conoce, y rehacerla las borraria sin avisar.
        if os.path.isfile(os.path.join(dest, 'index.html')):
            print('  %-22s ya publicada, no se toca' % slug); continue
        os.makedirs(dest, exist_ok=True)
        h = pagina(molde, slug, FICHAS[slug], o['campos'], o['es'], fotos)
        io.open(os.path.join(dest, 'index.html'), 'w', encoding='utf-8').write(h)
        print('  %-22s %2d fotos  %2d parrafos' % (slug, len(fotos), len(o['es'])))
        hechas.append(slug)
    print('\naltas: %d   sin fotos: %s' % (len(hechas), ', '.join(sin_foto) or '—'))
    return hechas


if __name__ == '__main__':
    main()
