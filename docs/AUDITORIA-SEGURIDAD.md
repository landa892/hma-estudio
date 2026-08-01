# Auditoría de seguridad — sitio de HMA

**Fecha:** 1 de agosto de 2026 · **Commit auditado:** `510262f` · **Repositorio:** `landa892/hma-estudio`

> Este documento **no se publica**. Vive en `docs/`, que está excluido del despliegue
> mediante `.vercelignore`. Ver el hallazgo **H1** para el motivo.

---

## 0. Qué se auditó, y por qué cambió el alcance

La auditoría anterior (26 de julio) describía un sitio estático de una sola página, sin
backend. **Eso ya no es cierto.** Hoy el proyecto es:

| Pieza | Detalle |
|---|---|
| Páginas | 112 archivos HTML — 55 en castellano, 56 en inglés bajo `/en/`, más el 404 |
| Funciones de servidor | 3: `api/contact.js`, `api/lead.js`, `api/youtube-latest.js` |
| Servicios externos | Resend (envío de correo), YouTube Data API v3 |
| JavaScript propio | `scripts/main.js` y 4 módulos de animación |
| Librerías de terceros | GSAP 3.15.0, ScrollTrigger 3.15.0 y Lenis, **servidas desde el propio dominio** |
| Hosting | Vercel |
| Dominio y correo | `estudiohma.com` — DNS en DreamHost, correo en Google Workspace |

Aparecieron por lo tanto categorías que antes no aplicaban: **entrada de datos de usuario,
llamadas a APIs de terceros, secretos de servidor y datos personales**. Este documento se
concentra ahí.

Lo que **no** entra en el alcance: la máquina local desde la que se trabaja. La auditoría
anterior la incluía y ese fue justamente el problema del hallazgo H1.

---

## 1. Hallazgos

### 🔴 H1 · La auditoría anterior se publicaba en el sitio — CORREGIDO

Vercel sirve todo lo que hay en el repositorio, y no existía `.vercelignore`. La carpeta
`docs/` quedaba accesible en `estudiohma.com/docs/`, y ahí vivía la auditoría previa, que
enumeraba los puertos abiertos de la máquina de desarrollo, su IP de red local y el hecho
de que la rama `main` no tenía protección.

`robots.txt` incluía `Disallow: /docs/`, pero eso **sólo evita que un buscador lo indexe,
no que alguien lo abra**. Es una señal para robots que se portan bien, no un control de
acceso.

**Corregido en `510262f`:** se agregó `.vercelignore` con `docs/`. Los archivos siguen
versionados en git, que es donde corresponde.

**Queda pendiente de tu lado:** el repositorio es público en GitHub, así que el documento
viejo sigue siendo legible ahí y en el historial. Como no contiene claves, el riesgo es
acotado, pero conviene decidir si el repositorio debe seguir siendo público.

**Verificación:** abrir `estudiohma.com/docs/AUDITORIA-SEGURIDAD.md` tras el próximo
despliegue. Debe responder 404.

---

### 🟠 H2 · El feed de YouTube escribía HTML sin escapar — CORREGIDO

`scripts/main.js` construía las tarjetas de video interpolando directamente el título, la
dirección y la miniatura que devuelve la API de YouTube:

```js
<div class="press-title">${v.title}</div>
```

Era **el único lugar del sitio donde un dato de origen externo llegaba al DOM sin
escapar**. Un título con etiquetas HTML se habría insertado tal cual.

El riesgo práctico era bajo —los títulos los escribe el propio estudio en su canal— y el
código además está dormido, porque sin `YOUTUBE_API_KEY` esa rama nunca se ejecuta. Pero
**está previsto activar esa clave**, y ahí dejaba de ser teórico.

**Corregido:** ahora el título se escapa, y de la dirección y la miniatura sólo se aceptan
direcciones `https` de `youtube.com`, `youtu.be`, `ytimg.com` y `ggpht.com`. Si la
respuesta trae otra cosa, la tarjeta se descarta en vez de escribirla.

---

### 🟡 H3 · El límite de envíos del formulario es más débil de lo que aparenta

`api/contact.js` y `api/lead.js` cuentan los envíos por IP en un `Map` en memoria, con un
tope de 3 por minuto.

