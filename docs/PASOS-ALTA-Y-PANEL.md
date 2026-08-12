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

**Es lo único del bloque A que queda pendiente.**

## A5 · El dominio — **hecho el 11/08/2026**

`estudiohma.com` sirve el sitio nuevo desde Vercel. `www` y
`hma-estudio.vercel.app` redirigen al apex con 308.

El apex es el canónico en todo el sitio —`rel="canonical"`, `og:url` y todas
las entradas del sitemap—, así que la redirección va de `www` hacia el apex y no al
revés. Vercel venía configurado al revés y se corrigió antes de mover el DNS.

Los registros que quedaron en DreamHost:

| Nombre | Tipo | Valor |
|---|---|---|
| `@` | A | `216.198.79.1` |
| `www` | CNAME | `bc0fe562eb9e786c.vercel-dns-017.com` |

> ### El paso que no es obvio: "Solo DNS"
> No alcanza con agregar el registro A. Mientras el dominio esté como sitio
> alojado, DreamHost mantiene su propio `@ A 64.90.39.10` y **ese le gana al
> personalizado**: el dominio siguió resolviendo a DreamHost aun con el registro
> de Vercel cargado.
>
> Se arregla en **Sitios Web → el dominio → Configuraciones → Establecer como
> Solo DNS**. Después hay que apretar **Actualizar DNS** en la pestaña DNS: el
> registro viejo no se va solo hasta que DreamHost reconstruye la zona.
>
> El CNAME de DreamHost no acepta el punto final. `...vercel-dns-017.com.` da
> "Nombre de dominio inválido"; sin el punto entra.

> ### El correo no se tocó
> Se verificaron los MX antes y después: los cinco de Google, prioridad 0.
> "Solo DNS" borra el alojamiento y los registros A, no el correo ni los TXT de
> Resend. Los archivos y la base del WordPress viejo siguen en el VPS y el
> cambio es reversible.
>
> Al WordPress viejo ya no se llega por `estudiohma.com`. Sigue accesible por
> `staging.estudiohma.com`.

## A6 · Search Console — **hecho el 11/08/2026**

Propiedad de tipo **Dominio** (`sc-domain:estudiohma.com`), verificada por TXT
en la raíz y creada **con la cuenta del estudio**, así que acá no hay deuda de
traspaso como con la clave de YouTube.

El TXT no se ve hasta apretar **Actualizar DNS** en DreamHost, igual que pasó
con el registro A.

Sitemap enviado como URL completa: `https://estudiohma.com/sitemap.xml`. Una
propiedad de tipo Dominio cubre varios hosts, así que la ruta suelta
(`sitemap.xml`) la rechaza con "Dirección de sitemap no válida".

### El sitemap se genera solo

Lo arma `docs/sitemap_gen.py` **enumerando las páginas del disco**:

```bash
python docs/sitemap_gen.py
```

Antes se mantenía a mano, y por eso **14 obras publicadas no estaban en el
sitemap**: Abasto, Burger 7167, Casa Olmo, Clásico Quilmes, Elyaki, Galería
Objeto A, Lucciano's Olivos, Malita, Oficina Casa Luna, PH El Salvador, PH Loft
Arias, Stella Artois Mercat, The Birra y Ualá II. Ahora la fuente son los
archivos, que es lo único que no puede desincronizarse del sitio.

Qué hace, además de listar:

- Agrega el par en `/en/` de cada página y anota los `<xhtml:link>` de idioma.
  Sin ese par, Google puede tomar las dos versiones como duplicadas y quedarse
  con una sola.
- **Saltea las páginas con `noindex`** — hoy `/buscar/`. Listarlas sería pedirle
  a Google que indexe algo que la propia página le prohíbe, y Search Console lo
  reporta como error.
- Conserva el `changefreq` y el `priority` que cada URL ya tenía, así sumar una
  obra no reescribe el archivo entero.

Es idempotente: correrlo dos veces da lo mismo. Quedaron 138 URLs, 69 en cada
idioma.

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
| 6 | `supabase/migrations/0006_banners.sql` | los rótulos de los banners del home |
| 7 | `supabase/migrations/0007_correcciones_cliente_agosto.sql` | correcciones de fichas y memorias |
| 8 | `supabase/migrations/0008_memorias_ingles.sql` | completa las seis memorias en inglés |
| 9 | `supabase/migrations/0009_seguridad_panel.sql` | restringe la edición al correo del estudio y limita el home a tres destacadas |

El orden importa: cada uno usa lo que creó el anterior.

