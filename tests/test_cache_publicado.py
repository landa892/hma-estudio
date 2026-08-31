# -*- coding: utf-8 -*-
import os
import sys
import tempfile
import unittest
from unittest import mock


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'docs'))

import cache_publicado


WEBP_MINIMO = b'RIFF' + (b'\x00' * 4) + b'WEBP' + b'contenido'


class Respuesta:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return WEBP_MINIMO


class CachePublicadoTest(unittest.TestCase):
    def test_la_huella_cambia_si_el_panel_reemplaza_la_ruta(self):
        self.assertNotEqual(
            cache_publicado.huella_ruta('obra/primera.webp'),
            cache_publicado.huella_ruta('obra/segunda.webp'))

    @mock.patch('cache_publicado.urllib.request.urlopen', return_value=Respuesta())
    def test_recupera_la_copia_exacta_del_sitio_publicado(self, abrir):
        with tempfile.TemporaryDirectory() as carpeta:
            destino = os.path.join(carpeta, 'panel.webp')
            self.assertTrue(cache_publicado.recuperar_publicada(
                '/assets/gallery/obra/panel.webp', destino))
            with open(destino, 'rb') as archivo:
                self.assertEqual(WEBP_MINIMO, archivo.read())
        self.assertEqual(1, abrir.call_count)

    @mock.patch('cache_publicado.urllib.request.urlopen')
    def test_un_html_de_error_no_se_guarda_como_imagen(self, abrir):
        respuesta = Respuesta()
        respuesta.read = lambda: b'<html>no existe</html>'
        abrir.return_value = respuesta
        with tempfile.TemporaryDirectory() as carpeta:
            destino = os.path.join(carpeta, 'panel.webp')
            self.assertFalse(cache_publicado.recuperar_publicada(
                '/assets/gallery/obra/ausente.webp', destino))
            self.assertFalse(os.path.exists(destino))


if __name__ == '__main__':
    unittest.main()
