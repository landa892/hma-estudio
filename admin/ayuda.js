/* Sesion y salida de la guia del panel. */

(function () {
  'use strict';

  HMA.exigirSesion().then(function () {
    var sesion = HMA.sesion();
    var quien = document.getElementById('quien');
    if (quien) quien.textContent = sesion && sesion.email ? sesion.email : '';

    document.getElementById('salir').addEventListener('click', function () {
      HMA.salir().then(function () { location.replace('/admin/'); });
    });
  }).catch(function () { /* exigirSesion ya redirigio */ });
})();
