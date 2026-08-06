# -*- coding: utf-8 -*-
"""Quinta capa del diccionario del espejo en ingles.

Junta lo que entro despues: el texto reescrito de la pagina Estudio y las
descripciones de los premios, que ahora dicen que obra se premio.
"""
import en_dic4
from en_dic import DIC, PASA_EXACTO

PASA_EXACTO.update({'Hyatt Ziva', 'Identidad'})

DIC.update({
    # --- pagina Estudio ---
    # Ojo: en_gen colapsa los espacios antes de buscar, asi que las frases
    # que en el HTML ocupan varias lineas van aca en una sola.
    'Identidad': 'Identity',
    'Entendemos el diseño como un proceso integral donde convergen estrategia, arquitectura e identidad. Cada decisión responde a una visión conceptual unificada, con la arquitectura de marca como eje del proyecto.':
        'We understand design as an integral process where strategy, architecture and identity converge. Every decision answers to a single conceptual vision, with brand architecture at the core of the project.',
    'Concebimos la arquitectura de interiores como una disciplina holística que trasciende lo funcional y lo estético, creando espacios con identidad propia y experiencias memorables.':
        'We see interior architecture as a holistic discipline that goes beyond the functional and the aesthetic, creating spaces with an identity of their own and experiences worth remembering.',
    'Resignificamos referencias culturales y del imaginario colectivo para crear espacios contemporáneos, profundamente conectados con su contexto y con una identidad genuina.':
        'We reframe cultural references and shared imagery to create contemporary spaces, deeply connected to their context and with a genuine identity.',
    'Colaboramos estrechamente con nuestros clientes para comprender sus objetivos y el potencial del proyecto.':
        'We work closely with our clients to understand their goals and the potential of the project.',
    'A través de un proceso integral que combina estrategia, creatividad y rigor técnico, desarrollamos soluciones innovadoras con una visión unificada.':
        'Through an integral process that combines strategy, creativity and technical rigour, we develop innovative solutions under a single vision.',
    'Trabajamos junto a socios estratégicos y consultores locales para integrar normativa, ingeniería y estándares constructivos, garantizando una ejecución coherente en cada contexto.':
        'We work alongside strategic partners and local consultants to bring together regulations, engineering and building standards, ensuring consistent delivery in every context.',
    'Vista general del estudio HMA y su equipo trabajando':
        'General view of the HMA studio and its team at work',
    'años de trayectoria creando espacios experienciales en América, Europa y Asia.':
        'years of practice creating experiential spaces across the Americas, Europe and Asia.',

    # --- estado de obra ---
    'Obra recientemente inaugurada': 'Recently opened',

    # --- que se premio en cada distincion ---
    'Mención especial para Movistar Arena en la categoría Commercial Interiors.':
        'Special mention for Movistar Arena in the Commercial Interiors category.',
    'Mercado Manduca obtuvo el 3er puesto en la etapa regional CABA, categoría obra privada de escala media.':
        'Mercado Manduca took 3rd place in the CABA regional stage, mid-scale private work category.',
    'Mención especial para Mercado Manduca en la categoría Commercial Renovations & Additions.':
        'Special mention for Mercado Manduca in the Commercial Renovations & Additions category.',
    'Fogón fue reconocido en arquitectura construida en el extranjero y Mamba Bar en arquitectura comercial e interiorismo.':
        'Fogón was recognised for architecture built abroad, and Mamba Bar for commercial architecture and interior design.',
    'Osten fue finalista en los SBID International Design Awards.':
        'Osten was a finalist at the SBID International Design Awards.',
    'El estudio fue finalista en la categoría Interior Design — Commercial.':
        'The studio was a finalist in the Interior Design — Commercial category.',
    'Osten fue reconocido en la categoría mejor restaurante y bar independiente de América.':
        'Osten was recognised as best independent restaurant and bar in the Americas.',
    'Fogón fue finalista como mejor restaurante de Medio Oriente y África.':
        'Fogón was a finalist for best restaurant in the Middle East and Africa.',
    'Mamba Bar fue finalista en la categoría mejor restaurante de diseño del mundo.':
        'Mamba Bar was a finalist for best designed restaurant in the world.',
    'The Nim Bar fue finalista del premio especial de diseño interior para restaurantes de Centroamérica, Sudamérica y el Caribe.':
        'The Nim Bar was a finalist for the special interior design award for restaurants in Central and South America and the Caribbean.',
    'Mamba Bar fue ganador como mejor bar de América.':
        'Mamba Bar won best bar in the Americas.',
    'The Nim Bar fue finalista como mejor bar de América.':
        'The Nim Bar was a finalist for best bar in the Americas.',
    'Atelier Vilela fue seleccionada como finalista de la Bienal Argentina de Arquitectura.':
        'Atelier Vilela was selected as a finalist at the Argentine Architecture Biennial.',
    'Casa PH El Salvador fue seleccionada como obra finalista.':
        'Casa PH El Salvador was selected as a finalist work.',
    'Galería de arte Objeto A fue seleccionada como obra finalista.':
        'The Objeto A art gallery was selected as a finalist work.',
})

traducir = en_dic4.traducir
