# -*- coding: utf-8 -*-
"""Arma el seed de la tabla textos leyendo las paginas fijas del sitio.

El panel edita los textos de home, estudio y contacto. Se extraen del sitio
para que la primera vez que alguien guarde no se pierda lo que ya dice.

Dos decisiones que valen la pena explicar:

- Los campos van enumerados a mano y no por barrido de clases. Son quince: con
  una lista explicita cada clave dice que cosa es ("contacto.direccion") y
  sobrevive a un rediseño, mientras que una clave por posicion se corre entera
  si alguien mete un parrafo en el medio.

- El ingles NO se toma por posicion de la pagina espejo. Asi salia cruzado: el
  titulo tres del castellano contra el cuatro del ingles. Sale del mismo
  diccionario con el que se genera el espejo, que es la correspondencia real.

    python docs/panel_textos_semilla.py

Escribe supabase/migrations/0003_textos.sql. No usa la salida estandar a
proposito: redirigida desde la consola de Windows el archivo sale en cp1252 y
Postgres recibe las eñes y los acentos partidos.
"""
import io, os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'docs'))

import en_dic7

# (clave, seccion, rotulo para el panel, archivo, patron, multilinea)
# El patron captura el texto en el grupo 1.
CAMPOS = [
    ('home.titular', 'home', 'Titular de la portada', 'index.html',
     r'<h1[^>]*class="display-1[^"]*"[^>]*>(.*?)</h1>', False),
    ('home.bajada', 'home', 'Bajada de la portada', 'index.html',
     r'<p class="lede[^"]*"[^>]*>(.*?)</p>', True),

    ('estudio.eyebrow', 'estudio', 'Rotulo sobre el titulo', 'estudio/index.html',
     r'<span class="eyebrow">(.*?)</span>', False),
    ('estudio.titular', 'estudio', 'Titulo de la pagina', 'estudio/index.html',
     r'<h1[^>]*>(.*?)</h1>', False),
    ('estudio.presentacion', 'estudio', 'Presentacion del estudio',
     'estudio/index.html', r'<p class="lede[^"]*"[^>]*>(.*?)</p>', True),

    ('contacto.titular', 'contacto', 'Titulo de la pagina', 'contacto/index.html',
     r'<h1[^>]*>(.*?)</h1>', False),
    ('contacto.direccion', 'contacto', 'Direccion', 'contacto/index.html',
     r'<p[^>]*>\s*(Soler[^<]*(?:<br>)?[^<]*)</p>', True),
    ('contacto.telefonos', 'contacto', 'Telefonos', 'contacto/index.html',
     r'<p class="office-tels"[^>]*>(.*?)</p>', True),
]

# Los tres bloques de "Que hacemos" y los tres de "Como trabajamos" de la
# pagina Estudio. Se toman por su titulo, que es lo que los distingue.
BLOQUES_ESTUDIO = ['Diseño integral', 'Identidad', 'Autenticidad']


def limpiar(t):
    t = re.sub(r'<br\s*/?>', '\n', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = t.replace('&amp;', '&').replace('&nbsp;', ' ')
    lineas = [re.sub(r'[ \t]+', ' ', x).strip() for x in t.split('\n')]
    return '\n'.join(x for x in lineas if x).strip()


def leer(ruta):
    p = os.path.join(RAIZ, ruta)
    if not os.path.isfile(p):
        return ''
    h = io.open(p, encoding='utf-8').read()
    # El menu y el pie se repiten en las seis paginas: si entraran, el panel
    # mostraria seis veces el mismo texto y editarlo en uno no lo cambiaria en
    # los demas.
    h = re.sub(r'(?s)<header.*?</header>', '', h)
    h = re.sub(r'(?s)<div id="site-menu".*?\n  </div>', '', h)
    h = re.sub(r'(?s)<footer.*?</footer>', '', h)
    return h


def ingles(es):
    """La version inglesa segun el diccionario del espejo, o None."""
    if not es:
        return None
    # Un texto sin letras —telefonos, por ejemplo— es el mismo en los dos
    # idiomas: pedirle una traduccion al diccionario lo reportaria como falta.
    if not re.search(r'[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]', es):
        return es

    # Primero el texto completo: en el HTML un parrafo puede venir cortado en
    # varias lineas por el formato, pero en el diccionario es una sola entrada.
    entero = en_dic7.traducir(re.sub(r'\s+', ' ', es))
    if entero is not None:
        return entero

    # Si no, linea por linea: asi entran los bloques donde cada renglon es una
    # frase suelta, como la direccion.
    fuera = []
    for p in [x.strip() for x in es.split('\n') if x.strip()]:
        r = en_dic7.traducir(re.sub(r'\s+', ' ', p))
        if r is None:
            return None
        fuera.append(r)
    return '\n'.join(fuera)


def sql(v):
    return "'" + v.replace("'", "''") + "'" if v is not None else 'null'


def main():
    filas, sin_ingles = [], []

    for i, (clave, seccion, rotulo, ruta, patron, multi) in enumerate(CAMPOS, 1):
        h = leer(ruta)
        m = re.search(patron, h, re.S)
        if not m:
            sys.stderr.write('  [!] %s: no encuentro el texto en %s\n' % (clave, ruta))
            continue
        es = limpiar(m.group(1))
        en = ingles(es)
        if en is None:
            sin_ingles.append(clave)
        filas.append((clave, seccion, rotulo, es, en, multi, i))

    # Los seis bloques de la pagina Estudio: titulo y parrafo de cada uno.
    h = leer('estudio/index.html')
    for j, titulo in enumerate(BLOQUES_ESTUDIO, 1):
        m = re.search(r'<h4>%s</h4>\s*<p>(.*?)</p>' % re.escape(titulo), h, re.S)
        if not m:
            sys.stderr.write('  [!] bloque "%s": no lo encuentro\n' % titulo)
            continue
        es = limpiar(m.group(1))
        en = ingles(es)
        if en is None:
            sin_ingles.append('estudio.bloque%d' % j)
        filas.append(('estudio.bloque%d' % j, 'estudio',
                      'Estudio — %s' % titulo, es, en, True, 20 + j))

    destino = os.path.join(RAIZ, 'supabase', 'migrations', '0003_textos.sql')
    out = io.open(destino, 'w', encoding='utf-8', newline='\n')
    out.write('-- Textos de las secciones fijas, tal como los dice el sitio hoy.\n')
    out.write('-- Generado por docs/panel_textos_semilla.py: no se edita a mano.\n')
    out.write('--\n')
    out.write('-- El ingles sale del diccionario del espejo, no de la posicion\n')
    out.write('-- del texto en la pagina traducida.\n\n')
    out.write('insert into textos '
              '(clave, seccion, rotulo, es, en, multilinea, orden) values\n')
    out.write(',\n'.join(
        '  (%s, %s, %s, %s, %s, %s, %d)'
        % (sql(c), sql(s), sql(r), sql(es), sql(en),
           'true' if mu else 'false', o)
        for c, s, r, es, en, mu, o in filas))
    out.write('\non conflict (clave) do nothing;\n')
    out.close()

    sys.stderr.write('textos: %d   ->  %s\n'
                     % (len(filas), os.path.relpath(destino, RAIZ)))
    for seccion in ('home', 'estudio', 'contacto'):
        sys.stderr.write('  %-9s %d\n'
                         % (seccion, sum(1 for f in filas if f[1] == seccion)))
    if sin_ingles:
        sys.stderr.write('sin version inglesa (%d): %s\n'
                         % (len(sin_ingles), ', '.join(sin_ingles)))


if __name__ == '__main__':
    main()
