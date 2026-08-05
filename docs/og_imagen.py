# -*- coding: utf-8 -*-
"""Arma la imagen que se ve al compartir el link del sitio.

Un video no sirve como preview: WhatsApp, LinkedIn y los demas piden una
imagen fija. Se saca un cuadro del video de la portada —el que muestra el
estudio trabajando con el logo en la pared— y se recorta a 1200x630, que es
la medida que esperan esas plataformas.

Sale en JPG y no en WebP: algunos lectores de preview todavia no abren WebP
y muestran el link sin imagen.

    python docs/og_imagen.py
"""
import io, os, subprocess, sys

ANCHO, ALTO = 1200, 630
SEGUNDO = '2'
VIDEO = os.path.join('assets', 'video', 'estudio-hero.mp4')
DEST = os.path.join('assets', 'og-portada.jpg')


def main():
    from PIL import Image
    tmp = os.path.join('assets', '_og_tmp.png')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', SEGUNDO, '-i', VIDEO,
                    '-frames:v', '1', tmp], check=True)
    im = Image.open(tmp).convert('RGB')
    # Recorte tipo "cover": el cuadro es 16:9 y el preview 1.9:1.
    escala = max(ANCHO / im.width, ALTO / im.height)
    im = im.resize((round(im.width * escala), round(im.height * escala)), Image.LANCZOS)
    x = (im.width - ANCHO) // 2
    y = (im.height - ALTO) // 2
    im = im.crop((x, y, x + ANCHO, y + ALTO))
    im.save(DEST, 'JPEG', quality=88, optimize=True, progressive=True)
    os.remove(tmp)
    print('%s  %dx%d  %d KB' % (DEST, im.width, im.height, os.path.getsize(DEST) // 1024))


if __name__ == '__main__':
    main()
