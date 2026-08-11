# Pasos para dar de alta el sitio y encender el panel

Dos bloques independientes. El **A** deja la página publicada en su dominio.
El **B** enciende el panel de autogestión. El B no bloquea al A.

---

## Antes que nada: qué no se comparte

Tres claves aparecen en estos pasos. Dos son públicas y una no.

| Clave | Dónde va | ¿Es secreta? |
|---|---|---|
| `SUPABASE_ANON_KEY` | navegador y Vercel | No. Viaja en cada visita. Lo que protege los datos son las reglas de la base, no esconderla. |
| `SUPABASE_URL` | navegador y Vercel | No. |
| `SUPABASE_SERVICE_KEY` | **sólo** variables de Vercel | **Sí.** Saltea todas las reglas de seguridad. Nunca en un archivo del repo, nunca en el navegador, nunca por chat. |

Lo mismo con `YOUTUBE_API_KEY`, `RESEND_API_KEY` y la URL del deploy hook:
se cargan directo en Vercel, no se pegan en una conversación.

---

# A · Dar de alta la página

## A1 · La cuenta de Gmail del estudio — **resuelto**

Es `hitzig.militello@gmail.com`. Tiene verificación en dos pasos y el código
llega al teléfono de la dueña del estudio, asi que no siempre se puede usar en
el momento: tenerlo en cuenta al planificar cualquier paso que la necesite.

## A2 · Clave de YouTube — **hecho, con una salvedad**

Sin esta clave, la sección de videos de la página de prensa se ve vacía. No
rompe nada más.

1. Entrar a `console.cloud.google.com`
2. Crear un proyecto
3. Activar **YouTube Data API v3**
4. **Credenciales → Crear credenciales → Clave de API**
5. Restringirla: **API** a `YouTube Data API v3`; **aplicación** en *Ninguna*
   (la usa el servidor de Vercel, cuya IP cambia)
6. En Vercel → proyecto → **Settings → Environment Variables**, agregar:
   `YOUTUBE_API_KEY`

> ### Pendiente de traspaso
> Esta clave quedó creada en la **cuenta de Google del desarrollador**, no en la
> del estudio: la del estudio tiene verificación en dos pasos y el código llega
> al teléfono de la dueña.
>
> Funciona igual, porque sólo lee la lista pública de videos del canal. Pero el
> día de la entrega hay que rehacerla desde la cuenta del estudio y reemplazar
> la variable en Vercel. Es un minuto, y si no se hace, el día que el
> desarrollador borre ese proyecto de Google la sección de videos queda vacía
> sin que nadie entienda por qué.

## A3 · El formulario de contacto — **hecho**

`estudiohma.com` quedó verificado en Resend el 10/08/2026 y las consultas ya
llegan a `hitzig.militello@gmail.com`. Se cambiaron los dos endpoints:
`api/contact.js` (el formulario) y `api/lead.js` (los datos que se dejan antes
de abrir WhatsApp).

El remitente es `web@estudiohma.com`, que no existe como casilla y no hace
falta: el formulario manda el correo de quien escribió en el campo de respuesta.

Los registros quedaron así, en el DNS de `estudiohma.com`:

| Nombre | Tipo | Para qué |
|---|---|---|
| `resend._domainkey` | TXT | firma DKIM |
| `send` | TXT | SPF |
| `_dmarc` | TXT | política DMARC |

Y el MX de Resend vive dentro de `send.estudiohma.com`, que se creó como sitio
web aparte sólo para poder colgárselo. **Los cinco MX de Google en la raíz no se
tocaron** — verificado antes y después.

<details>
<summary>Cómo era antes (por si hay que rehacerlo)</summary>

**Las consultas llegaban a `nacholanda08@gmail.com`, no al estudio.** Está
así porque Resend en modo prueba sólo entrega a la casilla dueña de la cuenta.
Si el sitio sale a producción con esto sin cambiar, las consultas de clientes
reales pasan por vos y alguna se pierde.

1. Entrar a `resend.com`
2. **Domains → Add Domain** → `estudiohma.com`
3. Copiar los registros DNS que da y cargarlos en DreamHost
4. Esperar a que diga **verified**
5. Avisar: hay que cambiar `TO_EMAIL` por `DESTINO_FINAL` en `api/contact.js`
   (ya está preparado y comentado)

</details>

## A4 · El número de WhatsApp

El botón flotante existe y funciona, pero el número está vacío: hoy no abre
nada.

Pedirlo al estudio con código de país, sin espacios ni signos:
`5491122334455`. Va en `scripts/main.js`, en la línea marcada.

## A5 · El dominio — **este va último**

Se hace cuando A2, A3 y A4 ya estén, para que el sitio no salga a medias.

1. Vercel → **Settings → Domains** → agregar `estudiohma.com`
2. Vercel devuelve un registro **A** y un **CNAME**
3. Cargarlos en DreamHost

> ### No tocar los registros MX
> El correo del estudio corre por Google Workspace. Si se pisan los MX, se
> les cae el mail. **Sólo se tocan A y CNAME.**

La propagación tarda entre minutos y unas horas.

