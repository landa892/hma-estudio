# El sitio de Hitzig Militello Arquitectos

Sitio estático de un estudio de arquitectura. HTML, CSS y JS a mano, sin
framework. Se publica en Vercel, en estudiohma.com. El contenido de las obras
vive en una base Supabase y el sitio se arma en cada deploy.

Esto es lo que hay que saber antes de tocar nada. Casi todo salió de
equivocarse primero.

---

## Cómo se trabaja

**Directo en `main`.** Nada de ramas ni de pull requests. Cada push a `main`
dispara el deploy: **pushear es publicar.**

El cliente es el estudio; el interlocutor es el desarrollador. Las correcciones
llegan en documentos de Word con capturas marcadas a mano, y en audios. Cuando
un Word dice "X es A, no B", **A es lo correcto** — ese patrón ya se leyó al
revés una vez y se publicaron datos invertidos.

---

## Lo primero: el repositorio no es el sitio

El build corre en Vercel, genera el HTML desde la base y **el resultado nunca
vuelve al repositorio**. Por eso:

- El HTML que ves en el repo puede estar viejo. No es la verdad.
- **Un arreglo a mano en un HTML se pierde en el próximo deploy**, si ese dato
  lo escribe el build.
- Para cambiar contenido de una obra se toca `docs/panel_correcciones_agosto.py`,
  que aplica correcciones a la base durante el build, cada una guardada contra
  el valor viejo. Si el estudio edita ese campo desde el panel, la guarda deja
  de coincidir y la corrección no lo pisa.

### La regla de verificación

**Verificar contra el sitio publicado.** Ni contra el repositorio ni contra la
base. Las tres veces que se dio algo por terminado sin estarlo fue por mirar el
lugar equivocado:

- Se auditaron las galerías del repo y se informó que faltaban fotos. El Drive
  las tenía; el repo era una importación vieja y parcial.
- Se verificaron los textos contra la base y se dijo que estaban. La base los
  tenía y **la página no los mostraba**.
- Se dio un deploy por hecho sin mirar que había fallado.

```bash
curl -s https://estudiohma.com/proyectos/<slug>/ | grep -c "lo que sea"
```

### La clave pública sólo ve lo publicado

Leer la base desde acá con la clave publicable **no muestra los borradores**.
No es una limitación del código: es la política de lectura de
`0001_esquema.sql`, `using (publicada)`, y su comentario lo dice — "no salen ni
siquiera consultando la API a mano: es el punto del modo borrador".

Así que una obra despublicada **desaparece de todas mis consultas**, y contar
obras contra esa clave da lo que ve un visitante, no lo que hay. Ya me llevó
puesto una vez: Comedor Diario quedó en borrador, mi consulta devolvió 61 de 62
y di por hecho que alguien la había borrado del panel. Estaba intacta.

Para cualquier cosa que involucre borradores, la fuente es el panel, no la API.

### Las migraciones se aplican a mano, y una faltaba

`supabase/migrations/` es el orden en que hay que correrlas, no la prueba de
que se corrieron. Se ejecutan a mano en el editor SQL del panel de Supabase, y
saltearse una no deja rastro: las siguientes se aplican igual.

Pasó el 20/08/2026. La 0013 fallo con `function es_admin_hma() does not exist`
porque la **0009 nunca se habia aplicado**, aunque la 0010, la 0011 y la 0012
si. Mientras tanto la base siguio con las reglas de escritura de la 0001, que
son mucho mas abiertas que las que el repositorio da por hechas.

Antes de dar por sentado que una migracion esta puesta, preguntarle a la base.
Con la clave publicable alcanza para ver si existe una columna o una tabla:

```bash
curl -s -H "apikey: $CLAVE" "$URL/rest/v1/obras?select=ultimo_cambio&limit=1"
# 400 con "column obras.ultimo_cambio does not exist" -> la 0013 no esta
```

La 0013 arranca con un `do $$` que revienta con un mensaje en castellano si le
falta la 0009. Vale la pena repetir ese patron en cualquier migracion que
dependa de otra.

### Guardar y publicar son dos pasos, y el panel ahora lo dice

La confusión más cara del panel: alguien guarda una bajada, entra al sitio y la
ve igual. El cambio está en la base; el sitio son archivos y no cambia hasta
que se reconstruye.

