-- El cliente pidio que la pagina use el titulo corto, sin numero ni bajada.
-- La condicion preserva cualquier edicion posterior hecha desde el panel.
update textos
set es = 'Contacto', en = 'Contact'
where clave = 'contacto.titular'
  and es = 'Hablemos de tu proyecto';
