# -*- coding: utf-8 -*-
"""Baja los planos de cada obra y los deja listos para el sitio.

Van a /assets/planos/<slug>/N.webp. Se topean en seis por obra: el cliente
pidio cuatro de minima y seis es lo que ocupa una fila entera de la grilla.

Los planos son dibujos sobre blanco, asi que se guardan con calidad alta:
una linea fina se rompe antes que una foto.
"""
import io, json, os, re, sys, unicodedata, difflib, html, urllib.request
from PIL import Image

RAIZ = os.environ['HMA_RAIZ']
TOPE = 6
ANCHO_MAX = 1800

# El WordPress nombra algunas obras distinto que el sitio.
ALIAS = {
    'edificioaraoz': 'araoz', 'araozbuilding': 'araoz',
    'edificiobolivar': 'bolivar', 'bolivarbuilding': 'bolivar',
    'edificiomalabia': 'malabia', 'malabiabuilding': 'malabia',
    'cafeteriaostencasafoa': 'osten-foa', 'ostencoffeeshopcasafoa': 'osten-foa',
    'moshutreehouse': 'moshu', 'thenimbar': 'nim-bar',
    'mercadomanduca': 'manduca', 'manducamarket': 'manduca',
    'movistararenaviplounges': 'movistar-arena',
    'kavakhub': 'kavak-hub', 'kavak': 'kavak-oficinas',
    'ualaii': 'uala-gigena', 'uala': 'uala-office',
    'stellaartoismercat': 'stella-artois-mercat',
    'abastoshoppingfoodcourt': 'abasto-patio-comidas',
    'patiocomidasabastoshopping': 'abasto-patio-comidas',
    'willamsburg': 'williamsburg',
    'tostadofast': 'tostado', 'tostadocallao': 'tostado',
    'luccianoscaballito': 'luccianos-caballito',
    'luccianosolivos': 'luccianos-olivos',
    'elclasicodequilmes': 'clasico-quilmes',
    '7167burger': 'burger-7167', 'burger7167': 'burger-7167',
    'sinapsispabellonargentinoparavenecia': 'bienal-venecia',
    'edificiodelplata': 'edificio-del-plata',
    'antichetentazioni': 'antiche', 'antiche': 'antiche',
    'hyattzivabarbados': 'hyatt-ziva',
}


def norm(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '', s)


def obras_del_sitio():
    h = io.open(os.path.join(RAIZ, 'proyectos', 'index.html'), encoding='utf-8').read()
    d = {}
    for m in re.finditer(r'(?s)<a href="/proyectos/([^"]+)/" class="project-card".*?'
                         r'class="p-name">(.*?)<', h):
        d[norm(html.unescape(m.group(2)))] = m.group(1)
        d[norm(m.group(1))] = m.group(1)
    return d


def bajar(u):
    r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(r, timeout=60).read()


def main():
    pl = json.load(io.open('planos.json', encoding='utf-8'))
    sitio = obras_del_sitio()
    slugs = set(sitio.values())

    porslug = {}
    for t, fs in pl.items():
        k = norm(t)
        s = ALIAS.get(k) or sitio.get(k)
        if not s:
            c = difflib.get_close_matches(k, sitio.keys(), 1, 0.84)
            s = sitio[c[0]] if c else None
        if s and s in slugs:
            # Si dos titulos caen en la misma obra, gana el que trae mas.
            if s not in porslug or len(fs) > len(porslug[s]):
                porslug[s] = fs

    print('obras con planos: %d de %d' % (len(porslug), len({v for v in sitio.values()})))
    resumen = {}
    for slug in sorted(porslug):
        fs = [f for f in porslug[slug] if f['w'] >= 900][:TOPE]
        if len(fs) < 4:
            print('  %-22s solo %d planos utiles, se saltea' % (slug, len(fs)))
            continue
        dest = os.path.join(RAIZ, 'assets', 'planos', slug)
        os.makedirs(dest, exist_ok=True)
        hechos = []
        for f in fs:
            i = len(hechos) + 1
            try:
                im = Image.open(io.BytesIO(bajar(f['url']))).convert('RGB')
                if im.width > ANCHO_MAX:
                    im = im.resize((ANCHO_MAX, round(im.height * ANCHO_MAX / im.width)),
                                   Image.LANCZOS)
                p = os.path.join(dest, '%d.webp' % i)
                im.save(p, 'WEBP', quality=90, method=5)
                hechos.append({'n': i, 'w': im.width, 'h': im.height})
            except Exception as e:
                print('     %s -> %s' % (f['url'].rsplit('/', 1)[-1][:34], e))
        if hechos:
            resumen[slug] = hechos
            print('  %-22s %d planos' % (slug, len(hechos)))
        sys.stdout.flush()

    io.open(os.path.join(RAIZ, 'docs', 'planos.json'), 'w', encoding='utf-8').write(
        json.dumps(resumen, ensure_ascii=False, indent=1))
    print('\nobras con planos en el sitio: %d' % len(resumen))


if __name__ == '__main__':
    main()
