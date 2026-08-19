-- 1) Equipo: la base tiene menos gente que el sitio. Al importar se
--    perdieron los nombres que se repetian bajo otro rol ("Arq. Leonardo G.
--    Militello", la direccion de obra de IOL) y dos colaboradores de
--    Cerveceria Austral. Estos valores son los que la ficha muestra hoy.

update obras set equipo = array['Arq. Fernando Hitzig', 'Arq. Leonardo Militello', 'Arq. Camila Lacarpia', 'Luciano Cichanowski', 'Josué Solano']
  where slug = 'cerveceria-austral';
update obras set equipo = array['Arq. Fernando Hitzig', 'Arq. Leonardo Militello', 'Documentación de obra:', 'Arq. Pilar Velasco', 'Arq. Victoria Nabias', 'Dirección de obra:', 'Arq. Fernando Hitzig']
  where slug = 'iol';
update obras set equipo = array['Arq. Fernando Hitzig', 'Arq. Leonardo Militello', 'Arq. Sabrina Perissinotto', 'Arq. Leonardo G. Militello']
  where slug = 'casa-olmo';
update obras set equipo = array['Arq. Fernando Hitzig', 'Arq. Leonardo Militello', 'Arq. Virginia Bottan', 'Arq. Leonardo G. Militello']
  where slug = 'the-birra';
update obras set equipo = array['Arq. Fernando Hitzig', 'Arq. Leonardo Militello', 'Arq. Leonardo G. Militello', 'Arq. Florencia schvartzman']
  where slug = 'atelier-vilela';

-- 2) Categoria de Casa Luna. El cliente la pidio en Oficinas y la ficha, la
--    tarjeta y el buscador ya lo dicen, pero la base sigue en 'residencial'.
--    Sin esto el proximo deploy la devuelve a Residencial.

update obras set categoria = 'oficinas' where slug = 'oficina-casa-luna';
