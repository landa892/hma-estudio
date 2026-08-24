/* Listado de obras del panel. */

(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var todas = [];
  var moviendo = false;

  function resumir() {
    $('totalObras').textContent = todas.length;
    $('totalPublicadas').textContent = todas.filter(function (o) { return o.publicada; }).length;
    $('totalBorradores').textContent = todas.filter(function (o) { return !o.publicada; }).length;
    $('resumen').classList.remove('oculto');
  }

  function avisar(texto, tipo) {
    var el = $('aviso');
    el.textContent = texto || '';
    el.className = 'aviso' + (texto ? ' aviso--' + tipo : '');
  }

  /* El titulo y el slug van al HTML sin escapar si se arma con innerHTML, y
     los escribe una persona: un apostrofe o un signo menor rompe la fila. Se
     arma con nodos para que el navegador no interprete nada. */
  function celda(fila, texto, rotulo, clase) {
    var td = document.createElement('td');
    td.textContent = texto == null ? '—' : String(texto);
    td.dataset.rotulo = rotulo;
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
      td.dataset.rotulo = 'Obra';
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

      celda(tr, o.anio, 'Año');
      celda(tr, DATOS.rotuloDe(DATOS.CATEGORIAS, o.categoria), 'Categoría');
      celda(tr, DATOS.rotuloDe(DATOS.ESTADOS, o.estado), 'Estado');

      // Publicada o borrador: es el dato que mas se consulta de un listado.
      var estado = document.createElement('td');
      estado.dataset.rotulo = 'En el sitio';
      var chip = document.createElement('span');
      chip.className = 'chip ' + (o.publicada ? 'chip--vive' : 'chip--borrador');
      chip.textContent = o.publicada ? 'Publicada' : 'Borrador';
      estado.appendChild(chip);
      tr.appendChild(estado);

      var orden = document.createElement('td');
      orden.className = 'tabla__orden';
      orden.dataset.rotulo = 'Orden';
      var indice = todas.indexOf(o);
      var subir = document.createElement('button');
      subir.type = 'button';
      subir.className = 'orden-btn';
      subir.textContent = '↑';
      subir.title = 'Subir en Trabajos';
      subir.setAttribute('aria-label', 'Subir ' + o.titulo + ' en Trabajos');
      subir.disabled = moviendo || indice <= 0;
      subir.addEventListener('click', function () { mover(o, -1); });
      orden.appendChild(subir);
      var bajar = document.createElement('button');
      bajar.type = 'button';
      bajar.className = 'orden-btn';
      bajar.textContent = '↓';
      bajar.title = 'Bajar en Trabajos';
      bajar.setAttribute('aria-label', 'Bajar ' + o.titulo + ' en Trabajos');
      bajar.disabled = moviendo || indice >= todas.length - 1;
      bajar.addEventListener('click', function () { mover(o, 1); });
      orden.appendChild(bajar);
      tr.appendChild(orden);

      var acciones = document.createElement('td');
      acciones.className = 'tabla__acciones';
      acciones.dataset.rotulo = 'Acciones';
      var editar = document.createElement('a');
      editar.href = '/admin/obra?id=' + encodeURIComponent(o.id);
      editar.className = 'enlace';
      editar.textContent = 'Editar';
      acciones.appendChild(editar);

      if (o.publicada) {
        var ver = document.createElement('a');
        ver.href = '/proyectos/' + encodeURIComponent(o.slug) + '/';
        ver.className = 'enlace';
        ver.textContent = 'Ver';
        ver.target = '_blank';
        ver.rel = 'noopener';
        acciones.appendChild(ver);
      }

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

  /* Intercambia dos posiciones reales, aunque haya un filtro activo. Si el
     listado heredado trae ordenes nulos o repetidos, primero lo normaliza: es
     preferible una escritura mas larga una sola vez a que dos tarjetas queden
     empatadas y el build las publique en un orden impredecible. */
  function mover(obra, direccion) {
    if (moviendo) return;
    var desde = todas.indexOf(obra);
    var hasta = desde + direccion;
    if (desde < 0 || hasta < 0 || hasta >= todas.length) return;

    moviendo = true;
    var otra = todas[hasta];
    todas[desde] = otra;
    todas[hasta] = obra;
    var cambios = [];
    todas.forEach(function (fila, indice) {
      if (fila.orden !== indice) {
        fila.orden = indice;
        cambios.push(DATOS.actualizarObra(fila.id, {
          orden: indice,
          ultimo_cambio: 'el orden en Trabajos',
        }));
      }
    });
    filtrar();
    avisar('Guardando el orden…', 'ok');

    Promise.all(cambios).then(function () {
      moviendo = false;
      filtrar();
      avisar('Orden guardado. Publicá los cambios para verlo en la web.', 'ok');
    }).catch(function (e) {
      moviendo = false;
      avisar(e.message, 'error');
      cargar();
    });
  }

  function filtrar() {
    var texto = $('buscador').value.trim().toLowerCase();
    var pub = $('filtroEstado').value;
    var categoria = $('filtroCategoria').value;
    pintar(todas.filter(function (o) {
      if (pub === 'si' && !o.publicada) return false;
      if (pub === 'no' && o.publicada) return false;
      if (categoria && o.categoria !== categoria) return false;
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
      resumir();
      filtrar();
      avisar('"' + obra.titulo + '" quedó eliminada.', 'ok');
    }).catch(function (e) {
      avisar(e.message, 'error');
    });
  }

  function cargar() {
    return DATOS.listarObras().then(function (lista) {
      todas = lista || [];
      resumir();
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
    DATOS.CATEGORIAS.forEach(function (categoria) {
      var opcion = document.createElement('option');
      opcion.value = categoria.valor;
      opcion.textContent = categoria.rotulo;
      $('filtroCategoria').appendChild(opcion);
    });
    $('filtroCategoria').addEventListener('change', filtrar);
    $('salir').addEventListener('click', function () {
      HMA.salir().then(function () { location.replace('/admin/'); });
    });
    return cargar();
  }).catch(function () { /* exigirSesion ya redirigio */ });
})();
