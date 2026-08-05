# -*- coding: utf-8 -*-
"""Elige los videos de charlas y entrevistas, con su fecha y su miniatura.

El cliente no quiere los "despiece de elementos" —que son animaciones de
planos— sino los videos donde el estudio habla: charlas, conferencias y
entrevistas. Se toman en el orden en que los lista el canal, que es del mas
nuevo al mas viejo.

La fecha exacta sale del feed RSS cuando el video esta entre los quince mas
recientes; para los mas viejos se estima a partir del "hace N meses/años"
que muestra el canal, y por eso se guarda solo el año.
"""
import io, json, re, urllib.request
from datetime import date

HOY = date(2026, 8, 5)          # fecha del sistema al generar esto
CUANTOS = 7

# Los que muestran a la gente hablando. Se listan por id para no depender de
# adivinar por titulo: "Movistar Arena VIP Lounge" tambien tiene gente, pero
# es un video de obra, no una charla.
CHARLAS = [
    '9Z2Q4iS2Ip0',   # El estudio detras del Movistar Arena
    '9z06HuZzhB4',   # DESTINO MIAMI
    'pDUnbL_uq5E',   # 10 Mandamientos industria gastronomica
    '_-nCkxIThi4',   # HMA en DINA
    'p6GLj-XBTB4',   # Charla Arquitectura e Interiorismo, MARQ & SCA
    'rRYYjdBox2g',   # La creatividad en estado presente
    'ZcC_m8EkeXY',   # Entrevista Galeria de Arte Objeto A
    'XgXUthNLQco',   # Charla FADU UBA
    '0sFr8XCyvJQ',   # Arquitectura interior e inmersion
    '7OKO4xfgjHI',   # Oradores Tendiez, MALBA
    'Xv4dcHYOLkM',   # Entrevista Los Destacados
]


def peso(u):
    try:
        r = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        return len(urllib.request.urlopen(r, timeout=20).read())
    except Exception:
        return 0


def mejor_miniatura(vid):
    """hqdefault trae bandas negras en los videos verticales; maxres no."""
    for v in ('maxresdefault', 'sddefault', 'hqdefault'):
        u = 'https://i.ytimg.com/vi/%s/%s.jpg' % (vid, v)
        if peso(u) >= 8000:
            return u
    return 'https://i.ytimg.com/vi/%s/hqdefault.jpg' % vid


def fecha_aprox(texto):
    m = re.search(r'hace (\d+)\s+(a\xf1o|mes|semana|d\xeda)', texto or '')
    if not m:
        return ''
    n, u = int(m.group(1)), m.group(2)
    dias = {'a\xf1o': 365, 'mes': 30, 'semana': 7, 'd\xeda': 1}[u] * n
    d = date.fromordinal(HOY.toordinal() - dias)
    return '%04d-%02d' % (d.year, d.month)


def main():
    todos = json.load(io.open('yt_todos.json', encoding='utf-8'))
    rss = io.open('yt2.xml', encoding='utf-8').read()
    exactas = dict(re.findall(
        r'(?s)<yt:videoId>(.*?)</yt:videoId>.*?<published>(.{7})', rss))

    out = []
    for vid in CHARLAS[:CUANTOS]:
        if vid not in todos:
            print('  %s no esta en el listado del canal' % vid)
            continue
        t = todos[vid]['titulo']
        f = exactas.get(vid) or fecha_aprox(todos[vid]['meta'])
        out.append({'id': vid, 'titulo': t, 'fecha': f + '-01' if len(f) == 7 else f,
                    'cat': 'charla', 'mini': mejor_miniatura(vid)})
        print('  %-13s %-9s %s' % (vid, f, t[:58]))

    io.open('yt_videos.json', 'w', encoding='utf-8').write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print('\nelegidos: %d' % len(out))


if __name__ == '__main__':
    main()
