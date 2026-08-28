/* Tarjetas sociales del Inicio. Instagram se mantiene editorialmente desde
   aca; LinkedIn y YouTube usan estos datos solo si sus APIs no responden. */
(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };
  var REDES = [
    { id: 'instagram', nombre: 'Instagram', automatica: false },
    { id: 'linkedin', nombre: 'LinkedIn', automatica: null },
    { id: 'youtube', nombre: 'YouTube', automatica: true },
  ];
  var datos = {};

  var PREDETERMINADOS = {
    'home.instagram_titulo': ['Movistar Arena', 'Movistar Arena'],
    'home.instagram_texto': ['Nuestro proyecto VIP Lounge Movistar Arena fue distinguido con una Mención Especial en la categoría Commercial Interiors de los Architizer A+ Awards 2026.', 'Our VIP Lounge Movistar Arena project received a Special Mention in the Commercial Interiors category of the 2026 Architizer A+ Awards.'],
    'home.instagram_url': ['https://www.instagram.com/p/DYANnd0CXnT/', 'https://www.instagram.com/p/DYANnd0CXnT/'],
    'home.instagram_imagen': ['@site:/assets/covers/movistar-arena.webp', '@site:/assets/covers/movistar-arena.webp'],
    'home.linkedin_titulo': ['Aire Libre: arquitectura y naturaleza', 'Aire Libre: architecture and nature'],
    'home.linkedin_texto': ['Inspirado en los antiguos invernaderos ingleses, Aire Libre combina recursos industriales, vegetación y coctelería en más de 900 m².', 'Inspired by historic English greenhouses, Aire Libre combines industrial materials, vegetation and cocktail culture across more than 900 m².'],
    'home.linkedin_url': ['https://www.linkedin.com/posts/hitzig-militello-arquitectos_interiordesign-dise%C3%B1odeinteriores-architecture-activity-7311051799749128194-7TTX', 'https://www.linkedin.com/posts/hitzig-militello-arquitectos_interiordesign-dise%C3%B1odeinteriores-architecture-activity-7311051799749128194-7TTX'],
    'home.linkedin_imagen': ['@site:/assets/covers/aire-libre.webp', '@site:/assets/covers/aire-libre.webp'],
    'home.youtube_titulo': ['Entrevista con @LadrilloInfo', 'Interview with @LadrilloInfo'],
    'home.youtube_texto': ['Leonardo Militello y Fernando Hitzig cuentan cómo diseñan espacios que generan experiencia.', 'Leonardo Militello and Fernando Hitzig explain how they design experience-led spaces.'],
    'home.youtube_url': ['https://www.youtube.com/watch?v=EalBF9mvgRI', 'https://www.youtube.com/watch?v=EalBF9mvgRI'],
    'home.youtube_imagen': ['@site:/assets/video/podcast-ladrillo.webp', '@site:/assets/video/podcast-ladrillo.webp'],
  };

  function rest(ruta, opciones) {
    opciones = opciones || {};
    return HMA.token().then(function (token) {
      var headers = {
        apikey: HMA.CLAVE,
        Authorization: 'Bearer ' + token,
        'Content-Type': 'application/json',
      };
      if (opciones.prefer) headers.Prefer = opciones.prefer;
      return fetch(HMA.BASE + '/rest/v1' + ruta, {
        method: opciones.method || 'GET', headers: headers,
        body: opciones.body ? JSON.stringify(opciones.body) : undefined,
      }).then(function (r) {
        return r.text().then(function (texto) {
          var cuerpo = null;
          try { cuerpo = texto ? JSON.parse(texto) : null; } catch (e) {}
          if (!r.ok) throw new Error((cuerpo && cuerpo.message) || 'No pudimos guardar.');
          return cuerpo;
        });
      });
    });
  }

  function urlImagen(ruta) {
    if (!ruta) return '';
    if (/^@site:/.test(ruta)) return ruta.replace(/^@site:/, '');
    if (/^(data:|blob:|https?:)/.test(ruta)) return ruta;
    return HMA.BASE + '/storage/v1/object/public/obras/' + ruta;
  }

  function optimizar(archivo) {
    if (!/^image\/(jpeg|png|webp)$/.test(archivo.type) || archivo.size > 20 * 1024 * 1024) {
      return Promise.reject(new Error('Usá una imagen JPG, PNG o WebP de hasta 20 MB.'));
    }
    return createImageBitmap(archivo, { imageOrientation: 'from-image' }).then(function (bmp) {
      var escala = Math.min(1, 1800 / Math.max(bmp.width, bmp.height));
      var canvas = document.createElement('canvas');
      canvas.width = Math.round(bmp.width * escala);
      canvas.height = Math.round(bmp.height * escala);
      canvas.getContext('2d').drawImage(bmp, 0, 0, canvas.width, canvas.height);
      bmp.close();
      return new Promise(function (resolver, rechazar) {
        canvas.toBlob(function (blob) {
          if (!blob) return rechazar(new Error('No pudimos procesar la imagen.'));
          resolver(blob);
        }, 'image/webp', .84);
      });
    });
  }

  function subirImagen(red, archivo) {
    return optimizar(archivo).then(function (blob) {
      var ruta = 'home/' + red + '-' + Date.now() + '.webp';
      return HMA.token().then(function (token) {
        return fetch(HMA.BASE + '/storage/v1/object/obras/' + ruta, {
          method: 'POST',
          headers: { apikey: HMA.CLAVE, Authorization: 'Bearer ' + token,
            'Content-Type': 'image/webp', 'x-upsert': 'false' },
          body: blob,
        }).then(function (r) {
          if (!r.ok) throw new Error('No pudimos subir la imagen.');
          return ruta;
        });
      });
    });
  }

  function valor(clave, idioma) {
    var fila = datos[clave];
    if (fila && fila[idioma]) return fila[idioma];
    return (PREDETERMINADOS[clave] || ['', ''])[idioma === 'es' ? 0 : 1];
  }

  function campo(caja, etiqueta, tipo, id, valorInicial, ayuda) {
    var grupo = document.createElement('div');
    grupo.className = 'campo';
    var label = document.createElement('label');
    label.htmlFor = id;
    label.textContent = etiqueta;
    var control = tipo === 'textarea' ? document.createElement('textarea') : document.createElement('input');
    control.id = id;
    control.name = id;
    if (tipo === 'textarea') control.rows = 4;
    else control.type = tipo;
    control.value = valorInicial || '';
    grupo.appendChild(label);
    grupo.appendChild(control);
    if (ayuda) {
      var p = document.createElement('p');
      p.className = 'campo__ayuda';
      p.textContent = ayuda;
      grupo.appendChild(p);
    }
    caja.appendChild(grupo);
    return control;
  }

  function formulario(red) {
    var form = document.createElement('form');
    form.className = 'ficha novedad-form';
    form.dataset.red = red.id;
    var h = document.createElement('h2');
    h.className = 'ficha__titulo';
    h.textContent = red.nombre;
    form.appendChild(h);
    if (red.automatica !== false) {
      var nota = document.createElement('p');
      nota.className = 'campo__ayuda';
      nota.id = 'estado-' + red.id;
      nota.textContent = red.automatica
        ? 'Se actualiza automáticamente. Estos campos son el respaldo si el servicio externo no responde.'
        : 'Comprobando si la actualización automática está conectada…';
      form.appendChild(nota);
    } else {
      var manual = document.createElement('p');
      manual.className = 'campo__ayuda';
      manual.textContent = 'No se actualiza sola: cargá acá la publicación que querés mostrar y después publicá los cambios desde Obras.';
      form.appendChild(manual);
    }

    var base = 'home.' + red.id + '_';
    campo(form, 'Título', 'text', red.id + '-titulo-es', valor(base + 'titulo', 'es'), 'Recomendado: 4 a 12 palabras.');
    campo(form, 'Título en inglés', 'text', red.id + '-titulo-en', valor(base + 'titulo', 'en'));
    campo(form, 'Descripción', 'textarea', red.id + '-texto-es', valor(base + 'texto', 'es'), 'Una o dos oraciones; recomendado hasta 260 caracteres.');
    campo(form, 'Descripción en inglés', 'textarea', red.id + '-texto-en', valor(base + 'texto', 'en'));
    campo(form, 'Enlace de la publicación', 'url', red.id + '-url', valor(base + 'url', 'es'), 'Pegá el enlace de una publicación, no el perfil general.');

    var imagen = document.createElement('div');
    imagen.className = 'campo';
    imagen.innerHTML = '<label for="' + red.id + '-imagen">Imagen</label>'
      + '<input type="file" id="' + red.id + '-imagen" accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp">'
      + '<p class="campo__ayuda">Horizontal, mínimo 1600 × 900 px. El panel la convierte a WebP.</p>';
    var preview = document.createElement('img');
    preview.className = 'novedad-form__preview';
    preview.alt = 'Vista previa de ' + red.nombre;
    preview.src = urlImagen(valor(base + 'imagen', 'es'));
    imagen.appendChild(preview);
    form.appendChild(imagen);

    var acciones = document.createElement('div');
    acciones.className = 'acciones';
    var guardar = document.createElement('button');
    guardar.type = 'submit';
    guardar.className = 'boton boton--compacto';
    guardar.textContent = 'Guardar ' + red.nombre;
    acciones.appendChild(guardar);
    form.appendChild(acciones);
    form.addEventListener('submit', guardarRed);
    return form;
  }

  function fila(clave, rotulo, es, en, multilinea, orden) {
    return { clave: clave, seccion: 'novedades', rotulo: rotulo, es: es || null,
      en: en || null, multilinea: !!multilinea, orden: orden };
  }

  function guardarRed(ev) {
    ev.preventDefault();
    var form = ev.currentTarget;
    var red = form.dataset.red;
    var boton = form.querySelector('button[type="submit"]');
    var archivo = $(red + '-imagen').files[0];
    var rutaActual = valor('home.' + red + '_imagen', 'es');
    boton.disabled = true;
    boton.textContent = 'Guardando…';
    $('aviso').textContent = '';

    (archivo ? subirImagen(red, archivo) : Promise.resolve(rutaActual)).then(function (ruta) {
      var base = 'home.' + red + '_';
      var ordenBase = { instagram: 40, linkedin: 44, youtube: 48 }[red];
      var filas = [
        fila(base + 'titulo', red + ' — título', $(red + '-titulo-es').value.trim(), $(red + '-titulo-en').value.trim(), false, ordenBase),
        fila(base + 'texto', red + ' — descripción', $(red + '-texto-es').value.trim(), $(red + '-texto-en').value.trim(), true, ordenBase + 1),
        fila(base + 'url', red + ' — enlace', $(red + '-url').value.trim(), $(red + '-url').value.trim(), false, ordenBase + 2),
        fila(base + 'imagen', red + ' — imagen', ruta, ruta, false, ordenBase + 3),
      ];
      return rest('/textos?on_conflict=clave', { method: 'POST', body: filas,
        prefer: 'resolution=merge-duplicates,return=representation' });
    }).then(function (filas) {
      (filas || []).forEach(function (f) { datos[f.clave] = f; });
      boton.disabled = false;
      boton.textContent = 'Guardar ' + red.charAt(0).toUpperCase() + red.slice(1);
      $('aviso').textContent = 'Guardado. Publicá los cambios desde Obras para verlo en la web.';
      $('aviso').className = 'aviso aviso--ok';
    }).catch(function (e) {
      boton.disabled = false;
      boton.textContent = 'Guardar ' + red.charAt(0).toUpperCase() + red.slice(1);
      $('aviso').textContent = e.message;
      $('aviso').className = 'aviso aviso--error';
    });
  }

  function comprobarLinkedIn() {
    var estado = $('estado-linkedin');
    if (!estado) return;
    fetch('/api/linkedin-latest').then(function (respuesta) {
      if (!respuesta.ok) throw new Error();
      return respuesta.json();
    }).then(function (nota) {
      estado.textContent = nota && nota.automatic === true
        ? 'La conexión automática está activa. Estos campos son el respaldo si LinkedIn no responde.'
        : 'La conexión automática no está activa: LinkedIn se administra desde acá. Guardá la última publicación y publicá los cambios desde Obras.';
    }).catch(function () {
      estado.textContent = 'No se pudo comprobar la conexión. LinkedIn se administra desde acá hasta que el servicio vuelva a responder.';
    });
  }

  HMA.exigirSesion().then(function () {
    var sesion = HMA.sesion();
    $('quien').textContent = sesion && sesion.email ? sesion.email : '';
    $('salir').addEventListener('click', function () {
      HMA.salir().then(function () { location.replace('/admin/'); });
    });
    return rest('/textos?select=*&seccion=eq.novedades&order=orden.asc');
  }).then(function (filas) {
    (filas || []).forEach(function (f) { datos[f.clave] = f; });
    REDES.forEach(function (red) { $('formularios').appendChild(formulario(red)); });
    comprobarLinkedIn();
    $('cargando').classList.add('oculto');
    $('formularios').classList.remove('oculto');
  }).catch(function (e) {
    $('cargando').textContent = e.message || 'No pudimos cargar las novedades.';
  });
})();
