# -*- coding: utf-8 -*-
"""Escribe en el sitio los textos fijos que el estudio edita desde el panel.

   Es el camino inverso de docs/panel_textos_semilla.py, que los saco de estas
   mismas paginas para sembrar la base. Las posiciones salen de ahi importadas y
   no copiadas: si alguien cambia un patron, los dos lados se mueven juntos.

   Tres cuidados que no son opcionales:

   - Solo se reescribe el campo que cambio. El sembrador aplano el HTML para
     leerlo —convirtio <br> en salto de linea y se comio los &nbsp;—, asi que
     reescribir todo cada vez iria degradando el marcado aunque nadie edite
     nada. Comparando primero, una pagina sin cambios queda byte a byte igual.

   - Los telefonos de Contacto abren WhatsApp. Escribirlos como texto plano o
     volverlos a tel: perderia el comportamiento pedido por el estudio. Se
     rearman los <a> desde cada renglon aunque el numero cambie en el panel.

   - El espejo en ingles se genera por diccionario, y un texto recien editado no
     esta en ningun diccionario: saldria en castellano dentro de la pagina en
     ingles. Por eso este script tambien escribe docs/en_textos.json con los
     pares que el estudio cargo, que en_gen.py consulta antes de traducir.

       python docs/panel_textos.py --verificar   # no escribe, solo compara
       python docs/panel_textos.py              # escribe desde el JSON local
       python docs/panel_textos.py --supabase   # escribe desde la base
"""
import html as _html
import io, json, os, re, sys
import urllib.parse
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'docs'))

from panel_textos_semilla import CAMPOS, BLOQUES_ESTUDIO, limpiar, leer, ingles

LOCAL = os.path.join(RAIZ, 'docs', 'panel_textos.json')
DESTINO_EN = os.path.join(RAIZ, 'docs', 'en_textos.json')


