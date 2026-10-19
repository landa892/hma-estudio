/* Edicion de la lista general de premios. Las filas historicas viven en la
   pagina publica; este panel agrega las nuevas sin tocar las obras existentes. */
(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var aviso = $('aviso');
  var filas = [];
  /* Mientras se guarda un reordenamiento las flechas quedan apagadas, para no
     encadenar dos movidas sobre un orden que todavia no confirmo la base. */
  var moviendo = false;
  var obras = [];

  function urlLogo(valor) {
    if (!valor) return '';
    if (/^(https?:|data:|blob:)/i.test(valor)) return valor;
    return valor.charAt(0) === '/' ? valor : '/' + valor;
  }

  /* Cuanto de la imagen es casi blanco. Devuelve null si el navegador no deja
     leer los pixeles: una imagen de otro dominio sin CORS mancha el canvas. En
     ese caso manda la vista previa sobre los dos fondos, que no depende de
     poder medir nada. */
  function proporcionClara(img) {
    try {
      var lienzo = document.createElement('canvas');
      lienzo.width = img.naturalWidth;
      lienzo.height = img.naturalHeight;
      var ctx = lienzo.getContext('2d');
      ctx.drawImage(img, 0, 0);
      var datos = ctx.getImageData(0, 0, lienzo.width, lienzo.height).data;
      var visibles = 0, claros = 0;
      for (var i = 0; i < datos.length; i += 4) {
        if (datos[i + 3] <= 40) continue;
        visibles++;
        if (datos[i] > 235 && datos[i + 1] > 235 && datos[i + 2] > 235) claros++;
      }
      return visibles ? claros / visibles : null;
    } catch (e) {
      return null;
    }
  }

  function rotulo(caja, texto, esAviso) {
    var p = document.createElement('p');
    p.className = 'premio-logo-rotulo' + (esAviso ? ' premio-logo-rotulo--aviso' : '');
    p.textContent = texto;
    caja.appendChild(p);
  }

  /* El logo se muestra sobre fondo claro y sobre fondo oscuro. El sitio lo
     publica sobre blanco, asi que un logo blanco -la version de un escudo para
     pie de pagina, por ejemplo- se publica invisible. Antes la vista previa
     tambien era clara y el estudio no tenia como darse cuenta: veia el recuadro
     vacio y daba por hecho que la imagen no habia cargado. */
  function pintarPreviewLogo(valor) {
    var caja = $('previewLogo');
    caja.textContent = '';
    caja.classList.remove('premio-logo-preview--doble');
    if (!valor) { caja.classList.add('oculto'); return; }

    caja.classList.add('premio-logo-preview--doble');
    var imgs = ['claro', 'oscuro'].map(function (fondo) {
      var celda = document.createElement('div');
      celda.className = 'premio-logo-fondo premio-logo-fondo--' + fondo;
      var img = document.createElement('img');
      img.src = urlLogo(valor);
      img.alt = fondo === 'claro'
        ? 'Vista previa del logo sobre fondo claro, que es como sale en el sitio'
        : 'La misma imagen sobre fondo oscuro, para ver un logo claro';
      celda.appendChild(img);
      caja.appendChild(celda);
      return img;
    });

    imgs[0].addEventListener('error', function () {
      caja.textContent = 'No se pudo mostrar la vista previa de esta imagen.';
      caja.classList.remove('premio-logo-preview--doble');
    }, { once: true });

    imgs[0].addEventListener('load', function () {
      // Las de otro dominio pueden medirse si el servidor manda CORS; si no,
      // crossOrigin haria fallar la carga, asi que se prueba sobre una copia.
      var copia = new Image();
      copia.crossOrigin = 'anonymous';
      copia.addEventListener('load', function () {
        var clara = proporcionClara(copia);
        if (clara !== null && clara > .9) {
          rotulo(caja, 'Ojo: este logo es casi todo blanco, así que en la página '
            + 'va a quedar invisible sobre el fondo claro. Usá la versión oscura '
            + 'o en color.', true);
        } else {
          rotulo(caja, 'Izquierda: como se ve en la página. Derecha: la misma '
            + 'imagen sobre fondo oscuro.', false);
        }
      }, { once: true });
      copia.addEventListener('error', function () {
        rotulo(caja, 'Izquierda: como se ve en la página. Derecha: la misma '
          + 'imagen sobre fondo oscuro. Si solo aparece a la derecha, el logo es '
          + 'blanco y en el sitio no se va a ver.', false);
      }, { once: true });
      copia.src = imgs[0].src;
    }, { once: true });

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
    /* Primero de su año. Lo ultimo que carga el estudio es lo que quiere ver
       arriba -lo dijo el 19/10/2026 sobre una obra, y para los premios vale
       igual-, y asi no hay que subirlo a flechazos.
       Se usa el minimo del año menos uno y no 0, porque 0 chocaria con el
       premio que ya ocupa ese puesto. El negativo se normaliza solo: lo
       renumera el build, y tambien la primera flecha que alguien toque. */
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
    /* En el mismo orden en que salen publicados. Recorrer filas tal como vino
       de la base dejaba la lista quieta despues de mover una flecha: el orden
       nuevo ya estaba guardado pero no se veia hasta recargar la pagina. */
    ordenadas().forEach(function (p) {
      var hermanos = delAnio(p.anio);
      var puesto = hermanos.indexOf(p);

      var caja = document.createElement('div');
      caja.className = 'premio-admin-fila';

      /* Las flechas mueven dentro del año, que es como se agrupa la pagina. El
         estudio lo pidio en audio el 16/10/2026: "si yo quiero poner otro
         arriba pueda hacerlo". Antes solo estaba el campo numerico "Orden
         dentro del año", que hay que abrir, escribir y guardar. */
      var orden = document.createElement('div');
      orden.className = 'premio-admin-orden';
      [['↑', -1, 'Subir', puesto <= 0],
       ['↓', 1, 'Bajar', puesto >= hermanos.length - 1]].forEach(function (x) {
        var boton = document.createElement('button');
        boton.type = 'button';
        boton.className = 'orden-btn';
        boton.textContent = x[0];
        boton.title = x[2] + ' dentro de ' + p.anio;
        boton.setAttribute('aria-label', x[2] + ' ' + p.nombre + ' dentro de ' + p.anio);
        boton.disabled = moviendo || x[3];
        boton.addEventListener('click', function () { mover(p, x[1]); });
        orden.appendChild(boton);
      });
      caja.appendChild(orden);

      /* El numero de puesto, para saltar lejos sin apretar la flecha treinta
         veces. El estudio lo propuso el 19/10/2026: "si le ponemos numero al
         lado de cada premio y lo movemos poniendo numeros, onda si esta 40 y
         queres 3 podes poner el 3 y se pone ahi".
         Va de 1 en adelante y no de 0, que es como se cuenta una lista cuando
         uno la mira. */
      var puestoCampo = document.createElement('input');
      puestoCampo.type = 'number';
      puestoCampo.className = 'premio-admin-puesto';
      puestoCampo.min = '1';
      puestoCampo.max = String(hermanos.length);
      puestoCampo.value = String(puesto + 1);
      puestoCampo.disabled = moviendo || hermanos.length < 2;
      puestoCampo.title = 'Puesto dentro de ' + p.anio
        + '. Escribí otro número y salí del casillero para moverlo.';
      puestoCampo.setAttribute('aria-label',
        'Puesto de ' + p.nombre + ' dentro de ' + p.anio);
      puestoCampo.addEventListener('change', function () {
        moverA(p, Number(this.value));
      });
      /* Enter mueve sin tener que salir del casillero. */
      puestoCampo.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') { e.preventDefault(); this.blur(); }
      });
      caja.appendChild(puestoCampo);

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
      caja.appendChild(boton);
      lista.appendChild(caja);
    });
  }

  /* Todos los premios como salen en la pagina: el año mas nuevo primero y,
     dentro de cada año, el orden que marcan las flechas. */
  function ordenadas() {
    return filas.slice().sort(function (a, b) {
      return Number(b.anio) - Number(a.anio)
        || (a.orden || 0) - (b.orden || 0)
        || String(a.created_at || '').localeCompare(String(b.created_at || ''));
    });
  }

  /* Arriba de su año es el puesto 0, y los que estaban se corren uno.
     En Trabajos alcanza con un numero negativo y una sola escritura, pero acá
     no se puede: premios_panel tiene check (orden between 0 and 9999), asi que
     la base rechaza cualquier negativo. Como un año tiene seis premios a lo
     sumo, correrlos sale barato. Si alguno de esos guardados fallara quedarian
     empates, y de eso ya se ocupa el build, que renumera cada año 0..n-1. */
  function correrHermanos(anio, exceptoId) {
    var hermanos = delAnio(anio).filter(function (f) {
      return exceptoId == null || String(f.id) !== String(exceptoId);
    });
    return Promise.all(hermanos.map(function (f, puesto) {
      if (f.orden === puesto + 1) return null;
      f.orden = puesto + 1;
      return DATOS.actualizarPremio(f.id, { orden: puesto + 1 });
    }).filter(Boolean));
  }

  /* Los premios de un año, en el orden en que salen publicados. */
  function delAnio(anio) {
    return filas.filter(function (f) { return String(f.anio) === String(anio); })
      .sort(function (a, b) {
        return (a.orden || 0) - (b.orden || 0)
          || String(a.created_at || '').localeCompare(String(b.created_at || ''));
      });
  }

  function mover(premio, direccion) {
    var hermanos = delAnio(premio.anio);
    moverA(premio, hermanos.indexOf(premio) + direccion + 1);
  }

  /* Lleva el premio al puesto pedido dentro de su año, contando desde 1. */
  function moverA(premio, puesto) {
    if (moviendo) return;
    var hermanos = delAnio(premio.anio);
    var desde = hermanos.indexOf(premio);
    var hasta = Math.round(puesto) - 1;
    if (desde < 0 || !Number.isFinite(hasta)) return pintar();
    // Un numero fuera de rango se acomoda al extremo mas cercano en vez de no
    // hacer nada: escribir 99 queriendo "al final" es lo que uno espera.
    hasta = Math.max(0, Math.min(hermanos.length - 1, hasta));
    if (hasta === desde) return pintar();

    moviendo = true;
    hermanos.splice(desde, 1);
    hermanos.splice(hasta, 0, premio);

    /* Se renumera el año entero de 0 en adelante. Guardar solo los dos que se
       tocaron deja huecos y empates cuando el orden venia de la siembra. */
    var cambios = [];
    hermanos.forEach(function (fila, indice) {
      if (fila.orden !== indice) {
        fila.orden = indice;
        cambios.push(DATOS.actualizarPremio(fila.id, { orden: indice }));
      }
    });
    pintar();
    mensaje('Guardando el orden…');

    Promise.all(cambios).then(function () {
      moviendo = false;
      pintar();
      mensaje('Orden guardado. Publicá los cambios para verlo en la web.');
    }).catch(function (e) {
      moviendo = false;
      mensaje(e.message, true);
      cargar();
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

    /* Guardar con el campo del logo vacio borra el logo que el premio tenia, y
       antes lo hacia sin decir nada. El 16/10/2026 el logo de Valk Gallery
       desaparecio de la base entre dos consultas con el archivo todavia subido
       al Storage, que es justo lo que deja este camino. Si habia logo y se va a
       guardar sin ninguno, se pregunta. */
    if (id && !archivo && !datos.logo) {
      var antes = filas.find(function (fila) { return String(fila.id) === String(id); });
      if (antes && antes.logo
          && !window.confirm('Este premio tenía un logo cargado y lo vas a dejar '
            + 'sin logo. ¿Seguro que querés sacarlo?')) {
        mensaje('No se guardó: el premio conserva su logo.');
        return;
      }
    }
    $('guardarPremio').disabled = true;
    mensaje(archivo ? 'Subiendo logo y guardando premio…' : 'Guardando…');
    var logoNuevo = '';
    (archivo ? subirLogo(archivo) : Promise.resolve(datos.logo)).then(function (logo) {
      logoNuevo = archivo ? logo : '';
      if (archivo) datos.logo = logo;
      /* El premio entra arriba de su año -orden 0- y los que ya estaban se
         corren uno. Solo al darlo de alta, o cuando se le cambia el año a uno
         que ya existe, que es otra forma de entrar a ese año.
         Editar un premio sin tocarle el año no mueve nada: si corriera siempre,
         arreglar una coma en el premio que el estudio puso tercero lo mandaria
         de vuelta al primer puesto. */
      var anterior = filas.find(function (f) { return String(f.id) === String(id); });
      var entraAlAnio = !id || (anterior && String(anterior.anio) !== String(datos.anio));
      if (!entraAlAnio) {
        datos.orden = anterior ? anterior.orden : datos.orden;
        return DATOS.actualizarPremio(id, datos);
      }
      return correrHermanos(datos.anio, id || null).then(function () {
        return id ? DATOS.actualizarPremio(id, datos) : DATOS.crearPremio(datos);
      });
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
  /* Cambiar el año manda el premio arriba de ese año. Si no, se lleva puesto
     el orden del año anterior y choca con el premio que ya ocupaba ese puesto.
     Despues se acomoda con las flechas. */
  $('anio').addEventListener('change', function () {
    $('orden').value = '0';
  });

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