En Vercel cada invocación puede correr en una instancia distinta, y las instancias se
reciclan. **El contador no se comparte**, así que quien reparta sus pedidos esquiva el
límite. Además el `Map` nunca purga entradas viejas: crece mientras la instancia viva.

**Riesgo real: bajo.** Lo que de verdad frena el spam automatizado es el campo trampa, que
sí funciona. El límite es una segunda barrera, no la principal.

**Si algún día llega correo basura**, ese es el punto a reforzar: un contador compartido
(Vercel KV o Upstash) en lugar de memoria local.

---

### 🟡 H4 · El buscador inserta direcciones de su índice sin escapar

En `scripts/main.js`, el render de resultados hace:

```js
'<a class="search-result" href="' + item.url + '">'
```

`item.url` e `item.img` salen de `scripts/search-index.js`, un archivo que generamos
nosotros. **Hoy no es explotable**: no hay forma de que un visitante meta datos ahí.

Queda anotado como deuda: si alguna vez ese índice pasa a generarse desde una fuente
externa —un gestor de contenidos, la base del WordPress viejo— habría que escapar esos dos
campos. El texto visible ya se escapa correctamente vía `escapeHtml` y `highlight`.

---

### 🟡 H5 · El correo sale desde el remitente de prueba de Resend

`FROM_EMAIL` es `onboarding@resend.dev`, el remitente de prueba. Dos consecuencias:

1. **Sólo entrega a la casilla dueña de la cuenta de Resend.** Cualquier otro destino se
   descarta en silencio. Por eso `TO_EMAIL` sigue apuntando a una casilla personal y no a
   la del estudio.
2. Los correos salen desde un dominio ajeno, lo que aumenta la probabilidad de que caigan
   en la carpeta de no deseados.

**Se resuelve verificando `estudiohma.com` en Resend**, que a su vez depende de apuntar el
dominio a Vercel. Está anotado en la lista de pendientes.

---

### 🟡 H6 · Los formularios llegan hoy a una casilla personal

`TO_EMAIL = "nacholanda08@gmail.com"`. Consultas de personas reales dirigidas al estudio
terminan en la casilla personal de quien desarrolla el sitio.

No es una falla técnica sino una situación provisoria, pero **es un tratamiento de datos
personales que la política de privacidad publicada no contempla**. Conviene resolverlo
pronto.

El destino definitivo está anotado en el código (`DESTINO_FINAL`) y el cambio es de una
línea, una vez que exista la casilla y el dominio esté verificado.

---

## 2. Lo que se revisó y está bien

### Secretos

- **Ninguna clave en el código ni en el historial de git.** Se buscaron los formatos de
  Resend (`re_…`) y de Google (`AIza…`) en todos los commits: cero coincidencias.
- `RESEND_API_KEY` y `YOUTUBE_API_KEY` se leen de variables de entorno.
- Ningún archivo `.env`, `.pem` o `.key` versionado. Se agregaron al `.gitignore` como
  resguardo.

### Entrada de datos en las funciones de servidor

Ambos formularios validan antes de hacer nada:

| Control | `contact.js` | `lead.js` |
|---|---|---|
| Método restringido a POST | sí | sí |
| Campo trampa para bots | sí | sí |
| Verificación de tipo | sí | sí |
| Tope de longitud | 120 / 200 / 4000 | 120 / 40 |
| Formato de correo | sí | — |
| Escape de HTML antes de armar el mail | sí | sí |
| CORS restringido | sí | sí |

No hay base de datos, así que **no existe superficie de inyección SQL**. El cuerpo del
correo se arma con los datos ya escapados. Como Resend recibe JSON y la expresión que
valida el correo rechaza espacios, **tampoco hay inyección de cabeceras**.

Los mensajes de error que ve el visitante no revelan nada: el detalle que devuelve Resend
va al registro del servidor, no a la respuesta.

### En el navegador

- **Cero scripts en línea** y **cero scripts de terceros**. GSAP y Lenis se sirven desde
  el propio dominio, así que la política de seguridad puede mantener `script-src 'self'`
  sin excepciones.
- **Cero iframes.**
- Sin `eval`, sin `new Function`, sin `document.write`.
- **Sin cookies, sin `localStorage`, sin `sessionStorage`.** El sitio no guarda nada en el
  navegador de quien lo visita.
