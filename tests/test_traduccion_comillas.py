"""Las novedades con comillas deben llegar al espejo sin bloquear el build."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'docs'))
import en_gen
import panel_novedades


class TraduccionComillasTest(unittest.TestCase):
    def test_titulo_linkedin_escapado_llega_en_ingles(self):
        es = '"Interfaz" instalaci\u00f3n en galer\u00eda de Arte'
        en = '\u2018Interfaz\u2019 \u2013 an installation at an art gallery'
        pagina = panel_novedades.reemplazar_texto(
            '<h2 data-linkedin-title>Anterior</h2>', 'data-linkedin-title', es)
        with patch.dict(en_gen.TEXTOS_EN, {es: en}, clear=True):
            self.assertEqual(en_gen.traducir_html(pagina),
                             '<h2 data-linkedin-title>' + en + '</h2>')

    def test_apostrofes_y_signos_siguen_siendo_texto(self):
        with patch.dict(en_gen.TEXTOS_EN,
                        {"'Arte' &amp; &lt;forma&gt;": 'Art &amp; &lt;shape&gt;'},
                        clear=True):
            self.assertEqual(en_gen.T('&#x27;Arte&#x27; &amp; &lt;forma&gt;'),
                             'Art &amp; &lt;shape&gt;')


if __name__ == '__main__':
    unittest.main()
