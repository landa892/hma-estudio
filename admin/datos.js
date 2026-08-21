/* Lectura y escritura de obras contra la API de la base.
   ---------------------------------------------------------------------------
   Supabase expone las tablas como REST. Toda llamada lleva el token de la
   sesion, asi que lo que se puede hacer no lo decide esta pantalla sino el RLS
   de la base: si el token vencio o alguien copia estas funciones a su consola,
   la base contesta que no. */

(function () {
  'use strict';

  var REST = HMA.BASE + '/rest/v1';

  /* Los campos que el listado necesita. Se piden explicitos y no con "*" para
     no arrastrar la memoria entera de 61 obras en cada carga del listado. */
  var CAMPOS_LISTA = 'id,slug,titulo,anio,categoria,estado,publicada,destacada,orden';

  function llamar(ruta, opciones) {
    opciones = opciones || {};
    return HMA.token().then(function (t) {
      var cabeceras = {
        apikey: HMA.CLAVE,
        Authorization: 'Bearer ' + t,
        'Content-Type': 'application/json',
      };
      // Sin esto la base contesta 204 sin cuerpo y no hay forma de saber que
      // quedo guardado ni de recuperar el id de una obra recien creada.
      if (opciones.devolver) cabeceras.Prefer = 'return=representation';

      return fetch(REST + ruta, {
        method: opciones.method || 'GET',
        headers: cabeceras,
        body: opciones.body ? JSON.stringify(opciones.body) : undefined,
      }).catch(function () {
        throw new Error('No pudimos conectar con el servidor. Revisá tu conexión.');
      }).then(function (r) {
        return r.text().then(function (t) {
          var datos = null;
          try { datos = t ? JSON.parse(t) : null; } catch (e) {}
          if (!r.ok) throw new Error(traducirError(r.status, datos));
          return datos;
        });
      });
    });
  }

  /* La base contesta en ingles y con el nombre de la restriccion. Los tres
     casos que el estudio va a ver de verdad se explican en castellano. */
  function traducirError(status, datos) {
    var crudo = (datos && (datos.message || datos.hint)) || '';

    if (/obras_slug_key|duplicate key/i.test(crudo)) {
      return 'Ya hay otra obra con esa dirección web. Cambiá el título o la dirección.';
    }
    if (/una_portada/i.test(crudo)) {
      return 'La obra ya tiene una portada elegida.';
    }
    if (/30 imagenes/i.test(crudo)) {
      return 'La obra ya llegó al máximo de 30 imágenes de galería.';
    }
    if (/15 (imagenes|imágenes)/i.test(crudo)) {
      return 'La base todavía conserva el límite anterior de 15 imágenes. '
        + 'Hay que aplicar la actualización 0015 antes de continuar.';
    }
    if (status === 401 || status === 403) {
      return 'Tu sesión venció. Volvé a entrar.';
    }
    return crudo || 'No pudimos guardar los cambios.';
  }

  /* --- obras ------------------------------------------------------------ */

  function listarObras() {
    // Este es tambien el orden de Trabajos. Desde el 21/08 se edita con las
    // flechas del listado y el build lo respeta sin volver a ordenar por año.
    return llamar('/obras?select=' + CAMPOS_LISTA
      + '&order=orden.asc.nullslast,titulo.asc');
  }

  function traerObra(id) {
    return llamar('/obras?select=*&id=eq.' + encodeURIComponent(id))
      .then(function (filas) {
        if (!filas || !filas.length) throw new Error('Esa obra ya no existe.');
        return filas[0];
      });
  }

  function crearObra(obra) {
    return sinColumnaNueva(obra, function (cuerpo) {
      return llamar('/obras', { method: 'POST', body: cuerpo, devolver: true });
    }).then(function (filas) { return filas[0]; });
  }

  function actualizarObra(id, cambios) {
    return sinColumnaNueva(cambios, function (cuerpo) {
      return llamar('/obras?id=eq.' + encodeURIComponent(id),
        { method: 'PATCH', body: cuerpo, devolver: true });
    }).then(function (filas) { return filas[0]; });
  }

  /* Las migraciones se corren a mano y el panel puede publicarse primero. En
     esa ventana no debe bloquearse la edicion de los campos que ya existian.
     Se quita solamente la columna nueva que la propia respuesta nombra. */
  function sinColumnaNueva(cuerpo, enviar) {
    return enviar(cuerpo).catch(function (e) {
      var columna = ['ultimo_cambio', 'premios'].find(function (nombre) {
        return e.message.indexOf(nombre) !== -1 && nombre in cuerpo;
      });
      if (!columna) throw e;
      var copia = {};
      Object.keys(cuerpo).forEach(function (k) {
        if (k !== columna) copia[k] = cuerpo[k];
      });
      return sinColumnaNueva(copia, enviar);
    });
  }

  /* Borrar la obra borra sus filas de imagenes por el cascade, pero NO los
     archivos del bucket. Se borra primero la fila: si despues falla Storage
     queda un archivo huerfano, pero nunca una obra viva con fotos rotas. */
  function borrarObra(id) {
    var rutas = [];
    return listarImagenes(id).then(function (imgs) {
      rutas = imgs.map(function (i) { return i.storage_path; });
      return llamar('/obras?id=eq.' + encodeURIComponent(id), { method: 'DELETE' });
    }).then(function () {
      // La obra ya no es visible ni regenerable. Un fallo al limpiar Storage
      // no debe presentar la baja como fallida ni invitar a repetirla.
      return borrarArchivos(rutas).catch(function () {});
    });
  }

  /* --- imagenes --------------------------------------------------------- */

  /* tipo es opcional: sin el trae fotos y planos juntos. La ficha de edicion
     siempre lo pasa (una galeria por tipo); validarRelacionados en obra.js lo
     usa para exigir al menos una foto al publicar, sin contar los planos. */
  function listarImagenes(obraId, tipo) {
    return llamar('/obra_imagenes?select=*&obra_id=eq.' + encodeURIComponent(obraId)
      + (tipo ? '&tipo=eq.' + encodeURIComponent(tipo) : '')
      + '&order=orden.asc');
  }

  function borrarArchivos(rutas) {
    rutas = (rutas || []).filter(function (ruta) {
      return ruta && !/^@(seed|site):/.test(ruta);
    });
    if (!rutas.length) return Promise.resolve();

    return HMA.token().then(function (t) {
      return fetch(HMA.BASE + '/storage/v1/object/obras', {
        method: 'DELETE',
        headers: {
          apikey: HMA.CLAVE,
          Authorization: 'Bearer ' + t,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prefixes: rutas }),
      }).then(function (r) {
        if (!r.ok) {
          throw new Error('No pudimos eliminar el archivo de la galería. Probá de nuevo.');
        }
      });
    });
  }

  /* --- lo guardado que todavia no esta en la web ------------------------- */

  /* El sitio publico son archivos, asi que guardar no alcanza: hasta que
     alguien aprieta "Publicar cambios" y el build corre, lo guardado vive solo
     en la base. Estas dos funciones son las que dejan avisarlo.

     La fecha contra la que se compara la escribe el ultimo paso del build
     (docs/panel_publicado.py), no el boton: si el build falla, no hay marca y
     el aviso se queda puesto, que es lo correcto. */

  function ultimaPublicacion() {
    return llamar('/publicaciones?select=publicada_en&order=publicada_en.desc&limit=1')
      .then(function (filas) {
        return filas && filas.length ? filas[0].publicada_en : null;
      });
  }

  /* Obras y textos tocados despues de esa fecha. Las obras traen ultimo_cambio,
     que es la frase que escribio el panel al guardar ("la bajada y el año") o
     el trigger de la galeria ("las fotos"). Puede venir vacia -por ejemplo si
     el cambio lo hizo el generador- y el aviso funciona igual, sin el detalle. */
  function cambiosSinPublicar(desde) {
    if (!desde) return Promise.resolve({ obras: [], textos: [] });
    var d = encodeURIComponent(desde);
    return Promise.all([
      llamar('/obras?select=id,slug,titulo,ultimo_cambio,publicada,updated_at'
        + '&updated_at=gt.' + d + '&order=updated_at.desc'),
      llamar('/textos?select=clave,rotulo,seccion,updated_at'
        + '&updated_at=gt.' + d + '&order=updated_at.desc'),
    ]).then(function (r) {
      return { obras: r[0] || [], textos: r[1] || [] };
    });
  }

  /* --- utilidades ------------------------------------------------------- */

  /* La direccion web de la obra. Se propone a partir del titulo pero queda
     editable: cambiar un titulo no deberia romper un link ya compartido. */
  function proponerSlug(titulo) {
    return (titulo || '')
      .toLowerCase()
      // NFD separa la letra de su tilde y despues se borran las tildes
      // sueltas: asi "Galería" queda "galeria" y no "galer-a".
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 60);
  }

  var ESTADOS = [
    { valor: 'en_proyecto', rotulo: 'En proyecto' },
    { valor: 'en_progreso', rotulo: 'En progreso' },
    { valor: 'concluida', rotulo: 'Concluida' },
  ];

  var CATEGORIAS = [
    { valor: 'gastronomico', rotulo: 'Gastronómico' },
    { valor: 'hoteleria', rotulo: 'Hotelería' },
    { valor: 'comercial', rotulo: 'Comercial' },
    { valor: 'oficinas', rotulo: 'Oficinas' },
    { valor: 'residencial', rotulo: 'Residencial' },
    { valor: 'cultural', rotulo: 'Cultural e institucional' },
  ];

  function rotuloDe(lista, valor) {
    for (var i = 0; i < lista.length; i++) {
      if (lista[i].valor === valor) return lista[i].rotulo;
    }
    return '—';
  }

  window.DATOS = {
    listarObras: listarObras,
    traerObra: traerObra,
    crearObra: crearObra,
    actualizarObra: actualizarObra,
    borrarObra: borrarObra,
    listarImagenes: listarImagenes,
    borrarArchivos: borrarArchivos,
    ultimaPublicacion: ultimaPublicacion,
    cambiosSinPublicar: cambiosSinPublicar,
    proponerSlug: proponerSlug,
    ESTADOS: ESTADOS,
    CATEGORIAS: CATEGORIAS,
    rotuloDe: rotuloDe,
  };
})();
