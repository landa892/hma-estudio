# -*- coding: utf-8 -*-
"""Anota en la base que el sitio se termino de reconstruir.

   Es el ultimo paso del build y existe para una sola pantalla: el aviso del
   panel que dice "guardaste esto y todavia no esta en la web". Ese aviso
   compara la fecha en que se toco cada obra contra la fecha de la ultima
   publicacion, y la fecha de la ultima publicacion es la fila que escribe este
   script.

   Va ultimo a proposito. Los pasos anteriores tambien escriben en la base -las
   correcciones, las galerias heredadas- y si la marca se pusiera antes, esos
   cambios quedarian con fecha posterior y el panel los denunciaria como
   pendientes apenas termine de publicar.

   Tampoco lo anota el boton del panel, que seria mas simple. Si el build falla
   a la mitad, el boton ya habria dicho que se publico algo que nunca salio:
   preferimos que el aviso se quede puesto de mas antes que quitarlo de menos.

       python docs/panel_publicado.py

   Si no puede escribir, avisa y termina bien igual. El sitio ya esta armado a
   esta altura y tirar abajo un deploy entero por una marca de aviso seria
   mucho peor que quedarse sin la marca.
"""
import json
import os
import sys
import urllib.error
import urllib.request


def origen():
    """De donde salio este build, en una linea legible."""
    if not os.environ.get('VERCEL'):
        return 'local'
    rama = os.environ.get('VERCEL_GIT_COMMIT_REF') or ''
    return ('vercel ' + rama).strip()


def main():
    url = (os.environ.get('SUPABASE_URL') or '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY') or ''
    if not url or not clave:
        print('sin SUPABASE_URL o SUPABASE_SERVICE_KEY: no se anota la '
              'publicacion. El panel va a seguir avisando que hay cambios '
              'sin publicar.')
        return 0

    cuerpo = json.dumps([{'origen': origen()}]).encode('utf-8')
    pedido = urllib.request.Request(
        url + '/rest/v1/publicaciones',
        data=cuerpo,
        method='POST',
        headers={
            'apikey': clave,
            'Authorization': 'Bearer ' + clave,
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal',
        })

    try:
        urllib.request.urlopen(pedido, timeout=30).read()
    except urllib.error.HTTPError as e:
        print('no se pudo anotar la publicacion (%s): %s'
              % (e.code, e.read().decode('utf-8', 'replace')[:200]))
        return 0
    except Exception as e:
        print('no se pudo anotar la publicacion: %s' % e)
        return 0

    print('publicacion anotada (%s)' % origen())
    return 0


if __name__ == '__main__':
    sys.exit(main())
