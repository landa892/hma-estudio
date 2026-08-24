# -*- coding: utf-8 -*-
"""Siembra en la base los escaneos que cada nota de prensa ya publica.

El panel de Prensa listaba solamente las imagenes subidas desde el propio panel
-las que llevan el prefijo ``panel-``-, y los 983 escaneos historicos viven en
``assets/prensa/<slug>/`` y no estaban en la base. Con lo cual el estudio abria
una nota, veia la galeria vacia y no podia reordenarla, elegir la tapa ni sacar
una imagen. No era una falla: el dato no existia ahi. Es lo mismo que pasaba
con los planos de las obras antes de la migracion 0011.

Se arregla igual que aquello: una fila por escaneo con el prefijo ``@seed:``,
que quiere decir "esto es la seleccion heredada del sitio". El panel la muestra
y, al primer cambio que haga el estudio, la pasa a ``@site:``; desde entonces
manda la base. Mientras sigan todas en ``@seed:``, ``panel_prensa.py`` no las
toca y la nota se publica con los escaneos de siempre.

Solo siembra las notas que todavia no tienen ninguna fila. Una nota ya
administrada no se vuelve a sembrar nunca, ni aunque el estudio haya borrado
imagenes: volver a meterlas seria deshacerle el trabajo.

    python docs/prensa_galerias.py --verificar   # no escribe, informa
    python docs/prensa_galerias.py
"""
import io
import json
import os
import struct
import sys
import urllib.error
import urllib.parse
import urllib.request


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, 'docs', 'prensa_datos.json')
GALERIAS = os.path.join(RAIZ, 'assets', 'prensa')

# Se siembran todos los escaneos, sin recortar. Aca no va el cupo de treinta de
# las galerias de obra: ni prensa_imagenes ni el panel de Prensa lo tienen, y
# poner uno haria perder imagenes. Tres notas pasan de treinta -archidiaries-2024
# con 66, casa-linda-entrevista-2024 con 44 y mas-arq-2024 con 36- y con un tope
# de treinta se sembrarian 927 de 983. Las 56 que quedan afuera se publicarian
# igual mientras nadie toque esas galerias, pero en cuanto el estudio reordenara
# una, la base pasaria a mandar y esa nota perderia treinta y seis escaneos sin
# que nadie los hubiera borrado.


def configuracion():
    url = (os.environ.get('SUPABASE_URL') or '').rstrip('/')
    clave = os.environ.get('SUPABASE_SERVICE_KEY') or ''
    if not url or not clave:
        raise RuntimeError('faltan SUPABASE_URL o SUPABASE_SERVICE_KEY')
    return url, clave


def pedir(url, clave, ruta, metodo='GET', cuerpo=None):
    datos = None if cuerpo is None else json.dumps(cuerpo).encode('utf-8')
    pedido = urllib.request.Request(url + ruta, data=datos, method=metodo)
    pedido.add_header('apikey', clave)
    pedido.add_header('Authorization', 'Bearer ' + clave)
    pedido.add_header('Content-Type', 'application/json')
    pedido.add_header('Prefer', 'return=representation')
    with urllib.request.urlopen(pedido) as respuesta:
        crudo = respuesta.read()
    if not crudo:
        return None
    return json.loads(crudo.decode('utf-8'))


def medidas_webp(ruta):
    """Ancho y alto de un WebP, leyendo la cabecera y sin abrir la imagen.

    El panel los usa para reservar el lugar de cada miniatura. Se lee a mano
    porque este paso corre en el servidor de Vercel, donde no hay Pillow.
    """
    try:
        with open(ruta, 'rb') as archivo:
            cabeza = archivo.read(30)
    except OSError:
        return None
    if len(cabeza) < 30 or cabeza[:4] != b'RIFF' or cabeza[8:12] != b'WEBP':
        return None
    tipo = cabeza[12:16]
    try:
        if tipo == b'VP8 ':
            ancho, alto = struct.unpack('<HH', cabeza[26:30])
            return ancho & 0x3FFF, alto & 0x3FFF
        if tipo == b'VP8L':
            bits = struct.unpack('<I', cabeza[21:25])[0]
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
        if tipo == b'VP8X':
            ancho = cabeza[24] | (cabeza[25] << 8) | (cabeza[26] << 16)
            alto = cabeza[27] | (cabeza[28] << 8) | (cabeza[29] << 16)
            return ancho + 1, alto + 1
    except struct.error:
        return None
    return None