- Los 51 enlaces externos de la página de prensa llevan `rel="noopener"`.

### Inyección en el buscador — probado, no teórico

Se intentó inyectar código de dos maneras: escribiéndolo en el campo, y armando una
dirección con el ataque en el parámetro `?q=`, que es el vector realista porque se puede
enviar por mensaje. En ambos casos el contenido se escapa y se muestra como texto. **No
ejecuta nada.**

### Cabeceras

`vercel.json` aplica a todas las rutas:

```
Content-Security-Policy      default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';
                             img-src 'self' data: https://i.ytimg.com; connect-src 'self';
                             object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'
Strict-Transport-Security    max-age=31536000; includeSubDomains; preload
X-Frame-Options              DENY
X-Content-Type-Options       nosniff
Referrer-Policy              strict-origin-when-cross-origin
Permissions-Policy           geolocation=(), microphone=(), camera=(), payment=()
```

La misma política está declarada en un `<meta>` de cada página, salvo `frame-ancestors`,
que los navegadores ignoran en un `meta` y sólo respetan como cabecera. **La diferencia es
correcta, no un descuido.**

`style-src` admite `'unsafe-inline'` porque algunas animaciones escriben estilos en
caliente. Es la única concesión y no permite ejecutar código.

### Dependencias

`npm audit` → **0 vulnerabilidades**. La alerta moderada anterior venía de una dependencia
transitiva de `shadcn`, herramienta de desarrollo que no corre en producción, y se cerró
actualizando `package-lock.json`.

### Integridad del sitio

Sobre las 112 páginas: **0** etiquetas desbalanceadas, **0** imágenes inexistentes, **0**
enlaces internos rotos, **0** imágenes sin texto alternativo y **0** medidas declaradas que
no coincidan con el archivo real.

---

## 3. Datos personales

| Qué se recoge | Dónde va | Base |
|---|---|---|
| Nombre, correo y mensaje | Resend → casilla de destino | Consentimiento al enviar |
| Nombre y teléfono (previo a WhatsApp) | Resend → casilla de destino | Consentimiento al enviar |
| IP de quien envía | Sólo en memoria, para el límite de envíos | Interés legítimo |

No hay analítica, ni píxeles de seguimiento, ni perfiles publicitarios. La política de
privacidad publicada lo declara así y **coincide con lo que hace el código**, con la única
salvedad del hallazgo H6.

Las miniaturas de YouTube se cargan desde servidores de Google, lo que transfiere la
dirección IP del visitante a Google. Está declarado en la política.

---

## 4. Gobernanza del repositorio

- La rama `main` **tiene una regla que exige pull request**, pero el usuario que publica
  puede saltearla. Cada push lo informa: `Bypassed rule violations for refs/heads/main`.
  Funciona, pero queda registrado cada vez. Decidir si se quiere trabajar con ramas o
  quitar la regla.
- **Dependabot está activo** y no reporta alertas abiertas.
- El repositorio es **público**. Correcto para un sitio de marketing, con la salvedad de H1.

---

## 5. Qué hacer, en orden

| | Acción | Quién | Estado |
|---|---|---|---|
| 1 | Sacar `docs/` del despliegue | — | hecho |
| 2 | Escapar los datos del feed de YouTube | — | hecho |
| 3 | Verificar que `/docs/` responda 404 tras el despliegue | vos | pendiente |
| 4 | Apuntar el dominio a Vercel y verificarlo en Resend | vos | pendiente |
| 5 | Mover el destino de los formularios a la casilla del estudio | — | espera el 4 |
| 6 | Decidir si el repositorio sigue público | vos | pendiente |
| 7 | Contador de envíos compartido | — | sólo si aparece spam |

---

## 6. Revisión periódica

| Cada | Qué mirar |
|---|---|
| Al agregar una función de servidor | Que valide tipos, tope de longitud y escape antes de armar HTML o correo |
| Al mostrar datos que vengan de afuera | Escapar y validar el origen de las direcciones, como se hizo en H2 |
| Mensual | `npm audit` y la pestaña Security de GitHub |
| Al tocar el DNS | **No modificar los registros MX**: el correo del estudio vive en Google Workspace y se cae si se pierden |
