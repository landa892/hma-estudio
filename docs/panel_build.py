# -*- coding: utf-8 -*-
"""Arma el sitio desde la base. Es lo unico que corre el build de Vercel.

   Los diez pasos podrian ir encadenados con && en la casilla de Vercel, pero el
   comando de build admite 256 caracteres y esa cadena mide mas del doble. Aca
   ademas se ve en el log donde falla, que en una sola linea de shell no se ve.

   El orden no es decorativo:

     1. panel_config    escribe admin/config.js desde las variables de entorno.
                        Sin el, el panel publicado no conecta con nada.
     2. panel_correcciones_agosto aplica correcciones pendientes solo cuando
                        encuentra el valor viejo; no pisa ediciones posteriores.
     3. panel_alta      crea la pagina de cada obra nueva y baja sus fotos.
                        Va antes del generador: si la pagina no existe, la saltea.
     4. panel_generar   rellena titulo, bajada, ficha y memoria en las publicadas.
     5. panel_sitio     saca del sitio las eliminadas o despublicadas.
     6. panel_estados   pone el sello "Obra"/"Proyecto" del listado de acuerdo
                        con el estado de la base. Va despues de las altas y las
                        bajas, que son las que agregan y sacan tarjetas.
     7. panel_textos    escribe los textos fijos de home, estudio y contacto.
     8. panel_home      pone las destacadas en los banners del home.
     9. sitemap_gen     rearma el sitemap leyendo el disco. Va despues de las
                        altas y las bajas, o lista paginas que no existen.
    10. en_gen          rehace /en/ de cero. Ultimo: traduce lo que dejaron los
                        pasos anteriores.

   Si un paso falla, corta ahi y devuelve error. Vercel no publica un build que
   no termino, asi que el sitio anterior sigue en pie: es preferible quedarse un
   rato con la version de antes que publicar un sitio a medio armar.

       python3 docs/panel_build.py
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PASOS = [
    ('la conexion del panel',        'panel_config.py',  []),
    ('las correcciones de contenido','panel_correcciones_agosto.py', ['--supabase']),
    ('las obras nuevas',             'panel_alta.py',    ['--supabase']),
    ('los datos de cada obra',       'panel_generar.py', ['--supabase']),
    ('las obras que ya no van',      'panel_sitio.py',   ['--supabase']),
    ('el estado en el listado',      'panel_estados.py', ['--supabase']),
    ('los textos fijos',             'panel_textos.py',  ['--supabase']),
    ('los banners del home',         'panel_home.py',    ['--supabase']),
    ('el sitemap',                   'sitemap_gen.py',   []),
    ('el sitio en ingles',           'en_gen.py',        []),
]


def main():
    for i, (que, script, args) in enumerate(PASOS, 1):
        print('\n' + '=' * 70)
        print('paso %d de %d — %s  (%s)' % (i, len(PASOS), que, script))
        print('=' * 70, flush=True)

        r = subprocess.run([sys.executable, os.path.join(RAIZ, 'docs', script)] + args,
                           cwd=RAIZ)
        if r.returncode != 0:
            print('\n' + '=' * 70)
            print('FALLO el paso %d (%s). No se publica nada: el sitio que ya '
                  'estaba sigue en pie.' % (i, script))
            print('=' * 70)
            return r.returncode

    print('\n' + '=' * 70)
    print('los %d pasos terminaron bien' % len(PASOS))
    print('=' * 70)

    limpiar_docs()
    return 0


def limpiar_docs():
    """Saca docs/ de lo que se publica, ya con el sitio armado.

    Vercel sirve todo lo que queda en la carpeta al terminar el build, asi que
    sin esto los generadores quedarian descargables en estudiohma.com/docs/.
    Antes se resolvia excluyendo docs/ en .vercelignore, pero eso los dejaba
    fuera del servidor y el build no podia correrlos.

    Solo corre en Vercel. En la maquina del desarrollador borraria el codigo
    fuente, que es exactamente lo que no queremos que pase por descuido.
    """
    if not os.environ.get('VERCEL'):
        print('\n(fuera de Vercel: no se toca docs/)')
        return
    import shutil
    shutil.rmtree(os.path.join(RAIZ, 'docs'), ignore_errors=True)
    print('\ndocs/ sacado de lo que se publica')


if __name__ == '__main__':
    sys.exit(main())
