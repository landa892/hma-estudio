/* Pantalla del enlace de recupero.

   Supabase manda al usuario aca con el token en el fragmento de la URL
   (#access_token=...&type=recovery). El fragmento no viaja al servidor: se lee
   en el navegador, se usa una vez y se borra de la barra de direcciones para
   que no quede en el historial ni en una captura. */

(function () {
  'use strict';

  var $ = function (id) { return document.getElementById(id); };

  function avisar(texto, tipo) {
    var el = $('avisoClave');
    el.textContent = texto || '';
    el.className = 'aviso' + (texto ? ' aviso--' + tipo : '');
  }

  var hash = new URLSearchParams(location.hash.replace(/^#/, ''));
  var token = hash.get('access_token');
  var tipo = hash.get('type');

  /* Sin token no hay nada que hacer: puede ser un enlace vencido, ya usado, o
     alguien que entro a la pagina de memoria. */
  if (!token || (tipo && tipo !== 'recovery')) {
    $('vistaClave').classList.add('oculto');
    $('vistaSinEnlace').classList.remove('oculto');
    return;
  }

  // El token sale de la barra de direcciones en cuanto lo tenemos en memoria.
  history.replaceState(null, '', location.pathname);

  $('formClave').addEventListener('submit', function (ev) {
    ev.preventDefault();
    var a = $('clave1').value;
    var b = $('clave2').value;
    var boton = $('botonClave');

    if (a.length < 8) {
      avisar('La contraseña tiene que tener 8 caracteres o más.', 'error');
      return;
    }
    if (a !== b) {
      avisar('Las dos contraseñas no coinciden.', 'error');
      return;
    }

    avisar('', 'ok');
    boton.disabled = true;
    boton.textContent = 'Guardando…';

    HMA.cambiarClave(a, token).then(function () {
      avisar('Listo. Ya podés entrar con la contraseña nueva.', 'ok');
      // Se manda al login y no al panel: el token del mail sirve para cambiar
      // la clave, no como sesion de trabajo.
      setTimeout(function () { location.replace('/admin/'); }, 1800);
    }).catch(function (e) {
      boton.disabled = false;
      boton.textContent = 'Guardar';
      if (e.status === 401 || e.status === 403) {
        $('vistaClave').classList.add('oculto');
        $('vistaSinEnlace').classList.remove('oculto');
        return;
      }
      avisar(e.message, 'error');
    });
  });

  $('clave1').focus();
})();
