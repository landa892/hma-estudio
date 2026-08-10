/* Listado de obras del panel. */

(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var todas = [];

  function avisar(texto, tipo) {
    var el = $('aviso');
    el.textContent = texto || '';
    el.className = 'aviso' + (texto ? ' aviso--' + tipo : '');
  }

  /* El titulo y el slug van al HTML sin escapar si se arma con innerHTML, y
     los escribe una persona: un apostrofe o un signo menor rompe la fila. Se
     arma con nodos para que el navegador no interprete nada. */
  function celda(fila, texto, clase) {
    var td = document.createElement('td');
    td.textContent = texto == null ? '—' : String(texto);
    if (clase) td.className = clase;
    fila.appendChild(td);
    return td;
  }

  function pintar(lista) {
    var cuerpo = $('filas');
    cuerpo.textContent = '';

    lista.forEach(function (o) {
      var tr = document.createElement('tr');

      // Titulo, con la direccion web abajo para reconocerla de un vistazo.
      var td = document.createElement('td');
      var a = document.createElement('a');
      a.href = '/admin/obra?id=' + encodeURIComponent(o.id);
      a.className = 'tabla__titulo';
      a.textContent = o.titulo;
      td.appendChild(a);
      var slug = document.createElement('span');
      slug.className = 'tabla__slug';
      slug.textContent = '/proyectos/' + o.slug + '/';
      td.appendChild(slug);
      tr.appendChild(td);

      celda(tr, o.anio);
      celda(tr, DATOS.rotuloDe(DATOS.CATEGORIAS, o.categoria));
      celda(tr, DATOS.rotuloDe(DATOS.ESTADOS, o.estado));

      // Publicada o borrador: es el dato que mas se consulta de un listado.
      var estado = document.createElement('td');
      var chip = document.createElement('span');
      chip.className = 'chip ' + (o.publicada ? 'chip--vive' : 'chip--borrador');
      chip.textContent = o.publicada ? 'Publicada' : 'Borrador';
      estado.appendChild(chip);
      if (o.destacada) {
        var d = document.createElement('span');
        d.className = 'chip chip--destacada';
        d.textContent = 'En el home';
        estado.appendChild(d);
      }
      tr.appendChild(estado);

      var acciones = document.createElement('td');
      acciones.className = 'tabla__acciones';
      var editar = document.createElement('a');
      editar.href = '/admin/obra?id=' + encodeURIComponent(o.id);
      editar.className = 'enlace';
      editar.textContent = 'Editar';
      acciones.appendChild(editar);

      var borrar = document.createElement('button');
      borrar.type = 'button';
      borrar.className = 'enlace enlace--riesgo';
      borrar.textContent = 'Eliminar';
      borrar.addEventListener('click', function () { confirmarBorrado(o); });
      acciones.appendChild(borrar);
      tr.appendChild(acciones);

      cuerpo.appendChild(tr);
    });

    $('tabla').classList.toggle('oculto', !lista.length);
    $('sinResultados').classList.toggle('oculto', !!lista.length);
    $('conteo').textContent = lista.length === todas.length
      ? todas.length + ' obras'
      : lista.length + ' de ' + todas.length + ' obras';
  }

  function filtrar() {
    var texto = $('buscador').value.trim().toLowerCase();
    var pub = $('filtroEstado').value;
    pintar(todas.filter(function (o) {
      if (pub === 'si' && !o.publicada) return false;
      if (pub === 'no' && o.publicada) return false;
      if (!texto) return true;
      return (o.titulo || '').toLowerCase().indexOf(texto) >= 0
        || (o.slug || '').toLowerCase().indexOf(texto) >= 0;
    }));
  }

  /* Eliminar es lo unico que no tiene vuelta atras, asi que se pide escribir
     el titulo. Un "¿estas seguro?" se acepta sin leer; copiar el nombre no. */
  function confirmarBorrado(obra) {
    var escrito = window.prompt(
      'Esto elimina "' + obra.titulo + '" y todas sus fotos. No se puede deshacer.\n\n'
      + 'Para confirmar, escribí el título de la obra:');
    if (escrito === null) return;
    if (escrito.trim().toLowerCase() !== obra.titulo.trim().toLowerCase()) {
      avisar('El título no coincide. No se eliminó nada.', 'error');
      return;
    }

    avisar('Eliminando…', 'ok');
    DATOS.borrarObra(obra.id).then(function () {
      todas = todas.filter(function (o) { return o.id !== obra.id; });
      filtrar();
      avisar('"' + obra.titulo + '" quedó eliminada.', 'ok');
    }).catch(function (e) {
      avisar(e.message, 'error');
    });
  }

  function cargar() {
    return DATOS.listarObras().then(function (lista) {
      todas = lista || [];
      $('cargando').classList.add('oculto');
      filtrar();
    }).catch(function (e) {
      $('cargando').classList.add('oculto');
      avisar(e.message, 'error');
    });
  }

  /* --- arranque --------------------------------------------------------- */

  HMA.exigirSesion().then(function () {
    var s = HMA.sesion();
    $('quien').textContent = s && s.email ? s.email : '';
    $('buscador').addEventListener('input', filtrar);
    $('filtroEstado').addEventListener('change', filtrar);
    $('salir').addEventListener('click', function () {
      HMA.salir().then(function () { location.replace('/admin/'); });
    });
    return cargar();
  }).catch(function () { /* exigirSesion ya redirigio */ });
})();
