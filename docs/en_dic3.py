# -*- coding: utf-8 -*-
"""Tercera capa: nombres propios que pasan tal cual y los textos largos."""
import en_dic2
import en_dic
from en_dic import DIC, PASA_EXACTO

# --- nombres de obra, ciudades y marcas: pasan tal cual ----------------------
PASA_EXACTO.update({
    'Antiche', 'Araoz', 'Aire Libre', 'Benedetta', 'Bolívar', 'CCEBA', 'Cien',
    'Fogón', 'Fresco', 'Goodsten', 'Hausscape', 'IguanaFix', 'Kavak Hub',
    'Kavak Oficinas', 'Malabia', 'Mamba', 'Manduca', 'Moshu', 'Novotel',
    'Novotel Corrientes', 'Osten', 'Osten Tower', 'Osten Coffee Shop',
    'Parfumerie', 'People', 'Plaza Mateo', 'Roket', 'Templo Mikdash',
    'Victoria Brown', 'Williamsburg', 'Accor Hotels', 'Atelier Vilela',
    'Café Artois', 'Cervecería Austral', 'Dos Casas Conde', 'FEHGRA',
    'Hyatt · Ziva', 'Indusparquet', 'IOL — Invertir Online', 'Juan Valdez Café',
    'Lucciano’s Caballito', 'Movistar Arena', 'The Nim Bar', 'Tostado Café Club',
    'Ualá Gigena', 'Ualá', 'Bienal de Venecia', 'Áreas VIP', 'Malita',
    'Montevideo', 'Puerto Madero', 'Santiago de Chile', 'Vitacura, Santiago de Chile',
    'Caballito, Buenos Aires', 'Conde, Buenos Aires', 'Puerto Madero, Buenos Aires',
    'Miami, Florida', 'Río Negro', 'Uruguay', 'Saedan Mall, Riad',
    'Next Landmark', 'Next Landmark Awards', 'Premios BIAR', 'SBID',
    'Vercel Inc.', 'Resend', '@hitzig.militello', 'Portfolio', 'Retail',
    'Movistar Arena — VIP Lounge',
})

