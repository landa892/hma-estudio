-- El credito de fotografia.
--
-- No estaba en el esquema original porque el estudio pidio no mostrar creditos
-- de foto. Pero una obra del sitio —Ualá II— si lo tiene, asi que la columna
-- hace falta para que el generador pueda reproducir esa pagina tal cual.
--
-- Va antes de la carga de obras, que ya la usa.
alter table obras add column if not exists fotografia text;
