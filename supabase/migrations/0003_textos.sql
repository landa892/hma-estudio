-- Textos de las secciones fijas, tal como los dice el sitio hoy.
-- Generado por docs/panel_textos_semilla.py: no se edita a mano.
--
-- El ingles sale del diccionario del espejo, no de la posicion
-- del texto en la pagina traducida.

insert into textos (clave, seccion, rotulo, es, en, multilinea, orden) values
  ('home.titular', 'home', 'Titular de la portada', 'Creando & construyendo ideas', 'Creating & building ideas', false, 1),
  ('home.bajada', 'home', 'Bajada de la portada', 'Arquitectura y diseño de interiores para hotelería, gastronomía, oficinas y vivienda.
Más de dos décadas creando identidades de marca en América Latina, Europa, Medio Oriente y EE.UU.', 'Architecture and interior design for hotels, restaurants, offices and homes. More than two decades creating brand identities across Latin America, Europe, the Middle East and the US.', true, 2),
  ('estudio.eyebrow', 'estudio', 'Rotulo sobre el titulo', 'Desde 2006 — Buenos Aires', 'Since 2006 — Buenos Aires', false, 3),
  ('estudio.titular', 'estudio', 'Titulo de la pagina', 'Quiénes somos', 'Who we are', false, 4),
  ('estudio.presentacion', 'estudio', 'Presentacion del estudio', 'En Hitzig Militello arquitectos realizamos proyectos comerciales de forma local y regional tanto en América Latina, como en Europa, Medio Oriente y EEUU, con especial enfoque en la industria de la hospitalidad. Más de dos décadas de trayectoria creado arquitectura e interiorismos de reconocimiento internacional.', 'At Hitzig Militello Architects, we deliver commercial projects locally and regionally across Latin America, Europe, the Middle East and the United States, with a particular focus on the hospitality industry. For more than two decades, we have created internationally recognised architecture and interior design.', true, 5),
  ('contacto.titular', 'contacto', 'Titulo de la pagina', 'Hablemos de tu proyecto', 'Let''s talk about your project', false, 6),
  ('contacto.direccion', 'contacto', 'Direccion', 'Soler 5130, 1° B — Palermo
C1425, Buenos Aires, Argentina', 'Soler 5130, 1° B — Palermo C1425, Buenos Aires, Argentina', true, 7),
  ('contacto.telefonos', 'contacto', 'Telefonos', '(+54) 11 4773 8658
+1 (305) 851 3565', '(+54) 11 4773 8658
+1 (305) 851 3565', true, 8),
  ('estudio.bloque1', 'estudio', 'Estudio — Diseño integral', 'Entendemos el diseño como un proceso integral donde convergen estrategia, arquitectura e identidad.
Cada decisión responde a una visión conceptual unificada, con la arquitectura de marca como eje del
proyecto.', 'We understand design as an integral process where strategy, architecture and identity converge. Every decision answers to a single conceptual vision, with brand architecture at the core of the project.', true, 21),
  ('estudio.bloque2', 'estudio', 'Estudio — Identidad', 'Concebimos la arquitectura de interiores como una disciplina holística que trasciende lo funcional y
lo estético, creando espacios con identidad propia y experiencias memorables.', 'We see interior architecture as a holistic discipline that goes beyond the functional and the aesthetic, creating spaces with an identity of their own and experiences worth remembering.', true, 22),
  ('estudio.bloque3', 'estudio', 'Estudio — Autenticidad', 'Resignificamos referencias culturales y del imaginario colectivo para crear espacios contemporáneos,
profundamente conectados con su contexto y con una identidad genuina.', 'We reframe cultural references and shared imagery to create contemporary spaces, deeply connected to their context and with a genuine identity.', true, 23)
on conflict (clave) do nothing;
