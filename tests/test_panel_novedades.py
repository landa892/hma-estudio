"""Una foto nueva debe salir del cache sin perder el respaldo del panel."""
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'docs'))
import panel_novedades as novedades


class ImagenNovedadesTest(unittest.TestCase):
    def test_cada_carga_tiene_otra_url_y_es_estable(self):
        vieja = novedades.ruta_imagen_salida('linkedin', 'home/linkedin-111.webp')
        nueva = novedades.ruta_imagen_salida('linkedin', 'home/linkedin-222.webp')
        self.assertNotEqual(vieja, nueva)
        self.assertEqual(nueva, novedades.ruta_imagen_salida(
            'linkedin', 'home/linkedin-222.webp'))
        self.assertTrue(nueva.startswith('/assets/home/linkedin-panel-'))

    def test_locales_no_cambian(self):
        for prefijo in ('@site:', '@seed:'):
            self.assertEqual(novedades.ruta_imagen_salida(
                'instagram', prefijo + '/assets/foto.webp'), '/assets/foto.webp')

    def test_descarga_coincide_con_ruta_del_verificador(self):
        with tempfile.TemporaryDirectory() as carpeta:
            with patch.object(novedades, 'CARPETA', carpeta), patch.object(
                    novedades.urllib.request, 'urlopen', return_value=io.BytesIO(b'foto')):
                salida = novedades.imagen_local('linkedin', 'home/linkedin-222.webp',
                                                'https://example.test', 'prueba')
            self.assertEqual(salida, novedades.ruta_imagen_salida(
                'linkedin', 'home/linkedin-222.webp'))
            self.assertEqual((Path(carpeta) / Path(salida).name).read_bytes(), b'foto')

    def test_descarga_vacia_no_publica_foto_vieja(self):
        with tempfile.TemporaryDirectory() as carpeta:
            with patch.object(novedades, 'CARPETA', carpeta), patch.object(
                    novedades.urllib.request, 'urlopen', return_value=io.BytesIO(b'')):
                with self.assertRaises(RuntimeError):
                    novedades.imagen_local('linkedin', 'home/linkedin-222.webp',
                                           'https://example.test', 'prueba')


if __name__ == '__main__':
    unittest.main()
