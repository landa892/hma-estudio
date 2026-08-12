# -*- coding: utf-8 -*-
"""Aplica una sola vez las correcciones de contenido recibidas en agosto.

Cada cambio comprueba primero el valor anterior. Asi, el build corrige la base
que ya estaba publicada pero no vuelve a pisar una edicion posterior hecha por
el estudio desde el panel.

    python docs/panel_correcciones_agosto.py
    python docs/panel_correcciones_agosto.py --supabase
"""
import io
import json
import os
import sys
import urllib.request


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def reemplazo(prefijo_viejo, prefijo_nuevo):
    def aplicar(valor):
        if isinstance(valor, str) and valor.startswith(prefijo_viejo):
            return prefijo_nuevo + valor[len(prefijo_viejo):]
        return valor
    return aplicar


def valor(viejo, nuevo):
    return lambda actual: nuevo if actual == viejo else actual


def completar_vacio(nuevo):
    return lambda actual: nuevo if not actual else actual


CORRECCIONES = {
    'edificio-del-plata': {
        'memoria': reemplazo('corresponde a oficinas:', 'Corresponde a oficinas:'),
        'memoria_en': reemplazo('corresponds to offices:', 'Corresponds to offices:'),
    },
    'osten-tower': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Sofía Kesting', 'Arq. Camila Lacarpia',
             'Arq. Victoria Nabias', 'Arq. Milagros Rivelli',
             'Arq. Chiara Beltrami', 'Arq. Paula Miano'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Sofía Kesting', 'Arq. Camila Lacarpia',
             'Arq. Victoria Nabias', 'Arq. Milagros Rivelli']),
    },
    'cerveceria-austral': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Camila Lacarpia', 'Arq. Luciano Cichanowski',
             'Arq. Josué Solano'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Camila Lacarpia', 'Luciano Cichanowski', 'Josué Solano']),
    },
    'juan-valdez': {
        'bajada': valor(
            'Cafetería Juan Valdez sobre Avenida Las Heras.',
            'Dos cafeterías Juan Valdez en Buenos Aires.'),
    },
    'movistar-arena': {
        'memoria': reemplazo(
            'A diferencia de la generalidad de los proyectos gastronómicos, '
            'en los que a priori se tiene bien definido el tipo de usuario…el\n\n'
            ', ya sea por rango etario, por tipo de propuesta gastronómica, '
            'por ubicación y horario de apertura, o incluso por el valor del '
            'cubierto, en este proyecto ninguna de esas variables era fija.',
            'A diferencia de la generalidad de los proyectos gastronómicos, '
            'en los que a priori se tiene bien definido el tipo de usuario '
            '—ya sea por rango etario, por tipo de propuesta gastronómica, '
            'por ubicación y horario de apertura, o incluso por el valor del '
            'cubierto—, en este proyecto ninguna de esas variables era fija.'),
        'memoria_en': reemplazo(
            'Unlike most gastronomic projects, where the type of user is well '
            'defined from the start — the\n\n, whether by age range, by the kind '
            'of food offered, by location and opening hours, or even by the '
            'price of a cover — in this project none of those variables was fixed.',
            'Unlike most gastronomic projects, where the type of user is well '
            'defined from the start — whether by age range, by the kind of food '
            'offered, by location and opening hours, or even by the price of a '
            'cover — none of those variables was fixed in this project.'),
    },
    'tostado': {
        'bajada': valor(
            'Local de Tostado Café Club en Miami.',
            'Locales de Tostado Café Club en Argentina, Uruguay, Miami y São Paulo.'),
    },
    'hausscape': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Vanik Margossian', 'Arq. Milca Amado,', 'Arq. Julieta Setton'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Vanik Margossian', 'Arq. Milca Amado', 'Arq. Julieta Setton']),
    },
    'moshu': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Vanik Margossian', 'Arq. Dolores Gayoso',
             'Arq. Marcela Bernat/ Arq. Vanik Margossian'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Vanik Margossian', 'Arq. Dolores Gayoso',
             'Arq. Marcela Bernat']),
    },
    'mamba-bar': {
        'bajada': valor(
            'Un bar de geometrías facetadas en cobre y hormigón, con un patio '
            'selvático al fondo.',
            'Un bar organizado por una pieza de hierro y paneles facetados, con '
            'un patio selvático al fondo.'),
    },
    'goodsten': {
        'bajada': valor(
            'Una cremería que se presenta como un volumen facetado de pizarra '
            'negra con una cuña de cobre.',
            'Una cremería concebida como una envolvente diamantada de superficies '
            'facetadas.'),
    },
    'iguanafix': {
        'bajada': valor(
            'Oficinas resueltas con tabiques y mobiliario de OSB, y la gráfica '
            'de la empresa sobre los vidrios.',
            'Remodelación integral de las oficinas de IguanaFix en Buenos Aires.'),
    },
    'victoria-brown': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Magdalena Molinari', 'Arq. Leonardo G. Militello'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Magdalena Molinari']),
    },
    'dos-casas-conde': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Leonardo G. Militello', 'Arq. Ruben Ruiz'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello', 'Arq. Ruben Ruiz']),
    },
    'oficina-casa-luna': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Leonardo G. Militello', 'Arq. Florencia Schvartzman',
             'Arq. Belen Lepro Delelis'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Florencia Schvartzman', 'Arq. Belen Lepro Delelis']),
    },
    'ph-el-salvador': {
        'equipo': valor(
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Leonardo G. Militello', 'Arq. Carmela Zuleta',
             'Arq. Juliana Zorza', 'Arq. Samira Attar'],
            ['Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
             'Arq. Carmela Zuleta', 'Arq. Juliana Zorza', 'Arq. Samira Attar']),
    },
}


