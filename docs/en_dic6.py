# -*- coding: utf-8 -*-
"""Sexta capa del diccionario del espejo en ingles.

Lo que trajo la segunda tanda de obras del Drive: PH El Salvador, PH Loft
Arias, Oficina + casa Luna y Galeria Objeto A. Son fichas de vivienda,
oficinas y cultura que suman tipos y superficies nuevas al sitio.
"""
import en_dic5
from en_dic import DIC

DIC.update({
    # --- tipo de obra ---
    'Vivienda': 'Housing',
    'Oficina y vivienda': 'Office and housing',
    'Galería de arte': 'Art gallery',
    'Galería Objeto A': 'Objeto A Art Gallery',
    'Galería de arte Objeto A': 'Objeto A Art Gallery',

    # --- superficies de las tarjetas ---
    '250 m² cubiertos': '250 m² covered',
    '126 m² cubiertos': '126 m² covered',
    '150 m² cubiertos': '150 m² covered',
    '253,3 m² cubiertos': '253.3 m² covered',
    '253,3 m² cubiertos · 52,1 m² descubiertos':
        '253.3 m² covered · 52.1 m² uncovered',

    # --- bajadas ---
    'Una oficina y una casa en un mismo edificio, sobre la calle Luna.':
        'An office and a house in a single building, on Luna street.',
    'Un PH de cuatro ambientes con piscina en Palermo, Buenos Aires.':
        'A four-room PH with a pool in Palermo, Buenos Aires.',
    'Un loft con quincho de 150 m² en Buenos Aires.':
        'A 150 m² loft with a barbecue house in Buenos Aires.',
    'Una galería de arte de 253 m² en Palermo, Buenos Aires.':
        'A 253 m² art gallery in Palermo, Buenos Aires.',
})

traducir = en_dic5.traducir