Desde la migración 0013 hay un aviso arriba del listado que nombra lo que quedó
en el medio — "Roket (la bajada)" — y se apaga solo cuando el build termina.
Las piezas:

| Pieza | Qué hace |
|---|---|
| tabla `publicaciones` | una fila por build terminado |
| `docs/panel_publicado.py` | la escribe, como último paso del build |
| `obras.ultimo_cambio` | la frase en castellano; la escribe el panel al guardar |
| trigger `obra_imagenes_marcan_obra` | mover o borrar fotos marca la obra |
| `admin/pendientes.js` | compara y pinta |

Dos cosas para no romper: la marca la escribe el **build**, no el botón — si el
build falla el aviso se queda puesto, que es la verdad. Y `ultimo_cambio` no
sale de `recoger()` en `admin/obra.js`: si entrara, `hayCambios()` compararía un
campo que el formulario no muestra y toda obra se vería siempre modificada.

### El patrón que se repite: el dato está y no se ve

Pasó tres veces con distintos campos. El generador **sólo completaba lo que la
página ya tenía**, así que un dato cargado después no llegaba nunca:

- La ficha técnica no agregaba una fila que no existiera (IguanaFix tenía sus
  320 m² en la base y la ficha no mostraba superficie).
- La línea de datos bajo el título no la escribía nadie: 36 fichas sin año.
- La última columna del listado tampoco: 16 filas con un guion.

Ante un "falta este dato", **mirar primero si está en la base**. Si está, el
problema es el generador, no el contenido.

---

## El build

`docs/panel_build.py`, 18 pasos en orden:

```
panel_config · panel_correcciones_agosto · panel_alta · panel_galerias
panel_generar · panel_sitio · panel_listado · panel_estados
panel_textos · panel_home · obras_layout · prensa_pagina
prensa_paginas · en_gen · obras_orden · seo_gen
sitemap_gen · panel_publicado
```

`panel_publicado` va último y tiene que seguir yendo último: anota en la tabla
`publicaciones` la fecha contra la que el panel compara para avisar que hay
cambios guardados sin publicar. Los pasos anteriores también escriben en la
base, así que moverlo hacia arriba haría que el panel denunciara como
pendientes los cambios del propio build.

