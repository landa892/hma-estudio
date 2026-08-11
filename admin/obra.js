/* Alta y edicion de una obra. */

(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };

  var id = new URLSearchParams(location.search).get('id');
  var esNueva = !id;
  var original = null;      // lo que se cargo de la base, para saber si cambio
  var slugTocado = false;   // si el usuario lo edito a mano, no se pisa
  var guardando = false;

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
    $('equipo').value = (o.equipo || []).join('\n');
    $('bajada').value = o.bajada || '';
    $('memoria').value = o.memoria || '';
    $('memoriaEn').value = o.memoria_en || '';
    $('estado').value = o.estado || 'en_proyecto';
    $('destacada').checked = !!o.destacada;
    $('bannerRotulo').value = o.banner_rotulo || '';
    $('bannerRotuloEn').value = o.banner_rotulo_en || '';
    $('publicada').checked = !!o.publicada;
    contarBajada();
    verBanner();
  }

  /* Los campos del banner solo tienen sentido si la obra va al home. Mostrarlos
     siempre haria pensar que toda obra tiene banner. */
  function verBanner() {
    $('camposBanner').classList.toggle('oculto', !$('destacada').checked);
  }

  function recoger() {
    var texto = function (campo) {
      var v = $(campo).value.trim();
      return v === '' ? null : v;
    };
    return {
      titulo: $('titulo').value.trim(),
      slug: $('slug').value.trim(),
      ubicacion: texto('ubicacion'),
      pais: texto('pais'),
      anio: texto('anio'),
      superficie: texto('superficie'),
      comitente: texto('comitente'),
      tipologia: texto('tipologia'),
      categoria: $('categoria').value || null,
      // Una linea por nombre. Se limpian las vacias que deja copiar y pegar.
      equipo: $('equipo').value.split('\n')
        .map(function (x) { return x.trim(); })
        .filter(Boolean),
      bajada: texto('bajada'),
      memoria: texto('memoria'),
      memoria_en: texto('memoriaEn'),
      estado: $('estado').value,
      destacada: $('destacada').checked,
      banner_rotulo: texto('bannerRotulo'),
      banner_rotulo_en: texto('bannerRotuloEn'),
      publicada: $('publicada').checked,
    };
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
    return null;
  }

  function contarBajada() {
    var n = $('bajada').value.length;
    $('contadorBajada').textContent = n ? '(' + n + ' de 200)' : '';
  }

  /* --- guardar ---------------------------------------------------------- */

  function guardar(ev) {
    ev.preventDefault();
    if (guardando) return;

    var o = recoger();
    var error = validar(o);
    if (error) {
      avisar(error, 'error');
      return;
    }

    guardando = true;
    $('guardar').disabled = true;
    $('guardar').textContent = 'Guardando…';
    avisar('', 'ok');

    var promesa = esNueva
      ? DATOS.crearObra(o)
      : DATOS.actualizarObra(id, o);

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
      avisar(o.publicada
        ? 'Guardada y publicada.'
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
      if (!slugTocado && esNueva) {
        $('slug').value = DATOS.proponerSlug($('titulo').value);
      }
    });
    $('slug').addEventListener('input', function () { slugTocado = true; });
    $('bajada').addEventListener('input', contarBajada);
    $('destacada').addEventListener('change', verBanner);
    $('formObra').addEventListener('submit', guardar);

    // Salir con cambios sin guardar es la forma mas facil de perder una
    // memoria entera recien escrita.
    window.addEventListener('beforeunload', function (ev) {
      if (!guardando && hayCambios()) ev.preventDefault();
    });

    if (esNueva) {
      $('cargando').classList.add('oculto');
      $('formObra').classList.remove('oculto');
      $('titulo').focus();
      return;
    }

    return DATOS.traerObra(id).then(function (fila) {
      original = fila;
      slugTocado = true;   // en una obra ya creada el slug no se recalcula
      volcar(fila);
      $('encabezado').textContent = fila.titulo;
      $('ayudaSlug').textContent = 'Cambiarla rompe los links a esta obra '
        + 'que ya estén compartidos o en Google.';
      $('cargando').classList.add('oculto');
      $('formObra').classList.remove('oculto');
      return GALERIA.iniciar(id);
    }).catch(function (e) {
      $('cargando').textContent = e.message;
    });
  }).catch(function () { /* exigirSesion ya redirigio */ });
})();
