-- Correcciones de contenido solicitadas por el estudio en agosto de 2026.
-- El build tambien las aplica de forma condicional a la base ya existente.

update obras
   set memoria = regexp_replace(memoria, '^corresponde a oficinas:', 'Corresponde a oficinas:'),
       memoria_en = regexp_replace(memoria_en, '^corresponds to offices:', 'Corresponds to offices:')
 where slug = 'edificio-del-plata';

update obras set equipo = array[
  'Arq. Fernando Hitzig', 'Arq. Leonardo Militello', 'Arq. Sofía Kesting',
  'Arq. Camila Lacarpia', 'Arq. Victoria Nabias', 'Arq. Milagros Rivelli'
] where slug = 'osten-tower';

update obras set equipo = array[
  'Arq. Fernando Hitzig', 'Arq. Leonardo Militello', 'Arq. Camila Lacarpia',
  'Luciano Cichanowski', 'Josué Solano'
] where slug = 'cerveceria-austral';

update obras set bajada = 'Dos cafeterías Juan Valdez en Buenos Aires.'
 where slug = 'juan-valdez';

update obras
   set memoria = replace(
     memoria,
     E'A diferencia de la generalidad de los proyectos gastronómicos, en los que a priori se tiene bien definido el tipo de usuario…el\n\n, ya sea por rango etario, por tipo de propuesta gastronómica, por ubicación y horario de apertura, o incluso por el valor del cubierto, en este proyecto ninguna de esas variables era fija.',
     'A diferencia de la generalidad de los proyectos gastronómicos, en los que a priori se tiene bien definido el tipo de usuario —ya sea por rango etario, por tipo de propuesta gastronómica, por ubicación y horario de apertura, o incluso por el valor del cubierto—, en este proyecto ninguna de esas variables era fija.'),
       memoria_en = replace(
     memoria_en,
     E'Unlike most gastronomic projects, where the type of user is well defined from the start — the\n\n, whether by age range, by the kind of food offered, by location and opening hours, or even by the price of a cover — in this project none of those variables was fixed.',
     'Unlike most gastronomic projects, where the type of user is well defined from the start — whether by age range, by the kind of food offered, by location and opening hours, or even by the price of a cover — none of those variables was fixed in this project.')
 where slug = 'movistar-arena';

update obras
   set bajada = 'Locales de Tostado Café Club en Argentina, Uruguay, Miami y São Paulo.'
 where slug = 'tostado';

update obras set equipo = array[
  'Arq. Fernando Hitzig', 'Arq. Leonardo Militello', 'Arq. Vanik Margossian',
  'Arq. Milca Amado', 'Arq. Julieta Setton'
] where slug = 'hausscape';

update obras set equipo = array[
  'Arq. Fernando Hitzig', 'Arq. Leonardo Militello', 'Arq. Vanik Margossian',
  'Arq. Dolores Gayoso', 'Arq. Marcela Bernat'
] where slug = 'moshu';

update obras
   set bajada = 'Un bar organizado por una pieza de hierro y paneles facetados, con un patio selvático al fondo.'
 where slug = 'mamba-bar';

update obras
   set bajada = 'Una cremería concebida como una envolvente diamantada de superficies facetadas.'
 where slug = 'goodsten';

update obras
   set bajada = 'Remodelación integral de las oficinas de IguanaFix en Buenos Aires.'
 where slug = 'iguanafix';

update obras set equipo = array[
  'Arq. Fernando Hitzig', 'Arq. Leonardo Militello', 'Arq. Magdalena Molinari'
] where slug = 'victoria-brown';

update obras set equipo = array[
  'Arq. Fernando Hitzig', 'Arq. Leonardo Militello', 'Arq. Ruben Ruiz'
] where slug = 'dos-casas-conde';

update obras set equipo = array[
  'Arq. Fernando Hitzig', 'Arq. Leonardo Militello',
  'Arq. Florencia Schvartzman', 'Arq. Belen Lepro Delelis'
] where slug = 'oficina-casa-luna';

update obras set equipo = array[
  'Arq. Fernando Hitzig', 'Arq. Leonardo Militello', 'Arq. Carmela Zuleta',
  'Arq. Juliana Zorza', 'Arq. Samira Attar'
] where slug = 'ph-el-salvador';