---

# B · Encender el panel

## B1 · Crear el proyecto de Supabase

**Con la cuenta del estudio, no con la tuya.** En la opción B que aceptó el
cliente, la infraestructura es de ellos desde el día uno. Si el proyecto nace
en tu cuenta, después hay que transferirlo y es un trámite evitable.

Región: **South America (São Paulo)**.

## B2 · Correr las migraciones

En Supabase → **SQL Editor**. Pegar y ejecutar **en este orden**, de a uno:

| Orden | Archivo | Qué hace |
|---|---|---|
| 1 | `supabase/migrations/0001_esquema.sql` | tablas y reglas de seguridad |
| 2 | `supabase/migrations/0002_storage.sql` | el depósito de fotos |
| 3 | `supabase/migrations/0003_textos.sql` | los 11 textos fijos |
| 4 | `supabase/migrations/0004a_fotografia.sql` | el campo de crédito de foto |
| 5 | `supabase/migrations/0005_obras.sql` | **las 61 obras del sitio** |

El orden importa: cada uno usa lo que creó el anterior.

Cargar las 61 obras **no cambia nada visible** — ya se muestran. Lo que
habilita es que el estudio pueda editarlas desde el panel.

## B3 · Crear el usuario del estudio

**Authentication → Users → Add user.** Correo del estudio y una contraseña.
Marcar *auto-confirm*.

Es el único usuario del sistema: no hay roles ni permisos diferenciados.

## B4 · Conectar el panel

En Supabase → **Settings → API**, copiar:
- **Project URL**
- la clave **anon / public**

En la compu, con la rama `panel` traída:

```bash
git fetch origin && git checkout panel
```

Copiar `admin/config.ejemplo.js` a `admin/config.js` y pegar esos dos valores.

Ese archivo no entra al repo a propósito: así el código no queda atado a
ninguna cuenta.

## B5 · El disparador de publicación

1. Vercel → **Settings → Git → Deploy Hooks**
2. Crear uno llamado `panel`, rama `main`
3. Copiar la URL que devuelve

En **Environment Variables**, agregar tres:

- `VERCEL_DEPLOY_HOOK` = esa URL
- `SUPABASE_URL` = la dirección del proyecto
- `SUPABASE_ANON_KEY` = la clave pública

> La URL del hook no puede vivir en el panel: cualquiera que abra el código de
> la página la vería, y con esa URL sola se pueden lanzar reconstrucciones sin
> límite hasta agotar la cuota. Por eso vive en el servidor.

## B6 · El generador en el build

Vercel → **Settings → Build & Development Settings → Build Command**:

```bash
python3 docs/panel_generar.py --supabase && python3 docs/en_gen.py
```

Y una variable más:

- `SUPABASE_SERVICE_KEY` = la clave **service_role**

Esta es la clave secreta de la tabla de arriba. Va **sólo acá**.

## B7 · Fusionar la rama

Con B1 a B6 hechos, fusionar `panel` en `main`. El panel queda vivo en
`estudiohma.com/admin`.

Antes de fusionar hay que resolver una cosa: `admin/config.js` no está en el
repo, así que en el sitio publicado no existe. Hay que generarlo en el build
desde las variables de entorno, o el panel no arranca. **Avisar cuando se
llegue a este punto.**

---

# Cómo funciona, una vez andando

**El estudio entra** a `estudiohma.com/admin` con correo y contraseña. Desde
la compu o el celular. Si olvida la contraseña, la recupera por mail sin que
nadie intervenga.

**Edita** obras, fotos y los textos fijos. Cada cambio se guarda en la base.

**Aprieta "Publicar cambios".** Eso dispara la reconstrucción del sitio. En
dos o tres minutos los cambios se ven.

El sitio sigue siendo archivos estáticos: misma velocidad de hoy, y si la base
se cae el sitio sigue en pie porque las páginas ya están escritas.

**El modo borrador es real:** una obra sin publicar no se puede ver ni
entrando a su dirección, ni consultando la base a mano.

---

# Lo que sigue pendiente de contenido

Nada de esto rompe el sitio. Son huecos que se ven si se buscan.

- **Ualá Gigena sin año** — no está en el sitio, ni en el WordPress viejo, ni
  en su ficha del Drive
- **Tostado**: la carátula y la memoria son de la sucursal Tribunales, pero la
  página es la de Miami
- **Parfumerie**: la carátula está en 643 px; el resto ronda los 1200
- **Seis obras sin memoria en inglés**: Accor, Antiche, Indusparquet, IOL,
  Lucciano's Caballito y Roket. En el sitio en inglés esas páginas van sin ese
  bloque
- **Tres obras con sólo los dos socios en el equipo**: Accor, Iguanafix y
  Tostado. No hay más nombres en ninguna fuente
- **"Comitente" vacío en las 61 obras** — el sitio nunca mostró ese campo. El
  panel lo tiene; cuando haya varios cargados se enciende en el sitio con un
  cambio chico
- **Ualá II es la única obra con crédito de fotografía**, y el cliente pidió no
  mostrar créditos de foto en ninguna
