# -*- coding: utf-8 -*-
"""Corrige el estado de las obras segun el CV extendido del estudio.

El CV marca "En curso" trabajo por trabajo. El sitio tenia doce marcados
como obra concluida que ahi figuran en curso. La fuente es el propio
estudio, asi que manda el CV.

Los tres que quedan como proyecto sin estar en esa lista —accor-hotels,
cceba y edificio-del-plata— son concursos, no obras que se esten
construyendo: siguen siendo proyecto con razon.

Despues de correr esto hay que volver a correr obras_estado.py y
home_banners.py, que leen data-estado.

    python docs/obras_estado_cv.py
"""
import io, re

# slug del sitio -> como figura en el CV
EN_CURSO = {
    'indusparquet': 'Tienda insignia de Indusparquet (2026)',
    'cerveceria-austral': 'Restaurante Cervecería Austral – CCU (2026)',
    'juan-valdez': 'Juan Valdez, aeropuerto de Ezeiza (2026)',
    'templo-mikdash': 'Templo Mikdash (2025)',
    'osten-foa': 'Casa Foa (2025)',
    'parfumerie': 'Parfumerie, varias ubicaciones (2025)',
    'iol': 'IOL Supervielle (2025)',
    'osten-tower': 'Torre Osten (2025)',
    'aire-libre': 'Aire Libre (2024)',
    'novotel': 'Novotel (2024)',
    'hyatt-ziva': 'Hyatt Ziva (2024)',
    'roket': 'Roket (2024)',
    'people': 'People – Torre 9 de Julio (2022)',
    'plaza-mateo': 'Plaza Mateo (2022)',
    'tostado': 'Tostado Café Club, Midtown Miami (2021)',
}


def main():
    p = 'proyectos/index.html'
    h = io.open(p, encoding='utf-8').read()
    cambios, ya = [], []

    def cambiar(m):
        slug, est = m.group(1), m.group(2)
        nuevo = 'proyecto' if slug in EN_CURSO else est
        if slug in EN_CURSO and est == 'proyecto':
            if slug not in ya:
                ya.append(slug)
        elif nuevo != est:
            if slug not in cambios:
                cambios.append(slug)
        return 'data-slug="%s" data-estado="%s"' % (slug, nuevo)

    h = re.sub(r'data-slug="([^"]+)" data-estado="([^"]+)"', cambiar, h)
    io.open(p, 'w', encoding='utf-8').write(h)

    print('pasan a proyecto en proceso (%d):' % len(cambios))
    for s in cambios:
        print('   %-22s %s' % (s, EN_CURSO[s]))
    print('\nya estaban bien (%d): %s' % (len(ya), ', '.join(ya)))
    n = len(re.findall(r'data-estado="proyecto"', h)) // 2
    print('\ntotal en proceso: %d de 56' % n)


if __name__ == '__main__':
    main()
