/* Publicaciones destacadas de Prensa. La tabla y el bucket siguen protegidos
   por las mismas reglas que Obras; esta pantalla solo ofrece la interfaz. */
(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var REST = HMA.BASE + '/rest/v1';
  var filas = [];
  var imagenes = [];
  var novedades = [];
  var pagina = 0;
  var paginaNovedades = 0;
  var POR_PAGINA = 24;

  function aviso(id, texto, tipo) {
    var el = $(id);
    el.textContent = texto || '';
    el.className = 'aviso' + (texto ? ' aviso--' + tipo : '');
  }

  function rest(ruta, opciones) {
    opciones = opciones || {};
    return HMA.token().then(function (token) {
      var cabeceras = {
        apikey: HMA.CLAVE,
        Authorization: 'Bearer ' + token,
        'Content-Type': 'application/json',
      };
      if (opciones.devolver) cabeceras.Prefer = 'return=representation';
      return fetch(REST + ruta, {
        method: opciones.method || 'GET',
        headers: cabeceras,
        body: opciones.body ? JSON.stringify(opciones.body) : undefined,
      }).then(function (r) {
        return r.text().then(function (texto) {
          var datos = null;
          try { datos = texto ? JSON.parse(texto) : null; } catch (e) {}
          if (!r.ok) {
            var mensaje = (datos && datos.message) || '';
            if (/prensa_(publicaciones|imagenes|novedades)/.test(mensaje)) {
              mensaje = 'Falta activar Conferencias y clases. En Supabase → SQL Editor, ejecutá completo 0017_aliases_y_novedades_prensa.sql.';
            }
            throw new Error(mensaje || 'No pudimos guardar la publicación.');
          }
          return datos;
        });
      });
    });
  }

  function slug(texto) {
    return (texto || '').toLowerCase().normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '').slice(0, 80);
  }

  /* Tres origenes posibles. @seed: es la seleccion heredada que siembra
     docs/prensa_galerias.py -el escaneo ya esta en el repositorio-, @site: es
     esa misma seleccion despues de que el estudio la toco, y el resto son
     archivos del Storage subidos desde aca. Los dos prefijos se resuelven
     igual: sacarlos deja la ruta del sitio. */
  function urlImagen(ruta) {
    if (!ruta) return '';
    if (/^(blob:|data:|https?:)/.test(ruta)) return ruta;
    if (/^@(site|seed):/.test(ruta)) return ruta.replace(/^@(site|seed):/, '');
    return HMA.BASE + '/storage/v1/object/public/obras/' + ruta;
  }

  function optimizar(archivo) {
    if (!/^image\/(jpeg|png|webp)$/.test(archivo.type) || archivo.size > 20 * 1024 * 1024) {
      return Promise.reject(new Error('Usá una imagen JPG, PNG o WebP de hasta 20 MB.'));
    }
    return createImageBitmap(archivo, { imageOrientation: 'from-image' }).then(function (bmp) {
      var escala = Math.min(1, 1800 / Math.max(bmp.width, bmp.height));
      var ancho = Math.round(bmp.width * escala);
      var alto = Math.round(bmp.height * escala);
      var canvas = document.createElement('canvas');
      canvas.width = ancho;
      canvas.height = alto;
      canvas.getContext('2d').drawImage(bmp, 0, 0, ancho, alto);
      bmp.close();
      return new Promise(function (resolver, rechazar) {
        canvas.toBlob(function (blob) {
          if (!blob) return rechazar(new Error('No pudimos procesar la imagen.'));
          resolver({ blob: blob, ancho: ancho, alto: alto });
        }, 'image/webp', .82);
      });
    });
  }

  function subirImagen(archivo) {
    return optimizar(archivo).then(function (opt) {
      var ruta = 'prensa/' + Date.now() + '-' + Math.random().toString(36).slice(2, 8) + '.webp';
      return HMA.token().then(function (token) {
        return fetch(HMA.BASE + '/storage/v1/object/obras/' + ruta, {
          method: 'POST',
          headers: {
            apikey: HMA.CLAVE,
            Authorization: 'Bearer ' + token,
            'Content-Type': 'image/webp',
            'x-upsert': 'false',
          },
          body: opt.blob,
        }).then(function (r) {
          if (!r.ok) throw new Error('No pudimos subir la imagen.');
          return ruta;
        });
      });
    });
  }

  function subirImagenInterna(archivo, publicacionId) {
    return optimizar(archivo).then(function (opt) {
      var ruta = 'prensa/' + publicacionId + '/' + Date.now() + '-'
        + Math.random().toString(36).slice(2, 8) + '.webp';
      return HMA.token().then(function (token) {
        return fetch(HMA.BASE + '/storage/v1/object/obras/' + ruta, {
          method: 'POST',
          headers: {
            apikey: HMA.CLAVE,
            Authorization: 'Bearer ' + token,
            'Content-Type': 'image/webp',
            'x-upsert': 'false',
          },
          body: opt.blob,
        }).then(function (r) {
          if (!r.ok) throw new Error('No pudimos subir la imagen.');
          return { ruta: ruta, ancho: opt.ancho, alto: opt.alto };
        });
      });
    });
  }

  /* Ni @site: ni @seed: viven en el Storage: son archivos del repositorio.
     Pedirle a Storage que borre "@seed:/assets/prensa/..." no borraria nada y
     ademas cortaria la cadena de eliminarImagen con un error. */
  function borrarImagen(ruta) {
    if (!ruta || /^@(site|seed):/.test(ruta)) return Promise.resolve();
    return HMA.token().then(function (token) {
      return fetch(HMA.BASE + '/storage/v1/object/obras', {
        method: 'DELETE',
        headers: {
          apikey: HMA.CLAVE,
          Authorization: 'Bearer ' + token,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prefixes: [ruta] }),
      });
    });
  }

  function pintarPreview(ruta) {
    var caja = $('previewPrensa');
    caja.textContent = '';
    if (!ruta) return caja.classList.add('oculto');
    var img = document.createElement('img');
    img.src = urlImagen(ruta);
    img.alt = 'Vista previa de la portada';
    caja.appendChild(img);
    caja.classList.remove('oculto');
  }

  function botonImagen(texto, titulo, deshabilitado, alTocar, clase) {
    var boton = document.createElement('button');
    boton.type = 'button';
    boton.className = clase || 'foto__flecha';
    boton.textContent = texto;
    boton.title = titulo;
    boton.setAttribute('aria-label', titulo);
    boton.disabled = !!deshabilitado;
    boton.addEventListener('click', alTocar);
    return boton;
  }

  function pintarImagenes() {
    var grilla = $('grillaPrensaGaleria');
    grilla.textContent = '';
    imagenes.forEach(function (fila, indice) {
      var tarjeta = document.createElement('figure');
      tarjeta.className = 'foto';
      var img = document.createElement('img');
      img.src = urlImagen(fila.storage_path);
      img.alt = fila.alt || 'Imagen de la publicación';
      img.loading = 'lazy';
      tarjeta.appendChild(img);
      if (fila.ancho && fila.alto) {
        var datos = document.createElement('span');
        datos.className = 'foto__datos';
        datos.textContent = fila.ancho + ' × ' + fila.alto + ' px';
        tarjeta.appendChild(datos);
      }
      var pie = document.createElement('figcaption');
      pie.className = 'foto__pie';
      pie.appendChild(botonImagen('‹', 'Mover antes', indice === 0, function () {
        moverImagen(indice, indice - 1);
      }));
      pie.appendChild(botonImagen('›', 'Mover después', indice === imagenes.length - 1, function () {
        moverImagen(indice, indice + 1);
      }));
      pie.appendChild(botonImagen('Eliminar', 'Eliminar esta imagen', false, function () {
        eliminarImagen(fila);
      }, 'foto__accion foto__accion--riesgo'));
      tarjeta.appendChild(pie);
      grilla.appendChild(tarjeta);
    });
    $('conteoPrensaGaleria').textContent = imagenes.length
      ? imagenes.length + ' imágenes' : 'Todavía no hay imágenes internas.';
  }

  function cargarImagenes(publicacionId) {
    imagenes = [];
    if (!publicacionId) {
      $('prensaGaleria').classList.add('oculto');
      $('prensaGaleriaSinGuardar').classList.remove('oculto');
      pintarImagenes();
      return Promise.resolve();
    }
    $('prensaGaleria').classList.remove('oculto');
    $('prensaGaleriaSinGuardar').classList.add('oculto');
    return rest('/prensa_imagenes?select=*&publicacion_id=eq.'
      + encodeURIComponent(publicacionId) + '&order=orden.asc,created_at.asc')
      .then(function (datos) {
        imagenes = datos || [];
        pintarImagenes();
      }).catch(function (e) {
        aviso('avisoPrensaGaleria', e.message, 'error');
      });
  }

  /* Igual que en las galerias de obra: la seleccion heredada se marca como
     administrada recien al primer cambio. Mientras siga entera en @seed:,
     panel_prensa.py publica los escaneos del repositorio y no toca nada, asi
     que un deploy no recorta una galeria historica sin que nadie la haya
     tocado. Cuando el estudio mueve, borra o agrega algo, estas filas pasan a
     @site: y desde ese momento manda la base. */
  var activando = null;

  function activarGestion() {
    var heredadas = imagenes.filter(function (f) {
      return /^@seed:/.test(f.storage_path || '');
    });
    if (!heredadas.length) return Promise.resolve();
    if (activando) return activando;

    activando = Promise.all(heredadas.map(function (f) {
      var nueva = f.storage_path.replace(/^@seed:/, '@site:');
      return rest('/prensa_imagenes?id=eq.' + encodeURIComponent(f.id), {
        method: 'PATCH', body: { storage_path: nueva },
      }).then(function () { f.storage_path = nueva; });
    })).then(function () { activando = null; }, function (e) {
      activando = null;
      throw e;
    });
    return activando;
  }

  function moverImagen(desde, hasta) {
    if (hasta < 0 || hasta >= imagenes.length) return;
    var movida = imagenes.splice(desde, 1)[0];
    imagenes.splice(hasta, 0, movida);
    pintarImagenes();
    aviso('avisoPrensaGaleria', 'Guardando el orden…', 'ok');
    activarGestion().then(function () {
      return Promise.all(imagenes.map(function (fila, indice) {
        fila.orden = indice;
        return rest('/prensa_imagenes?id=eq.' + encodeURIComponent(fila.id), {
          method: 'PATCH', body: { orden: indice },
        });
      }));
    }).then(function () {
      aviso('avisoPrensaGaleria', 'Orden guardado.', 'ok');
    }).catch(function (e) {
      aviso('avisoPrensaGaleria', e.message, 'error');
      cargarImagenes($('publicacionId').value);
    });
  }

  function eliminarImagen(fila) {
    if (!confirm('¿Eliminar esta imagen? No se puede deshacer.')) return;
    activarGestion()
      .then(function () {
        return rest('/prensa_imagenes?id=eq.' + encodeURIComponent(fila.id),
          { method: 'DELETE' });
      })
      .then(function () { return borrarImagen(fila.storage_path); })
      .then(function () { return cargarImagenes($('publicacionId').value); })
      .then(function () { aviso('avisoPrensaGaleria', 'Imagen eliminada.', 'ok'); })
      .catch(function (e) { aviso('avisoPrensaGaleria', e.message, 'error'); });
  }

  function agregarImagenes(archivos) {
    var publicacionId = $('publicacionId').value;
    if (!publicacionId || !archivos.length) return;
    var fallos = [];
    // Subir una imagen tambien es tocar la galeria: las heredadas pasan a
    // @site: antes de sumar nada, para que la nota quede administrada entera y
    // no mitad en el repositorio y mitad en la base.
    var cadena = activarGestion();
    Array.prototype.forEach.call(archivos, function (archivo) {
      cadena = cadena.then(function () {
        aviso('avisoPrensaGaleria', 'Optimizando ' + archivo.name + '…', 'ok');
        var subida;
        return subirImagenInterna(archivo, publicacionId).then(function (datos) {
          subida = datos;
          return rest('/prensa_imagenes', {
            method: 'POST', devolver: true,
            body: {
              publicacion_id: publicacionId,
              storage_path: datos.ruta,
              alt: $('titulo').value.trim() + ' — imagen ' + (imagenes.length + 1),
              orden: imagenes.length,
              ancho: datos.ancho,
              alto: datos.alto,
            },
          });
        }).catch(function (e) {
          if (subida) borrarImagen(subida.ruta).catch(function () {});
          fallos.push(archivo.name + ': ' + e.message);
        }).then(function () { return cargarImagenes(publicacionId); });
      });
    });
    cadena.then(function () {
      aviso('avisoPrensaGaleria', fallos.length
        ? 'No se pudieron cargar: ' + fallos.join(', ')
        : 'Imágenes guardadas. Publicá los cambios desde Obras.', fallos.length ? 'error' : 'ok');
    });
  }

  function pintarLista() {
    var lista = $('listaPrensa');
    var consulta = (($('buscarPrensa') && $('buscarPrensa').value) || '')
      .toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim();
    lista.textContent = '';
    if (!filas.length) {
      lista.textContent = 'Todavía no hay publicaciones cargadas.';
      return;
    }
    var visibles = filas.filter(function (fila) {
      if (!consulta) return true;
      return [fila.titulo, fila.medio, fila.pais, fila.fecha, fila.obra]
        .join(' ').toLowerCase().normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '').indexOf(consulta) !== -1;
    });
    if (!visibles.length) {
      lista.textContent = 'No hay publicaciones que coincidan con la búsqueda.';
      return;
    }
    var paginas = Math.max(1, Math.ceil(visibles.length / POR_PAGINA));
    pagina = Math.min(pagina, paginas - 1);
    var desde = pagina * POR_PAGINA;
    visibles.slice(desde, desde + POR_PAGINA).forEach(function (fila) {
      var boton = document.createElement('button');
      boton.type = 'button';
      boton.className = 'prensa-admin-item';
      boton.setAttribute('aria-label', 'Editar publicación: ' + fila.titulo);

      var miniatura = document.createElement('span');
      miniatura.className = 'prensa-admin-item__miniatura';
      var sinImagen = document.createElement('span');
      sinImagen.className = 'prensa-admin-item__sin-imagen';
      sinImagen.textContent = 'Sin imagen';
      if (fila.storage_path) {
        var img = document.createElement('img');
        img.src = urlImagen(fila.storage_path);
        img.alt = '';
        img.loading = 'lazy';
        img.addEventListener('error', function () {
          img.remove();
          miniatura.appendChild(sinImagen);
        }, { once: true });
        miniatura.appendChild(img);
      } else {
        miniatura.appendChild(sinImagen);
      }
      boton.appendChild(miniatura);

      var publicacion = document.createElement('span');
      publicacion.className = 'prensa-admin-item__publicacion';
      var fuerte = document.createElement('strong');
      fuerte.textContent = fila.titulo;
      var detalle = document.createElement('small');
      detalle.textContent = [fila.pais, fila.obra ? 'Obra: ' + fila.obra : '']
        .filter(Boolean).join(' · ') || fila.slug;
      publicacion.appendChild(fuerte);
      publicacion.appendChild(detalle);
      boton.appendChild(publicacion);

      var medio = document.createElement('span');
      medio.className = 'prensa-admin-item__dato';
      medio.dataset.rotulo = 'Medio';
      medio.textContent = fila.medio || '—';
      boton.appendChild(medio);

      var fecha = document.createElement('span');
      fecha.className = 'prensa-admin-item__dato';
      fecha.dataset.rotulo = 'Fecha';
      fecha.textContent = fila.fecha || '—';
      boton.appendChild(fecha);

      var estado = document.createElement('span');
      estado.className = 'chip ' + (fila.publicada ? 'chip--vive' : 'chip--borrador');
      estado.textContent = fila.publicada ? 'Publicada' : 'Borrador';
      boton.appendChild(estado);
      boton.addEventListener('click', function () { editar(fila); });
      lista.appendChild(boton);
    });
    $('paginaActual').textContent = 'Página ' + (pagina + 1) + ' de ' + paginas;
    $('paginaAnterior').disabled = pagina === 0;
    $('paginaSiguiente').disabled = pagina >= paginas - 1;
  }

  function limpiar() {
    $('formPrensa').reset();
    $('publicacionId').value = '';
    $('storagePath').value = '';
    $('orden').value = filas.length;
    $('publicada').checked = true;
    $('formTitulo').textContent = 'Nueva publicación';
    $('eliminar').classList.add('oculto');
    pintarPreview('');
    cargarImagenes('');
    aviso('avisoForm', '', 'ok');
    $('formPrensa').classList.remove('oculto');
    $('titulo').focus();
  }

  function editar(fila) {
    ['id', 'titulo', 'medio', 'pais', 'fecha', 'link', 'obra', 'slug', 'orden'].forEach(function (campo) {
      var id = campo === 'id' ? 'publicacionId' : campo;
      $(id).value = fila[campo] == null ? '' : fila[campo];
    });
    $('storagePath').value = fila.storage_path || '';
    $('publicada').checked = !!fila.publicada;
    $('formTitulo').textContent = 'Editar publicación';
    $('eliminar').classList.remove('oculto');
    pintarPreview(fila.storage_path);
    cargarImagenes(fila.id);
    $('formPrensa').classList.remove('oculto');
    aviso('avisoForm', '', 'ok');
    $('formPrensa').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function datosFormulario(ruta) {
    return {
      titulo: $('titulo').value.trim(),
      medio: $('medio').value.trim(),
      pais: $('pais').value.trim() || null,
      fecha: $('fecha').value.trim() || null,
      link: $('link').value.trim() || null,
      obra: $('obra').value.trim() || null,
      slug: $('slug').value.trim(),
      orden: Number($('orden').value) || 0,
      publicada: $('publicada').checked,
      storage_path: ruta || null,
    };
  }

  function guardar(ev) {
    ev.preventDefault();
    var id = $('publicacionId').value;
    var anterior = $('storagePath').value;
    var archivo = $('imagenPrensa').files[0];
    if (!archivo && !anterior) return aviso('avisoForm', 'Elegí una imagen de portada.', 'error');
    $('guardar').disabled = true;
    aviso('avisoForm', archivo ? 'Optimizando y subiendo la portada…' : 'Guardando…', 'ok');
    var nuevaRuta = anterior;
    (archivo ? subirImagen(archivo) : Promise.resolve(anterior)).then(function (ruta) {
      nuevaRuta = ruta;
      var cuerpo = datosFormulario(ruta);
      return rest('/prensa_publicaciones' + (id ? '?id=eq.' + encodeURIComponent(id) : ''), {
        method: id ? 'PATCH' : 'POST', body: cuerpo, devolver: true,
      });
    }).then(function (guardadas) {
      var guardada = guardadas && guardadas[0];
      if (guardada) {
        $('publicacionId').value = guardada.id;
        $('storagePath').value = guardada.storage_path || nuevaRuta;
        $('formTitulo').textContent = 'Editar publicación';
        $('eliminar').classList.remove('oculto');
      }
      if (archivo && anterior && anterior !== nuevaRuta) borrarImagen(anterior).catch(function () {});
      aviso('avisoForm', 'Guardado. Publicalo desde la pantalla Obras.', 'ok');
      return Promise.all([cargar(), cargarImagenes($('publicacionId').value)]);
    }).catch(function (e) {
      if (archivo && nuevaRuta !== anterior) borrarImagen(nuevaRuta).catch(function () {});
      aviso('avisoForm', e.message, 'error');
    }).finally(function () { $('guardar').disabled = false; });
  }

  function eliminar() {
    var id = $('publicacionId').value;
    if (!id || !confirm('¿Eliminar esta publicación? No se puede deshacer.')) return;
    var ruta = $('storagePath').value;
    var rutasInternas = imagenes.map(function (fila) { return fila.storage_path; });
    rest('/prensa_publicaciones?id=eq.' + encodeURIComponent(id), { method: 'DELETE' })
      .then(function () {
        return Promise.all([borrarImagen(ruta)].concat(rutasInternas.map(borrarImagen)));
      })
      .then(function () { limpiar(); return cargar(); })
      .catch(function (e) { aviso('avisoForm', e.message, 'error'); });
  }

  function cargar() {
    return rest('/prensa_publicaciones?select=*&order=orden.asc,created_at.desc').then(function (datos) {
      filas = datos || [];
      pintarLista();
      $('cantidadPublicaciones').textContent = '(' + filas.length + ')';
      aviso('avisoLista', filas.length + ' publicaciones cargadas.', 'ok');
    }).catch(function (e) { aviso('avisoLista', e.message, 'error'); });
  }

  function cambiarTab(novedad) {
    $('tabPublicaciones').classList.toggle('oculto', novedad);
    $('tabNovedades').classList.toggle('oculto', !novedad);
    $('abrirPublicaciones').classList.toggle('activa', !novedad);
    $('abrirNovedades').classList.toggle('activa', novedad);
    $('abrirPublicaciones').setAttribute('aria-selected', String(!novedad));
    $('abrirNovedades').setAttribute('aria-selected', String(novedad));
  }

  function pintarNovedades() {
    var lista = $('listaNovedades');
    var consulta = $('buscarNovedades').value.toLowerCase().normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '').trim();
    lista.textContent = '';
    var visibles = novedades.filter(function (fila) {
      if (fila.eliminada) return false;
      if (!consulta) return true;
      return [fila.rubro, fila.titulo, fila.detalle, fila.anio].join(' ')
        .toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        .indexOf(consulta) !== -1;
    });
    if (!visibles.length) {
      lista.textContent = 'No hay novedades que coincidan con la búsqueda.';
      $('novedadesPaginaActual').textContent = '';
      $('novedadesAnterior').disabled = true;
      $('novedadesSiguiente').disabled = true;
      return;
    }
    var paginas = Math.max(1, Math.ceil(visibles.length / POR_PAGINA));
    paginaNovedades = Math.min(paginaNovedades, paginas - 1);
    var desde = paginaNovedades * POR_PAGINA;
    visibles.slice(desde, desde + POR_PAGINA).forEach(function (fila) {
      var boton = document.createElement('button');
      boton.type = 'button';
      boton.className = 'prensa-admin-item';

      var anio = document.createElement('span');
      anio.className = 'prensa-admin-item__anio';
      anio.textContent = fila.anio || '—';
      boton.appendChild(anio);

      var texto = document.createElement('span');
      texto.className = 'prensa-admin-item__publicacion';
      var fuerte = document.createElement('strong');
      fuerte.textContent = fila.detalle || fila.titulo;
      var chico = document.createElement('small');
      chico.textContent = fila.titulo || '';
      texto.appendChild(fuerte);
      texto.appendChild(chico);
      boton.appendChild(texto);

      var rubro = document.createElement('span');
      rubro.className = 'prensa-admin-item__dato';
      rubro.dataset.rotulo = 'Rubro';
      rubro.textContent = fila.rubro || '—';
      boton.appendChild(rubro);

      var estado = document.createElement('span');
      estado.className = 'chip ' + (fila.publicada ? 'chip--vive' : 'chip--borrador');
      estado.textContent = fila.publicada ? 'Publicada' : 'Borrador';
      boton.appendChild(estado);
      boton.addEventListener('click', function () { editarNovedad(fila); });
      lista.appendChild(boton);
    });
    $('novedadesPaginaActual').textContent = 'Página ' + (paginaNovedades + 1) + ' de ' + paginas;
    $('novedadesAnterior').disabled = paginaNovedades === 0;
    $('novedadesSiguiente').disabled = paginaNovedades >= paginas - 1;
  }

  function nuevaNovedad() {
    $('formNovedad').reset();
    $('novedadId').value = '';
    $('novedadOrden').value = novedades.length;
    $('novedadPublicada').checked = true;
    $('formNovedadTitulo').textContent = 'Nueva novedad';
    $('eliminarNovedad').classList.add('oculto');
    $('formNovedad').classList.remove('oculto');
    aviso('avisoFormNovedad', '', 'ok');
    $('novedadTituloCampo').focus();
  }

  function editarNovedad(fila) {
    $('novedadId').value = fila.id;
    $('novedadRubro').value = fila.rubro || 'CONFERENCIA';
    $('novedadAnio').value = fila.anio || '';
    $('novedadTituloCampo').value = fila.titulo || '';
    $('novedadDetalle').value = fila.detalle || '';
    $('novedadLink').value = fila.link || '';
    $('novedadOrden').value = fila.orden || 0;
    $('novedadPublicada').checked = !!fila.publicada;
    $('formNovedadTitulo').textContent = 'Editar novedad';
    $('eliminarNovedad').classList.remove('oculto');
    $('formNovedad').classList.remove('oculto');
    aviso('avisoFormNovedad', '', 'ok');
    $('formNovedad').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function guardarNovedad(ev) {
    ev.preventDefault();
    var idNovedad = $('novedadId').value;
    var titulo = $('novedadTituloCampo').value.trim();
    var detalle = $('novedadDetalle').value.trim();
    var anio = $('novedadAnio').value.trim();
    if (!titulo || !detalle || !/^\d{4}$/.test(anio)) {
      return aviso('avisoFormNovedad', 'Completá título, texto y un año de cuatro cifras.', 'error');
    }
    var cuerpo = {
      rubro: $('novedadRubro').value,
      titulo: titulo,
      detalle: detalle,
      anio: anio,
      link: $('novedadLink').value.trim() || null,
      orden: Number($('novedadOrden').value) || 0,
      publicada: $('novedadPublicada').checked,
      eliminada: false,
    };
    if (!idNovedad) cuerpo.clave = slug(anio + '-' + titulo) + '-' + Date.now().toString(36);
    $('guardarNovedad').disabled = true;
    aviso('avisoFormNovedad', 'Guardando…', 'ok');
    rest('/prensa_novedades' + (idNovedad ? '?id=eq.' + encodeURIComponent(idNovedad) : ''), {
      method: idNovedad ? 'PATCH' : 'POST', body: cuerpo, devolver: true,
    }).then(function () {
      aviso('avisoFormNovedad', 'Guardado. Publicalo desde Obras.', 'ok');
      return cargarNovedades();
    }).catch(function (e) {
      aviso('avisoFormNovedad', e.message, 'error');
    }).finally(function () { $('guardarNovedad').disabled = false; });
  }

  function eliminarNovedad() {
    var idNovedad = $('novedadId').value;
    if (!idNovedad || !confirm('¿Eliminar esta novedad? No aparecerá en el sitio.')) return;
    rest('/prensa_novedades?id=eq.' + encodeURIComponent(idNovedad), {
      method: 'PATCH', body: { eliminada: true, publicada: false },
    }).then(function () {
      $('formNovedad').classList.add('oculto');
      return cargarNovedades();
    }).catch(function (e) { aviso('avisoFormNovedad', e.message, 'error'); });
  }

  function cargarNovedades() {
    return rest('/prensa_novedades?select=*&eliminada=is.false&order=orden.asc,created_at.asc')
      .then(function (datos) {
        novedades = datos || [];
        pintarNovedades();
        $('cantidadNovedades').textContent = '(' + novedades.length + ')';
        aviso('avisoNovedades', novedades.length + ' novedades cargadas.', 'ok');
      }).catch(function (e) {
        novedades = [];
        $('cantidadNovedades').textContent = '';
        aviso('avisoNovedades', e.message, 'error');
      });
  }

  HMA.exigirSesion().then(function () {
    var sesion = HMA.sesion();
    $('quien').textContent = sesion && sesion.email ? sesion.email : '';
    $('salir').addEventListener('click', function () {
      HMA.salir().then(function () { location.replace('/admin/'); });
    });
    $('nueva').addEventListener('click', limpiar);
    $('buscarPrensa').addEventListener('input', function () { pagina = 0; pintarLista(); });
    $('paginaAnterior').addEventListener('click', function () { pagina--; pintarLista(); });
    $('paginaSiguiente').addEventListener('click', function () { pagina++; pintarLista(); });
    $('abrirPublicaciones').addEventListener('click', function () { cambiarTab(false); });
    $('abrirNovedades').addEventListener('click', function () { cambiarTab(true); });
    $('nuevaNovedad').addEventListener('click', nuevaNovedad);
    $('buscarNovedades').addEventListener('input', function () {
      paginaNovedades = 0;
      pintarNovedades();
    });
    $('novedadesAnterior').addEventListener('click', function () {
      paginaNovedades--;
      pintarNovedades();
    });
    $('novedadesSiguiente').addEventListener('click', function () {
      paginaNovedades++;
      pintarNovedades();
    });
    $('formNovedad').addEventListener('submit', guardarNovedad);
    $('eliminarNovedad').addEventListener('click', eliminarNovedad);
    $('formPrensa').addEventListener('submit', guardar);
    $('eliminar').addEventListener('click', eliminar);
    $('titulo').addEventListener('input', function () {
      if (!$('publicacionId').value) $('slug').value = slug($('titulo').value);
    });
    $('imagenPrensa').addEventListener('change', function () {
      var archivo = $('imagenPrensa').files[0];
      if (archivo) pintarPreview(URL.createObjectURL(archivo));
    });
    $('subirPrensaGaleria').addEventListener('click', function () {
      $('archivosPrensaGaleria').click();
    });
    $('archivosPrensaGaleria').addEventListener('change', function (ev) {
      agregarImagenes(ev.target.files);
      ev.target.value = '';
    });
    return Promise.all([cargar(), cargarNovedades()]);
  }).catch(function () {});
})();
