# El token de Instagram

Al 04/10/2026. Qué hay que hacer para que el Inicio muestre sola la última
publicación del Instagram del estudio, y por qué se cayó.

Este archivo no se publica: `.vercelignore` excluye `docs/*.md`.

---

## Qué pasó

El token largo de Instagram dura **60 días y no tiene período de gracia**. Si
nadie lo renueva antes de que venza, muere, y desde el código no hay forma de
recuperarlo: hay que volver a autorizar la app a mano en Meta for Developers.

Hasta ahora el token vivía sólo en la variable `INSTAGRAM_ACCESS_TOKEN` de
Vercel y nadie lo renovaba. Venció, y el Inicio quedó mostrando la publicación
de respaldo —Movistar Arena— durante semanas.

Una variable de entorno no se puede reescribir desde el propio sitio, así que
el arreglo pasa por guardar el token en la base.

---

## Cómo quedó

| Pieza | Qué hace |
|---|---|
| tabla `credenciales` | guarda el token, cuándo vence y cuándo se refrescó |
| `api/_token-instagram.js` | lo lee y lo escribe; lo usan los dos endpoints |
| `api/instagram-refresh.js` | lo renueva; lo llama el cron |
| `api/instagram-latest.js` | lo usa para pedir la última publicación |
| `crons` en `vercel.json` | dispara el refresco todas las noches a las 4 |

El cron corre todos los días porque el plan Hobby de Vercel no permite más de
una vez por día, pero **el refresco real ocurre sólo cuando faltan menos de 20
días** para el vencimiento. Las demás noches el endpoint contesta "todavía no
hace falta" y no gasta nada.

El margen de 20 días es a propósito: si el cron no corre una noche, o si Meta
contesta mal unos días, quedan casi tres semanas de reintentos antes de que el
token muera sin vuelta atrás.

### La tabla no la ve nadie más que el servidor

`credenciales` tiene RLS prendido y **ninguna policy**, a propósito. Sin
policies no entra ni la clave publicable ni un usuario con sesión: sólo la
clave de servicio, que saltea el RLS y vive únicamente en las variables del
servidor. Es la diferencia con `textos`, que tiene lectura pública porque su
contenido se publica igual.

---

## Puesta en marcha

Tres pasos, en este orden.

**1. Correr la migración.** En el editor SQL de Supabase, el contenido de
`supabase/migrations/0021_token_instagram.sql`. Como todas, se corre a mano.

**2. Generar un token nuevo** en Meta for Developers, en el caso de uso de
Instagram, y pegarlo en la variable `INSTAGRAM_ACCESS_TOKEN` de Vercel
(Production). Ese es el único token que se carga a mano en la vida del sitio:
el primer refresco lo pasa a la base y de ahí en más se renueva solo.

**3. Probar el refresco a mano**, sin esperar al cron:

```bash
curl -s "https://estudiohma.com/api/instagram-refresh?forzar=1"
```

Tiene que contestar `{"ok":true,"estado":"refrescado", ...}` con la fecha de
vencimiento a 60 días. Si contesta `"sin token"`, falta el paso 2. Si da 500
con *Session has expired*, el token que se pegó ya estaba vencido.

Y después, que la publicación salga de verdad:

```bash
curl -s https://estudiohma.com/api/instagram-latest
```

Con `"automatic": true` está andando. Con `"automatic": false` está mostrando
el respaldo.

**Opcional pero recomendado:** poner una variable `CRON_SECRET` en Vercel con
cualquier cadena larga. Vercel la manda sola en la cabecera cuando dispara el
cron, y el endpoint deja de aceptar llamadas de afuera. Sin esa variable el
endpoint queda abierto: no expone el token —nunca lo devuelve— pero cualquiera
podría hacer que se refresque.

---

## Si algo falla

El endpoint devuelve **500 a propósito** cuando no puede renovar, para que el
fallo aparezca en rojo en el panel de Vercel en vez de pasar por exitoso. Si se
repite varias noches seguidas, el token está por morir: hay que mirarlo antes
de que se cumplan los 60 días.

Probado contra los casos feos, y en todos el sitio sigue en pie:

| Qué falla | Qué contesta el refresco | Qué ve el visitante |
|---|---|---|
| no hay token en ningún lado | 200 `sin token` | el respaldo |
| el token ya venció | 500 con el mensaje de Meta | el respaldo |
| Meta devuelve HTML en vez de JSON | 500 explicando qué llegó | el respaldo |
| la base no deja escribir | 500 `row level security` | el respaldo |
| la base está caída | 500 `ECONNREFUSED` | el respaldo |

`instagram-latest` nunca tira: si no puede leer el token o Instagram contesta
mal, devuelve la publicación de respaldo con `automatic: false` y el Inicio se
ve igual que siempre.

---

## Si el token igual muere

Pasa si nadie mira los errores del cron durante tres semanas. No se recupera
desde el código: hay que repetir el paso 2 de la puesta en marcha.

Y si al ir a generarlo el popup de Instagram dice *"No pudimos establecer una
conexión con Instagram"*, no es la red. Casi siempre es que el navegador tiene
abierta la sesión de otra cuenta de Instagram y el popup la hereda. Se resuelve
entrando primero a instagram.com con la cuenta del estudio en una ventana de
incógnito, y recién ahí abriendo Meta for Developers en esa misma ventana.
