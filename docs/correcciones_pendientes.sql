-- Lo que falta esta en la base y no en el repositorio, asi que tocar el HTML
-- no alcanza: el proximo deploy lo revierte.


-- 1) Dos categorias que el cliente pidio cambiar. El HTML de main ya quedo
--    con estos valores; esto los deja firmes.

-- Casa Luna va en Oficinas, no en Residencial.
update obras set categoria = 'oficinas' where slug = 'oficina-casa-luna';

-- Patio de Comidas Abasto va en Gastronomico, no en Comercial.
update obras set categoria = 'gastronomico' where slug = 'abasto-patio-comidas';


-- 2) Memoria en ingles de Ualá Gigena. Era la unica obra con memoria
-- castellana y sin su version inglesa: 57 de 61 ya la tenian, y las
-- otras tres (parfumerie, novotel, iguanafix) no tienen ninguna de las
-- dos porque nadie las escribio todavia.

update obras set memoria_en = $memoria$The challenge of designing workspaces always calls for particular reflection on the way we conceive activity and the unfolding of working life. Architecture, in this respect, undoubtedly has a great deal to contribute to the user's quality of life. We took on the project for the Ualá offices with that premise.

The project is structured around two large spaces joined by a connecting corridor and a courtyard that works as a lung. Starting from the client's programmatic requirements and from the conditions inherent to the space to be intervened —a shed in the heart of Palermo— the decision was to segment the total floor area according to needs of use. This produced a reception area that serves as an anteroom to a large double-height space, proposing a single place organised in work islands.

The use of the exposed structure is part of a balance between the old building and the new intervention. The black corrugated sheet plays a contrasting role, by its nature as a contemporary material, in relation to the rough concrete. In the same way, the roof structure painted white holds a very subtle relationship in detaching itself from the existing structure through the darker tones. This chromatic shift makes it possible to read a space between what was already there and the new intervention.

This room plays the leading role in the project, allowing for 60 workstations, all with views onto an outdoor courtyard whose attraction is the vertical garden, and in full natural light. A large skin of planked and stained timber lines walls and ceiling, generating a large space clear of fittings and services. Beams, reveals, electrical and thermomechanical installations remain concealed.

As in the first office, this building has a space for informal meetings and rest. It is designed as a honeycomb wall, where the interstices are spaces of use, all defined by three different materials: timber, glass and iron.

The choice of materials, both for the finishes and for the furniture, seeks to give the space simplicity and visual calm through the use of noble materials. The construction materials and those of the furnishings, together with the lighting study —direct, indirect and natural— and the thermomechanical conditions, generate a whole that achieves ideal comfort in conceiving a workspace.$memoria$
  where slug = 'uala-gigena';
