# -*- coding: utf-8 -*-
"""Incorpora los planos que el estudio agrego al Drive en agosto de 2026.

Cada lista contiene las laminas en castellano y en el orden en que deben verse.
Algunas obras tienen menos de cuatro archivos distintos en Drive; se publican
los disponibles sin duplicar laminas para completar artificialmente una fila.

    python docs/planos_drive_agosto.py
    python docs/planos_fichas.py
    python docs/en_gen.py
"""
import io
import json
import os
import urllib.request

from PIL import Image


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, 'docs', 'planos.json')
ANCHO_MAX = 1800
FUENTE_LOCAL = os.environ.get('HMA_PLANOS_FUENTE', '')

# slug: IDs de las imagenes del Drive, en orden.
PLANOS = {
    'cerveceria-austral': [
        '1N_zcKtv7j10C4rE8A-LrdmIv74cl7vUS',
        '17j7zdcorph1uhWwcouS9-96rk490QBlD',
        '1WTFfk32LEvd9RgFQNqkWER_eL6QMO9QQ',
        '11ODuFmkZS3qndUypioVxsAq0XrMq81C4',
        '1meqDXmeSqNcThcKEm7Ba7UfqVaoJG9l5',
    ],
    'cceba': [
        '1TomUdaO-9j_l0FlDfa5gzInKkB4kuCry',
        '1SNjrZUFMPN6QE1cJzJBg8pgg3Taq04_b',
        '1q2i6obOl15yBDmDfRBnjIN25o51Lr0KB',
        '14GvkFkhTFnj_ozUgw9e2i4B6p9QYGBcS',
    ],
    'indusparquet': [
        '1fKYSGlZYXk9hx-qr9PiTYRHookLsjxMU',
        '1XUugnWjZ0qPHeL0UL3ve4hTCioUppFh3',
        '12Znqs2I1JIsLUdbPHRALYWA1oLeiPTXx',
        '1ppzVfaIe6wfdPNaHaiJmPlCGjenvwSfK',
    ],
    'iol': [
        '1gASKYYLhlpjh45p8jGFKj0voZ-2W9dm_',
        '1LmFs38fg2o97iSBSXXIOQreNEgrlcclY',
        '1O-mcwYEGSwNthZNqwrWS_FsQxfYGp4iV',
        '1L5DNYiPb05-Kx5hBFGXGkAC7R9QSlleI',
    ],
    'kavak-oficinas': [
        '1SN-NN-WtIJOAeo__AS53JKBVXgQ-kQha',
        '1wEf8IGcoH0sWDoXES7Fhs5GTaAOEu4EI',
        '1HG6tjUAwxYkmrVEGR6b5e4fDbONSZWdH',
    ],
    'novotel': [
        '1XqyrS0JvhCgGauhaWr4CBL_uK--s1F9x',
        '1kOwS_0Sg-CZbdFh_tNO6LSjMXDyPPu-W',
        '1qDQlUWTMZuShymEY5bqJ1XSk6Gv3qWkg',
        '1ZsLcXdxIVwKyVunaTwwRP7-qRRkqjQWU',
    ],
    'oficina-casa-luna': [
        '1njcsglFxWXB1Mdmy_VpYCtTkmjl6_8X3',
        '1HN0968uKALMPNtGe4uMQeaaffxevHgQy',
        '1VUd5-24Y8ecie-olBfXgbhlAaDC1X_lC',
        '1upWLRpIENeLhM_MyqLdRmch1WQrnECsd',
    ],
    'parfumerie': [
        '1EGPTjNJdoCHNVqXgOwfYXzvfhh76uq_N',
        '1d2gpYz7ms-WzZnruPIn8oLMqkJ-BiPnN',
        '15KDjKdNH7bH5LaRhDATthEdpWRMpF98w',
        '19LWfkg4Vdg-Xkg_XlejDT1kWfLKk4IXA',
        '1fXo_nZ6_aA2Zp2tCJ72WyBwsQNotyqrh',
        '1Zu0m7w036GVLssVHJxlP3DgvfgOQXzqW',
        '1kr9wSciG4SXrnm_d8aq5gCM2PaoNSA66',
        '14f2Qtm55Ru10yfTxyn0RGwtZbZiobrcm',
    ],
    'ph-el-salvador': [
        '1fqqWqUD9IUTr5qxNkO0gltPM47cHgFhG',
        '1zVnD-rKxeSQIIftymIyEe3vD-OmpI4tc',
        '1hTVDyUwbhEZ0XuYNIwk-aYF1hjvFLSYn',
        '1UmhKmdyHd67H_B3IePMuoy6i6u-JtSlE',
    ],
    'ph-loft-arias': [
        '1pYCdeMSlfbTA5rufnnHUnmG_ObnPYv6x',
        '1AFezV0iZLZr2vauC1K4zzt2uN0WMnc37',
        '1W78646AHt4YdxlUG0zdepvmn13JM1OZ0',
        '1wtUCikHpS7qQVbs9hC60jj9zBx93Kz8g',
    ],
    'roket': [
        '1Jswotjodiblxpfg7oddwMh75Vbk4w7e1',
        '1PfJfAtnWrdBaITfEGzAFF-fkVOQr5l2h',
    ],
    'uala-ii': [
        '1hEG0NIsV4e1AoB05JbKNacEC7z11VU2P',
        '1WUaalW5MzWaVCWUDzBblKLMUOE86MUkh',
        '1zlxvTAuC5TVWXK2iwdVZktKkKiri5XK5',
        '1vZHWSd1X3zGL4DqIdn2jyMXH1tfuA4wd',
        '1M17SHApHKz4Y7_YW4TKV3-y4h_Nmv3np',
    ],
}


def descargar(slug, numero, file_id):
    local = os.path.join(FUENTE_LOCAL, slug, '%d.img' % numero)
    if FUENTE_LOCAL and os.path.isfile(local):
        return open(local, 'rb').read()
    url = ('https://drive.usercontent.google.com/download?id=%s&export=download&confirm=t'
           % file_id)
    pedido = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(pedido, timeout=90) as respuesta:
        return respuesta.read()


def main():
    datos = json.load(io.open(DATOS, encoding='utf-8'))
    for slug, ids in PLANOS.items():
        destino = os.path.join(RAIZ, 'assets', 'planos', slug)
        os.makedirs(destino, exist_ok=True)
        resumen = []
        for numero, file_id in enumerate(ids, 1):
            imagen = Image.open(io.BytesIO(descargar(slug, numero, file_id))).convert('RGB')
            if imagen.width > ANCHO_MAX:
                alto = round(imagen.height * ANCHO_MAX / imagen.width)
                imagen = imagen.resize((ANCHO_MAX, alto), Image.LANCZOS)
            imagen.save(os.path.join(destino, '%d.webp' % numero), 'WEBP',
                        quality=90, method=5)
            resumen.append({'n': numero, 'w': imagen.width, 'h': imagen.height})
        datos[slug] = resumen
        print('%-22s %d planos' % (slug, len(resumen)), flush=True)

    io.open(DATOS, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(datos, ensure_ascii=False, indent=1) + '\n')
    print('\nobras actualizadas: %d' % len(PLANOS))


if __name__ == '__main__':
    main()
