/* El aviso de "esto lo guardaste y todavia no esta en la web".
   ---------------------------------------------------------------------------
   Guardar y publicar son dos pasos distintos, y esa es la parte del panel que
   mas confunde: alguien corrige una bajada, la guarda, entra al sitio y la ve
   igual que antes. El cambio esta -en la base-, pero el sitio publico son
   archivos y hasta que no se reconstruye no cambia nada.

   Este aviso cierra esa distancia. Compara la fecha de la ultima publicacion
   con la fecha en que se toco cada obra y cada texto, y nombra lo que quedo en
   el medio: "Roket (la bajada)", "Cervecería Austral (las fotos)".

   Se refresca solo cada minuto por dos razones: para apagarse cuando el build
   que se acaba de disparar termina -tarda dos o tres minutos, nadie va a estar
   recargando- y para enterarse de lo que guardo otra persona desde otra
   computadora. */

(function () {
  'use strict';

  var caja = document.getElementById('pendientes');
  if (!caja) return;

  var CADA = 60000;   // un minuto
  var NOMBRES = 6;    // cuantos se nombran antes de resumir en "y N más"

  var reloj = null;
  var pidiendo = false;

  /* --- redaccion --------------------------------------------------------- */

  function hace(iso) {
    var minutos = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
    if (minutos < 1) return 'recién';
    if (minutos < 60) return 'hace ' + minutos + (minutos === 1 ? ' minuto' : ' minutos');
    var horas = Math.round(minutos / 60);
    if (horas < 24) return 'hace ' + horas + (horas === 1 ? ' hora' : ' horas');
    var dias = Math.round(horas / 24);
    return 'hace ' + dias + (dias === 1 ? ' día' : ' días');
  }

  /* Una obra o un texto, con el detalle entre parentesis si lo hay. El detalle
     lo escribio el panel al guardar; cuando no esta, no se inventa nada. */
  function frase(nombre, detalle) {
    return detalle ? nombre + ' (' + detalle + ')' : nombre;
  }

  function listar(cambios) {
    var items = [];
    cambios.obras.forEach(function (o) {
      items.push({ texto: frase(o.titulo, o.ultimo_cambio), cuando: o.updated_at,
                   // Una obra en borrador tambien cuenta como pendiente -si la
                   // acaban de despublicar, sigue en la web hasta el proximo
                   // build-, pero no hay que prometer que publicar la va a
                   // mostrar. Sin esta marca el aviso dice "todavia no esta en
                   // la web" de algo que no va a aparecer igual.
                   borrador: !o.publicada,
                   href: '/admin/obra?id=' + encodeURIComponent(o.id) });
    });
    cambios.textos.forEach(function (t) {
      items.push({ texto: frase(t.rotulo, 'texto del sitio'), cuando: t.updated_at,
                   href: '/admin/textos' });
    });
    items.sort(function (a, b) { return a.cuando < b.cuando ? 1 : -1; });
    return items;
  }

  /* --- pantalla ---------------------------------------------------------- */

  function alDia() {
    caja.className = 'pendientes pendientes--aldia';
    caja.textContent = '';
    var p = document.createElement('p');
    p.className = 'pendientes__titulo';
    p.textContent = 'El sitio está al día: no hay cambios guardados sin publicar.';
    caja.appendChild(p);
  }

  function pintar(items) {
    caja.className = 'pendientes';
    caja.textContent = '';

    var titulo = document.createElement('p');
    titulo.className = 'pendientes__titulo';
    titulo.textContent = items.length === 1
      ? 'Hay un cambio guardado que todavía no está en la web:'
      : 'Hay ' + items.length + ' cambios guardados que todavía no están en la web:';
    caja.appendChild(titulo);

    var lista = document.createElement('ul');
    lista.className = 'pendientes__lista';
    items.slice(0, NOMBRES).forEach(function (i) {
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = i.href;
      a.textContent = i.texto;
      li.appendChild(a);
      if (i.borrador) {
        var marca = document.createElement('span');
        marca.className = 'pendientes__borrador';
        marca.textContent = ' borrador';
        li.appendChild(marca);
      }
      var cuando = document.createElement('span');
      cuando.className = 'pendientes__cuando';
      // El espacio va en el texto y no solo en el margen: sin el, un lector
      // de pantalla lee "Roketrecien" de corrido.
      cuando.textContent = ' ' + hace(i.cuando);
      li.appendChild(cuando);
      lista.appendChild(li);
    });
    if (items.length > NOMBRES) {
      var mas = document.createElement('li');
      mas.className = 'pendientes__mas';
      mas.textContent = 'y ' + (items.length - NOMBRES) + ' más';
      lista.appendChild(mas);
    }
    caja.appendChild(lista);

    var pie = document.createElement('p');
    pie.className = 'pendientes__pie';
    pie.textContent = 'Para que se vean, apretá Publicar cambios. Tarda entre 2 y 3 minutos, '
      + 'y este aviso se apaga solo cuando termina.';
    caja.appendChild(pie);
  }

  /* --- consulta ---------------------------------------------------------- */

  function revisar() {
    if (pidiendo) return Promise.resolve();
    pidiendo = true;

    return DATOS.ultimaPublicacion().then(function (desde) {
      // Sin ninguna publicacion anotada no hay contra que comparar. Es el caso
      // de una base recien creada: mejor callarse que listar todas las obras.
      if (!desde) { caja.className = 'pendientes oculto'; return; }
      return DATOS.cambiosSinPublicar(desde).then(function (cambios) {
        var items = listar(cambios);
        if (items.length) pintar(items); else alDia();
      });
    }).catch(function () {
      // Un fallo de red no tiene que llenar el panel de errores rojos: el
      // aviso es informativo y el proximo intento llega en un minuto.
      caja.className = 'pendientes oculto';
    }).then(function () {
      pidiendo = false;
    });
  }

  function arrancarReloj() {
    if (reloj) clearInterval(reloj);
    reloj = setInterval(function () {
      if (!document.hidden) revisar();
    }, CADA);
  }

  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) revisar();
  });

  window.PENDIENTES = { revisar: revisar };

  HMA.exigirSesion().then(function () {
    arrancarReloj();
    return revisar();
  }).catch(function () { /* exigirSesion ya redirigio */ });
})();
