/* Edicion de la lista general de premios. Las filas historicas viven en la
   pagina publica; este panel agrega las nuevas sin tocar las obras existentes. */
(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var aviso = $('aviso');
  var filas = [];
  var obras = [];

  function urlLogo(valor) {
    if (!valor) return '';
    if (/^(https?:|data:|blob:)/i.test(valor)) return valor;
    return valor.charAt(0) === '/' ? valor : '/' + valor;
  }

  function pintarPreviewLogo(valor) {
    var caja = $('previewLogo');
    caja.textContent = '';
    if (!valor) { caja.classList.add('oculto'); return; }
    var img = document.createElement('img');
    img.src = urlLogo(valor);
    img.alt = 'Vista previa del logo del premio';
    img.addEventListener('error', function () {
      caja.textContent = 'No se pudo mostrar la vista previa de esta imagen.';
    }, { once: true });
    caja.appendChild(img);
    caja.classList.remove('oculto');
  }

  function cargarObras() {
    return DATOS.listarObras().then(function (resultado) {
      obras = resultado || [];
      pintarSelectorObras();
    });
  }

  function pintarSelectorObras(slugSeleccionado) {
    var selector = $('obraSlug');
    var actual = slugSeleccionado == null ? selector.value : slugSeleccionado;
    selector.textContent = '';
    var sinObra = document.createElement('option');
    sinObra.value = '';
    sinObra.textContent = 'Sin obra relacionada';
    selector.appendChild(sinObra);
    obras.forEach(function (obra) {
      var opcion = document.createElement('option');
      opcion.value = obra.slug;
      opcion.textContent = (obra.titulo || obra.slug) + ' · ' + obra.slug
        + (obra.publicada ? '' : ' (borrador)');
      selector.appendChild(opcion);
    });
    // Un slug guardado puede quedar fuera del catálogo si alguien cambió la
    // dirección de la obra. Mantenerlo visible evita borrar el vínculo al editar.
    if (actual && !obras.some(function (obra) { return obra.slug === actual; })) {
      var anterior = document.createElement('option');
      anterior.value = actual;
      anterior.textContent = 'Obra vinculada (dirección anterior): ' + actual;
      selector.appendChild(anterior);
    }
    selector.value = actual || '';
  }

  function rutaLogoSubido(url) {
    if (!url) return '';
    var prefijo = HMA.BASE.replace(/\/+$/, '') + '/storage/v1/object/public/obras/';
    if (url.indexOf(prefijo) !== 0) return '';
    var ruta = url.slice(prefijo.length);
    return /^premios\/[A-Za-z0-9._-]+$/.test(ruta) ? ruta : '';
  }

  function subirLogo(archivo) {
    if (!/^image\/(jpeg|png|webp)$/.test(archivo.type) || archivo.size > 20 * 1024 * 1024) {
      return Promise.reject(new Error('Usá un logo JPG, PNG o WebP de hasta 20 MB.'));
    }
    return createImageBitmap(archivo, { imageOrientation: 'from-image' }).then(function (bmp) {
      var escala = Math.min(1, 1600 / Math.max(bmp.width, bmp.height));
      var canvas = document.createElement('canvas');
      canvas.width = Math.max(1, Math.round(bmp.width * escala));
      canvas.height = Math.max(1, Math.round(bmp.height * escala));
      canvas.getContext('2d').drawImage(bmp, 0, 0, canvas.width, canvas.height);
      bmp.close();
      return new Promise(function (resolver, rechazar) {
        canvas.toBlob(function (blob) {
          if (!blob) return rechazar(new Error('No pudimos procesar el logo.'));
          resolver(blob);
        }, 'image/webp', .9);
      });
    }).then(function (blob) {
      var ruta = 'premios/' + Date.now() + '-' + Math.random().toString(36).slice(2, 10) + '.webp';
      return HMA.token().then(function (token) {
        return fetch(HMA.BASE + '/storage/v1/object/obras/' + ruta, {
          method: 'POST',
          headers: {
            apikey: HMA.CLAVE,
            Authorization: 'Bearer ' + token,
            'Content-Type': 'image/webp',
            'x-upsert': 'false',
          },
          body: blob,
        }).then(function (respuesta) {
          if (!respuesta.ok) throw new Error('No pudimos subir el logo. Revisá tu conexión y probá de nuevo.');
          return HMA.BASE + '/storage/v1/object/public/obras/' + ruta;
        });
      });
    });
  }

  /* El sitio publicado puede seguir apuntando al logo viejo hasta el próximo
     build. Solo se borra un archivo nuevo cuando falla el guardado en la base. */
  function borrarLogoSubido(url) {
    var ruta = rutaLogoSubido(url);
    if (!ruta) return Promise.resolve();
    return DATOS.borrarArchivos([ruta]);
  }

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
    $('logoArchivo').value = '';
    pintarPreviewLogo('');
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
    pintarSelectorObras(premio.obra_slug || '');
    $('logo').value = premio.logo || '';
    $('logoArchivo').value = '';
    pintarPreviewLogo(premio.logo || '');
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
    var slug = $('obraSlug').value;
    var logo = $('logo').value.trim();
    var obra = obras.find(function (fila) { return fila.slug === slug; });
    if (!Number.isInteger(anio) || anio < 1900 || anio > 2100) throw new Error('Escribí un año válido.');
    if (nombre.length < 2) throw new Error('Escribí el nombre del premio.');
    if (enlace && !/^https?:\/\//i.test(enlace)) throw new Error('El enlace tiene que empezar con http:// o https://.');
    if ($('publicada').checked && obra && !obra.publicada) {
      throw new Error('Publicá primero la obra relacionada o dejá este premio como borrador.');
    }
    if (!$('logoArchivo').files.length && logo
        && !/^https:\/\/[^\s]+$/i.test(logo) && !/^\/assets\/[A-Za-z0-9._/-]+$/.test(logo)) {
      throw new Error('La imagen debe ser un enlace https:// o una ruta que empiece con /assets/.');
    }
    return {
      anio: anio, orden: Number.isInteger(orden) && orden >= 0 ? orden : 0,
      nombre: nombre, resultado: $('resultado').value.trim() || null,
      ciudad: $('ciudad').value.trim() || null, descripcion: $('descripcion').value.trim() || null,
      enlace: enlace || null, obra_slug: slug || null, logo: logo || null,
      publicada: $('publicada').checked,
    };
  }

  $('formPremio').addEventListener('submit', function (evento) {
    evento.preventDefault();
    var datos;
    try { datos = recoger(); } catch (e) { mensaje(e.message, true); return; }
    var id = $('premioId').value;
    var archivo = $('logoArchivo').files[0];
    $('guardarPremio').disabled = true;
    mensaje(archivo ? 'Subiendo logo y guardando premio…' : 'Guardando…');
    var logoNuevo = '';
    (archivo ? subirLogo(archivo) : Promise.resolve(datos.logo)).then(function (logo) {
      logoNuevo = archivo ? logo : '';
      if (archivo) datos.logo = logo;
      var accion = id ? DATOS.actualizarPremio(id, datos) : DATOS.crearPremio(datos);
      return accion;
    }).then(function () {
      mensaje('Premio guardado. Ahora falta publicar los cambios desde Obras.');
      limpiar();
    }).catch(function (e) {
      if (logoNuevo) borrarLogoSubido(logoNuevo).catch(function () {});
      mensaje(e.message, true);
      throw e;
    }).then(function () {
      return cargar();
    }).catch(function () {
      // El premio puede haberse guardado aunque haya fallado la recarga del listado.
    }).then(function () {
      $('guardarPremio').disabled = false;
    });
  });

  $('borrarPremio').addEventListener('click', function () {
    var id = $('premioId').value;
    if (!id || !window.confirm('¿Eliminar este premio?')) return;
    $('borrarPremio').disabled = true;
    DATOS.borrarPremio(id).then(function () {
      mensaje('Premio eliminado.'); limpiar();
      return cargar();
    }).catch(function (e) { mensaje(e.message, true); }).then(function () {
      $('borrarPremio').disabled = false;
    });
  });

  $('nuevoPremio').addEventListener('click', function () { limpiar(); $('anio').focus(); });
  $('cancelarPremio').addEventListener('click', limpiar);
  $('logoArchivo').addEventListener('change', function () {
    var archivo = this.files[0];
    if (!archivo) return;
    if (!/^image\/(jpeg|png|webp)$/.test(archivo.type) || archivo.size > 20 * 1024 * 1024) {
      this.value = '';
      mensaje('Usá un logo JPG, PNG o WebP de hasta 20 MB.', true);
      return;
    }
    pintarPreviewLogo(URL.createObjectURL(archivo));
  });
  $('logo').addEventListener('input', function () {
    if (!$('logoArchivo').files.length) pintarPreviewLogo(this.value.trim());
  });
  $('salir').addEventListener('click', function () { HMA.salir(); });

  HMA.exigirSesion().then(function () {
    limpiar();
    return Promise.all([cargar(), cargarObras()]);
  })
    .catch(function (e) {
      if (e.message !== 'Sin sesión.') mensaje(e.message, true);
    });
})();