def escapar(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def como_lo_dice_el_sitio(interior):
    """El texto del HTML en la misma forma en que lo guarda la base.

    limpiar() viene del sembrador y desescapa &amp; y &nbsp;, pero no &lt; ni
    &gt;. Comparando con eso, un texto que contenga un "<" nunca coincide
    consigo mismo y el campo se reescribe en cada publicacion: el archivo cambia
    siempre, el espejo se regenera al vuelto y nada converge. Se desescapa
    completo solo para comparar; lo que se escribe sigue saliendo de escapar().
    """
    return _html.unescape(limpiar(interior))


# ---------------------------------------------------------------------------
# De donde salen los textos
# ---------------------------------------------------------------------------

def desde_supabase():
    url = os.environ.get('SUPABASE_URL', '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY', '')
    if not url or not clave:
        raise SystemExit('Faltan SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno.')
    pedido = urllib.request.Request(
        url + '/rest/v1/textos?select=clave,es,en',
        headers={'apikey': clave, 'Authorization': 'Bearer ' + clave})
    with urllib.request.urlopen(pedido, timeout=30) as r:
        filas = json.loads(r.read().decode('utf-8'))

    # Al incorporar una nueva seccion editable, el propio build siembra sus
    # textos actuales. Asi ampliar el panel no obliga al estudio a correr SQL.
    existentes = set(f.get('clave') for f in filas)
    nuevas = []
    paginas = {}
    for orden, (campo, seccion, rotulo, ruta, patron, multilinea) in enumerate(CAMPOS, 1):
        if campo in existentes:
            continue
        if ruta not in paginas:
            paginas[ruta] = leer(ruta)
        m = re.search(patron, paginas[ruta], re.S)
        if not m:
            continue
        es = limpiar(m.group(1))
        en = ingles(es)
        nuevas.append({
            'clave': campo, 'seccion': seccion, 'rotulo': rotulo,
            'es': es, 'en': en or es, 'multilinea': multilinea, 'orden': orden,
        })
    if nuevas:
        alta = urllib.request.Request(
            url + '/rest/v1/textos', data=json.dumps(nuevas, ensure_ascii=False).encode('utf-8'),
            method='POST', headers={
                'apikey': clave, 'Authorization': 'Bearer ' + clave,
                'Content-Type': 'application/json', 'Prefer': 'return=minimal',
            })
        with urllib.request.urlopen(alta, timeout=30):
            pass
        filas.extend(nuevas)
        print('textos nuevos sembrados: %d' % len(nuevas))

    # Correccion puntual pedida por el estudio. Es condicional para no pisar
    # una edicion futura hecha desde el panel: solo migra el valor anterior.
    anterior = 'Hablemos de tu proyecto'
    for fila in filas:
        if fila.get('clave') != 'contacto.titular' or fila.get('es') != anterior:
            continue
        nuevo = {'es': 'Contacto', 'en': 'Contact'}
        consulta = ('/rest/v1/textos?clave=eq.contacto.titular&es=eq.' +
                    urllib.parse.quote(anterior, safe=''))
        parche = urllib.request.Request(
            url + consulta,
            data=json.dumps(nuevo).encode('utf-8'),
            method='PATCH',
            headers={
                'apikey': clave,
                'Authorization': 'Bearer ' + clave,
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal',
            })
        with urllib.request.urlopen(parche, timeout=30):
            pass
        fila.update(nuevo)
        print('correccion aplicada: contacto.titular')
    return filas


def desde_json():
    if not os.path.isfile(LOCAL):
        raise SystemExit(
            'No existe %s. Corre con --supabase, o guarda ahi un volcado de la '
            'tabla textos.' % os.path.relpath(LOCAL, RAIZ))
    return json.load(io.open(LOCAL, encoding='utf-8'))


# ---------------------------------------------------------------------------
# Como estaba armado el bloque que se va a reescribir
# ---------------------------------------------------------------------------

BR = re.compile(r'<br\s*/?>')
TEL = re.compile(r'<a href="(?:tel:|https://wa\.me/)')


def piezas(interior):
    """Lee del HTML actual como separaba los renglones, para imitarlo.

    Devuelve (prefijo, separador, sufijo, con_tel). Sin esto habria que elegir
    un formato y el archivo cambiaria de forma en cada campo que se toque.
    """
    con_tel = bool(TEL.search(interior))
    m_br = BR.search(interior)

    prefijo = re.match(r'^\s*', interior).group(0)
    sufijo = re.search(r'\s*$', interior).group(0)

    # La sangria de los renglones siguientes: el primer salto de linea que
    # aparece despues de algo que no sea espacio.
    m_ind = re.search(r'\n([ \t]*)', interior[len(prefijo):])
    sangria = m_ind.group(1) if m_ind else ''

    if m_br:
        # ¿El <br> venia seguido de salto de linea o pegado al texto?
        resto = interior[m_br.end():]
        separador = m_br.group(0) + (('\n' + sangria) if resto[:1] == '\n' else '')
    elif sangria or '\n' in interior[len(prefijo):]:
        separador = '\n' + sangria
    else:
        separador = ' '

    return prefijo, separador, sufijo, con_tel


def renglon_tel(linea):
    """El fijo argentino llama; los moviles confirmados abren WhatsApp."""
    numero = re.sub(r'[^0-9]', '', linea)
    rotulo = escapar(linea)
    if numero.startswith('5411'):
        return '<a href="tel:+%s">%s</a>' % (numero, rotulo)
    return ('<a href="https://wa.me/%s" target="_blank" rel="noopener" '
            'aria-label="WhatsApp %s">WhatsApp: %s</a>'
            % (numero, rotulo, rotulo))


def armar(texto, interior_actual):
    """El interior nuevo, con el mismo formato que tenia el anterior."""
    prefijo, separador, sufijo, con_tel = piezas(interior_actual)
    lineas = [x.strip() for x in texto.split('\n') if x.strip()]
    if not lineas:
        return None
    partes = [renglon_tel(x) if con_tel else escapar(x) for x in lineas]
    return prefijo + separador.join(partes) + sufijo


# ---------------------------------------------------------------------------
# Donde vive cada campo
# ---------------------------------------------------------------------------

# El sembrador borra menu y pie antes de buscar, para no confundir un texto de
# la pagina con uno que se repite en las seis. Aca no se puede borrar nada
# —hay que escribir sobre el archivo real—, asi que se busca a partir del
# final del <header> y del menu, que es donde empieza el contenido propio.
def zona_de_contenido(html):
    fin = 0
    for patron in (r'(?s)<header.*?</header>', r'(?s)<div id="site-menu".*?\n  </div>'):
        m = re.search(patron, html)
        if m and m.end() > fin:
            fin = m.end()
    return fin


def ubicaciones(textos):
    """[(clave, ruta, patron)] para los 11 campos."""
    fuera = [(clave, ruta, patron) for clave, _s, _r, ruta, patron, _m in CAMPOS]
    for j, titulo in enumerate(BLOQUES_ESTUDIO, 1):
        fuera.append(('estudio.bloque%d' % j, 'estudio/index.html',
                      r'<h4>%s</h4>\s*<p>(.*?)</p>' % re.escape(titulo)))
    return fuera


# ---------------------------------------------------------------------------

def main(verificar, supabase):
    filas = desde_supabase() if supabase else desde_json()
    por_clave = dict((f['clave'], f) for f in filas)
    print('textos en la base: %d' % len(filas))

    # Se agrupan por archivo: una pagina con tres campos se lee y se escribe
    # una sola vez.
    porarchivo = {}
    for clave, ruta, patron in ubicaciones(filas):
        porarchivo.setdefault(ruta, []).append((clave, patron))

    cambiados, avisos = [], []
    for ruta, campos in sorted(porarchivo.items()):
        p = os.path.join(RAIZ, ruta)
        if not os.path.isfile(p):
            avisos.append('%s: no existe' % ruta)
            continue

        antes = io.open(p, encoding='utf-8').read()
        html = antes
        desde = zona_de_contenido(html)

        for clave, patron in campos:
            fila = por_clave.get(clave)
            if not fila:
                avisos.append('%s: no esta en la base' % clave)
                continue
            nuevo_texto = (fila.get('es') or '').strip()
            if not nuevo_texto:
                # Un campo vaciado no borra lo que dice el sitio: seria una
                # perdida silenciosa y el panel no avisa de eso.
                avisos.append('%s: vacio en la base, no se toca' % clave)
                continue

            m = re.search(patron, html[desde:], re.S)
            if not m:
                avisos.append('%s: no encuentro el texto en %s' % (clave, ruta))
                continue

            interior = m.group(1)
            actual = como_lo_dice_el_sitio(interior)
            # "WhatsApp:" explica la accion en la pagina, pero no forma parte
            # del numero editable. Sin sacarlo, cada build creeria que el panel
            # y el HTML difieren y reescribiria Contacto aunque nada cambiara.
            if clave == 'contacto.telefonos':
                actual = re.sub(r'(?m)^WhatsApp:\s*', '', actual)
            if actual == nuevo_texto:
                continue          # igual: no se toca, asi el archivo no cambia

            armado = armar(nuevo_texto, interior)
            if armado is None:
                avisos.append('%s: el texto nuevo quedo vacio' % clave)
                continue

            ini = desde + m.start(1)
            fin = desde + m.end(1)
            html = html[:ini] + armado + html[fin:]
            cambiados.append(clave)

        if html != antes and not verificar:
            io.open(p, 'w', encoding='utf-8', newline='\n').write(html)

    # --- los pares para el espejo en ingles ---
    # Van escapados de los dos lados. en_gen lee los nodos de texto tal como
    # estan en el archivo, y ahi un "&" ya es "&amp;": con la clave sin escapar
    # no coincide nunca y el texto sale en castellano en la pagina en ingles.
    # El valor tambien, porque se escribe directo en el HTML del espejo.
    def plano(t):
        return escapar(re.sub(r'\s+', ' ', t.strip()))

    pares = {}
    for f in filas:
        es, en = (f.get('es') or '').strip(), (f.get('en') or '').strip()
        if not es or not en:
            continue
        # El texto entero: es la forma en la que en_gen ve un nodo de texto.
        pares[plano(es)] = plano(en)
        # Y renglon por renglon, para los bloques partidos con <br>: ahi cada
        # renglon es un nodo de texto suelto.
        les = [x for x in es.split('\n') if x.strip()]
        len_ = [x for x in en.split('\n') if x.strip()]
        if len(les) == len(len_) and len(les) > 1:
            for a, b in zip(les, len_):
                pares[plano(a)] = plano(b)

    if not verificar:
        io.open(DESTINO_EN, 'w', encoding='utf-8', newline='\n').write(
            json.dumps(pares, ensure_ascii=False, indent=1, sort_keys=True) + '\n')

    print('reescritos: %d' % len(cambiados))
    if cambiados:
        print('  ' + ', '.join(cambiados))
    print('pares para el espejo: %d' % len(pares))
    if avisos:
        print('\navisos (%d):' % len(avisos))
        for a in avisos:
            print('  ' + a)

    if verificar and cambiados:
        print('\nEl sitio y la base no dicen lo mismo en esos campos.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main('--verificar' in sys.argv, '--supabase' in sys.argv))
