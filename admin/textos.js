/* Textos de las secciones fijas: home, estudio y contacto.

   Cada texto se guarda solo, con su propio boton. No hay un "guardar todo" a
   proposito: son once campos en dos idiomas y un guardado unico obligaria a
   revisar los veintidos para entender que fallo si uno se rechaza. */

(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };

  var TITULOS = {
    home: 'Portada',
    estudio: 'Estudio',
    contacto: 'Contacto',
  };

  var GUIAS = {
    'home.titular': {
      hasta: 60,
      ayuda: 'Frase principal sobre el video del home. Recomendado: 3 a 7 palabras.',
    },
    'home.bajada': {
      hasta: 260,
      ayuda: 'Presentación breve del estudio. Recomendado: una o dos oraciones.',
    },
    'estudio.eyebrow': {
      hasta: 60,
      ayuda: 'Línea pequeña sobre el título. Ejemplo: Desde 2006 — Buenos Aires.',
    },
    'estudio.titular': {
      hasta: 70,
      ayuda: 'Título principal de la página Estudio.',
    },
    'estudio.presentacion': {
      hasta: 500,
      ayuda: 'Resumen institucional. Recomendado: 60 a 90 palabras.',
    },
    'contacto.titular': {
      hasta: 70,
      ayuda: 'Título principal de Contacto. Recomendado: 3 a 7 palabras.',
    },
    'contacto.direccion': {
      hasta: 180,
      ayuda: 'Dirección pública. Usá una línea para la calle y otra para ciudad y país.',
    },
    'contacto.telefonos': {
      hasta: 120,
      ayuda: 'Un teléfono por línea, siempre con código de país.',
    },
    'estudio.bloque1': {
      hasta: 500,
      ayuda: 'Texto de Diseño integral. Recomendado: 35 a 70 palabras.',
    },
    'estudio.bloque2': {
      hasta: 500,
      ayuda: 'Texto de Identidad. Recomendado: 35 a 70 palabras.',
    },
    'estudio.bloque3': {
      hasta: 500,
      ayuda: 'Texto de ADN. Recomendado: 35 a 70 palabras.',
    },
  };

  function avisar(texto, tipo) {
    var el = $('aviso');
    el.textContent = texto || '';
    el.className = 'aviso' + (texto ? ' aviso--' + tipo : '');
  }

  function rest(ruta, opciones) {
    opciones = opciones || {};
    return HMA.token().then(function (t) {
      return fetch(HMA.BASE + '/rest/v1' + ruta, {
        method: opciones.method || 'GET',
        headers: {
          apikey: HMA.CLAVE,
          Authorization: 'Bearer ' + t,
          'Content-Type': 'application/json',
        },
        body: opciones.body ? JSON.stringify(opciones.body) : undefined,
      }).catch(function () {
        throw new Error('No pudimos conectar con el servidor.');
      }).then(function (r) {
        return r.text().then(function (txt) {
          var datos = null;
          try { datos = txt ? JSON.parse(txt) : null; } catch (e) {}
          if (!r.ok) {
            throw new Error((datos && datos.message) || 'No pudimos guardar.');
          }
          return datos;
        });
      });
    });
  }

  /* --- pantalla --------------------------------------------------------- */

  function campo(t) {
    var caja = document.createElement('div');
    caja.className = 'texto';

    var rot = document.createElement('label');
    rot.textContent = t.rotulo;
    rot.htmlFor = 'es-' + t.clave;
    caja.appendChild(rot);

    var es = control(t, 'es');
    caja.appendChild(es);
    caja.appendChild(ayudaCampo(t, es, false));

    /* El ingles va junto al castellano y no en otra pantalla: si estuvieran
       separados, cambiar uno y olvidarse del otro seria lo normal, y el sitio
       tiene espejo completo en ingles. */
    var rotEn = document.createElement('label');
    rotEn.className = 'texto__rotulo-en';
    rotEn.textContent = 'En inglés';
    rotEn.htmlFor = 'en-' + t.clave;
    caja.appendChild(rotEn);

    var en = control(t, 'en');
    caja.appendChild(en);
    caja.appendChild(ayudaCampo(t, en, true));

    var pie = document.createElement('div');
    pie.className = 'texto__pie';

    var guardar = document.createElement('button');
    guardar.type = 'button';
    guardar.className = 'boton boton--compacto';
    guardar.textContent = 'Guardar';
    guardar.disabled = true;

    var estado = document.createElement('span');
    estado.className = 'aviso';

    var marcarCambio = function () {
      guardar.disabled = (es.value === (t.es || '') && en.value === (t.en || ''));
      estado.textContent = '';
      estado.className = 'aviso';
    };
    es.addEventListener('input', marcarCambio);
    en.addEventListener('input', marcarCambio);

    guardar.addEventListener('click', function () {
      guardar.disabled = true;
      guardar.textContent = 'Guardando…';
      estado.textContent = '';

      rest('/textos?clave=eq.' + encodeURIComponent(t.clave), {
        method: 'PATCH',
        body: { es: es.value || null, en: en.value || null },
      }).then(function () {
        t.es = es.value;
        t.en = en.value;
        guardar.textContent = 'Guardar';
        estado.textContent = 'Guardado.';
        estado.className = 'aviso aviso--ok';
      }).catch(function (e) {
        guardar.disabled = false;
        guardar.textContent = 'Guardar';
        estado.textContent = e.message;
        estado.className = 'aviso aviso--error';
      });
    });

    pie.appendChild(guardar);
    pie.appendChild(estado);
    caja.appendChild(pie);
    return caja;
  }

  function control(t, idioma) {
    var el;
    if (t.multilinea) {
      el = document.createElement('textarea');
      el.rows = Math.min(8, Math.max(2, ((t[idioma] || '').length / 90) | 0) + 2);
    } else {
      el = document.createElement('input');
      el.type = 'text';
    }
    el.id = idioma + '-' + t.clave;
    el.value = t[idioma] || '';
    return el;
  }

  function ayudaCampo(t, control, ingles) {
    var guia = GUIAS[t.clave] || { hasta: 500, ayuda: 'Texto visible en el sitio.' };
    var ayuda = document.createElement('p');
    ayuda.className = 'campo__ayuda texto__ayuda';

    var actualizar = function () {
      var n = control.value.length;
      ayuda.textContent = (ingles ? 'Mismo contenido, traducido al inglés. ' : guia.ayuda + ' ')
        + n + ' caracteres; recomendado hasta ' + guia.hasta + '.';
      ayuda.classList.toggle('texto__ayuda--alerta', n > guia.hasta);
    };
    control.addEventListener('input', actualizar);
    actualizar();
    return ayuda;
  }

  function pintar(textos) {
    var cont = $('secciones');
    cont.textContent = '';

    ['home', 'estudio', 'contacto'].forEach(function (seccion) {
      var propios = textos.filter(function (t) { return t.seccion === seccion; });
      if (!propios.length) return;

      var caja = document.createElement('section');
      caja.className = 'ficha';

      var titulo = document.createElement('h2');
      titulo.className = 'ficha__titulo';
      titulo.textContent = TITULOS[seccion] || seccion;
      caja.appendChild(titulo);

      propios.forEach(function (t) { caja.appendChild(campo(t)); });
      cont.appendChild(caja);
    });

    if (!cont.children.length) {
      cont.innerHTML = '';
      var vacio = document.createElement('p');
      vacio.className = 'vacio';
      vacio.textContent = 'Todavía no hay textos cargados en la base.';
      cont.appendChild(vacio);
    }
  }

  /* --- arranque --------------------------------------------------------- */

  HMA.exigirSesion().then(function () {
    var s = HMA.sesion();
    $('quien').textContent = s && s.email ? s.email : '';
    $('salir').addEventListener('click', function () {
      HMA.salir().then(function () { location.replace('/admin/'); });
    });

    return rest('/textos?select=*&order=seccion.asc,orden.asc');
  }).then(function (textos) {
    $('cargando').classList.add('oculto');
    pintar(textos || []);
  }).catch(function (e) {
    $('cargando').classList.add('oculto');
    if (e && e.message !== 'Sin sesión.') avisar(e.message, 'error');
  });
})();