DIC.update({
    # ciudades que si cambian
    'Nueva York': 'New York', 'París': 'Paris', 'Shanghái': 'Shanghai',
    'San Pablo': 'São Paulo', 'São Paulo': 'São Paulo', 'Venecia': 'Venice',
    'Riad': 'Riyadh',

    # interfaz que faltaba
    'Nombre': 'Name', 'Teléfono': 'Phone', 'Todos': 'All', 'Video': 'Video',
    'Volver al inicio': 'Back to home', 'Quiénes somos': 'Who we are',
    'Reconocimientos': 'Recognition', 'Socio fundador': 'Founding partner',
    'Mención especial': 'Special mention', 'Otras distinciones': 'Other distinctions',
    'Proyectos realizados': 'Completed projects',
    'Países con obra construida': 'Countries with built work',
    'Opciones de contacto': 'Contact options',
    'Navegación por sección': 'Section navigation',
    'No completar': 'Do not fill in',
    'Medios · desde 2003': 'Media · since 2003',
    'política de privacidad': 'privacy policy',
    'Premio Nacional ARQ-FADEA': 'ARQ-FADEA National Award',
    'Mercado · Paseo La Plaza': 'Market · Paseo La Plaza',
    'Restaurante &amp; pastelería': 'Restaurant &amp; patisserie',
    'Restaurante &amp; bar': 'Restaurant &amp; bar',
    'Restaurante & bar': 'Restaurant & bar',
    'Restaurante exterior': 'Outdoor restaurant',
    'Reforma de oficinas': 'Office refurbishment',
    'Hotel de 1.486 m² sobre la Avenida Corrientes.':
        '1,486 m² hotel on Avenida Corrientes.',
    'YouTube — jul 2026': 'YouTube — Jul 2026',
    'YouTube — may 2026': 'YouTube — May 2026',
    'no utiliza cookies': 'does not use cookies',

    # fragmentos legales sueltos
    'consentimiento': 'consent', 'acceso': 'access', 'rectificación': 'rectification',
    'actualización': 'update', 'supresión': 'erasure',
    ', su': ', its', '. La': '. The', 'o su': 'or its',
    'a tus datos personales, su': 'to your personal data, its',

    # --- textos largos -------------------------------------------------------
    'Estas piezas dispuestas en conjunto conforman un organismo vivo, versátil y adaptable a cada “key spaces” del hotel, el cual conforma y organiza desde la iluminación hasta el equipamiento fijo y móvil del hotel. l. Además de su función organizativa tiene una simbólica: alojar a través de sus antiguas valijas los objetos personales de cada viajero que transitara por este hotel. De las antiguas valijas, sus estampillas que evidencian el paso por los estados y provincias, son parte de la identidad local plasmados en un wallpaper. Desde la comunicación visual hacemos hincapié en la identidad local colectiva de los ciudadanos a través de un gran videowall en el front desk. Además proponemos la presencia activa de la naturaleza más representativa de la flora local (ECO CONCEIVED). Todo ello reunido en un único sistema constructivo vinculante.':
        'Assembled together, these pieces form a living organism, versatile and adaptable to each of the hotel’s key spaces, shaping and organising everything from the lighting to the fixed and movable furniture. Beyond its organising role it carries a symbolic one: to hold, inside its vintage suitcases, the personal belongings of every traveller passing through. The stamps on those suitcases, evidence of journeys across states and provinces, become part of the local identity and are carried over into a wallpaper. In the visual communication we stress the collective local identity of the city’s people through a large videowall at the front desk. We also propose an active presence of the most representative local flora (ECO CONCEIVED). All of it gathered into a single binding construction system.',

    'El proyecto desarrollado para Indus Parquet, empresa brasilera especializada en producción e instalación de pisos de madera con más de 80 años de trayectoria, surge como una interpretación arquitectónica de los valores de sustentabilidad, trazabilidad y vínculo con la naturaleza que definen a la marca. Implantado en el barrio de Núñez, el flagship propone una experiencia inmersiva donde la madera se manifiesta en su estado más puro y esencial. El proyecto toma como inspiración los procesos de siembra y tala controlada que la firma desarrolla en distintas regiones de Brasil, incorporando una narrativa espacial asociada al paisaje boscoso y al origen orgánico de la materia prima.':
        'The project for Indus Parquet — a Brazilian company specialising in the production and installation of wood flooring, with more than 80 years of history — is an architectural reading of the values that define the brand: sustainability, traceability and a bond with nature. Set in the Núñez neighbourhood, the flagship offers an immersive experience in which wood appears in its purest, most essential state. The design draws on the controlled planting and felling processes the firm runs across different regions of Brazil, building a spatial narrative tied to the forest landscape and to the organic origin of the raw material.',

    'El eje central del proyecto está conformado por una serie de estructuras pivotantes de piso a techo que exhiben más de cuarenta variedades de maderas y terminaciones. Complementariamente, se incorpora una “mesa creativa” destinada al trabajo conjunto entre profesionales, clientes y asesores de la marca. El recorrido culmina en un nivel superior destinado a reuniones, eventos y experiencias gastronómicas, integrando una terraza parquizada, mobiliario de diseño, piezas de autor, iluminación especializada y obras artísticas que consolidan una experiencia integral de marca donde arquitectura, paisaje, arte y materialidad operan como un único sistema narrativo.':
        'The spine of the project is a series of floor-to-ceiling pivoting structures displaying more than forty varieties of wood and finishes. Alongside them sits a “creative table” for professionals, clients and brand consultants to work together. The route ends on an upper level given over to meetings, events and dining, taking in a landscaped terrace, designer furniture, one-off pieces, specialist lighting and artworks that consolidate a complete brand experience in which architecture, landscape, art and materiality operate as a single narrative system.',

    'No es posible ignorar que los hoteles hoy basan todas sus propuestas en estéticas temáticas y actividades de integración para el agrado de sus pasajeros y esto es una ventaja innegable frente a los espacios temporarios, caso Airbnb. Entonces, porque Airbnb es una amenaza para el negocio hotelero? O porque la mayoría de los hoteles basan su propuestas en hoteles temáticos o historiados? Hoy en día Airbnb es como vivir en tu casa. Por lo contrario los hoteles son un lugar de tránsito a pesar de la renovada propuesta temática, todos ellos visten y desvisten según la moda sin una identidad clara.Esto explica una falta de IDENTIDAD.':
        'It is impossible to ignore that hotels today base their entire offer on themed aesthetics and social activities for the enjoyment of their guests, and that this is an undeniable advantage over temporary spaces such as Airbnb. So why is Airbnb a threat to the hotel business? And why do most hotels build their offer around themes and storytelling? Today Airbnb feels like being at home. Hotels, by contrast, are places of transit: despite the renewed thematic offer, they all dress and undress according to fashion, without a clear identity. That explains a lack of IDENTITY.',

    'La propuesta arquitectónica se estructura a partir de una composición ortogonal de troncos naturales expuestos, utilizados como elementos de fachada, revestimiento y conformación topográfica del acceso exterior. Este plano de ingreso funciona como una superficie escultórica que organiza el vínculo con el espacio público y construye una barrera física y perceptiva respecto de la vereda. Hacia el interior, el espacio se organiza mediante un recorrido sinuoso y no lineal, inspirado en la experiencia de desplazarse dentro de un bosque, articulando áreas de exhibición, atención y exploración material.':
        'The architecture is structured around an orthogonal composition of exposed natural logs, used as façade, cladding and as the topography of the outdoor entrance. That entrance plane works as a sculptural surface: it organises the relationship with the public realm and builds a physical and perceptual barrier from the pavement. Inside, the space unfolds along a winding, non-linear route inspired by the experience of moving through a forest, articulating areas for display, service and material exploration.',

    'El diseño de espacios de trabajo para el universo fintech implica el desafío de traducir arquitectónicamente un ecosistema digital complejo: la velocidad y la innovación tecnológica conviviendo con la solidez y el respaldo institucional. En el caso de IOL (Invertir Online), una de las empresas unicornio del sector y pieza clave del Grupo Supervielle, el proyecto requería una identidad tectónica que reflejara su liderazgo y dinamismo. Con esta premisa conceptual asumimos el desarrollo de sus nuevas oficinas, ubicadas en el piso 23 del edificio QIUB, en Palermo.':
        'Designing workspaces for the fintech world means translating a complex digital ecosystem into architecture: speed and technological innovation living alongside solidity and institutional backing. For IOL (Invertir Online), one of the sector’s unicorns and a key part of Grupo Supervielle, the project called for a tectonic identity that would reflect its leadership and its drive. On that premise we took on their new offices, on the 23rd floor of the QIUB building in Palermo.',

    'De estos puntos de conflicto emerge una sinapsis, una interconexión, una relación entre partes, una estructura que -caos mediante- pretende inter-ligar (en el sentido de la inte-ligenza) las inteligencias en cuestión, aportando a modo de soporte el contenido de la exhibición. De esta forma, el pabellón se recorre hilvanando las seis tipos de inteligencia que producen cinco intersecciones, siendo finalmente estos cinco focos de atención los que exhiben, sostienen e iluminan la totalidad de la obra.':
        'From these points of conflict a synapse emerges: an interconnection, a relationship between parts, a structure that — through chaos — seeks to inter-link (in the sense of inte-ligenza) the intelligences at play, carrying the content of the exhibition as its support. The pavilion is therefore walked by threading together the six kinds of intelligence, which produce five intersections; those five focal points are what ultimately display, hold up and light the work as a whole.',

    'Es un vacio, como tal definido por una estética pura y simple. Estéril de esteticidad impuesta, aunque sin dudas sus líneas construyen un universo asociado a aquella modernidad del despojo del eclecticismo y lo ornamental, el status del individuo contemporáneo. Ese despojo es hoy llamado minimalismo, es decir la vida con lo mínimo y necesario. Algo verdaderamente atemporal. Lo mínimo nos llama a la reflexión a partir de concebir la vida en un consumo mínimo y medido, básico, sustentable.':
        'It is a void, and as such defined by a pure, simple aesthetic. Free of any imposed prettiness, though its lines undoubtedly build a world tied to that modernity which stripped away eclecticism and ornament — the status of the contemporary individual. That stripping away is what we now call minimalism: living with the minimum and the necessary. Something genuinely timeless. The minimum invites reflection, because it asks us to conceive life around measured, basic, sustainable consumption.',

    'El complejo Madero Harbour se emplaza con protagonismo en el enclave de Puerto Madero, ese territorio en que la ciudad se refleja sobre el agua y lo natural tensiona con lo artificial. El concepto de margen, de borde, de límite en que la traza urbana producto de la cultura colisiona con la inmensidad natural del río se convierte en el punto de partida del proyecto que invita a repensar la arquitectura como una contradicción compleja y estimulante por el choque entre los opuestos.':
        'The Madero Harbour complex stands out within Puerto Madero, a stretch of city where the skyline is mirrored on the water and the natural pulls against the artificial. The idea of the margin, the edge, the boundary where the cultural grid of the city collides with the natural immensity of the river becomes the starting point of the project, which invites us to rethink architecture as a complex, stimulating contradiction born of the clash between opposites.',

    'La cultura patagónica también forma parte central del concepto. Sus tradiciones, oficios y vestimentas inspiran la composición espacial y el diseño interior, reinterpretadas de manera contemporánea mediante capas, texturas y tramas que aportan identidad sin recurrir a elementos decorativos evidentes. Esto permite construir un relato sutil pero potente, alineado con una imagen de marca sólida y sofisticada, capaz de perdurar en el tiempo, al igual que las tradiciones locales.':
        'Patagonian culture is also central to the concept. Its traditions, crafts and dress inspire the spatial composition and the interior design, reinterpreted in a contemporary way through layers, textures and weaves that give identity without resorting to obvious decorative devices. The result is a subtle but powerful story, aligned with a solid and sophisticated brand image, built to last — much like the local traditions themselves.',

    'Rocket dialoga en un código industrial futurista, dada sus formas y sus materiales. Hay chapas perforadas, placas de acero inoxidables, pisos y muros de goma, placas de policarbonato, costillas metálicas todos elementos que emulan los interiores de las aeronaves espaciales. Algunos elementos pétreos, como si se tratara de rocas espaciales, hacen su aparición en detalles específicos y componen el mobiliario fundamentalmente en las áreas vips.':
        'Roket speaks a futuristic industrial language, in both its forms and its materials. Perforated sheet metal, stainless steel panels, rubber floors and walls, polycarbonate sheets and metal ribs all echo the interiors of spacecraft. Stone elements, like space rocks, appear in specific details and make up much of the furniture in the VIP areas.',

    'Fue un gran desafío resolver el proyecto acondicionándolo a las ordenanzas sanitarias que debían responder a espacios abiertos y con distanciamiento social. La propuesta no solo debía responder a estos condicionamientos, sino que además por tratarse de un espacio anexo a un restaurante justo ubicado frente a la fachada de este, necesitaba contar con una identidad muy fuerte que hable por si misma y ser la cara visible del local comercial.':
        'Resolving the project under the health regulations of the time — open spaces, social distancing — was a real challenge. The proposal not only had to answer those constraints: since it was an annexe sitting directly in front of the restaurant’s façade, it also needed a strong identity that could speak for itself and become the venue’s public face.',

    'Nuestra propuesta se resume en dos palabras IDENTIDAD & COMUNIDAD, ambas resueltas como parte del funcionamiento y entretenimiento del hotel. La identidad es una integración de conceptos que definen a un individuo o cosa, pero el hotel no debe tener una identidad definida más bien debe servir de envase. Un gran esqueleto donde cada pasajero pueda llenarlo con sus posesiones, así como en el hogar de cada uno. Un verdadero Tailored Offer.':
        'Our proposal comes down to two words, IDENTITY & COMMUNITY, both resolved as part of how the hotel runs and entertains. Identity is an integration of the concepts that define a person or a thing — but the hotel should not have a fixed identity; it should serve as a container. A large skeleton that each guest can fill with their own belongings, just as they do at home. A true tailored offer.',

    'El proyecto emerge entonces como un territorio de dualidades y conflictos. Es un minimalismo maximizado, es lo contemporáneo y lo moderno; con placas pétreas rectas disgregados y las curvas hiper texturizadas, una vegetación dinámica integrada, pero a la vez estática y enmarcada. Sus neutrales tonalidades equilibran la expresividad de sus materiales, y sus contradicciones, en definitiva, invitan a la provocación de una experiencia.':
        'The project emerges, then, as a territory of dualities and conflicts. It is a maximised minimalism; it is both the contemporary and the modern, with straight stone panels broken apart and hyper-textured curves, with planting that is dynamic and integrated yet also static and framed. Its neutral tones balance the expressiveness of the materials, and its contradictions, ultimately, provoke an experience.',

    'El proyecto está inspirado en el universo onírico, de texturas y materiales provenientes del mundo mediterráneo. El elemento más característico son las ondas y olas del mar que implementamos a través de dos elementos constructivos en planta baja y alta. Ambos dan una función específica; uno de ellos, como back de barra en planta baja, y el otro, como una larga bancada zigzagueante que organiza el área central de la planta alta.':
        'The project draws on a dreamlike world of Mediterranean textures and materials. Its most characteristic element is the swell and break of the sea, which we build through two construction elements on the ground and upper floors. Each has a specific job: one as the back bar downstairs, the other as a long zigzagging bench that organises the central area upstairs.',

    'La disposición de listones de madera pintados de blanco crea una forma dinámica e integrada en el espacio. En la planta baja, la expresividad de este elemento queda encapsulada en el bar situado frente a la entrada. Del mismo modo, el largo banco en zigzag y su estructura de listones de madera pintada de blanco en la planta baja sugieren una utilización distinta del espacio, ofreciendo una experiencia notablemente diferente.':
        'The arrangement of white-painted timber slats creates a dynamic form that is fully part of the space. On the ground floor, the expressiveness of that element is concentrated in the bar facing the entrance. In the same way, the long zigzag bench and its white-painted slatted structure suggest a different use of the space, offering a noticeably different experience.',

    'Esta construcción funciona como espacio contiguo y de apoyo al local existente debajo de la construcción ferroviaria de principios de siglo XX. Este espacio plenamente exterior ha resuelto cualidades estéticas y constructivas como si se tratara de una local en sí mismo. Esta área de 54 m2 de únicamente sitting permitan albergar comensales bajo los cuidados sanitarios necesarios impuestos por las autoridades sanitarias.':
        'This structure works as an adjoining support space to the existing venue beneath the early twentieth-century railway construction. Although entirely outdoors, it resolves its aesthetic and constructional qualities as if it were a venue in its own right. The 54 m² area, given over solely to seating, allows diners to be accommodated under the health measures required by the authorities.',

    'La composición debe ser coherente a un sistema que le otorgue unidad. No concebimos la arquitectura interior como una sumatoria de elementos individuales (objetos decorativos, mobiliario, iluminación). Nuestra propuesta está definida por un grupo amplio de piezas que conforman un espacio en sí mismo. Esto permite múltiples posibles configuraciones para el uso en nuevos hoteles o en hoteles existentes a ser renovados.':
        'The composition has to be consistent with a system that gives it unity. We do not conceive interior architecture as a sum of individual elements — decorative objects, furniture, lighting. Our proposal is defined by a broad family of pieces that together constitute a space in itself. That allows for many possible configurations, whether in new hotels or in existing ones being refurbished.',

    'Con el objetivo de trasladar la esencia del sur del mundo al corazón de la capital chilena, el diseño de Joseph Fischer se concibe como una experiencia de marca, donde no se cuentan historias de manera literal, sino que se experimentan a través de atmósferas, sensaciones y materialidades inspiradas en la Patagonia, generando un espacio reconocible, auténtico y memorable para los clientes.':
        'With the aim of carrying the essence of the far south into the heart of the Chilean capital, the Joseph Fischer design is conceived as a brand experience: stories are not told literally, they are felt through atmospheres, sensations and materials drawn from Patagonia, producing a space that is recognisable, authentic and memorable for customers.',

    'El desafío ha sido de componer un volumen inspirado estas antiguas edificaciones y sus techos tan característicos de Bélgica, pero ejecutando la figura bajo una visión contemporánea, es decir, modificar las caídas del techo generando un dinamismo y evitando un volumen regular. Pareciera la imagen de las típicas edificaciones frente al canal de Dijver o al mercado de Brujas.':
        'The challenge was to compose a volume inspired by those old buildings and the rooflines so characteristic of Belgium, but executed through a contemporary lens: altering the pitches of the roof to create movement and avoid a regular volume. It reads like the typical buildings facing the Dijver canal or the market square in Bruges.',

    'El contenido se propone bajo un criterio curatorial en las 5 intersecciones según un orden cronológico. El criterio expositivo que define a cada una de las intersecciones exhibe entonces una selección de obras que conlleva una relación integral y directa a lo expuesto, y responde a una línea temporal que se inicia en la inteligencia individual y culmina en la artificial.':
        'The content is set out under a curatorial criterion across the five intersections, in chronological order. The exhibition logic defining each intersection therefore shows a selection of works bearing a direct, integral relationship to what is on display, following a timeline that begins with individual intelligence and ends with artificial intelligence.',

    'La disposición de estos cinco soportes recorribles, materializados mediante andamiaje y articulaciones, se encuentran dispuestos en el espacio de forma a priori aleatoria contraponiéndose al camino central, sereno y lineal que ofrece al visitante la posibilidad de detenerse, sentarse bajo la nube de supuestas inteligencias y recuperar la capacidad de contemplación.':
        'These five walkable supports, built from scaffolding and joints, are laid out in what at first appears to be a random arrangement, set against a calm, linear central path that offers the visitor the chance to stop, sit beneath the cloud of supposed intelligences and recover the capacity for contemplation.',

    'La pieza longitudinal cuenta con una presencia activa en todas sus vistas, sobre todo desde el parque. El diseño de la misma cuenta con dos fachadas que no son simétricas entre sí, una de ellas cuenta con un gesto de apertura hacia la fachada principal del local comercial. Este gesto invita al acceso y además propone un espacio para comensales.':
        'The long volume has an active presence from every angle, above all from the park. Its two façades are not symmetrical: one opens up towards the main frontage of the venue. That gesture invites people in and, at the same time, creates space for diners.',

    'De allí surge la propuesta: dos espacios que encarnan la dualidad entre, por un lado, el orden racionalista (minimalismo) y por otro la exaltación sensorial (maximalismo). La grilla Miesiana ofrece un marco conceptual: organiza la planta mediante ejes axiales afectando al resto de los elementos que proponen diferentes situaciones de uso.':
        'From there comes the proposal: two spaces embodying the duality between rationalist order (minimalism) on one side and sensory exaltation (maximalism) on the other. The Miesian grid provides the conceptual frame, organising the plan through axial lines that govern the remaining elements and the different situations of use they set up.',

    'Inspirada en la luz y la velocidad de ella, como elemento predominante. Con la velocidad la humanidad conoció nuevos horizontes más allá de lo imaginado, el espacio. La tecnología de los propulsores en sus naves, pareciera contarnos la historia de lo que ocurre en el espacio, circunferencias de luz y gases envuelven planetas enteros.':
        'Inspired by light and its speed as the dominant element. Through speed, humanity reached horizons beyond anything imagined: outer space. The technology of a spacecraft’s thrusters seems to tell us the story of what happens out there — rings of light and gas wrapping entire planets.',

    'Las piezas ovales y circulares se repiten en varias áreas de la discoteca representando con sus figuras la velocidad, a través de su iluminación en movimiento (pixel led) que acompaña los bits del sonido musical. La iluminación más estática de las costillas (Led rgb) componen diferentes escenarios lumínicos según la circunstancia.':
        'Oval and circular pieces recur across the club, their shapes standing for speed through moving light (pixel LED) that follows the beat of the music. The more static lighting of the ribs (RGB LED) composes different lighting scenes as the occasion requires.',

    'En Hitzig Militello Arquitectos llevamos a cabo proyectos comerciales y residenciales de alta calidad en toda Latinoamérica, Europa, Oriente Medio y Estados Unidos. Con un enfoque especial en hotelería y espacios de trabajo, nos hemos convertido en auténticos artesanos de las marcas, con reconocimiento internacional.':
        'At Hitzig Militello Architects we deliver high-quality commercial and residential projects across Latin America, Europe, the Middle East and the United States. With a particular focus on hospitality and workspaces, we have become genuine craftsmen of brands, with international recognition.',

    'Algunos contenidos se alojan en servicios externos: si en el sitio se muestran videos del canal de YouTube del Estudio, las imágenes de vista previa se cargan desde servidores de Google. Los enlaces a Instagram y WhatsApp te llevan a esas plataformas, que se rigen por sus propias políticas de privacidad.':
        'Some content is hosted by external services: where the site shows videos from the Studio’s YouTube channel, the preview images are loaded from Google servers. Links to Instagram and WhatsApp take you to those platforms, which are governed by their own privacy policies.',

    'En el primer nivel se usaron viguetas pretensadas y en el segundo estructura tubular 100×50, reproduciendo una modulación que se lee en la fachada. Las aberturas y el sistema de protección responden estrictamente a esa modulación, al revés de las de la obra vieja, que no siguen ninguna lógica proyectual.':
        'Prestressed joists were used on the first level and a 100×50 tubular structure on the second, reproducing a module that reads across the façade. The openings and the screening system follow that module strictly — unlike those of the old building, which obey no design logic at all.',

    'Los tonos blancos son los más predominantes en todo el espacio, sugerido por las construcciones tan características de aquellas latitudes. La utilización del mosaiquismo en tonos azules y turquesas es claramente un recurso constructivo que representa una época y un arte propio del mediterráneo.':
        'Whites dominate throughout the space, suggested by the buildings so characteristic of those latitudes. The use of mosaic in blues and turquoises is plainly a constructional device that stands for a period and for an art form of the Mediterranean.',

    'La consigna fue operar sobre lo antiguo con un elemento que no se mimetizara en absoluto. No hay asociación material, pero sí volumétrica: el volumen superior existente contra la nueva pieza, y una cubierta a dos aguas que le hace un guiño contemporáneo a la vecina, de tejado a una sola agua.':
        'The brief was to work on the old building with an element that would not blend in at all. There is no material association, but there is a volumetric one: the existing upper volume set against the new piece, and a gable roof that nods, in contemporary terms, to the neighbouring single-pitch one.',

    'La organización de las barras perimetrales mirando al exterior ha sido determinante para una configuración que considera cuestiones de higiene y salubridad. La vegetación presente, no solo por las cualidades que le otorga al aire, sino como una presencia concientizadora hacia la naturaleza.':
        'Arranging the perimeter counters to face outwards was decisive for a layout that takes hygiene and public health into account. The planting is there not only for what it does to the air, but as a presence that raises awareness of nature.',

    'A partir de la configuración que delimita esta pastilla central, el espacio perimetral se organiza de manera fluida, evitando la monotonía de la gran planta libre tradicional. El programa se subdivide según dinámicas de uso específicas que responden a las metodologías de trabajo actuales:':
        'From the configuration set by this central core, the perimeter space is organised fluidly, avoiding the monotony of the traditional large open plan. The programme is subdivided according to specific patterns of use that answer to current ways of working:',

    'Para oponer lo nuevo a lo viejo se usó un sistema constructivo liviano revestido en chapa acanalada, componiendo un volumen puramente cúbico. El excedente de metros se liberó como un pequeño patio triangular, y una malla de metal desplegado «cose» la intervención nueva a la antigua.':
        'To set the new against the old, a lightweight construction system clad in corrugated sheet was used, composing a purely cubic volume. The surplus square metres were released as a small triangular courtyard, and a mesh of expanded metal “stitches” the new intervention to the old.',

    'Con dos décadas de experiencia en espacios comerciales, hotelería y oficinas, cubrimos todas las fases del desarrollo. En cada proyecto nos centramos en generar conceptos sólidos, con especial énfasis en la arquitectura de marca: creamos o revitalizamos la identidad de cada obra.':
        'With two decades of experience in retail, hospitality and offices, we cover every phase of development. On each project we focus on building solid concepts, with particular emphasis on brand architecture: we create or revive the identity of every job.',

    'Cada una de las inteligencias actúa individualmente, pero interaccionan entre sí de forma diversa. De esta interacción entre dos inteligencias surge una tensión (un caos) que se evidencia a través de la expresividad sin una lógica aparente de las estructuras que las sostienen.':
        'Each of the intelligences acts on its own, yet they interact with one another in many ways. From the interaction between two intelligences a tension arises — a chaos — made visible through the expressiveness, apparently without logic, of the structures that hold them up.',

    'La intervención no se limitó a la unidad de esquina: hubo que resolver una expansión sobre un antiguo techo de chapa que cubre la unidad vecina. Con un sistema liviano tubular revestido en deck de madera se logró una terraza amplia, a la que se accede desde el segundo nivel.':
        'The work was not confined to the corner unit: an extension had to be resolved over an old sheet-metal roof covering the neighbouring unit. A lightweight tubular system clad in timber decking produced a generous terrace, reached from the second level.',

    'A primera vista hay un gran pasillo construido con andamios y el nombre Osten en un cartel colgado en un metal perforado situado en la entrada principal que funciona como sala de espera, como resultado de un efecto de provocación para descubrir el espacio paso a paso.':
        'At first glance there is a long corridor built from scaffolding, with the name Osten on a sign hung from perforated metal at the main entrance, which doubles as a waiting area — the result of a deliberate provocation, so the space is discovered step by step.',

    'Se trata de renovación absoluta de la discoteca Roket, en San Carlos de Bariloche. Un desafío de gran envergadura dada la complejidad de la obra en términos dimensionales (1500 m2) y por su complejidad constructiva de 5 niveles con balcones y gradas.':
        'This is a complete refurbishment of the Roket nightclub in San Carlos de Bariloche. A large undertaking, given the scale of the job (1,500 m²) and the constructional complexity of five levels with balconies and tiered seating.',

    'Creemos en la arquitectura de interiores más que en el diseño de interiores: un trabajo holístico y multidisciplinar que va más allá de los límites estrictos de la profesión, convirtiendo cada espacio en un contenedor de experiencias sensoriales.':
        'We believe in interior architecture rather than interior design: holistic, multidisciplinary work that goes beyond the strict limits of the profession, turning every space into a container of sensory experience.',

    'Esta nueva versión de discoteca, contempla desafíos estéticos y tecnológicos propios de esta época. Ambas características se encuentran plasmadas en un criterio común, donde la iluminación es tecnología y dibuja la estética de la discoteca.':
        'This new take on the nightclub takes on the aesthetic and technological challenges of our time. Both come together under a single criterion, in which lighting is the technology and also draws the aesthetic of the club.',

    'Integramos elementos del imaginario colectivo con los que los usuarios se identifican, reformulando el contexto del encargo en vez de partir de cero — una respuesta contemporánea a los espacios comerciales que no carecen de autenticidad.':
        'We bring in elements of the collective imagination that people recognise themselves in, reframing the context of the brief rather than starting from scratch — a contemporary answer to commercial spaces that does not lack authenticity.',

    'La utilización de listones de madera pintados de blanco como revestimiento en la gran mayoría del local, genera una textura rítmica la cual sugiere una relación con la estrategia utilizada en las áreas desarrolladas con las ondas.':
        'Using white-painted timber slats as cladding across most of the venue produces a rhythmic texture that echoes the strategy used in the areas built around the waves.',

    'El acceso al bar se encuentra al final del corredor, coronador por un metal perforado con el diseño de identidad del bar. Este corredor divide la totalidad del espacio en dos grandes áreas de uso y contra el fondo una gran barra':
        'The entrance to the bar sits at the end of the corridor, crowned by perforated metal carrying the bar’s identity design. That corridor splits the whole space into two large areas of use, with a long counter along the back',

    'La propuesta se plantea como un refugio dentro de la ciudad, un lugar donde el cliente puede desconectarse y vivir una experiencia asociada al origen de la marca: la fuerza del paisaje, el clima extremo y la tradición cervecera.':
        'The proposal is set up as a refuge within the city, a place where the customer can switch off and live an experience tied to the origin of the brand: the force of the landscape, the extreme climate and the brewing tradition.',

    'En nuestra propuesta para el pabellón argentino en la bienal de arquitectura Venecia 2025 representamos un circuito en el que identificamos seis tipos de inteligencia que articulan el accionar humano a lo largo de su evolución:':
        'In our proposal for the Argentine pavilion at the Venice Architecture Biennale 2025 we set out a circuit identifying six kinds of intelligence that have articulated human action throughout its evolution:',

    'al enviar un formulario, nuestro servidor registra de forma temporal la dirección IP desde la que se envía, con el único fin de limitar envíos automatizados (spam). No se guarda de forma permanente ni se asocia a tu identidad.':
        'when you submit a form, our server temporarily records the IP address it was sent from, for the sole purpose of limiting automated submissions (spam). It is not stored permanently and is not linked to your identity.',

    'Trabajamos de forma integral, fusionando lo abstracto con lo intrínseco. Tenemos en cuenta todos los aspectos fundamentales para llegar a un diseño conceptual integrado, con especial énfasis en la arquitectura de marca.':
        'We work comprehensively, fusing the abstract with the intrinsic. We take account of every fundamental aspect in order to arrive at an integrated conceptual design, with particular emphasis on brand architecture.',

    'La intervención se hizo sobre una antigua casa de esquina de mediados del siglo XX, de autoconstrucción, subdividida en tres unidades. Se trabajó sobre la de esquina, donde funcionaba una vieja bicicletería de barrio.':
        'The work was carried out on an old mid-twentieth-century corner house, self-built and subdivided into three units. We worked on the corner unit, which had housed an old neighbourhood bicycle shop.',

    'Por un lado, el volumen edilicio nos interesó referenciarlo a las siluetas constructivas medievales que definen el típico skyline de Brujas, muy identitario de Bélgica, país en el cual dio origen a la marca.':
        'On one hand, we wanted the volume of the building to reference the medieval silhouettes that define the typical skyline of Bruges — very much part of the identity of Belgium, the country where the brand began.',

    'Estudio de arquitectura y diseño de interiores en Buenos Aires con más de dos décadas de trayectoria. Proyectos de hotelería, gastronomía, oficinas y arquitectura residencial en Argentina, Miami y el mundo.':
        'Architecture and interior design studio in Buenos Aires with more than two decades of practice. Hospitality, restaurant, office and residential projects in Argentina, Miami and around the world.',

    'Como si se rememorara el oficio que ahí se practicaba, el destino es un espacio de artes y oficios: clases de orfebrería y carpintería en planta baja y primer nivel, y yoga y meditación en la planta alta.':
        'As if recalling the trade once practised there, the building is now given over to arts and crafts: silversmithing and carpentry classes on the ground and first floors, and yoga and meditation upstairs.',

    'El sitio se sirve íntegramente cifrado (HTTPS) y aplicamos medidas técnicas razonables para proteger la información que nos enviás. Ningún sistema es infalible, pero trabajamos para reducir los riesgos.':
        'The site is served entirely over an encrypted connection (HTTPS) and we apply reasonable technical measures to protect the information you send us. No system is infallible, but we work to reduce the risks.',

    'Las áreas operativas: diseñada bajo premisas de máximo confort acústico y lumínico para potenciar el enfoque de los colaboradores, logrando que todas las posiciones tengan visuales hacia el exterior.':
        'The operational areas: designed for maximum acoustic and lighting comfort to sharpen the team’s focus, with every workstation given a view to the outside.',

    'Estos proveedores tienen servidores fuera de Argentina, por lo que el envío de un formulario implica una transferencia internacional de esos datos, limitada a lo necesario para prestar el servicio.':
        'These providers have servers outside Argentina, so submitting a form involves an international transfer of that data, limited to what is necessary to provide the service.',

    '(en adelante, «el Estudio»), con oficinas en Soler 5130, 1° B, Palermo, C1425, Ciudad Autónoma de Buenos Aires, Argentina, y en 2980 NE 207 St., Fl. 33180, Wynwood, Miami, Estados Unidos.':
        '(hereinafter, “the Studio”), with offices at Soler 5130, 1° B, Palermo, C1425, Ciudad Autónoma de Buenos Aires, Argentina, and at 2980 NE 207 St., Fl. 33180, Wynwood, Miami, United States.',

    'Usamos esos datos exclusivamente para responder tu consulta y para poder contactarte en relación con ella. No los usamos para enviarte publicidad ni comunicaciones que no hayas pedido.':
        'We use that data solely to answer your enquiry and to be able to contact you about it. We do not use it to send you advertising or any communication you have not asked for.',

    'Arquitectura y diseño de interiores para hotelería, gastronomía, oficinas y vivienda. Más de dos décadas creando identidades de marca en América Latina, Europa, Medio Oriente y EE.UU.':
        'Architecture and interior design for hotels, restaurants, offices and homes. More than two decades creating brand identities across Latin America, Europe, the Middle East and the US.',

    'El corredor cuenta con 6 diferentes accesos al espacio general. Esto se debe fundamentalmente a que puede independizarse estos espacios para dividir las áreas como espacios privados.':
        'The corridor has six different points of access to the main space. That is chiefly so these spaces can be separated off and the areas divided into private rooms.',

    'Hitzig Militello Arquitectos en los medios: Dezeen, ArchDaily, Wallpaper*, Architectural Digest, Design Boom, La Nación, Clarín y más de dos décadas de publicaciones internacionales.':
        'Hitzig Militello Architects in the media: Dezeen, ArchDaily, Wallpaper*, Architectural Digest, Design Boom, La Nación, Clarín and more than two decades of international coverage.',

    'Conservamos las consultas mientras sean necesarias para atenderlas y darles seguimiento. Si ya no querés que guardemos tus datos, alcanza con que nos lo pidas y los eliminamos.':
        'We keep enquiries for as long as we need them to answer and follow up. If you no longer want us to hold your data, just ask and we will delete it.',

    'La idea generatriz parte del momento exacto del crack económico del año 29. Inspirado en la novela el crack up de Scott Fitzgerald, y la decadencia del glamour el Gran Gatsby.':
        'The generating idea starts at the exact moment of the crash of ’29. It draws on Scott Fitzgerald’s The Crack-Up and on the decadent glamour of The Great Gatsby.',

    'EL suelo de terrazo en tonos naturales y ocres en todo el local le otorga al espacio una sensibilidad de sutiles y minúsculas piedras que se integran al “mood mediterráneo”.':
        'The terrazzo floor in natural and ochre tones throughout the venue gives the space the feel of tiny, subtle stones that fold into the “Mediterranean mood”.',

    'No vendemos, alquilamos ni cedemos datos personales a terceros con fines comerciales. Para que el sitio funcione utilizamos estos proveedores, que actúan por nuestra cuenta:':
        'We do not sell, rent or transfer personal data to third parties for commercial purposes. To keep the site running we use the following providers, which act on our behalf:',

    'Un proceso colaborativo de disciplinas integradas, plenamente comprometidas con el proyecto, que refuerza los conceptos fundamentales del producto arquitectónico final.':
        'A collaborative process of integrated disciplines, fully committed to the project, that reinforces the fundamental concepts of the final architectural product.',

    ', que otorgás al completar y enviar voluntariamente cualquiera de los formularios del sitio. Podés retirarlo en cualquier momento, tal como se explica en el punto 8.':
        ', which you give by voluntarily completing and submitting any of the forms on the site. You can withdraw it at any time, as explained in point 8.',

    'El proyecto es resultado de una investigación de dos aspectos en relación a la empresa que nos convocó al proyecto Stella Artois, que a continuación describiremos.':
        'The project is the result of research into two aspects of the company that brought us onto the Stella Artois project, which we describe below.',

    'Las áreas Colaborativas: que propician el intercambio espontáneo, la sinergia grupal y las reuniones de distinas características: formales o descontracturadas.':
        'The collaborative areas: these encourage spontaneous exchange, group synergy and meetings of different kinds, formal or relaxed.',

    'Por otro lado, el trabajo interior debía remitir al concepto de los viejos cafés típicos europeos de principios del siglo XX, muy emparentados a los Parisinos.':
        'On the other hand, the interior had to evoke the old European cafés of the early twentieth century, closely related to the Parisian ones.',

    'Portfolio de proyectos de Hitzig Militello Arquitectos: hotelería, gastronomía, oficinas y arquitectura residencial en Argentina, Chile, Barbados y el mundo.':
        'Project portfolio of Hitzig Militello Architects: hospitality, restaurants, offices and residential architecture in Argentina, Chile, Barbados and around the world.',

    'Arquitectura de interiores más que diseño de interiores: un trabajo holístico que convierte cada espacio en un contenedor de experiencias sensoriales.':
        'Interior architecture rather than interior design: holistic work that turns every space into a container of sensory experience.',

    'Más de dos décadas diseñando espacios de hotelería, gastronomía, oficinas y arquitectura residencial en América Latina, Europa, Medio Oriente y EE.UU.':
        'More than two decades designing hospitality, restaurant, office and residential spaces across Latin America, Europe, the Middle East and the US.',

    'Dezeen, ArchDaily, Wallpaper*, Architectural Digest, Design Boom, La Nación, Clarín, Newsweek y más de dos décadas de publicaciones internacionales.':
        'Dezeen, ArchDaily, Wallpaper*, Architectural Digest, Design Boom, La Nación, Clarín, Newsweek and more than two decades of international coverage.',

    'Profesor de Arquitectura Comercial Interior en La Haus (Leonardo Militello) · Ciclo de conferencias DINA, Auditorio Diego de Torres, UCC Córdoba.':
        'Lecturer in Commercial Interior Architecture at La Haus (Leonardo Militello) · DINA lecture series, Diego de Torres Auditorium, UCC Córdoba.',

    ', en su carácter de autoridad de aplicación, atiende las denuncias y reclamos de quienes vean afectado su derecho a la protección de sus datos.':
        ', as the enforcement authority, handles complaints and claims from anyone whose right to data protection has been affected.',

    'El proyecto está ubicado en una zona exclusiva de la ciudad de Buenos Aires, dentro del predio del campo de polo más importante de Sud América.':
        'The project sits in an exclusive part of Buenos Aires, within the grounds of the most important polo field in South America.',

    'Hitzig Militello Arquitectos: quiénes somos, cómo trabajamos, nuestro equipo y más de 50 premios y distinciones internacionales desde 2004.':
        'Hitzig Militello Architects: who we are, how we work, our team and more than 50 international awards and distinctions since 2004.',

    'Este encargo ha sido muy particular dada las características específicas del sitio y la situación contextual y particular del COVID 19.':
        'This was a very particular commission, given the specific characteristics of the site and the unusual context of COVID-19.',

    'Trabajamos junto a socios estratégicos y consultores locales para resolver normativa, estándares de construcción e ingeniería M.E.P.':
        'We work alongside strategic partners and local consultants to resolve regulations, construction standards and MEP engineering.',

    'International Architecture Festival ARQfestival, Guadalajara, México · Congreso SCA, "Experiencias en arquitectura de interiores".':
        'ARQfestival International Architecture Festival, Guadalajara, Mexico · SCA Congress, “Experiences in interior architecture”.',

    ', ni herramientas de analítica, ni píxeles de seguimiento, ni perfiles publicitarios. No hacemos seguimiento de tu navegación.':
        ', no analytics tools, no tracking pixels and no advertising profiles. We do not track your browsing.',

    'Conceptualizamos ideas, generamos la documentación técnica, creamos el producto arquitectónico y construimos nuestras ideas.':
        'We conceptualise ideas, produce the technical documentation, create the architectural product and build our ideas.',

    'Trabajamos de forma holística, considerando todos los aspectos y variables para llegar a un diseño conceptual único y total.':
        'We work holistically, considering every aspect and variable in order to arrive at a single, complete conceptual design.',

    'Colaboramos estrechamente con nuestros clientes para comprender sus ambiciones, expectativas y el potencial del proyecto.':
        'We work closely with our clients to understand their ambitions, their expectations and the potential of the project.',

    'Más de dos décadas de reconocimientos internacionales, de Buenos Aires a Londres, Chicago, París, Shanghái y Nueva York.':
        'More than two decades of international recognition, from Buenos Aires to London, Chicago, Paris, Shanghai and New York.',

    'UADE FADI · Clase magistral FAD-UPC Córdoba · IED Barcelona, Master in Interior Design for Commercial Spaces and Retail.':
        'UADE FADI · FAD-UPC Córdoba masterclass · IED Barcelona, Master in Interior Design for Commercial Spaces and Retail.',

    'Un restaurante mediterráneo en Palermo, donde las olas del mar se construyen con listones de madera pintados de blanco.':
        'A Mediterranean restaurant in Palermo, where the waves of the sea are built from white-painted timber slats.',

    'Aplicamos un proceso integral, creativo y técnico, para diseñar y desarrollar ideas totalmente nuevas con maestría.':
        'We apply a comprehensive process, creative and technical, to design and develop entirely new ideas with mastery.',

    'Osten, un bar de alta coctelería y restaurante ubicado en el distinguido barrio de Puerto Madero, en Buenos Aires.':
        'Osten, a high-end cocktail bar and restaurant in the distinguished neighbourhood of Puerto Madero, Buenos Aires.',

    'Bar de cocktails en Puerto Madero, 460 m² donde el minimalismo racionalista dialoga con la exaltación sensorial.':
        'Cocktail bar in Puerto Madero: 460 m² where rationalist minimalism meets sensory exaltation.',

    'Si modificamos esta política, actualizaremos la fecha que figura al comienzo. Te sugerimos revisarla cada tanto.':
        'If we change this policy, we will update the date shown at the top. We suggest you check back from time to time.',

    'Sólo recogemos los datos que vos mismo nos enviás. No pedimos ni almacenamos ninguna otra información personal.':
        'We only collect the data you send us yourself. We do not ask for or store any other personal information.',

    'proyectos construidos en Argentina y el mundo, desde grandes espacios públicos hasta locales de escala íntima.':
        'projects built in Argentina and around the world, from large public spaces to venues of intimate scale.',

    'Arquitecto, FADU — Universidad de Buenos Aires, 2003. Profesor de Arquitectura Comercial Interior en La Haus.':
        'Architect, FADU — University of Buenos Aires, 2003. Lecturer in Commercial Interior Architecture at La Haus.',

    'El contenido que buscás se movió o nunca estuvo acá. Volvé al inicio para ver nuestros proyectos y servicios.':
        'The content you are looking for has moved, or was never here. Go back to the home page to see our projects and services.',

    'Renovación total de la discoteca Roket: cinco niveles donde la luz es la tecnología y también la estética.':
        'Complete refurbishment of the Roket nightclub: five levels where light is both the technology and the aesthetic.',

    'Este sitio está dirigido a personas mayores de edad. No recogemos de forma consciente datos de menores.':
        'This site is intended for adults. We do not knowingly collect data from minors.',

    'Propuesta para el pabellón argentino de la Bienal de Venecia 2025: seis inteligencias, cinco sinapsis.':
        'Proposal for the Argentine pavilion at the 2025 Venice Biennale: six intelligences, five synapses.',

    'Un restaurante mediterráneo en Palermo, donde las olas del mar se construyen con listones de madera.':
        'A Mediterranean restaurant in Palermo, where the waves of the sea are built from timber slats.',

    'Una cafetería de día que esconde, detrás de una puerta, un bar de coctelería de estética industrial.':
        'A daytime coffee shop that hides, behind a door, an industrial-looking cocktail bar.',

    'Cómo Hitzig Militello Arquitectos trata los datos personales que se envían a través de este sitio.':
        'How Hitzig Militello Architects handles the personal data submitted through this site.',

    'Oficinas resueltas con tabiques y mobiliario de OSB, y la gráfica de la empresa sobre los vidrios.':
        'Offices resolved with OSB partitions and furniture, and the company graphics applied to the glass.',

    'En el Design District de Miami: una envolvente de chapa perforada que de noche se ilumina entera.':
        'In the Miami Design District: a perforated metal envelope that lights up entirely at night.',

    'TENDIEZ LAB — "Arquitectura Gastronómica y Hotelera: Negocio, Diseño, Experiencia", Buenos Aires.':
        'TENDIEZ LAB — “Restaurant and Hotel Architecture: Business, Design, Experience”, Buenos Aires.',

    'Un salón enteramente al aire libre bajo los arcos del ferrocarril, proyectado en plena pandemia.':
        'An entirely open-air room under the railway arches, designed in the middle of the pandemic.',

    'Un territorio de dualidades: minimalismo racionalista y exaltación sensorial, en Madero Harbour.':
        'A territory of dualities: rationalist minimalism and sensory exaltation, at Madero Harbour.',

    'Heladería Lucciano’s en Caballito: vitrales de composición geométrica, capitoné y piso damero.':
        'Lucciano’s ice cream shop in Caballito: geometric stained glass, buttoned upholstery and a chequerboard floor.',

    'Premios y distinciones internacionales de Hitzig Militello Arquitectos, desde 2008 hasta hoy.':
        'International awards and distinctions of Hitzig Militello Architects, from 2008 to today.',

    'Un atelier de artes y oficios resuelto en 62 m² cubiertos, con envolvente de chapa perforada.':
        'An arts and crafts atelier resolved in 62 m² indoors, with a perforated metal envelope.',

    'Una cremería que se presenta como un volumen facetado de pizarra negra con una cuña de cobre.':
        'A creamery presented as a faceted volume of black slate with a copper wedge.',

    'Oficinas de una fintech en el piso 23: un núcleo compacto libera todo el perímetro vidriado.':
        'Fintech offices on the 23rd floor: a compact core frees up the entire glazed perimeter.',

    'Concurso internacional para Accor: identidad y comunidad como programa, no como decoración.':
        'International competition for Accor: identity and community as programme, not decoration.',

    'IED Kunsthal Bilbao · 10ª TENDIEZ Experiences, Auditorio del Malba · UADE FADI, Proyecto 6.':
        'IED Kunsthal Bilbao · 10th TENDIEZ Experiences, MALBA Auditorium · UADE FADI, Proyecto 6.',

    'TENDIEZ LAB Mar del Plata · UADE FADI · Mesa redonda HOTELGA 2024, podcast Cerrame la Ocho.':
        'TENDIEZ LAB Mar del Plata · UADE FADI · HOTELGA 2024 round table, Cerrame la Ocho podcast.',

    'Un restaurante bajo cerchas blancas, con columnas vegetales que atraviesan las dos plantas.':
        'A restaurant under white trusses, with planted columns running through both floors.',

    'Oficinas de Kavak en el edificio Philips, con volúmenes de chapa blanca dentro de la nave.':
        'Kavak’s offices in the Philips building, with white sheet-metal volumes set inside the shed.',

    'Mercado gastronómico de 1.525 m² dentro de Paseo La Plaza, en el corazón de Buenos Aires.':
        'A 1,525 m² food market inside Paseo La Plaza, in the heart of Buenos Aires.',

    'Áreas VIP y comunes para el mayor arena de Buenos Aires — 640 m² de experiencia de marca.':
        'VIP and common areas for the largest arena in Buenos Aires — 640 m² of brand experience.',

    'El flagship de una empresa de pisos de madera, resuelto con troncos naturales expuestos.':
        'The flagship of a wood flooring company, resolved with exposed natural logs.',

    'Arquitectura interior e inmersión de la experiencia — charla en la Universidad de Morón':
        'Interior architecture and immersion in experience — talk at Universidad de Morón',

    'Desde 2002 diseñamos espacios comerciales y residenciales — hoy con obra construida en':
        'Since 2002 we have designed commercial and residential spaces — today with built work in',

    '10 mandamientos para no fracasar en la industria gastronómica — especial HOTELGA 2024':
        '10 commandments for not failing in the restaurant industry — HOTELGA 2024 special',

    'El estudio de arquitectura y diseño detrás del Movistar Arena, hoteles y restaurantes':
        'The architecture and design studio behind the Movistar Arena, hotels and restaurants',

    'Reforma de oficinas en Buenos Aires para una de las fintech más grandes de la región.':
        'Office refurbishment in Buenos Aires for one of the largest fintechs in the region.',

    '«La creatividad en estado presente» — Leonardo Militello en la Universidad de Palermo':
        '“Creativity in the present tense” — Leonardo Militello at Universidad de Palermo',

    'Un bar de geometrías facetadas en cobre y hormigón, con un patio selvático al fondo.':
        'A bar of faceted geometries in copper and concrete, with a jungle courtyard at the back.',

    'Centro de desarrollo gastronómico de la FEHGRA, bajo una bóveda continua de madera.':
        'FEHGRA’s hospitality development centre, under a continuous timber vault.',

    'Club nocturno en Puerto Madero: luz de neón, cortinados y superficies reflectantes.':
        'Nightclub in Puerto Madero: neon light, drapery and reflective surfaces.',

    'Arquitectura de marca para América Latina, Europa, Medio Oriente y Estados Unidos.':
        'Brand architecture for Latin America, Europe, the Middle East and the United States.',

    'Restaurante y bar en San Telmo, con celosías de madera que filtran toda la planta.':
        'Restaurant and bar in San Telmo, with timber screens filtering the whole floor.',

    'Un volumen inspirado en el skyline medieval de Brujas, frente a la cancha de polo.':
        'A volume inspired by the medieval skyline of Bruges, facing the polo field.',

    'Concurso privado de 44.000 m²: residencias y restauración del Edificio del Plata.':
        'A 44,000 m² private competition: residences and restoration of the Edificio del Plata.',

    'Profesores de Diseño Arquitectónico I, Cátedra Lestard-Cajide-Janchez, FADU-UBA.':
        'Lecturers in Architectural Design I, Lestard-Cajide-Janchez chair, FADU-UBA.',

    'El hub de Kavak dentro del Dot Baires: showroom, oficinas y 15.000 m² de playa.':
        'Kavak’s hub inside Dot Baires: showroom, offices and 15,000 m² of parking.',

    'Un restaurante que crece alrededor de los arboles que ya estaban en el terreno.':
        'A restaurant that grows around the trees that were already on the site.',

    ', así como retirar el consentimiento que nos diste. Para hacerlo, escribinos a':
        ', as well as to withdraw the consent you gave us. To do so, write to us at',

    'Una heladería en esquina, con arcos de metal y mosaicos calcáreos recuperados.':
        'A corner ice cream shop, with metal arches and reclaimed cement tiles.',

    'Un lugar para sentarse al aire libre en la normalidad pandémica: Williamsburg':
        'A place to sit outdoors in the pandemic normal: Williamsburg',

    'Sala de concierto, night club y restaurante sobre la rambla de Montevideo.':
        'Concert hall, nightclub and restaurant on the Montevideo waterfront.',

    '5.290 m² de co-work y co-living: habitar y trabajar en el mismo edificio.':
        '5,290 m² of co-working and co-living: living and working in the same building.',

    'Acepto que el estudio me contacte y el tratamiento de mis datos según la':
        'I agree to be contacted by the studio and to my data being processed under the',

    'Cómo tratamos los datos personales que nos dejás a través de este sitio.':
        'How we handle the personal data you leave us through this site.',

    'Destino Miami — por qué es el mercado inmobiliario del que todos hablan':
        'Destination Miami — why it is the property market everyone is talking about',

    'Hitzig Militello Arquitectos en DINA — Diseñadores Nacionales Asociados':
        'Hitzig Militello Architects at DINA — Diseñadores Nacionales Asociados',

    'Trasladar la esencia del sur del mundo al corazón de Santiago de Chile.':
        'Carrying the essence of the far south into the heart of Santiago de Chile.',
    'nombre y número de teléfono.': 'name and phone number.',
    '— alojamiento del sitio web.': '— website hosting.',
    'Ver menos fotos': 'See fewer photos',
    # el indice del buscador guarda el texto sin escapar, asi que hacen falta
    # las dos formas: con &amp; y con & pelado
    'Proyecto': 'Project',
    'Página': 'Page',
    'Hotelería & Comercial': 'Hotels & Retail',
    'Cultural & Institucional': 'Cultural & Institutional',
    'Restaurante & pastelería': 'Restaurant & patisserie',
    'G&G Magazine — Italia': 'G&G Magazine — Italia',
    '100 NE 38th St & NE 1st Ave, Design District, Miami, Florida':
        '100 NE 38th St & NE 1st Ave, Design District, Miami, Florida',
    'Hotelería, gastronomía, oficinas y arquitectura residencial.':
        'Hospitality, restaurants, offices and residential architecture.',
    'Equipo, premios y trayectoria desde 2002.':
        'Team, awards and practice since 2002.',
    'Publicaciones internacionales desde 2003.':
        'International coverage since 2003.',
    'Buenos Aires y Miami.': 'Buenos Aires and Miami.',
    'Premios y distinciones internacionales desde 2008.':
        'International awards and distinctions since 2008.',
    'Al encontrarnos en un piso 23, con una planta libre expuesta a visuales, la primera decisión proyectual fue no fragmentar el paisaje urbano. Diseñamos una "pastilla" funcional: un núcleo central y compacto que condensa y encapsula todas las funciones fijas, técnicas y de servicio de la empresa (coffee, pantry, sanitarios, copy point, áreas de guardado, booths y data center). Esta operación geométrica funciona como el corazón de la planta, liberando el perímetro del edificio. Así, la totalidad de los puestos habitables se vuelcan hacia la fachada vidriada, garantizando luz natural plena y democratizando las vistas de la ciudad para todo el equipo.':
        'On a 23rd floor with an open plan exposed to the views, the first design decision was not to fragment the urban landscape. We designed a functional "core": a compact central block that condenses and encapsulates all the company’s fixed, technical and service functions (coffee, pantry, washrooms, copy point, storage, booths and data centre). That geometric move works as the heart of the floor, freeing up the perimeter of the building. Every workstation therefore faces the glazed façade, guaranteeing full daylight and democratising the views over the city for the whole team.',
    'Más de 30 distinciones internacionales desde 2008, de Buenos Aires a Londres, Chicago, París, Shanghái y Nueva York. También formamos parte de IIDA, SBID, SCA/CPAU y la Cámara de Comercio Argentino-Estadounidense de Florida (AACC).':
        'More than 30 international distinctions since 2008, from Buenos Aires to London, Chicago, Paris, Shanghai and New York. We are also members of IIDA, SBID, SCA/CPAU and the Argentine-American Chamber of Commerce of Florida (AACC).',
    'todos los premios': 'all the awards',
    'Ver todos los premios': 'See all the awards',
    'Ver menos videos': 'See fewer videos',
    'estudio de arquitectura Buenos Aires, diseño de interiores, arquitectura comercial, arquitectura de hotelería, diseño gastronómico, arquitectura de oficinas, arquitectura residencial':
        'architecture studio Buenos Aires, interior design, commercial architecture, hospitality architecture, restaurant design, office architecture, residential architecture',
})

traducir = en_dic.traducir