def escaneos_de(nota):
    """Los archivos que la nota publica hoy, en el orden en que los publica."""
    salida = []
    for nombre in (nota.get('imagenes') or []):
        # Las que ya vienen del panel no se siembran: son de la base.
        if nombre.startswith('panel-'):
            continue
        local = os.path.join(GALERIAS, nota['slug'], nombre)
        if not os.path.isfile(local):
            continue
        salida.append((nombre, local))
    return salida


def main():
    verificar = '--verificar' in sys.argv
    with io.open(DATOS, encoding='utf-8') as archivo:
        notas = json.load(archivo)
    por_slug = {n['slug']: n for n in notas}

    # Con --verificar y sin credenciales se informa igual, contando desde el
    # JSON local. Sirve para mirar que se sembraria antes de publicar, que es
    # justo cuando no se tiene a mano la clave de servicio. Sin la base no se
    # sabe cuales notas ya tienen galeria, asi que el numero es el techo.
    try:
        url, clave = configuracion()
    except RuntimeError:
        if not verificar:
            raise
        cuantas = sum(len(escaneos_de(n)) for n in notas)
        con = [n for n in notas if escaneos_de(n)]
        print('sin credenciales: se cuenta desde docs/prensa_datos.json')
        print('notas con escaneos:  %d de %d' % (len(con), len(notas)))
        print('imagenes a sembrar:  %d como maximo' % cuantas)
        print('\n(--verificar: no se toco nada; sin la base no se sabe cuales '
              'notas ya tienen galeria cargada)')
        return 0

    publicaciones = pedir(
        url, clave, '/rest/v1/prensa_publicaciones?select=id,slug,titulo') or []
    existentes = pedir(
        url, clave, '/rest/v1/prensa_imagenes?select=publicacion_id') or []
    con_filas = {i['publicacion_id'] for i in existentes}

    nuevas, sembradas, sin_archivos = [], 0, []
    for publicacion in publicaciones:
        if publicacion['id'] in con_filas:
            continue
        nota = por_slug.get(publicacion['slug'])
        if not nota:
            continue
        archivos = escaneos_de(nota)
        if not archivos:
            sin_archivos.append(publicacion['slug'])
            continue
        for orden, (nombre, local) in enumerate(archivos):
            medidas = medidas_webp(local)
            nuevas.append({
                'publicacion_id': publicacion['id'],
                'storage_path': '@seed:/assets/prensa/%s/%s' % (publicacion['slug'], nombre),
                'alt': '%s — imagen %d' % (publicacion['titulo'], orden + 1),
                'orden': orden,
                'ancho': medidas[0] if medidas else None,
                'alto': medidas[1] if medidas else None,
            })
        sembradas += 1

    print('publicaciones en la base:      %d' % len(publicaciones))
    print('ya tenian galeria cargada:     %d' % len(con_filas))
    print('notas a sembrar:               %d' % sembradas)
    print('imagenes a sembrar:            %d' % len(nuevas))
    if sin_archivos:
        print('sin escaneos en el repositorio: %d (%s%s)'
              % (len(sin_archivos), ', '.join(sorted(sin_archivos)[:6]),
                 ' ...' if len(sin_archivos) > 6 else ''))

    if verificar:
        print('\n(--verificar: no se toco nada)')
        return 0
    if not nuevas:
        print('\nno hay nada que sembrar')
        return 0

    # De a tandas: un insert de mil filas de una vez se corta por tamano.
    for principio in range(0, len(nuevas), 200):
        pedir(url, clave, '/rest/v1/prensa_imagenes', metodo='POST',
              cuerpo=nuevas[principio:principio + 200])
    print('\nsembradas %d imagenes en %d notas' % (len(nuevas), sembradas))
    return 0


if __name__ == '__main__':
    sys.exit(main())
