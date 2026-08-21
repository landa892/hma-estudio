# -*- coding: utf-8 -*-
"""Reescribe la galeria de una ficha con lo que dice la base.

panel_galerias.py no toca las fichas cuyas filas son todas @seed: esas
galerias son la seleccion heredada y viven en el HTML del repositorio, y
reescribirlas en el build pisaria lo que el estudio haya elegido.

Eso vale mientras la carpeta de imagenes no cambie. Cuando drive_sync rehace
una galeria desde el Drive, los archivos se renumeran y el HTML del repositorio
pasa a nombrar fotos que ya no son esas. sacar_figuras_huerfanas() saca las que
apuntan a un archivo que no existe, pero no agrega las que faltan.

Este guion cierra esa mitad, y a proposito usa actualizar_pagina() -la misma
funcion que escribe el build- para que el marcado salga identico al de las
demas fichas en vez de parecerse.

    python docs/ficha_desde_base.py <slug>
"""
import json
import os
import sys
import urllib.request

RAIZ = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'Trabajo para naza',
                    'hma-estudio')
sys.path.insert(0, os.path.join(RAIZ, 'docs'))
os.chdir(RAIZ)

import panel_galerias as pg

# La publicable alcanza: aca solo se lee. Sale del entorno para no atar el
# codigo a una cuenta, igual que en panel_config.py.
URL = os.environ.get('SUPABASE_URL', '').rstrip('/')
CLAVE = os.environ.get('SUPABASE_ANON_KEY', '')


def pedir(ruta):
    p = urllib.request.Request(URL + ruta,
                               headers={'apikey': CLAVE,
                                        'Authorization': 'Bearer ' + CLAVE})
    return json.loads(urllib.request.urlopen(p, timeout=60).read().decode('utf-8'))


def main(slug):
    if not URL or not CLAVE:
        raise SystemExit('Faltan SUPABASE_URL y SUPABASE_ANON_KEY en el entorno.')
    obra = pedir('/rest/v1/obras?select=id,titulo&slug=eq.' + slug)[0]
    filas = pedir('/rest/v1/obra_imagenes?select=*&obra_id=eq.%s&order=orden.asc'
                  % obra['id'])

    fotos = [f for f in filas if f['tipo'] == 'foto']
    planos = [f for f in filas if f['tipo'] == 'plano']

    # La misma poda que hace el build: la repetida se saca, salvo que sea la
    # portada, que no se toca nunca.
    sobran = pg.fotos_fuera().get(slug, set())
    if sobran:
        fotos = [f for f in fotos
                 if f['es_portada']
                 or os.path.basename(f['storage_path']) not in sobran]

    print('%s: %d fotos y %d planos segun la base' % (slug, len(fotos), len(planos)))

    resueltas = [pg.resolver_imagen(slug, f, URL) for f in fotos]
    resueltos = [pg.resolver_imagen(slug, f, URL) for f in planos]

    if pg.actualizar_pagina(slug, obra['titulo'], resueltas, resueltos):
        print('ficha reescrita')
    else:
        print('la ficha ya estaba igual')
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    sys.exit(main(sys.argv[1]))
