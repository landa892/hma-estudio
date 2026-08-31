# -*- coding: utf-8 -*-
import os
import sys
import tempfile
import unittest
from unittest import mock


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'docs'))

import cache_publicado
import panel_galerias
import panel_prensa


WEBP_MINIMO = b'RIFF' + (b'\x00' * 4) + b'WEBP' + b'contenido'


class Respuesta:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return WEBP_MINIMO


class PanelCacheTest(unittest.TestCase):
    def test_obra_publicada_no_vuelve_a_storage(self):
        foto = {
            'id': 'fila-1',
            'storage_path': 'obra/1700000000-nueva.webp',
            'tipo': 'foto',
            'ancho': 1200,
            'alto': 800,
        }
        with tempfile.TemporaryDirectory() as raiz:
            with mock.patch.object(panel_galerias, 'RAIZ', raiz), \
                    mock.patch.object(panel_galerias, 'recuperar_publicada',
                                      return_value=True) as recuperar, \
                    mock.patch.object(panel_galerias.urllib.request,
                                      'urlopen') as storage:
                resuelta = panel_galerias.resolver_imagen(
                    'obra', foto, 'https://base.example')
        self.assertIn(cache_publicado.huella_ruta(foto['storage_path']),
                      resuelta['src'])
        recuperar.assert_called_once()
        storage.assert_not_called()

    def test_obra_nueva_va_a_storage_y_guarda_la_imagen(self):
        foto = {
            'id': 'fila-2',
            'storage_path': 'obra/1700000001-reemplazo.webp',
            'tipo': 'foto',
            'ancho': 1200,
            'alto': 800,
        }
        with tempfile.TemporaryDirectory() as raiz:
            with mock.patch.object(panel_galerias, 'RAIZ', raiz), \
                    mock.patch.object(panel_galerias, 'recuperar_publicada',
                                      return_value=False), \
                    mock.patch.object(panel_galerias.urllib.request,
                                      'urlopen', return_value=Respuesta()) as storage:
                resuelta = panel_galerias.resolver_imagen(
                    'obra', foto, 'https://base.example')
            destino = os.path.join(raiz, resuelta['src'].lstrip('/'))
            with open(destino, 'rb') as archivo:
                self.assertEqual(WEBP_MINIMO, archivo.read())
        storage.assert_called_once()

    def test_tapa_publicada_no_vuelve_a_storage(self):
        fila = {
            'slug': 'nota',
            'storage_path': 'prensa/1700000000-portada.webp',
        }
        with tempfile.TemporaryDirectory() as carpeta:
            with mock.patch.object(panel_prensa, 'ASSETS', carpeta), \
                    mock.patch.object(panel_prensa, 'recuperar_publicada',
                                      return_value=True) as recuperar, \
                    mock.patch.object(panel_prensa, 'pedir') as storage:
                publica = panel_prensa.tapa_local(
                    'https://base.example', 'clave', fila)
        self.assertIn(cache_publicado.huella_ruta(fila['storage_path']), publica)
        recuperar.assert_called_once()
        storage.assert_not_called()


if __name__ == '__main__':
    unittest.main()
