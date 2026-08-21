# -*- coding: utf-8 -*-
"""Arma el sitio desde la base. Es lo unico que corre el build de Vercel.

   Los quince pasos podrian ir encadenados con && en la casilla de Vercel, pero el
   comando de build admite 256 caracteres y esa cadena mide mas del doble. Aca
   ademas se ve en el log donde falla, que en una sola linea de shell no se ve.

   El orden no es decorativo:

     1. panel_config    escribe admin/config.js desde las variables de entorno.
                        Sin el, el panel publicado no conecta con nada.
     2. panel_correcciones_agosto aplica correcciones pendientes solo cuando
                        encuentra el valor viejo; no pisa ediciones posteriores.
     3. panel_alta      crea la pagina de cada obra nueva y baja sus fotos.
                        Va antes del generador: si la pagina no existe, la saltea.
     4. panel_galerias  conecta fotos y planos historicos y aplica portada y
                        orden. Saltea las repetidas segun
                        docs/galeria_repetidas.json, que se regenera a mano con
                        docs/galeria_repetidas.py cuando cambian las fotos: ese
                        paso necesita Pillow y aca no hay.
     5. panel_generar   rellena titulo, bajada, ficha y memoria en las publicadas.
     6. panel_sitio     saca del sitio las eliminadas o despublicadas.
     7. panel_listado   sincroniza titulo y categoria de cada tarjeta con la
                        base.
     8. panel_estados   pone el sello "Obra"/"Proyecto" del listado de acuerdo
                        con el estado de la base. Va despues de las altas y las
                        bajas, que son las que agregan y sacan tarjetas.
     9. panel_textos    escribe los textos fijos de home, estudio y contacto.
    10. panel_home      pone las destacadas en los banners del home.
    11. obras_layout    garantiza que la portada abra cada ficha y deja una
                        composicion consistente para la memoria editorial.
                        Los planos van en el paso 4: panel_galerias los trae
                        como filas de obra_imagenes con tipo='plano', ya no
                        hay un paso planos_fichas aparte.
    12. prensa_pagina   rearma el archivo completo de publicaciones.
    13. prensa_paginas  arma la pagina propia de cada nota y enlaza su
                        tarjeta. Va despues del archivo, que es quien
                        rehace el listado.
    13. en_gen          rehace /en/ de cero. Traduce lo que dejaron los pasos
                        anteriores.
    14. obras_orden     ordena grilla y lista por el ano final, tanto en
                        castellano como en ingles. Asi una obra nueva no queda
                        al final solo por haberse cargado despues.
    15. seo_gen         agrega datos estructurados a cada pagina publica ya con
                        el contenido y el orden definitivos.
    16. sitemap_gen     rearma el sitemap leyendo el disco, incluido el espejo.

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
    ('las galerias y portadas',       'panel_galerias.py', []),
    ('los datos de cada obra',       'panel_generar.py', ['--supabase']),
    ('las obras que ya no van',      'panel_sitio.py',   ['--supabase']),
    ('las tarjetas del listado',     'panel_listado.py', ['--supabase']),
    ('el estado en el listado',      'panel_estados.py', ['--supabase']),
    ('los textos fijos',             'panel_textos.py',  ['--supabase']),
    ('los banners del home',         'panel_home.py',    ['--supabase']),
    ('la composicion de las fichas', 'obras_layout.py',  []),
    ('el archivo de prensa',         'prensa_pagina.py', []),
    ('la pagina de cada nota',       'prensa_paginas.py', []),
    ('el sitio en ingles',           'en_gen.py',        []),
    ('el orden cronologico',         'obras_orden.py',   []),
    ('los datos estructurados SEO',  'seo_gen.py',       []),
    ('el sitemap',                   'sitemap_gen.py',   []),
    # Ultimo: deja anotada la fecha contra la que el panel compara para
    # avisar que hay cambios guardados sin publicar. Ver panel_publicado.py.
    ('la marca de publicado',        'panel_publicado.py', []),
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
