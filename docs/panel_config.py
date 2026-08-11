# -*- coding: utf-8 -*-
"""Escribe admin/config.js en el build, desde las variables de entorno.

   El archivo no esta en el repositorio a proposito: asi el codigo no queda atado
   a una cuenta de Supabase y transferir el proyecto es cambiar dos variables. El
   costo de esa decision es que en el sitio publicado el archivo no existe, y sin
   el el panel carga la pantalla de login y no puede conectarse a nada.

   Este script lo genera en cada build. Los dos valores que escribe son publicos
   por diseño —viajan al navegador en cada visita del panel— y lo que protege los
   datos es el RLS de la base. La clave de servicio no se toca aca ni podria: no
   la lee.

       python docs/panel_config.py

   Si falta alguna variable, no escribe nada y devuelve error: es mejor que el
   deploy falle avisando que publicar un panel que no conecta.
"""
import io
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, 'admin', 'config.js')

CABEZA = """/* Generado por docs/panel_config.py en cada build. No se edita a mano y no
   entra al repositorio.

   Los dos valores son publicos por diseño: viajan al navegador en cada visita
   del panel. Lo que impide que alguien con esta clave borre las obras no es
   esconderla -no se puede-, es el RLS de la base. La clave service_role NUNCA
   va aca: esa sortea el RLS por completo y vive solo en las variables de
   entorno del servidor. */
"""


def main():
    url = (os.environ.get('SUPABASE_URL') or '').strip().rstrip('/')
    clave = (os.environ.get('SUPABASE_ANON_KEY') or '').strip()

    faltan = [n for n, v in (('SUPABASE_URL', url), ('SUPABASE_ANON_KEY', clave))
              if not v]
    if faltan:
        print('ERROR: faltan las variables %s. No se escribe admin/config.js: '
              'sin ellas el panel se publica sin poder conectarse.'
              % ', '.join(faltan))
        return 1

    # Un descuido facil y caro: pegar la clave de servicio donde va la publica.
    # La de servicio saltea todo el RLS, asi que publicarla en el navegador deja
    # la base abierta a cualquiera.
    if 'service_role' in clave or clave.startswith('sb_secret_'):
        print('ERROR: SUPABASE_ANON_KEY parece ser la clave de servicio. Esa no '
              'puede ir al navegador: saltea el RLS. Revisar la variable.')
        return 1

    io.open(DESTINO, 'w', encoding='utf-8', newline='\n').write(
        CABEZA
        + 'window.HMA_CONFIG = {\n'
        + '  SUPABASE_URL: %s,\n' % json.dumps(url)
        + '  SUPABASE_ANON_KEY: %s,\n' % json.dumps(clave)
        + '};\n')

    print('admin/config.js escrito para %s' % url)
    return 0


if __name__ == '__main__':
    sys.exit(main())