Variables de entorno en Vercel: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`,
`SUPABASE_ANON_KEY`.

Para leer la base desde acá alcanza la clave publicable, que es de sólo
lectura. `panel_config.py` aborta si le pasan una de servicio.

---

## Trampas conocidas

### El versionado de assets rompe los ids de YouTube

Los archivos llevan `?v=N` para invalidar caché. **Nunca hacer un reemplazo
general de `?v=N`**: pisa los ids de los videos de YouTube, que también son
alfanuméricos. El reemplazo va acotado:

```bash
sed -i 's/main\.css?v=93/main.css?v=94/g'
```

Y después se controla que sigan los 18 ids distintos, todos de 11 caracteres.

Ojo: `scripts/animations/*.js` y `scripts/config/gsap.js` **tienen su propia
versión**. Se cambió `scrollEffects.js` y quedó en la versión vieja: a quien
tuviera caché le seguía llegando el archivo sin el arreglo.

### El panel de vista previa no corre animaciones

No ejecuta `requestAnimationFrame`, así que las transiciones y las timelines de
GSAP **no avanzan** y las capturas de pantalla fallan. Medir ahí da valores del
primer cuadro: elementos en opacidad 0, campos en ancho 0. Antes de medir:

```js
if (window.gsap) gsap.globalTimeline.progress(1);
// o, para transiciones de CSS:
document.head.insertAdjacentHTML('beforeend',
  '<style>*{transition:none !important;animation:none !important}</style>');
```

Ya hubo tres falsos positivos por esto.

### Heredocs de bash con Python adentro

Un `\n` o un `\d` dentro de una cadena que no sea `r'...'` se come la barra y
corrompe el código generado. **Usar la herramienta Write** para cualquier
script con expresiones regulares.

---

## Las galerías

Cada obra tiene fotos en `assets/gallery/<slug>/`, planos en
`assets/planos/<slug>/` y carátula en `assets/covers/<slug>.webp`.

**El Drive del estudio es la fuente.** `docs/drive_sync.py` rehace todo desde
los ZIP que baja Google Drive, sin descomprimirlos:

```bash
python docs/drive_sync.py --verificar     # no escribe, informa
python docs/drive_sync.py --obra <slug>
python docs/drive_sync.py --catalogos     # sólo pone al día los catálogos
```

Corre en la máquina del desarrollador: necesita Pillow y los ZIP en
`HMA_DRIVE_ZIPS`. **Desde la nube no se puede.**

Dos cosas que hace y conviene no romper:

- **Descarta lo repetido.** El estudio guarda cada plano en dos idiomas — el
  mismo dibujo con los rótulos en castellano y en inglés — y a veces la misma
  foto dos veces. Se comparan las imágenes, no los nombres, con el corte en
  0,99.
- **Deja los catálogos al día** (`docs/planos.json` y las galerías de
  `docs/panel_datos.json`) y saca de las fichas las figuras cuyo archivo ya no
  existe. Sin eso, borrar un archivo deja una imagen rota: pasó con 18.

### Sacar una foto de una galería

Dos listas:

- `docs/galeria_repetidas.json` — automática, la escribe
  `docs/galeria_repetidas.py`. Son las fotos que **son** otra foto.
- `docs/galeria_excluidas.json` — a mano, con el motivo escrito. Para las que
  no están repetidas pero no van igual: dos tomas casi iguales, una lámina de
  presentación.

**La foto de apertura de una ficha no se toca nunca.** En varias obras la
primera foto de la galería *es* la carátula, y la exclusión apunta a la
repetición de más abajo. Sin esa salvedad se le cambia la foto principal a la
obra.

Y ojo: las galerías cuyas filas en la base son `@seed` **no las reescribe**
`panel_galerias`, para no pisar lo que el estudio haya elegido. Viven en el
HTML del repositorio. Por eso existe `sacar_excluidas_de_las_fichas()`.

### Los planos también están en el panel

Antes vivían aparte del todo: sólo `docs/planos.json` + `assets/planos/`, y un
paso de build (`planos_fichas.py`) los escribía directo en el HTML. El panel
de edición no los mostraba porque no estaban en la base — no era un bug, era
que el dato ni existía ahí.

Ahora son filas de `obra_imagenes` con `tipo='plano'`, igual que las fotos
(`tipo='foto'` es el default). `docs/planos.json` sigue siendo la entrada de
`drive_sync.py`: cada plano nuevo del Drive se siembra solo en la base la
próxima vez que corre `panel_galerias.py`, con el mismo mecanismo `@seed:` que
usan las fotos heredadas. Llevan su propio cupo de 15, separado del de fotos.

---

## El espejo en inglés

`docs/en_gen.py` **borra y regenera `en/` entero** desde las páginas en
castellano. No se edita nada dentro de `en/`.

Traduce con siete capas de diccionario (`docs/en_dic.py` … `en_dic7.py`). Todo
texto visible nuevo tiene que tener su entrada, o el guion lo reporta como
faltante. Lo que se agrega va en `en_dic7.py`.

Las memorias son la excepción: se sacan antes de traducir y se reemplazan por
la versión en inglés de la base, buscada por slug.

```bash
python docs/en_gen.py   # tiene que decir "sin faltantes"
```

---

## Nombres y decisiones ya tomadas

- Son **tres Ualá** distintos: **Ualá Gigena** (proyecto, 2022), **Ualá
  Nicaragua I** (obra, 2017) y **Ualá Nicaragua II** (obra concluida). El
  buscador automático los cruzaba; van fijos en `A_MANO`, en `drive_sync.py`.
- **Novotel** va sin memoria descriptiva: su carpeta del Drive tiene sólo ficha
  técnica. Decisión tomada, no es un pendiente.
- **Abasto Patio de Comidas** es la única obra sin carpeta en el Drive.
- El archivo `Elyaki - Memoria Descriptiva.doc` **contiene el texto de Mamba
  Bar**, palabra por palabra. No es un título mal puesto. La ficha de Elyaki
  tiene un texto propio que se queda.

---

## Escribir en este proyecto

Los comentarios y los mensajes de commit van **en castellano**, sin tildes en
el código y con tildes en el texto de las páginas. Explican **por qué**, no
qué: casi todos los comentarios del repositorio cuentan qué se rompió y cómo se
llegó al número que está escrito. Seguir esa línea.

Los mensajes de commit son largos a propósito: cuentan el síntoma, la causa y
la medición que confirma el arreglo.
