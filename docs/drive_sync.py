# -*- coding: utf-8 -*-
"""Rehace fotos, portada y planos de cada obra desde el Drive del estudio.

Las galerias del sitio venian de una importacion vieja y parcial: en varias
obras habia planos y capturas de pantalla ocupando el lugar de las fotos, y
faltaban fotos que en el Drive estaban desde siempre. Burger 7167 es el caso
claro: el Drive tiene once fotos de Federico Kulekdjian y en el sitio habia una
sola foto real, seis planos repetidos y dos capturas de una pagina web.

Aca el Drive pasa a ser la fuente. De cada obra se toma:

    01 - Fotos     -> assets/gallery/<slug>/1..N.webp
    03 - Carátula  -> assets/covers/<slug>.webp
    00 - Planos    -> assets/planos/<slug>/1..N.webp

El estudio nombra esas carpetas de formas distintas segun la obra -"01- Fotos",
"02 - Fotos", "01-Pics", "00 - Panos", "02 - Texts"-, asi que se reconocen por
lo que dicen y no por el nombre exacto.

Lee directo de los ZIP que baja Google Drive, sin descomprimirlos: son unos 15
GB y no hay disco para dejarlos abiertos. De cada archivo solo queda el WebP
final, al 82% y con el lado mayor hasta 1800 px, que es lo mismo que hace el
panel al subir una foto.

    python docs/drive_sync.py --verificar       # no escribe, informa
    python docs/drive_sync.py --obra burger-7167
    python docs/drive_sync.py
"""
import collections
import glob
import io
import json
import os
import re
import sys
import unicodedata
import zipfile

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIPS = os.environ.get('HMA_DRIVE_ZIPS', r'E:\descargas\pagina hma-*.zip')
DATOS = os.path.join(RAIZ, 'docs', 'panel_datos.json')

LADO_MAYOR = 1800
CALIDAD = 82
ANCHO_PORTADA = 1200

# Carpetas del Drive que no tienen obra en el sitio. Se listan para que el
# informe no las de por perdidas cada vez.
SIN_OBRA = {
    '36-Comedor Diario': 'obra que todavia no esta en el sitio',
    '90-Supervielle': 'obra nueva, sin textos cargados',
}

# Los nombres que el buscador automatico no resuelve solo.
A_MANO = {
    # Los tres Uala van fijos: el buscador por parecido los cruzaba -le daba
    # los cuatro renders de Gigena a Uala II y las doce fotos de Nicaragua II a
    # Gigena-, que es justo la mezcla que el cliente marco el 19/08/2026.
    '82-Ualá III (Gigena)': 'uala-gigena',
    '37-Uala 2': 'uala-ii',
    '36-Uala': 'uala-office',
    '00 Vilela': 'atelier-vilela',
    '26-The Birra - Roca 63': 'the-birra',
    '71-Ziva Hyatt': 'hyatt-ziva',
    '70-FOA Osten': 'osten-foa',
    '89-Austral': 'cerveceria-austral',
}


def normal(texto):
    t = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode().lower()
    t = re.sub(r'\(.*?\)', ' ', t)
    t = re.sub(r'^\s*\d+\s*[-.]?\s*', '', t)
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]+', ' ', t)).strip()


def que_carpeta(nombre):
    """Que guarda esta subcarpeta, mirando lo que dice y no el nombre exacto."""
    s = normal(nombre)
    if 'caratula' in s:
        return 'caratula'
    if 'foto' in s or 'pic' in s:
        return 'fotos'
    # "plan" cubre Planos, Panos y Plans: el estudio usa las tres.
    if 'plan' in s or 'pano' in s:
        return 'planos'
    if 'texto' in s or 'text' in s:
        return 'textos'
    return None


def orden_natural(ruta):
    """Ordena 2 antes que 10, respetando como nombra el estudio."""
    nombre = ruta.rsplit('/', 1)[-1]
    partes = re.split(r'(\d+)', nombre)
    return [int(p) if p.isdigit() else p.lower() for p in partes]


def indexar():
    """{(anio, carpeta): {tipo: [(zip, entrada)]}} recorriendo los ZIP."""
    obras = collections.defaultdict(lambda: collections.defaultdict(list))
    archivos = sorted(glob.glob(ZIPS))
    if not archivos:
        raise SystemExit('No encuentro los ZIP en %s' % ZIPS)
    for ruta in archivos:
        with zipfile.ZipFile(ruta) as z:
            for entrada in z.namelist():
                if entrada.endswith('/'):
                    continue
                p = entrada.split('/')
                if len(p) < 6 or p[1] != 'trabajos':
                    continue
                # Se mira toda la ruta debajo de la obra y gana la carpeta
                # mas profunda que se reconozca: Araoz guarda sus planos en
                # "01- Fotos/00- Planos/JPG", asi que quedarse con el primer
                # nivel los daba por fotos.
                tipo = None
                for tramo in p[4:-1]:
                    t = que_carpeta(tramo)
                    if t:
                        tipo = t
                if tipo:
                    obras[(p[2], p[3])][tipo].append((ruta, entrada))
    return obras, archivos


