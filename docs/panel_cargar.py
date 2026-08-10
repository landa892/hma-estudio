# -*- coding: utf-8 -*-
"""Genera el SQL que sube las 61 obras del sitio a la base.

Sale de docs/panel_datos.json, que produce docs/panel_exportar.py leyendo las
paginas. Escribe supabase/migrations/0005_obras.sql.

Dos cosas que conviene saber antes de correrlo:

- No sube las fotos. Las 1.280 imagenes ya viven en assets/gallery y las sirve
  el sitio; moverlas al bucket es otra tarea y no hace falta para que el panel
  edite fichas y memorias. Las obras nuevas que cargue el estudio si van al
  bucket.

- Por eso mismo la tabla obra_imagenes queda vacia en esta carga, y el tope de
  15 imagenes no molesta: recien cuenta cuando alguien sube una foto desde el
  panel.

    python docs/panel_cargar.py
"""
import io, json, os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sql(v):
    if v is None or v == '':
        return 'null'
    return "'" + str(v).replace("'", "''") + "'"


def arreglo(lista):
    """Un text[] de Postgres. Vacio va como '{}' y no como null."""
    if not lista:
        return "'{}'"
    partes = ['"' + str(x).replace('\\', '\\\\').replace('"', '\\"') + '"'
              for x in lista]
    return "'{" + ','.join(partes) + "}'"


def main():
    datos = json.load(io.open(os.path.join(RAIZ, 'docs', 'panel_datos.json'),
                              encoding='utf-8'))

    filas = []
    for o in datos:
        filas.append('  (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
                     '%s, %s, %s, %s)' % (
            sql(o['slug']), sql(o['titulo']), sql(o.get('ubicacion')),
            sql(o.get('pais')), sql(o.get('anio')), sql(o.get('superficie')),
            sql(o.get('comitente')), sql(o.get('tipologia')),
            sql(o.get('fotografia')),
            sql(o.get('categoria')) + '::obra_categoria'
            if o.get('categoria') else 'null',
            arreglo(o.get('equipo')), sql(o.get('bajada')),
            sql(o.get('memoria')), sql(o.get('memoria_en')),
            sql(o['estado']) + '::obra_estado',
            'true' if o.get('publicada') else 'false',
            o.get('orden') if o.get('orden') is not None else 'null'))

    destino = os.path.join(RAIZ, 'supabase', 'migrations', '0005_obras.sql')
    out = io.open(destino, 'w', encoding='utf-8', newline='\n')
    out.write('-- Las 61 obras que hoy tiene el sitio.\n')
    out.write('-- Generado por docs/panel_cargar.py: no se edita a mano.\n')
    out.write('--\n')
    out.write('-- Se puede volver a correr sin duplicar: el slug es unico y en\n')
    out.write('-- conflicto no hace nada, asi que no pisa lo que el estudio haya\n')
    out.write('-- editado despues desde el panel.\n\n')
    out.write('insert into obras (slug, titulo, ubicacion, pais, anio, superficie,\n')
    out.write('  comitente, tipologia, fotografia, categoria, equipo, bajada,\n')
    out.write('  memoria, memoria_en, estado, publicada, orden) values\n')
    out.write(',\n'.join(filas))
    out.write('\non conflict (slug) do nothing;\n')
    out.close()

    print('obras en el SQL: %d  ->  supabase/migrations/0005_obras.sql' % len(filas))
    print('sin categoria:   %d' % sum(1 for o in datos if not o.get('categoria')))
    print('sin memoria:     %d' % sum(1 for o in datos if not o.get('memoria')))


if __name__ == '__main__':
    main()
