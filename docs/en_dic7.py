# -*- coding: utf-8 -*-
"""Septima capa del diccionario del espejo en ingles.

Cubre el campo Equipo, que entro despues en las 61 fichas y nunca habia
pasado por el traductor, y la obra Ualá II.

Los nombres propios no se traducen, pero el titulo "Arq." si: en una pagina
en ingles queda "Arch.". Como la lista de gente crece con cada obra, va como
regla y no como entrada del diccionario.
"""
import re

import en_dic6
from en_dic import DIC, PASA_EXACTO

# Nombres sueltos de la ficha de Indusparquet y Ualá Gigena: van sin titulo,
# asi que la regla de "Arq." no los alcanza y el traductor los reportaria.
PASA_EXACTO.update({
    'Dolores Gayoso', 'Alfana Nizza', 'Josué Solano', 'Joaquín Medina',
    'Federico Kulekdjian',
    # Nombre de la obra en la barra de premios, desde que el premio del concurso
    # internacional dejo de estar atribuido a Novotel. Es marca, no se traduce.
    'Accor',
})

DIC.update({
    # El titular de la portada lleva un espacio duro dentro, asi que en el HTML
    # nunca aparece como una frase suelta y el diccionario no lo tenia. Se
    # necesita entero para el panel de autogestion.
    'Creando & construyendo ideas': 'Creating & building ideas',

    # --- fotos nuevas de la pagina Estudio ---
    # Reemplazan a la del plano y al fotograma del video: el estudio pidio dos
    # fotos propias en buena resolucion.
    'La planta del estudio HMA en Buenos Aires, con el equipo trabajando':
        'The HMA studio floor in Buenos Aires, with the team at work',
    'Los socios y el equipo de HMA revisando un proyecto en pantalla':
        'HMA’s partners and team reviewing a project on screen',

    # --- rotulos de la ficha ---
    'Equipo': 'Team',
    'Fotografía': 'Photography',
    'Dirección de obra:': 'Site management:',
    'Documentación de obra:': 'Construction documentation:',
    'Project manager:': 'Project manager:',
    'Colaboradores:': 'Collaborators:',
    'Renders:': 'Renders:',

    # --- categorias que faltaban ---
    'Comercial': 'Commercial',
    'Hotelería': 'Hospitality',

    # --- Ualá II ---
    'Ualá II': 'Ualá II',
    'Diseño interior de oficinas': 'Office interior design',
    'Segundas oficinas de Ualá en Palermo: 757 m² organizados alrededor de un patio central y jardín vertical.':
        "Ualá's second offices in Palermo: 757 m² organised around a central courtyard and a vertical garden.",
    'Dos áreas de trabajo conectadas por un pasillo y un patio central dentro de un antiguo tinglado de Palermo.':
        'Two work areas linked by a corridor and a central courtyard inside an old Palermo shed.',
    'La recepción da paso a un espacio de trabajo en doble altura organizado por islas.':
        'The reception opens onto a double-height workspace organised in islands.',
    'La estructura existente y los nuevos materiales construyen un diálogo claro entre lo antiguo y lo nuevo.':
        'The existing structure and the new materials build a clear dialogue between old and new.',
    'El patio central y el jardín vertical llevan luz natural a las áreas de trabajo.':
        'The central courtyard and the vertical garden bring natural light into the work areas.',
})

# "Arq. Fernando Hitzig" -> "Arch. Fernando Hitzig". El nombre se copia tal
# cual: traducirlo seria un error, no una omision.
TITULO = re.compile(r'^Arq(?:\.|ta\.)? (.+)$')
MEDIA = re.compile(r'^(.*?) — (foto|plano) (\d+)$')


def traducir(t):
    m = MEDIA.match(t)
    if m:
        tipo = 'photo' if m.group(2) == 'foto' else 'plan'
        return '%s — %s %s' % (m.group(1), tipo, m.group(3))
    m = TITULO.match(t)
    if m:
        return 'Arch. %s' % m.group(1).replace('Arq. ', 'Arch. ')
    return en_dic6.traducir(t)
