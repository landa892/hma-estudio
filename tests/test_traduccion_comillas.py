"""Las novedades con comillas deben llegar al espejo sin bloquear el build."""
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'docs'))
import en_gen
import panel_novedades


class TraduccionComillasTest(unittest.TestCase):
    def test_traducciones_separadas_por_red_y_multilinea(self):
        pagina = ('<h2 data-linkedin-title>Noticias</h2>'
                  '<h2 data-instagram-title>Noticias</h2>'
                  '<p data-linkedin-text>Anterior</p>')
        salida = en_gen.traducir_novedades(pagina, {
            'data-linkedin-title': 'Studio news',
            'data-instagram-title': 'Latest work',
            'data-linkedin-text': 'First line\nSecond line & more',
        })
        self.assertIn('data-linkedin-title>Studio news</h2>', salida)
        self.assertIn('data-instagram-title>Latest work</h2>', salida)
        self.assertIn('First line\nSecond line &amp; more', salida)

    def test_numeros_emojis_y_html_literal_en_novedades(self):
        for texto in ('2027', '\U0001f3c6', '"Art" & <design>', "Designer\u2019s studio"):
            with self.subTest(texto=texto):
                salida = en_gen.traducir_novedades(
                    '<h2 data-linkedin-title>Anterior</h2>',
                    {'data-linkedin-title': texto})
                import html
                self.assertEqual(html.unescape(salida.split('>', 1)[1].split('</h2>')[0]), texto)
                self.assertNotIn('<design>', salida)

    def test_comillas_en_atributos_no_crean_atributos_nuevos(self):
        class Etiquetas(HTMLParser):
            def __init__(self):
                super().__init__()
                self.etiquetas = []
            def handle_starttag(self, tag, attrs):
                self.etiquetas.append((tag, dict(attrs)))
        texto = 'Art "quoted" &amp; &lt;work&gt;'
        with patch.dict(en_gen.TEXTOS_EN, {'Arte': texto}, clear=True):
            salida = en_gen.traducir_html(
                '<img alt="Arte"><meta name="description" content="Arte">')
        parser = Etiquetas()
        parser.feed(salida)
        esperado = 'Art "quoted" & <work>'
        self.assertEqual(parser.etiquetas, [
            ('img', {'alt': esperado}),
            ('meta', {'name': 'description', 'content': esperado})])

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
