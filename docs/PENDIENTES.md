# Pendientes

Al 23/08/2026. Lo que queda de los tres Word del 21/08 y de lo que salio al
auditar. Todo lo demas de esos Word esta hecho y verificado contra
estudiohma.com, no contra el repositorio.

Este archivo no se publica: `.vercelignore` excluye `docs/*.md`.

---

## Los destraba el estudio

### 1. Confirmar 63 obras de prensa

115 de las 210 notas no tienen cargada la obra de la que hablan. Sin ese dato
la nota no puede mostrar ni la caratula de la obra como tapa provisoria.

Hay 63 con propuesta, sacada del titulo de la nota o de la URL del medio. Estan
en la pagina de revision, cada una con el enlace a la nota de un lado y a la
ficha de la obra del otro, para poder compararlas.

**No aplicar sin revisar.** El cruce por nombre en este sitio ya fallo una vez:
"Malita" cruzo con "Edificio Malabia", que es otra obra. Los ambiguos quedaron
afuera a proposito: "Uala" son tres obras distintas y "Kavak" son dos.

Cuando el estudio confirme, van a `panel_correcciones_agosto.py` con
`completar_vacio()`, para que una edicion posterior desde el panel no se pise.

### 2. Asignar las 369 imagenes rescatadas

Estan en `docs/rescate_prensa/` a 1600 px, y en la pagina de revision a 600 px
para poder mirarlas todas juntas. 123 tienen una nota candidata, que sale de
comparar el nombre del archivo con el medio y el titulo de la nota y pide dos
palabras en comun. Es una pista: emparejando solo por titulo daba 142
candidatos para una sola nota.

Las que el estudio confirme se copian a `assets/prensa/<slug>/` como el resto.

### 3. Fotografo de siete obras concluidas

    antiche  galeria-objeto-a  indusparquet  iol  parfumerie  roket  uala-office

Las otras 39 se completaron desde el campo `fotografias_proyecto` del WordPress
viejo. Antiche tiene el dato pero las direcciones se contradicen -la base dice
Nueva York 4002, Villa Devoto y el WordPress dice Libertador y Juramento- y una
foto no se firma con la duda. Las otras seis el WordPress nunca las tuvo.

Se cargan desde el panel, en la ficha de cada obra. El renglon aparece solo si
la obra esta concluida y el campo tiene algo, que es lo que pide el segundo
Word del 21/08.

### 4. Dos notas para subir al Drive

    archdaily-com-2014           Oficina + casa Luna, feb 2014 - jul 2014 - may 2017
    entrevista-los-destacados-2019   dic 2019

Sin escaneo, sin obra asociada y sin caratula que sirva de provisoria. El
archivo web no las tiene.

Las otras 22 sin tapa se resuelven solas en cuanto se confirme el punto 1: 18
tienen link, y para esas el tercer Word del 21/08 dice que no hace falta foto
-"al clickear te lleva directo a la pagina, total ya existe"-.

### 5. Pais de 41 notas de prensa

Falta el dato, no la estructura. El estudio decidio el 23/08 dejarlo para mas
adelante.

### 6. Actualizar Instagram y LinkedIn a mano

En `/admin/novedades`, cada vez que el estudio publique algo nuevo.

El tercer Word pedia que se actualizara solo. Se puede en YouTube y ya esta
hecho: `/api/youtube-latest` devuelve el ultimo video de verdad. En LinkedIn e
Instagram no: `/api/linkedin-latest` contesta `"automatic": false` porque
Instagram dio de baja la API publica y LinkedIn la reserva a partners
aprobados. La segunda opcion que ofrecia el propio Word -poder cambiarlo desde
el panel- es la que quedo.

---

## Cerrado el 23/08

- **El indice lateral del Inicio queda con los siete puntos.** El Word del
  21/08 pide "TODOS los items" y contradice al del 19/08, que pedia cuatro. El
  estudio confirmo que manda el mas nuevo.
- **El orden del grid de Trabajos ya era el pedido.** La captura numeraba
  1 FEHGRA, 2 Movistar Arena, 3 Cien, 4 Roket, y el sitio publica exactamente
  esa secuencia en las posiciones 17 a 20. La captura mostraba el orden viejo.
- **El panel de Prensa ya lista los escaneos de cada nota.** Se siembran como
  `@seed:` con `docs/prensa_galerias.py`, igual que las galerias de obra: las
  983 imagenes de las 184 notas que tienen. Antes la galeria salia vacia y no
  se podia reordenar, elegir tapa ni sacar una.

---

## Como se verifica

Contra el sitio publicado, nunca contra el repositorio ni contra la base: el
build no commitea de vuelta y el HTML del repo puede estar viejo.

    curl -s https://estudiohma.com/proyectos/<slug>/ | grep -c "lo que sea"

Y para los borradores, el panel: la clave publicable solo ve lo publicado, asi
que una obra despublicada no aparece en ninguna consulta hecha con ella.
`docs/panel_datos.json` es una copia y envejece: el 23/08 daba a Banco
Supervielle como despublicada cuando la base decia que si.

La tabla `publicaciones` -la que alimenta el aviso de "hay cambios guardados
sin publicar"- tiene su politica restringida a usuarios autenticados, asi que
desde afuera devuelve cero filas siempre y no se puede saber si esta vacia. Esa
se mira desde el panel. `prensa_imagenes` no: esa tiene lectura publica, y
desde el 23/08 la llena `docs/prensa_galerias.py` en cada build con los
escaneos historicos de cada nota.