def sumar_memorias_en_pendientes():
    ruta = os.path.join(RAIZ, 'docs', 'memorias_en_agosto.json')
    with io.open(ruta, encoding='utf-8') as archivo:
        traducciones = json.load(archivo)
    for slug, traduccion in traducciones.items():
        CORRECCIONES.setdefault(slug, {})['memoria_en'] = completar_vacio(traduccion)


sumar_memorias_en_pendientes()


def corregir(obras):
    cambios = {}
    por_slug = {o['slug']: o for o in obras}
    for slug, campos in CORRECCIONES.items():
        obra = por_slug.get(slug)
        if not obra:
            continue
        for campo, transformar in campos.items():
            anterior = obra.get(campo)
            nuevo = transformar(anterior)
            if nuevo != anterior:
                obra[campo] = nuevo
                cambios.setdefault(slug, {})[campo] = nuevo
    return cambios


def parchear_supabase(cambios, url, clave):
    cabeceras = {
        'apikey': clave,
        'Authorization': 'Bearer ' + clave,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal',
    }
    for slug, campos in cambios.items():
        pedido = urllib.request.Request(
            url + '/rest/v1/obras?slug=eq.' + slug,
            data=json.dumps(campos, ensure_ascii=False).encode('utf-8'),
            headers=cabeceras,
            method='PATCH')
        with urllib.request.urlopen(pedido, timeout=30):
            pass


def desde_supabase(url, clave):
    campos = sorted({campo for cs in CORRECCIONES.values() for campo in cs})
    pedido = urllib.request.Request(
        url + '/rest/v1/obras?select=slug,' + ','.join(campos),
        headers={'apikey': clave, 'Authorization': 'Bearer ' + clave})
    with urllib.request.urlopen(pedido, timeout=30) as respuesta:
        return json.loads(respuesta.read().decode('utf-8'))


def main(supabase):
    if supabase:
        url = os.environ.get('SUPABASE_URL', '').rstrip('/')
        clave = os.environ.get('SUPABASE_SERVICE_KEY', '')
        if not url or not clave:
            raise SystemExit('Faltan SUPABASE_URL y SUPABASE_SERVICE_KEY en el entorno.')
        obras = desde_supabase(url, clave)
        cambios = corregir(obras)
        parchear_supabase(cambios, url, clave)
        print('correcciones aplicadas en Supabase: %d obras' % len(cambios))
        return

    ruta = os.path.join(RAIZ, 'docs', 'panel_datos.json')
    with io.open(ruta, encoding='utf-8') as archivo:
        obras = json.load(archivo)
    cambios = corregir(obras)
    if cambios:
        with io.open(ruta, 'w', encoding='utf-8', newline='\n') as archivo:
            json.dump(obras, archivo, ensure_ascii=False, indent=1)
            archivo.write('\n')
    print('correcciones aplicadas en panel_datos.json: %d obras' % len(cambios))


if __name__ == '__main__':
    main('--supabase' in sys.argv[1:])
