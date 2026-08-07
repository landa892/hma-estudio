# -*- coding: utf-8 -*-
"""Equipos que salen de las fichas tecnicas del Drive del estudio.

El WordPress viejo no conoce las obras nuevas: para esas dejaba solo a los dos
socios. Estos son los nombres que el estudio escribio en cada ficha.

Es solo la tabla; quien la aplica es docs/cambios_cliente_agosto.py, que ya se
ocupa de la ficha en los dos idiomas. Tener un unico escritor evita que dos
scripts se pisen el campo entre corridas.

Los rotulos que terminan en ":" marcan un rol y el estudio los separa asi en
su ficha, por eso se conservan como una linea mas.
"""

EQUIPOS = {
    'cceba': [
        'Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
        'Arq. Sofía Kesting', 'Arq. Victoria Nabias'],
    'cerveceria-austral': [
        'Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
        'Arq. Camila Lacarpia', 'Arq. Luciano Cichanowski',
        'Arq. Josué Solano'],
    'indusparquet': [
        'Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
        'Dolores Gayoso', 'Alfana Nizza', 'Josué Solano',
        'Dirección de obra:', 'Joaquín Medina'],
    'iol': [
        'Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
        'Documentación de obra:', 'Arq. Pilar Velasco', 'Arq. Victoria Nabias',
        'Dirección de obra:', 'Arq. Fernando Hitzig'],
    'parfumerie': [
        'Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
        'Arq. Florencia Beserga', 'Arq. Gabriela Zarwanitzer',
        'Arq. Victoria Nabias', 'Arq. Julieta Leibovich'],
    'roket': [
        'Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
        'Arq. Ludmila Timerman', 'Arq. Sofía Kesting',
        'Arq. Belén Irigoytia'],
    'templo-mikdash': [
        'Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
        'Arq. Julieta Leibovich'],
    'uala-gigena': [
        'Arq. Leonardo Militello', 'Arq. Fernando Hitzig',
        'Project manager:', 'Arq. Gastón González Vivo',
        'Colaboradores:', 'Arq. María Belén Baratta',
        'Arq. Carolina Marinelli', 'Arq. Ana Laura Martínez',
        'Renders:', 'Arq. Vanik Margossian'],
}
