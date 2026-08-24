/* Alta y edicion de una obra. */

(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };

  var id = new URLSearchParams(location.search).get('id');
  var esNueva = !id;
  var original = null;      // lo que se cargo de la base, para saber si cambio
  var slugTocado = false;   // si el usuario lo edito a mano, no se pisa
  var guardando = false;
  var cantidadCuerpoDisponible = false;

  function avisar(texto, tipo) {
    var el = $('aviso');
    el.textContent = texto || '';
    el.className = 'aviso' + (texto ? ' aviso--' + tipo : '');
  }

  function opciones(select, lista, vacio) {
    select.textContent = '';
    if (vacio) {
      var o = document.createElement('option');
      o.value = '';
      o.textContent = vacio;
      select.appendChild(o);
    }
    lista.forEach(function (x) {
      var o = document.createElement('option');
      o.value = x.valor;
      o.textContent = x.rotulo;
      select.appendChild(o);
    });
  }

  /* --- formulario <-> obra ---------------------------------------------- */

  function volcar(o) {
    $('titulo').value = o.titulo || '';
    $('slug').value = o.slug || '';
    $('ubicacion').value = o.ubicacion || '';
    $('pais').value = o.pais || '';
    $('anio').value = o.anio || '';
    $('superficie').value = o.superficie || '';
    $('comitente').value = o.comitente || '';
    $('tipologia').value = o.tipologia || '';
    $('categoria').value = o.categoria || '';
    $('intervencion').value = o.intervencion || '';
    $('fotografia').value = o.fotografia || '';
    $('equipo').value = (o.equipo || []).join('\n');
    $('bajada').value = o.bajada || '';
    $('memoria').value = o.memoria || '';
    $('memoriaEn').value = o.memoria_en || '';
    $('premios').value = o.premios || '';
    cantidadCuerpoDisponible = Object.prototype.hasOwnProperty.call(
      o, 'fotos_cuerpo_cantidad');
    prepararCantidadCuerpo(cantidadCuerpoDisponible);
    $('fotosCuerpoCantidad').value = cantidadCuerpoDisponible
      ? o.fotos_cuerpo_cantidad : 3;
    $('estado').value = o.estado || 'en_proyecto';
    $('publicada').checked = !!o.publicada;
    contarTitulo();
    contarBajada();
    contarMemoria('memoria', 'contadorMemoria');
    contarMemoria('memoriaEn', 'contadorMemoriaEn');
    verFotografia();
  }

  /* El credito no corresponde a proyectos que solo muestran renders. Se
     conserva el valor al cambiar de estado, pero el campo y el generador solo
     lo exponen cuando la obra esta concluida. */
  function verFotografia() {
    $('campoFotografia').classList.toggle('oculto', $('estado').value !== 'concluida');
  }

  function prepararCantidadCuerpo(disponible) {
    cantidadCuerpoDisponible = !!disponible;
    $('fotosCuerpoCantidad').disabled = !cantidadCuerpoDisponible;
    $('ayudaFotosCuerpoCantidad').classList.toggle(
      'campo__ayuda--alerta', !cantidadCuerpoDisponible);
    $('ayudaFotosCuerpoCantidad').textContent = cantidadCuerpoDisponible
      ? 'Elegí de 0 a 30. La portada cuenta como la primera; después se usa la selección ordenada de abajo o, si está vacía, la galería. Cambiar este número no elimina ninguna imagen.'
      : 'Falta activar esta opción en la base. Aplicá 0018_cantidad_fotos_cuerpo.sql; mientras tanto la obra conserva sus 3 fotos actuales.';
  }

  function actualizarEnlacePublico() {
    var slug = $('slug').value.trim();
    var visible = !esNueva && !!slug && $('publicada').checked;
    $('verObra').classList.toggle('oculto', !visible);
    if (visible) $('verObra').href = '/proyectos/' + encodeURIComponent(slug) + '/';
  }

  function recoger() {
    var texto = function (campo) {
      var v = $(campo).value.trim();
      return v === '' ? null : v;
    };
    var obra = {
      titulo: $('titulo').value.trim(),
      slug: $('slug').value.trim(),
      ubicacion: texto('ubicacion'),
      pais: texto('pais'),
      anio: texto('anio'),
      superficie: texto('superficie'),
      comitente: texto('comitente'),
      tipologia: texto('tipologia'),
      categoria: $('categoria').value || null,
      intervencion: $('intervencion').value || null,
      fotografia: texto('fotografia'),
      // Una linea por nombre. Se limpian las vacias que deja copiar y pegar.
      equipo: $('equipo').value.split('\n')
        .map(function (x) { return x.trim(); })
        .filter(Boolean),
      bajada: texto('bajada'),
      memoria: texto('memoria'),
      memoria_en: texto('memoriaEn'),
      premios: texto('premios'),
      estado: $('estado').value,
      // El Inicio actual ya no tiene banners de obras. Se limpian las marcas
      // heredadas al guardar para que el panel no anuncie una configuracion
      // que la pagina no usa.
      destacada: false,
      banner_rotulo: null,
      banner_rotulo_en: null,
      publicada: $('publicada').checked,
    };
    if (cantidadCuerpoDisponible) {
      obra.fotos_cuerpo_cantidad = Number($('fotosCuerpoCantidad').value);
    }
    return obra;
  }

  function hayCambios() {
    if (esNueva) {
      var o = recoger();
      return !!(o.titulo || o.memoria || o.ubicacion);
    }
    return JSON.stringify(recoger()) !== JSON.stringify(comparable(original));
  }

  /* La fila de la base trae campos que el formulario no toca (id, fechas,
     orden). Se recorta a los mismos campos para poder comparar de igual a
     igual y no avisar de cambios que no existen. */
  function comparable(fila) {
    var o = {};
    Object.keys(recoger()).forEach(function (k) {
      o[k] = fila[k] === undefined ? null : fila[k];
    });
    o.equipo = fila.equipo || [];
    return o;
  }

  /* --- que cambio ------------------------------------------------------- */

  /* Como se llama cada campo cuando hay que nombrarlo en una frase. Sirve para
     dos cosas: el aviso de "sin guardar" de esta pantalla y la frase que se
     guarda en la base para que el listado pueda decir "Roket (la bajada)". */
  var NOMBRES = {
    titulo: 'el título',
    slug: 'la dirección web',
    ubicacion: 'la ubicación',
    pais: 'el país',
    anio: 'el año',
    superficie: 'la superficie',
    comitente: 'el comitente',
    tipologia: 'la tipología',
    categoria: 'la categoría',
    intervencion: 'la intervención',
    fotografia: 'el fotógrafo',
    equipo: 'el equipo',
    bajada: 'la bajada',
    memoria: 'la memoria',
    memoria_en: 'la memoria en inglés',
    premios: 'los premios',
    fotos_cuerpo_cantidad: 'la cantidad de fotos del cuerpo',
    estado: 'el estado',
    destacada: 'si va al home',
    banner_rotulo: 'el rótulo del banner',
    banner_rotulo_en: 'el rótulo del banner en inglés',
    publicada: 'la publicación',
  };

  function camposCambiados() {
    if (esNueva) return [];
    var ahora = recoger();
    var antes = comparable(original);
    return Object.keys(ahora).filter(function (k) {
      return JSON.stringify(ahora[k]) !== JSON.stringify(antes[k]);
    });
  }

  /* "la bajada y el año", "el título, la memoria y 3 campos más". Se corta en
     tres porque el aviso vive en una linea al lado del boton. */
  function enPalabras(campos) {
    var nombres = campos.map(function (k) { return NOMBRES[k] || k; });
    if (!nombres.length) return '';
    if (nombres.length > 3) {
      var resto = nombres.length - 2;
      nombres = nombres.slice(0, 2).concat(
        [resto + (resto === 1 ? ' campo más' : ' campos más')]);
    }
    if (nombres.length === 1) return nombres[0];
    return nombres.slice(0, -1).join(', ') + ' y ' + nombres[nombres.length - 1];
  }

  /* El cartelito al lado de Guardar. */
  function verSinGuardar() {
    var el = $('sinGuardar');
    var campos = esNueva ? [] : camposCambiados();
    var hay = esNueva ? hayCambios() : campos.length > 0;
    el.classList.toggle('oculto', !hay);
    if (!hay) return;
    el.textContent = esNueva
      ? 'Sin guardar'
      : 'Sin guardar: ' + enPalabras(campos);
  }

  /* --- validacion ------------------------------------------------------- */

  function validar(o) {
    if (!o.titulo) return 'La obra necesita un título.';
    if (!o.slug) return 'La obra necesita una dirección web.';
    if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(o.slug)) {
      return 'La dirección web solo admite minúsculas, números y guiones. '
        + 'Sin espacios, tildes ni eñes.';
    }
    // Publicar algo sin memoria deja la pagina de la obra practicamente vacia.
    if (o.publicada && !o.memoria) {
      return 'Para publicarla falta la memoria descriptiva. '
        + 'Podés guardarla como borrador y completarla después.';
    }
    if (o.publicada && !o.categoria) {
      return 'Para publicarla elegí una categoría. Es la que usa el filtro de Trabajos.';
    }
    if (o.publicada && !o.tipologia) {
      return 'Para publicarla completá la tipología. Se muestra debajo del nombre en Trabajos.';
    }
    if (o.publicada && !o.intervencion) {
      return 'Para publicarla elegí la intervención: interiorismo, arquitectura o ambos.';
    }
    if (o.publicada && !o.ubicacion) {
      return 'Para publicarla completá la ubicación. Se muestra en la tarjeta de Trabajos.';
    }
    if (o.publicada && !o.superficie) {
      return 'Para publicarla completá la superficie. Incluí el número y la unidad, por ejemplo 325 m².';
    }
    if (o.publicada && !o.anio) {
      return 'Para publicarla completá el año. Usá cuatro cifras o un rango, por ejemplo 2025–2026.';
    }
    if (cantidadCuerpoDisponible
        && (!Number.isInteger(o.fotos_cuerpo_cantidad)
            || o.fotos_cuerpo_cantidad < 0
            || o.fotos_cuerpo_cantidad > 30)) {
      return 'Elegí entre 0 y 30 fotos para acompañar la memoria.';
    }
    return null;
  }

  function validarRelacionados(o) {
    if (esNueva && o.publicada) {
      return Promise.reject(new Error(
        'Primero guardala como borrador, cargá al menos una foto y después publicala.'
      ));
    }

    var fotos = o.publicada
      ? DATOS.listarImagenes(id, 'foto').then(function (lista) {
        if (!lista.length) {
          throw new Error('Para publicarla cargá al menos una foto y elegí una portada.');
        }
      })
      : Promise.resolve();

    return fotos;
  }

  function contarBajada() {
    var n = $('bajada').value.length;
    $('contadorBajada').textContent = '(' + n + ' de 200 caracteres)';
  }

  function contarTitulo() {
    $('contadorTitulo').textContent = '(' + $('titulo').value.length + ' de 120)';
  }

  function contarMemoria(campo, contador) {
    var texto = $(campo).value.trim();
    var palabras = texto ? texto.split(/\s+/).length : 0;
    var parrafos = texto ? texto.split(/\n\s*\n/).filter(Boolean).length : 0;
    $(contador).textContent = '(' + palabras + (palabras === 1 ? ' palabra' : ' palabras')
      + ', ' + parrafos + (parrafos === 1 ? ' párrafo' : ' párrafos') + ')';
  }

  /* --- guardar ---------------------------------------------------------- */

  /* Cambiar la direccion web sigue siendo una decision importante. El
     24/08/2026 se renombraron dos obras y sus rutas de imagen quedaron bajo el
     slug anterior. Desde la 0017 el historial y la redireccion se guardan
     solos, pero se conserva la confirmacion para evitar cambios accidentales. */
  /* El mismo aviso, pero mientras escribe: que se vea antes de llegar al boton
     de guardar y no como una sorpresa al final. */
  function avisarSiCambiaLaDireccion() {
    var ayuda = $('ayudaSlug');
    if (!ayuda || esNueva || !original) return;
    var antes = (original.slug || '').trim();
    var ahora = $('slug').value.trim();
    if (!antes || antes === ahora) {
      ayuda.classList.remove('campo__ayuda--alerta');
      ayuda.textContent = 'No la cambies salvo que sea imprescindible. Si cambia, el panel '
        + 'conserva la dirección anterior y las fotos en el próximo deploy. Sólo admite '
        + 'minúsculas, números y guiones.';
      return;
    }
    ayuda.classList.add('campo__ayuda--alerta');
    ayuda.textContent = 'Ojo: estás cambiando la dirección pública. El panel conservará '
      + '/proyectos/' + antes + '/ como acceso a /proyectos/' + (ahora || '…')
      + '/ y trasladará sus imágenes al publicar.';
  }

  function confirmarCambioDeSlug(o) {
    if (esNueva || !original) return true;
    var antes = (original.slug || '').trim();
    var ahora = (o.slug || '').trim();
    if (!antes || antes === ahora) return true;
    return window.confirm(
      'Vas a cambiar la dirección web de esta obra.\n\n'
      + 'Antes:  estudiohma.com/proyectos/' + antes + '/\n'
      + 'Ahora:  estudiohma.com/proyectos/' + ahora + '/\n\n'
      + 'Al publicar, la dirección anterior seguirá llevando a la nueva y las '
      + 'imágenes se trasladarán automáticamente.\n\n'
      + '¿Seguimos?');
  }

  function guardar(ev) {
    ev.preventDefault();
    if (guardando) return;

    var o = recoger();
    var error = validar(o);
    if (error) {
      avisar(error, 'error');
      return;
    }
    if (!confirmarCambioDeSlug(o)) {
      avisar('No se guardó nada. La dirección web quedó como estaba.', 'ok');
      return;
    }

    guardando = true;
    $('guardar').disabled = true;
    $('guardar').textContent = 'Guardando…';
    avisar('', 'ok');

    // Que se toco, en castellano, para que el listado pueda decir "Roket (la
    // bajada)". Se calcula antes de guardar, que es cuando todavia hay contra
    // que comparar, y se suma al cuerpo despues de validar: recoger() no lo
    // devuelve a proposito, porque entonces hayCambios() compararia un campo
    // que el formulario no muestra y la obra se veria siempre modificada.
    o.ultimo_cambio = esNueva
      ? 'la obra nueva'
      : (enPalabras(camposCambiados()) || null);

    var promesa = validarRelacionados(o).then(function () {
      if (!esNueva) return DATOS.actualizarObra(id, o);
      // Una obra nueva entra al final del orden que ve el estudio. Si quedara
      // null, el panel y el sitio no tendrian una posicion comun que mover.
      return DATOS.listarObras().then(function (obras) {
        o.orden = obras.reduce(function (maximo, obra) {
          var n = Number(obra.orden);
          return Number.isFinite(n) ? Math.max(maximo, n) : maximo;
        }, -1) + 1;
        return DATOS.crearObra(o);
      });
    });

    promesa.then(function (fila) {
      original = fila;
      guardando = false;
      $('guardar').disabled = false;
      $('guardar').textContent = 'Guardar';

      if (esNueva) {
        // Se pasa a modo edicion sin recargar: si volviera a guardar crearia
        // una segunda obra con el mismo contenido.
        esNueva = false;
        id = fila.id;
        history.replaceState(null, '', '/admin/obra?id=' + encodeURIComponent(id));
        $('encabezado').textContent = fila.titulo;
        // Ya hay id, asi que las fotos tienen a donde colgarse.
        GALERIA.iniciar(id);
      }
      actualizarEnlacePublico();
      verSinGuardar();
      avisar(o.publicada
        ? 'Guardada. Para verla en el sitio, publicá los cambios desde Obras.'
        : 'Guardada como borrador.', 'ok');
    }).catch(function (e) {
      guardando = false;
      $('guardar').disabled = false;
      $('guardar').textContent = 'Guardar';
      avisar(e.message, 'error');
    });
  }

  /* --- arranque --------------------------------------------------------- */

  HMA.exigirSesion().then(function () {
    var s = HMA.sesion();
    $('quien').textContent = s && s.email ? s.email : '';
    $('salir').addEventListener('click', function () {
      HMA.salir().then(function () { location.replace('/admin/'); });
    });

    opciones($('categoria'), DATOS.CATEGORIAS, 'Sin categoría');
    opciones($('estado'), DATOS.ESTADOS);

    // La direccion web se propone del titulo mientras nadie la haya tocado.
    $('titulo').addEventListener('input', function () {
      contarTitulo();
      if (!slugTocado && esNueva) {
        $('slug').value = DATOS.proponerSlug($('titulo').value);
      }
    });
    $('slug').addEventListener('input', function () {
      slugTocado = true;
      avisarSiCambiaLaDireccion();
      actualizarEnlacePublico();
    });
    $('bajada').addEventListener('input', contarBajada);
    $('memoria').addEventListener('input', function () {
      contarMemoria('memoria', 'contadorMemoria');
    });
    $('memoriaEn').addEventListener('input', function () {
      contarMemoria('memoriaEn', 'contadorMemoriaEn');
    });
    document.querySelectorAll('[data-negrita]').forEach(function (boton) {
      boton.addEventListener('click', function () {
        var campo = $(boton.dataset.negrita);
        var inicio = campo.selectionStart;
        var fin = campo.selectionEnd;
        var elegido = campo.value.slice(inicio, fin) || 'texto destacado';
        campo.setRangeText('**' + elegido + '**', inicio, fin, 'select');
        campo.dispatchEvent(new Event('input', { bubbles: true }));
        campo.focus();
      });
    });
    $('estado').addEventListener('change', verFotografia);
    $('publicada').addEventListener('change', actualizarEnlacePublico);
    $('formObra').addEventListener('submit', guardar);

    // Un solo escuchador para todo el formulario. input cubre lo que se
    // escribe y change lo que se elige o se tilda.
    $('formObra').addEventListener('input', verSinGuardar);
    $('formObra').addEventListener('change', verSinGuardar);

    // Salir con cambios sin guardar es la forma mas facil de perder una
    // memoria entera recien escrita.
    window.addEventListener('beforeunload', function (ev) {
      if (!guardando && hayCambios()) ev.preventDefault();
    });

    if (esNueva) {
      return DATOS.admiteCantidadCuerpo().then(function (disponible) {
        prepararCantidadCuerpo(disponible);
        $('fotosCuerpoCantidad').value = 3;
        $('cargando').classList.add('oculto');
        $('formObra').classList.remove('oculto');
        contarTitulo();
        contarBajada();
        contarMemoria('memoria', 'contadorMemoria');
        contarMemoria('memoriaEn', 'contadorMemoriaEn');
        verFotografia();
        $('titulo').focus();
      });
    }

    return DATOS.traerObra(id).then(function (fila) {
      // El Inicio vigente no contiene banners de obras. Se normaliza tambien
      // la copia comparable para que una marca vieja no aparezca como cambio
      // sin guardar apenas se abre la ficha.
      fila.destacada = false;
      fila.banner_rotulo = null;
      fila.banner_rotulo_en = null;
      original = fila;
      slugTocado = true;   // en una obra ya creada el slug no se recalcula
      volcar(fila);
      $('encabezado').textContent = fila.titulo;
      $('ayudaSlug').textContent = 'No la cambies salvo que sea imprescindible: rompe los enlaces '
        + 'compartidos y la dirección que conoce Google. Sólo admite minúsculas, números y guiones.';
      $('cargando').classList.add('oculto');
      $('formObra').classList.remove('oculto');
      actualizarEnlacePublico();
      return GALERIA.iniciar(id);
    }).catch(function (e) {
      $('cargando').textContent = e.message;
    });
  }).catch(function () { /* exigirSesion ya redirigio */ });
})();
