"""La presentacion nueva no debe borrar trabajos ni reaparecer en otro build."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'docs'))
import panel_estados as estados
import en_gen


class EstadosTest(unittest.TestCase):
    def tarjeta(self, valor, rotulo):
        return ('<a class="project-card" data-slug="prueba" data-estado="%s">'
                '<span class="card-estado card-estado--%s">%s</span>'
                '<img src="foto.webp"><div class="p-name">Trabajo</div></a>'
                % (valor, valor, rotulo))

    def test_concluida_sin_sello_conserva_tarjeta(self):
        resultado = estados.arreglar(self.tarjeta('proyecto', 'Proyecto'), 'obra', '', True)
        self.assertNotIn('card-estado', resultado)
        self.assertIn('data-estado="obra"', resultado)
        self.assertIn('<img src="foto.webp">', resultado)

    def test_proyecto_y_concurso(self):
        for valor, rotulo in [('proyecto', 'En progreso'), ('concurso', 'Concurso')]:
            resultado = estados.arreglar(self.tarjeta('obra', 'Obra'), valor, rotulo, True)
            self.assertIn('>%s</span>' % rotulo, resultado)
            self.assertEqual(resultado.count('class="card-estado '), 1)
            self.assertEqual(estados.arreglar(resultado, valor, rotulo, True), resultado)

    def test_fila_no_agrega_sello(self):
        fila = '<a class="project-list-row" data-estado="obra">Trabajo</a>'
        self.assertNotIn('card-estado', estados.arreglar(fila, 'proyecto', 'En progreso', False))

    def test_filtros_e_idempotencia(self):
        html = ('<button data-estado-filtro="all">Todas</button>'
                '<button data-estado-filtro="obra">Obras</button>'
                '<button data-estado-filtro="proyecto">Proyectos</button>'
                '<button data-estado-filtro="concurso">Concursos</button>'
                + self.tarjeta('obra', 'Obra') + self.tarjeta('proyecto', 'Proyecto'))
        resultado = estados.presentacion(html)
        self.assertNotIn('data-estado-filtro="obra"', resultado)
        self.assertEqual(resultado.count('<button'), 3)
        self.assertEqual(resultado.count('class="project-card"'), 2)
        self.assertIn('>En progreso</button>', resultado)
        self.assertEqual(estados.presentacion(resultado), resultado)

    def test_estados_de_base(self):
        self.assertEqual(estados.SELLO['concluida'], ('obra', ''))
        for estado in ('en_proyecto', 'en_progreso'):
            self.assertEqual(estados.SELLO[estado], ('proyecto', 'En progreso'))

    def test_listado_real_y_traduccion(self):
        import re
        ruta = Path(estados.LISTADO)
        original = ruta.read_text(encoding='utf-8')
        resultado = estados.presentacion(original)
        self.assertEqual(re.findall(r'data-slug="[^"]+"', original),
                         re.findall(r'data-slug="[^"]+"', resultado))
        self.assertEqual(re.findall(r'data-cat="[^"]+"', original),
                         re.findall(r'data-cat="[^"]+"', resultado))
        self.assertNotIn('card-estado--obra', resultado)
        ingles = en_gen.traducir_html(resultado)
        filtros = re.findall(r'data-estado-filtro="([^"]+)"[^>]*>(.*?)</button>', ingles)
        self.assertEqual(filtros, [('all', 'All'), ('proyecto', 'In progress'),
                                  ('concurso', 'Competition')])
        self.assertNotIn('>Proyecto</span>', resultado)


if __name__ == '__main__':
    unittest.main()