def emparejar(obras):
    """Cada carpeta del Drive con la obra del sitio que le corresponde."""
    import difflib
    datos = json.load(io.open(DATOS, encoding='utf-8'))
    por_norm = {}
    for o in datos:
        por_norm.setdefault(normal(o['titulo']), o['slug'])
        por_norm.setdefault(normal(o['slug'].replace('-', ' ')), o['slug'])

    pares, sueltas = {}, []
    for (anio, carpeta) in sorted(obras):
        if carpeta in SIN_OBRA:
            sueltas.append((carpeta, SIN_OBRA[carpeta]))
            continue
        slug = A_MANO.get(carpeta) or por_norm.get(normal(carpeta))
        if not slug:
            cerca = difflib.get_close_matches(normal(carpeta), list(por_norm),
                                              n=1, cutoff=0.72)
            slug = por_norm[cerca[0]] if cerca else None
        if slug:
            pares[(anio, carpeta)] = slug
        else:
            sueltas.append((carpeta, 'sin obra que le corresponda'))
    return pares, sueltas


def convertir(datos, destino, ancho_fijo=None):
    """Guarda la imagen como WebP, del tamano que usa el sitio."""
    try:
        im = Image.open(io.BytesIO(datos))
        im = im.convert('RGB')
    except Exception:
        return None
    if ancho_fijo:
        alto = round(im.height * ancho_fijo / im.width)
        im = im.resize((ancho_fijo, alto), Image.LANCZOS)
    elif max(im.size) > LADO_MAYOR:
        e = LADO_MAYOR / max(im.size)
        im = im.resize((round(im.width * e), round(im.height * e)), Image.LANCZOS)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    im.save(destino, 'WEBP', quality=CALIDAD, method=6)
    return im.size


def imagenes(lista):
    return [x for x in lista
            if x[1].lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff'))]


def volcar(slug, tipo, lista, verificar, abiertos):
    """Reescribe una carpeta del sitio con lo que trae el Drive."""
    lista = sorted(imagenes(lista), key=lambda x: orden_natural(x[1]))
    if not lista:
        return 0

    if tipo == 'caratula':
        destino = os.path.join(RAIZ, 'assets', 'covers', slug + '.webp')
        if verificar:
            return 1
        z = abiertos[lista[0][0]]
        convertir(z.read(lista[0][1]), destino, ancho_fijo=ANCHO_PORTADA)
        return 1

    carpeta = os.path.join(RAIZ, 'assets',
                           'gallery' if tipo == 'fotos' else 'planos', slug)
    if verificar:
        return len(lista)

    if os.path.isdir(carpeta):
        for viejo in glob.glob(os.path.join(carpeta, '*.webp')):
            os.remove(viejo)
    puestas = 0
    for i, (ruta_zip, entrada) in enumerate(lista, 1):
        z = abiertos[ruta_zip]
        if convertir(z.read(entrada), os.path.join(carpeta, '%d.webp' % i)):
            puestas += 1
    return puestas


def main(verificar, solo):
    obras, archivos = indexar()
    pares, sueltas = emparejar(obras)
    print('carpetas de obra en el Drive: %d   emparejadas: %d' % (len(obras), len(pares)))
    print()

    abiertos = {r: zipfile.ZipFile(r) for r in archivos} if not verificar else {}
    try:
        print('%-24s %6s %6s %8s' % ('obra', 'fotos', 'planos', 'portada'))
        print('-' * 50)
        for (anio, carpeta), slug in sorted(pares.items(), key=lambda x: x[1]):
            if solo and slug != solo:
                continue
            partes = obras[(anio, carpeta)]
            f = volcar(slug, 'fotos', partes.get('fotos', []), verificar, abiertos)
            p = volcar(slug, 'planos', partes.get('planos', []), verificar, abiertos)
            c = volcar(slug, 'caratula', partes.get('caratula', []), verificar, abiertos)
            print('%-24s %6d %6d %8s' % (slug, f, p, 'si' if c else '—'))
    finally:
        for z in abiertos.values():
            z.close()

    if sueltas:
        print()
        print('carpetas del Drive sin obra en el sitio:')
        for carpeta, motivo in sueltas:
            print('  %-34s %s' % (carpeta, motivo))

    datos = json.load(io.open(DATOS, encoding='utf-8'))
    huerfanas = sorted(set(o['slug'] for o in datos) - set(pares.values()))
    if huerfanas:
        print()
        print('obras del sitio sin carpeta en el Drive -no se tocan-:')
        for slug in huerfanas:
            print('  ' + slug)
    if verificar:
        print()
        print('(--verificar: no se escribio nada)')
    return 0


if __name__ == '__main__':
    solo = None
    if '--obra' in sys.argv:
        solo = sys.argv[sys.argv.index('--obra') + 1]
    sys.exit(main('--verificar' in sys.argv, solo))
