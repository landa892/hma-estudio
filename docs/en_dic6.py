# -*- coding: utf-8 -*-
"""Sexta capa del diccionario del espejo en ingles.

Lo que trajo la segunda tanda de obras del Drive: PH El Salvador, PH Loft
Arias y Oficina + casa Luna. Son fichas de vivienda, un programa que el sitio
no tenia hasta ahora, asi que entran tipos y superficies nuevas.
"""
import en_dic5
from en_dic import DIC

DIC.update({
    # --- tipo de obra ---
    'Vivienda': 'Housing',
    'Oficina y vivienda': 'Office and housing',

    # --- superficies de las tarjetas ---
    '250 m² cubiertos': '250 m² covered',
    '126 m² cubiertos': '126 m² covered',
    '150 m² cubiertos': '150 m² covered',

    # --- bajadas ---
    'Una oficina y una casa en un mismo edificio, sobre la calle Luna.':
        'An office and a house in a single building, on Luna street.',
    'Un PH de cuatro ambientes con piscina en Palermo, Buenos Aires.':
        'A four-room PH with a pool in Palermo, Buenos Aires.',
    'Un loft con quincho de 150 m² en Buenos Aires.':
        'A 150 m² loft with a barbecue house in Buenos Aires.',
})

traducir = en_dic5.traducir
