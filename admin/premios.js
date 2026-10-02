/* Edicion de la lista general de premios. Las filas historicas viven en la
   pagina publica; este panel agrega las nuevas sin tocar las obras existentes. */
(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var aviso = $('aviso');
  var filas = [];

  function mensaje(texto, error) {
    aviso.textContent = texto || '';
    aviso.className = error ? 'aviso aviso--error' : 'aviso';
  }

  function esc(valor) {
    return String(valor == null ? '' : valor).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }

  function limpiar() {
    $('premioId').value = '';
    $('anio').value = new Date().getFullYear();
    $('orden').value = '0';
    $('nombre').value = '';
    $('resultado').value = '';
    $('ciudad').value = '';
    $('descripcion').value = '';
    $('enlace').value = '';
    $('obraSlug').value = '';
    $('logo').value = '';
    $('publicada').checked = false;
    $('formTitulo').textContent = 'Nuevo premio';
    $('borrarPremio').classList.add('oculto');
  }

  function editar(premio) {
    $('premioId').value = premio.id;
    $('anio').value = premio.anio;
    $('orden').value = premio.orden || 0;
    $('nombre').value = premio.nombre || '';
    $('resultado').value = premio.resultado || '';
    $('ciudad').value = premio.ciudad || '';
    $('descripcion').value = premio.descripcion || '';
    $('enlace').value = premio.enlace || '';
    $('obraSlug').value = premio.obra_slug || '';
    $('logo').value = premio.logo || '';
    $('publicada').checked = !!premio.publicada;
    $('formTitulo').textContent = 'Editar premio';
    $('borrarPremio').classList.remove('oculto');
    $('nombre').focus();
  }

  function pintar() {
    var lista = $('listaPremios');
    lista.textContent = '';
    if (!filas.length) {
      var vacio = document.createElement('p');
      vacio.className = 'vacio';
      vacio.textContent = 'Todavía no hay premios agregados desde el panel.';
      lista.appendChild(vacio);
      return;
    }
    filas.forEach(function (p) {
      var boton = document.createElement('button');
      boton.type = 'button';
      boton.className = 'premio-admin-item';
      boton.dataset.id = p.id;
      boton.innerHTML = '<strong class="premio-admin-item__anio">' + esc(p.anio)
        + '</strong><span><b>' + esc(p.nombre) + '</b><small>'
        + esc(p.resultado || p.ciudad || 'Sin detalle') + '</small></span>'
        + '<em class="premio-admin-item__estado ' + (p.publicada ? '' : 'premio-admin-item__estado--borrador')
        + '">' + (p.publicada ? 'Publicado' : 'Borrador') + '</em>';
      boton.addEventListener('click', function () { editar(p); });
      lista.appendChild(boton);
    });
  }

  function cargar() {
    return DATOS.listarPremios().then(function (resultado) {
      filas = resultado || [];
      pintar();
    }).catch(function (e) {
      pintar();
      mensaje(e.message, true);
    });
  }

  function recoger() {
    var anio = Number($('anio').value);
    var orden = Number($('orden').value || 0);
    var nombre = $('nombre').value.trim();
    var enlace = $('enlace').value.trim();
    var slug = $('obraSlug').value.trim();
    if (!Number.isInteger(anio) || anio < 1900 || anio > 2100) throw new Error('Escribí un año válido.');
    if (nombre.length < 2) throw new Error('Escribí el nombre del premio.');
    if (enlace && !/^https?:\/\//i.test(enlace)) throw new Error('El enlace tiene que empezar con http:// o https://.');
    if (slug && !/^[a-z0-9-]+$/.test(slug)) throw new Error('El slug solo puede tener minúsculas, números y guiones.');
    return {
      anio: anio, orden: Number.isInteger(orden) && orden >= 0 ? orden : 0,
      nombre: nombre, resultado: $('resultado').value.trim() || null,
      ciudad: $('ciudad').value.trim() || null, descripcion: $('descripcion').value.trim() || null,
      enlace: enlace || null, obra_slug: slug || null, logo: $('logo').value.trim() || null,
      publicada: $('publicada').checked,
    };
  }

  $('formPremio').addEventListener('submit', function (evento) {
    evento.preventDefault();
    var datos;
    try { datos = recoger(); } catch (e) { mensaje(e.message, true); return; }
    var id = $('premioId').value;
    $('guardarPremio').disabled = true;
    mensaje('Guardando…');
    var accion = id ? DATOS.actualizarPremio(id, datos) : DATOS.crearPremio(datos);
    accion.then(function () {
      mensaje('Premio guardado. Ahora falta publicar los cambios desde Obras.');
      limpiar();
      return cargar();
    }).catch(function (e) { mensaje(e.message, true); }).then(function () {
      $('guardarPremio').disabled = false;
    });
  });

  $('borrarPremio').addEventListener('click', function () {
    var id = $('premioId').value;
    if (!id || !window.confirm('¿Eliminar este premio?')) return;
    $('borrarPremio').disabled = true;
    DATOS.borrarPremio(id).then(function () {
      mensaje('Premio eliminado.'); limpiar(); return cargar();
    }).catch(function (e) { mensaje(e.message, true); }).then(function () {
      $('borrarPremio').disabled = false;
    });
  });

  $('nuevoPremio').addEventListener('click', function () { limpiar(); $('anio').focus(); });
  $('cancelarPremio').addEventListener('click', limpiar);
  $('salir').addEventListener('click', function () { HMA.salir(); });

  HMA.exigirSesion().then(function () { limpiar(); return cargar(); })
    .catch(function () { /* exigirSesion ya redirigio */ });
})();
