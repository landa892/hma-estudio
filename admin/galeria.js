/* Galeria de una obra: subir, ordenar, elegir portada y eliminar.
   ---------------------------------------------------------------------------
   Las fotos se achican y se convierten a WebP en el navegador, antes de subir.
   No es un lujo: el estudio carga desde el telefono y una foto sale de 8 MB.
   Subir eso llena el almacenamiento en dos obras y deja la pagina lenta para
   siempre, porque despues se sirve tal cual. */

(function () {
  'use strict';

  var LADO_MAX = 1800;      // el mismo tope que ya usan las galerias del sitio
  var CALIDAD = 0.82;
  var TOPE = 15;            // lo que se cotizo; la base lo valida tambien

  var $ = function (id) { return document.getElementById(id); };

  var obraId = null;
  var fotos = [];
  var arrastrada = null;
  var activando = null;

  /* --- optimizacion ----------------------------------------------------- */

  /* Devuelve un blob WebP redimensionado.
     imageOrientation: 'from-image' aplica la rotacion del EXIF: sin eso las
     fotos verticales del telefono se suben acostadas. */
  function optimizar(archivo) {
    return createImageBitmap(archivo, { imageOrientation: 'from-image' })
      .then(function (bmp) {
        var escala = Math.min(1, LADO_MAX / Math.max(bmp.width, bmp.height));
        var ancho = Math.round(bmp.width * escala);
        var alto = Math.round(bmp.height * escala);

        var lienzo = document.createElement('canvas');
        lienzo.width = ancho;
        lienzo.height = alto;
        lienzo.getContext('2d').drawImage(bmp, 0, 0, ancho, alto);
        bmp.close();

        return new Promise(function (resolver, rechazar) {
          lienzo.toBlob(function (blob) {
            if (!blob) return rechazar(new Error('No pudimos procesar la imagen.'));
            resolver({ blob: blob, ancho: ancho, alto: alto });
          }, 'image/webp', CALIDAD);
        });
      })
      .catch(function () {
        throw new Error('No pudimos leer esa imagen. ¿Es un archivo JPG o PNG?');
      });
  }

  /* --- almacenamiento --------------------------------------------------- */

  function subirArchivo(ruta, blob) {
    return HMA.token().then(function (t) {
      return fetch(HMA.BASE + '/storage/v1/object/obras/' + ruta, {
        method: 'POST',
        headers: {
          apikey: HMA.CLAVE,
          Authorization: 'Bearer ' + t,
          'Content-Type': 'image/webp',
          'x-upsert': 'false',
        },
        body: blob,
      }).then(function (r) {
        if (!r.ok) throw new Error('No pudimos subir la imagen.');
        return ruta;
      });
    });
  }

  function urlPublica(ruta) {
    if (/^@(seed|site):/.test(ruta || '')) {
      return ruta.replace(/^@(seed|site):/, '');
    }
    return HMA.BASE + '/storage/v1/object/public/obras/' + ruta;
  }

  /* Las obras anteriores al panel arrancan con una selección de fotos del
     sitio. Recién al primer cambio se marca esa selección como administrada:
     así el primer deploy no recorta una galería histórica sin intervención. */
  function activarGestion() {
    var heredadas = fotos.filter(function (f) {
      return /^@seed:/.test(f.storage_path || '');
    });
    if (!heredadas.length) return Promise.resolve();
    if (activando) return activando;

    activando = Promise.all(heredadas.map(function (f) {
      var nueva = f.storage_path.replace(/^@seed:/, '@site:');
      return rest('/obra_imagenes?id=eq.' + encodeURIComponent(f.id), {
        method: 'PATCH',
        body: { storage_path: nueva },
      }).then(function () { f.storage_path = nueva; });
    })).finally(function () { activando = null; });
    return activando;
  }

  function rest(ruta, opciones) {
    opciones = opciones || {};
    return HMA.token().then(function (t) {
      var cab = {
        apikey: HMA.CLAVE,
        Authorization: 'Bearer ' + t,
        'Content-Type': 'application/json',
      };
      if (opciones.devolver) cab.Prefer = 'return=representation';
      return fetch(HMA.BASE + '/rest/v1' + ruta, {
        method: opciones.method || 'GET',
        headers: cab,
        body: opciones.body ? JSON.stringify(opciones.body) : undefined,
      }).then(function (r) {
        return r.text().then(function (txt) {
          var datos = null;
          try { datos = txt ? JSON.parse(txt) : null; } catch (e) {}
          if (!r.ok) {
            var m = (datos && datos.message) || '';
            if (/15 imagenes/i.test(m)) m = 'La obra ya llegó a las 15 imágenes.';
            throw new Error(m || 'No pudimos guardar el cambio.');
          }
          return datos;
        });
      });
    });
  }

  /* --- pantalla --------------------------------------------------------- */

  function avisar(texto, tipo) {
    var el = $('avisoGaleria');
    el.textContent = texto || '';
    el.className = 'aviso' + (texto ? ' aviso--' + tipo : '');
  }

  function pintar() {
    var cont = $('grilla');
    cont.textContent = '';

    fotos.forEach(function (f, i) {
      var tarjeta = document.createElement('figure');
      tarjeta.className = 'foto' + (f.es_portada ? ' foto--portada' : '');
      tarjeta.draggable = true;
      tarjeta.dataset.indice = i;

      var img = document.createElement('img');
      img.src = urlPublica(f.storage_path);
      img.alt = f.alt || '';
      img.loading = 'lazy';
      tarjeta.appendChild(img);

      if (f.es_portada) {
        var sello = document.createElement('span');
        sello.className = 'foto__sello';
        sello.textContent = 'Portada';
        tarjeta.appendChild(sello);
      }

      var pie = document.createElement('figcaption');
      pie.className = 'foto__pie';

      /* Las flechas no son un adorno del arrastre: en el telefono arrastrar no
         funciona, y el estudio va a cargar obras desde el celular. */
      pie.appendChild(boton('‹', 'Mover antes', i === 0, function () {
        mover(i, i - 1);
      }));
      pie.appendChild(boton('›', 'Mover después', i === fotos.length - 1, function () {
        mover(i, i + 1);
      }));

      if (!f.es_portada) {
        pie.appendChild(boton('Portada', 'Usar como portada', false, function () {
          elegirPortada(f);
        }, 'foto__accion'));
      }

      pie.appendChild(boton('Eliminar', 'Eliminar la foto', false, function () {
        eliminar(f);
      }, 'foto__accion foto__accion--riesgo'));

      tarjeta.appendChild(pie);
      cont.appendChild(tarjeta);
    });

    $('conteoFotos').textContent = fotos.length
      ? fotos.length + ' de ' + TOPE + ' imágenes'
      : 'Todavía no hay fotos.';
    $('subir').disabled = fotos.length >= TOPE;
    $('ayudaTope').classList.toggle('oculto', fotos.length < TOPE);
  }

  function boton(texto, titulo, deshabilitado, alTocar, clase) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = clase || 'foto__flecha';
    b.textContent = texto;
    b.title = titulo;
    b.setAttribute('aria-label', titulo);
    b.disabled = !!deshabilitado;
    b.addEventListener('click', alTocar);
    return b;
  }

  /* --- orden ------------------------------------------------------------ */

  function mover(desde, hasta) {
    if (hasta < 0 || hasta >= fotos.length) return;
    var f = fotos.splice(desde, 1)[0];
    fotos.splice(hasta, 0, f);
    pintar();
    activarGestion().then(guardarOrden).catch(function (e) {
      avisar(e.message, 'error');
      cargar();
    });
  }

  /* Se graba solo lo que cambio de lugar: mover la ultima foto de 15 no tiene
     por que escribir las quince filas. */
  function guardarOrden() {
    var pendientes = [];
    fotos.forEach(function (f, i) {
      if (f.orden !== i) {
        f.orden = i;
        pendientes.push(rest('/obra_imagenes?id=eq.' + encodeURIComponent(f.id),
          { method: 'PATCH', body: { orden: i } }));
      }
    });
    if (!pendientes.length) return;
    avisar('Guardando el orden…', 'ok');
    Promise.all(pendientes).then(function () {
      avisar('Orden guardado.', 'ok');
    }).catch(function (e) {
      avisar(e.message, 'error');
    });
  }

  /* --- portada ---------------------------------------------------------- */

  /* La base tiene un indice unico de una portada por obra, asi que primero se
     saca la vieja y recien despues se marca la nueva: al reves, la segunda
     escritura choca contra la primera. */
  function elegirPortada(foto) {
    var anterior = fotos.filter(function (f) { return f.es_portada; })[0];
    avisar('Cambiando la portada…', 'ok');

    var paso = activarGestion().then(function () {
      return anterior
        ? rest('/obra_imagenes?id=eq.' + encodeURIComponent(anterior.id),
          { method: 'PATCH', body: { es_portada: false } })
        : Promise.resolve();
    });

    return paso.then(function () {
      return rest('/obra_imagenes?id=eq.' + encodeURIComponent(foto.id),
        { method: 'PATCH', body: { es_portada: true } });
    }).then(function () {
      fotos.forEach(function (f) { f.es_portada = (f.id === foto.id); });
      pintar();
      avisar('Portada cambiada.', 'ok');
    }).catch(function (e) {
      avisar(e.message, 'error');
      // Si marcar la nueva fallo despues de sacar la anterior, se intenta
      // restaurar la portada previa antes de recargar el estado real.
      var restaurar = anterior
        ? rest('/obra_imagenes?id=eq.' + encodeURIComponent(anterior.id),
          { method: 'PATCH', body: { es_portada: true } }).catch(function () {})
        : Promise.resolve();
      return restaurar.then(cargar);
    });
  }

  /* --- eliminar --------------------------------------------------------- */

  function eliminar(foto) {
    var puedeEliminar = fotos.length === 1
      ? rest('/obras?id=eq.' + encodeURIComponent(obraId) + '&select=publicada')
        .then(function (obras) {
          if (obras[0] && obras[0].publicada) {
            throw new Error(
              'Una obra publicada necesita al menos una foto. Despublicala antes de eliminar la última.'
            );
          }
        })
      : Promise.resolve();

    // Primero se saca la fila y despues el archivo. Si falla la limpieza del
    // bucket puede quedar un archivo huerfano para borrar mas tarde, pero la
    // pagina nunca queda apuntando a una imagen que ya no existe.
    puedeEliminar.then(function () {
      if (!window.confirm('¿Eliminar esta foto? No se puede deshacer.')) {
        throw { cancelada: true };
      }
      avisar('Eliminando…', 'ok');
      return activarGestion();
    }).then(function () {
      return rest('/obra_imagenes?id=eq.' + encodeURIComponent(foto.id),
        { method: 'DELETE' });
    }).then(function () {
      return DATOS.borrarArchivos([foto.storage_path]).catch(function () {
        // La baja visible ya termino. La limpieza del archivo no debe hacer
        // creer que la foto sigue en la galeria ni reintentar una fila borrada.
      });
    }).then(function () {
      fotos = fotos.filter(function (f) { return f.id !== foto.id; });
      // Si se borro la portada, la primera pasa a serlo: una obra sin portada
      // sale sin imagen en el listado del sitio.
      if (foto.es_portada && fotos.length) {
        return elegirPortada(fotos[0]);
      } else {
        pintar();
        guardarOrden();
        avisar('Foto eliminada.', 'ok');
      }
    }).catch(function (e) {
      if (e && e.cancelada) return;
      avisar(e.message, 'error');
    });
  }

  /* --- subir ------------------------------------------------------------ */

  function subir(archivos) {
    var lista = Array.prototype.slice.call(archivos)
      .filter(function (a) { return /^image\//.test(a.type); });
    if (!lista.length) return;

    var lugar = TOPE - fotos.length;
    var sobran = 0;
    if (lista.length > lugar) {
      sobran = lista.length - lugar;
      lista = lista.slice(0, lugar);
    }
    if (!lista.length) {
      avisar('La obra ya llegó a las ' + TOPE + ' imágenes.', 'error');
      return;
    }

    var hechas = 0;
    var fallos = [];
    $('subir').disabled = true;

    // De a una y no todas juntas: quince fotos en paralelo desde un telefono
    // saturan la subida y encima no se puede mostrar por donde va.
    var siguiente = function (i) {
      if (i >= lista.length) {
        $('subir').disabled = fotos.length >= TOPE;
        pintar();
        var texto = hechas + (hechas === 1 ? ' foto subida' : ' fotos subidas');
        if (sobran) texto += '. ' + sobran + ' quedaron afuera por el tope de ' + TOPE + '.';
        if (fallos.length) texto += ' No entraron: ' + fallos.join(', ') + '.';
        avisar(texto, fallos.length ? 'error' : 'ok');
        return;
      }

      var archivo = lista[i];
      avisar('Subiendo ' + (i + 1) + ' de ' + lista.length + '…', 'ok');

      var rutaSubida = null;
      activarGestion().then(function () {
        return optimizar(archivo);
      }).then(function (opt) {
        var ruta = obraId + '/' + Date.now() + '-' + Math.random().toString(36).slice(2, 8) + '.webp';
        return subirArchivo(ruta, opt.blob).then(function () {
          rutaSubida = ruta;
          return rest('/obra_imagenes', {
            method: 'POST',
            devolver: true,
            body: {
              obra_id: obraId,
              storage_path: ruta,
              orden: fotos.length,
              ancho: opt.ancho,
              alto: opt.alto,
              // La primera foto de una obra vacia queda de portada sola: si no,
              // la obra sale sin imagen en el listado hasta que alguien elija.
              es_portada: fotos.length === 0,
            },
          });
        });
      }).then(function (filas) {
        fotos.push(filas[0]);
        hechas++;
        pintar();
        siguiente(i + 1);
      }).catch(function (e) {
        var limpiar = rutaSubida
          ? DATOS.borrarArchivos([rutaSubida]).catch(function () {})
          : Promise.resolve();
        limpiar.then(function () {
          fallos.push(archivo.name + (e.message ? ' (' + e.message + ')' : ''));
          siguiente(i + 1);
        });
      });
    };

    siguiente(0);
  }

  /* --- arrastrar -------------------------------------------------------- */

  function conectarArrastre() {
    var cont = $('grilla');

    cont.addEventListener('dragstart', function (ev) {
      var t = ev.target.closest('.foto');
      if (!t) return;
      arrastrada = Number(t.dataset.indice);
      t.classList.add('foto--moviendo');
      ev.dataTransfer.effectAllowed = 'move';
      // Firefox no arranca el arrastre sin datos en el portapapeles.
      ev.dataTransfer.setData('text/plain', String(arrastrada));
    });

    cont.addEventListener('dragover', function (ev) {
      ev.preventDefault();
      ev.dataTransfer.dropEffect = 'move';
    });

    cont.addEventListener('drop', function (ev) {
      ev.preventDefault();
      var t = ev.target.closest('.foto');
      if (!t || arrastrada === null) return;
      var hasta = Number(t.dataset.indice);
      if (hasta !== arrastrada) mover(arrastrada, hasta);
      arrastrada = null;
    });

    cont.addEventListener('dragend', function () {
      var m = cont.querySelector('.foto--moviendo');
      if (m) m.classList.remove('foto--moviendo');
      arrastrada = null;
    });
  }

  /* --- arranque --------------------------------------------------------- */

  function cargar() {
    return DATOS.listarImagenes(obraId).then(function (lista) {
      fotos = lista || [];
      pintar();
    }).catch(function (e) {
      avisar(e.message, 'error');
    });
  }

  window.GALERIA = {
    iniciar: function (id) {
      obraId = id;
      $('galeria').classList.remove('oculto');
      $('galeriaSinObra').classList.add('oculto');

      $('subir').addEventListener('click', function () { $('archivos').click(); });
      $('archivos').addEventListener('change', function (ev) {
        subir(ev.target.files);
        ev.target.value = '';   // permite volver a elegir el mismo archivo
      });
      conectarArrastre();
      return cargar();
    },
  };
})();
