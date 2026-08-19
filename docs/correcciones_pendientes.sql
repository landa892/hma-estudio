-- Dos categorias que el cliente pidio cambiar. Viven en la base, asi que
-- tocarlas solo en el HTML no alcanza: el proximo deploy las revierte.
--
-- El HTML de main ya quedo con estos valores. Correr esto los deja firmes.

-- Casa Luna va en Oficinas, no en Residencial.
update obras set categoria = 'oficinas' where slug = 'oficina-casa-luna';

-- Patio de Comidas Abasto va en Gastronomico, no en Comercial.
update obras set categoria = 'gastronomico' where slug = 'abasto-patio-comidas';
