# -*- coding: utf-8 -*-
"""Rutas del espejo en ingles y reescritura de enlaces.

   El sitio en castellano vive en la raiz y el ingles debajo de /en/, con los
   tramos traducidos: /proyectos/ pasa a /en/projects/. El slug de cada obra
   no se toca —son nombres propios y ya estan indexados— asi que
   /proyectos/moshu/ es /en/projects/moshu/.
"""
import re

# tramo en castellano -> tramo en ingles
SECCIONES = {
    'proyectos': 'projects',
    'estudio': 'studio',
    'premios': 'awards',
    'prensa': 'press',
    'contacto': 'contact',
    'privacidad': 'privacy',
    'buscar': 'search',
}


def a_ingles(ruta):
    """/proyectos/moshu/ -> /en/projects/moshu/"""
    if not ruta.startswith('/') or ruta.startswith('//'):
        return ruta
    if ruta.startswith(('/assets/', '/styles/', '/scripts/', '/api/', '/en/')):
        return ruta
    if ruta == '/':
        return '/en/'
    p = ruta.lstrip('/').split('/')
    p[0] = SECCIONES.get(p[0], p[0])
    return '/en/' + '/'.join(p)


def a_castellano(ruta):
    """El camino inverso, para el boton de idioma de las paginas en ingles."""
    if not ruta.startswith('/en'):
        return ruta
    resto = ruta[3:] or '/'
    if resto == '/':
        return '/'
    inverso = {v: k for k, v in SECCIONES.items()}
    p = resto.lstrip('/').split('/')
    p[0] = inverso.get(p[0], p[0])
    return '/' + '/'.join(p)


def reescribir_enlaces(html):
    """Todos los href/action internos apuntan a su equivalente en ingles."""
    def rep(m):
        attr, url = m.group(1), m.group(2)
        return '%s="%s"' % (attr, a_ingles(url))
    return re.sub(r'\b(href|action)="(/[^"]*)"', rep, html)