En **Authentication → Providers → Email**, desactivar **Allow new users to sign
up**. El usuario se crea manualmente en el paso siguiente; ninguna otra cuenta
debe poder registrarse por API.

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
python3 docs/panel_build.py
```

Los doce pasos viven en ese script y no encadenados con `&&` en la casilla por
una razón concreta: **Vercel admite 256 caracteres en el comando de build** y la
cadena completa mide más del doble. De paso, en el log se ve en qué paso falló,
que en una sola línea de shell no se ve.

Y una variable más:

- `SUPABASE_SERVICE_KEY` = la clave **service_role**

Esta es la clave secreta de la tabla de arriba. Va **sólo acá**.

### Qué hace cada paso, y por qué en ese orden (son doce)

| Paso | Qué hace |
|---|---|
| `panel_config.py` | Escribe `admin/config.js` desde las variables. Sin esto el panel publicado no conecta con nada. |
| `panel_correcciones_agosto.py` | Migra los valores viejos marcados por el cliente. Es condicional: no pisa una edición posterior hecha desde el panel. |
| `panel_alta.py` | Crea la página de cada obra nueva y baja sus fotos de Storage. **Va antes que el generador**: si la página no existe, el generador la saltea. |
| `panel_galerias.py` | Conecta hasta 15 fotos de cada obra histórica con el panel y aplica orden, portada, altas y bajas desde la primera edición. |
| `panel_generar.py` | Rellena título, bajada, ficha y memoria en todas las páginas publicadas. |
| `panel_sitio.py` | Saca del sitio las obras eliminadas o despublicadas. |
| `panel_estados.py` | Pone el sello "Obra"/"Proyecto" del listado de acuerdo con el estado de la base. **Va después de las altas y las bajas**, que son las que agregan y sacan tarjetas. |
| `panel_textos.py` | Escribe los 11 textos fijos de home, estudio y contacto. |
| `panel_home.py` | Pone las obras destacadas en los tres banners del home. |
| `prensa_pagina.py` | Genera `/prensa/publicaciones/` desde `docs/prensa-listado.html`, el archivo cronológico completo de prensa. |
| `en_gen.py` | Rehace `/en/` de cero y traduce lo que dejaron los pasos anteriores. |
| `sitemap_gen.py` | Rearma el sitemap leyendo las páginas en castellano y el espejo inglés ya generado. **Va último** para incluir ambas versiones. |

Si un paso falla, el deploy se corta y el sitio anterior sigue en pie: Vercel
no publica un build que no terminó.

### Dos cosas de Vercel que no son obvias

**`"outputDirectory": "."` en `vercel.json`.** Mientras no había comando de
build, Vercel servía la raíz del repositorio. En cuanto se define uno, espera
encontrar el sitio en una carpeta `public` y el deploy falla con *No Output
Directory named "public" found*. Nuestro sitio se arma en la raíz.

Y `vercel.json` **no admite comentarios ni claves inventadas**: una clave `"//"`
para explicar algo hace fallar la validación del esquema. Por eso esto está
acá y no en el archivo.

**`"cleanUrls": true`, o el panel no anda.** Los enlaces del panel van sin
extensión —`/admin/obras`, no `/admin/obras.html`— porque el servidor de
desarrollo perdía el `?id=` al redirigir de uno a otro. Vercel no resuelve eso
solo: sin `cleanUrls`, las cuatro pantallas dan 404 y, como el login manda a
`/admin/obras` al entrar, el panel queda inusable apenas alguien se loguea.

El sitio público no se ve afectado: sus enlaces son de directorio
(`/proyectos/moshu/`) y no hay ni un `href` a un `.html` fuera del panel.

**`.vercelignore` ya no excluye `docs/` entero.** No puede: los generadores
viven ahí y el build los necesita. Excluye las notas —que era lo sensible, por
`AUDITORIA-SEGURIDAD.md`— y del resto se encarga `panel_build.py`, que borra la
carpeta como último paso, ya en el servidor. Ese borrado mira la variable
`VERCEL`: en una máquina de desarrollo no se ejecuta.

## B7 · Fusionar la rama

Con B1 a B6 hechos, fusionar `panel` en `main`. El panel queda vivo en
`estudiohma.com/admin`.

`admin/config.js` ya no bloquea: lo genera `docs/panel_config.py` en el build,
desde `SUPABASE_URL` y `SUPABASE_ANON_KEY`. Aborta el deploy si falta alguna, o
si la clave que le pasan parece la de servicio — esa saltea el RLS y en el
navegador dejaría la base abierta.

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

- **Parfumerie**: la carátula está en 643 px; el resto ronda los 1200
- **Tres obras con sólo los dos socios en el equipo**: Accor, Iguanafix y
  Tostado. No hay más nombres en ninguna fuente
- **"Comitente" vacío en las 61 obras** — el sitio nunca mostró ese campo. El
  panel lo tiene; cuando haya varios cargados se enciende en el sitio con un
  cambio chico
- **Ualá II es la única obra con crédito de fotografía**, y el cliente pidió no
  mostrar créditos de foto en ninguna
