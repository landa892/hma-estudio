/* Pantalla de acceso: entrar y pedir el enlace de recupero. */

(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };

  var vistaEntrar = $('vistaEntrar');
  var vistaRecuperar = $('vistaRecuperar');

  /* A donde ir despues de entrar. Sale de ?volver= para que quien llego a una
     pagina del panel sin sesion vuelva a esa y no al listado. Se acepta solo
     una ruta interna del propio panel: con una URL completa esto seria un
     redirect abierto, util para mandar a alguien a un login falso. */
  function destino() {
    var pedido = new URLSearchParams(location.search).get('volver') || '';
    return /^\/admin\/[A-Za-z0-9._~/-]*$/.test(pedido) ? pedido : '/admin/obras';
  }

  /* Ver la contraseña. La eligio otra persona y se escribe una vez cada tanto:
     a ciegas, un rebote no distingue un dedazo de una contraseña equivocada. */
  (function () {
    var ojo = document.getElementById('verClave');
    var campo = document.getElementById('clave');
    if (!ojo || !campo) return;
    ojo.addEventListener('click', function () {
      var visible = campo.type === 'text';
      campo.type = visible ? 'password' : 'text';
      ojo.textContent = visible ? 'Mostrar' : 'Ocultar';
      ojo.setAttribute('aria-pressed', visible ? 'false' : 'true');
      ojo.setAttribute('aria-label',
        visible ? 'Mostrar la contraseña' : 'Ocultar la contraseña');
      campo.focus();
    });
  })();

  function avisar(el, texto, tipo) {
    el.textContent = texto || '';
    el.className = 'aviso' + (texto ? ' aviso--' + tipo : '');
  }

  function ocupado(boton, si, rotulo) {
    boton.disabled = si;
    boton.textContent = si ? 'Un momento…' : rotulo;
  }

  /* --- si ya hay sesion, no mostramos el login --------------------------- */
  if (HMA.sesion()) {
    location.replace(destino());
    return;
  }

  /* --- entrar ----------------------------------------------------------- */
  $('formEntrar').addEventListener('submit', function (ev) {
    ev.preventDefault();
    var aviso = $('avisoEntrar');
    var boton = $('botonEntrar');
    var email = $('email').value.trim();
    var clave = $('clave').value;

    if (!email || !clave) {
      avisar(aviso, 'Completá el correo y la contraseña.', 'error');
      return;
    }

    avisar(aviso, '', 'ok');
    ocupado(boton, true, 'Entrar');

    HMA.entrar(email, clave).then(function () {
      location.replace(destino());
    }).catch(function (e) {
      ocupado(boton, false, 'Entrar');
      avisar(aviso, e.message, 'error');
      $('clave').value = '';
      $('clave').focus();
    });
  });

  /* --- recuperar -------------------------------------------------------- */
  $('irARecuperar').addEventListener('click', function () {
    vistaEntrar.classList.add('oculto');
    vistaRecuperar.classList.remove('oculto');
    $('emailRecuperar').value = $('email').value.trim();
    $('emailRecuperar').focus();
  });

  $('volverAEntrar').addEventListener('click', function () {
    vistaRecuperar.classList.add('oculto');
    vistaEntrar.classList.remove('oculto');
    $('email').focus();
  });

  $('formRecuperar').addEventListener('submit', function (ev) {
    ev.preventDefault();
    var aviso = $('avisoRecuperar');
    var boton = $('botonRecuperar');
    var email = $('emailRecuperar').value.trim();

    if (!email) {
      avisar(aviso, 'Escribí tu correo.', 'error');
      return;
    }

    avisar(aviso, '', 'ok');
    ocupado(boton, true, 'Enviar enlace');

    /* El mismo mensaje salga bien o mal, y sin decir si el correo existe: si
       contestara distinto, cualquiera podria averiguar quien tiene cuenta. */
    var listo = function () {
      ocupado(boton, false, 'Enviar enlace');
      avisar(aviso, 'Si ese correo tiene cuenta, ya te llegó el enlace. '
        + 'Revisá también el correo no deseado.', 'ok');
    };
    HMA.recuperar(email).then(listo, listo);
  });

  $('email').focus();
})();
