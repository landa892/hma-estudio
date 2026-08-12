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
    if (/15 imagenes/i.test(crudo)) {
      return 'La obra ya llegó al máximo de 15 imágenes.';
    }
    if (status === 401 || status === 403) {
      return 'Tu sesión venció. Volvé a entrar.';
    }
    return crudo || 'No pudimos guardar los cambios.';
  }

  /* --- obras ------------------------------------------------------------ */

  function listarObras() {
    // Sin año primero no: van al final. Postgres ordena los nulos al final con
    // nullslast, y despues por año descendente, que es el orden del sitio.
    return llamar('/obras?select=' + CAMPOS_LISTA
      + '&order=anio.desc.nullslast,titulo.asc');
  }

  function traerObra(id) {
    return llamar('/obras?select=*&id=eq.' + encodeURIComponent(id))
      .then(function (filas) {
        if (!filas || !filas.length) throw new Error('Esa obra ya no existe.');
        return filas[0];
      });
  }

  function crearObra(obra) {
    return llamar('/obras', { method: 'POST', body: obra, devolver: true })
      .then(function (filas) { return filas[0]; });
  }

  function actualizarObra(id, cambios) {
    return llamar('/obras?id=eq.' + encodeURIComponent(id),
      { method: 'PATCH', body: cambios, devolver: true })
      .then(function (filas) { return filas[0]; });
  }

  /* Borrar la obra borra sus filas de imagenes por el cascade, pero NO los
     archivos del bucket: eso se hace antes, aparte, o quedan ocupando espacio
     para siempre. */
  function borrarObra(id) {
    return listarImagenes(id).then(function (imgs) {
      if (!imgs.length) return null;
      return borrarArchivos(imgs.map(function (i) { return i.storage_path; }));
    }).then(function () {
      return llamar('/obras?id=eq.' + encodeURIComponent(id), { method: 'DELETE' });
    });
  }

  /* --- imagenes --------------------------------------------------------- */

  function listarImagenes(obraId) {
    return llamar('/obra_imagenes?select=*&obra_id=eq.'
      + encodeURIComponent(obraId) + '&order=orden.asc');
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
    proponerSlug: proponerSlug,
    ESTADOS: ESTADOS,
    CATEGORIAS: CATEGORIAS,
    rotuloDe: rotuloDe,
  };
})();
