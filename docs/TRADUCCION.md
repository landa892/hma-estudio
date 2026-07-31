# Cómo se mantiene el sitio en inglés

El castellano es la fuente. `/en/` es un **espejo generado**: no se edita a
mano, se regenera. Editás el castellano y volvés a correr el generador.

```bash
python docs/en_gen.py
```

Eso borra `/en/` entero y lo vuelve a escribir desde las páginas en
castellano: traduce los textos, reescribe los enlaces internos, cambia el
`lang`, arma el `hreflang` y pone el botón de idioma en las dos versiones.
Correrlo dos veces seguidas da exactamente el mismo resultado.

## Las piezas

| archivo | qué hace |
|---|---|
| `en_gen.py` | el generador |
| `en_rutas.py` | `/proyectos/` ↔ `/en/projects/` y la reescritura de enlaces |
| `en_dic.py` | interfaz, fichas técnicas, reglas de patrones |
| `en_dic2.py` | superficies, titulares de prensa, más patrones |
| `en_dic3.py` | nombres propios que no se traducen y los textos largos |

## Si agregás texto nuevo en castellano

El generador **avisa** lo que no supo traducir, con el conteo:

```
SIN TRADUCIR (3 distintas):
    1 x Un restaurante nuevo en Palermo...
```

Cada línea de esas se agrega a `en_dic3.py` y se vuelve a correr. Mientras
diga `sin faltantes`, no quedó nada en castellano.

## Tres trampas que ya costaron una vez

1. **Los textos que arma el JavaScript no pasan por acá.** Los estados de los
   formularios, el conteo del buscador y los rótulos de los botones salen de
   `scripts/main.js`, que es uno solo para los dos idiomas. Ahí se usa
   `T('castellano', 'inglés')`, que elige por el `lang` del documento. Texto
   nuevo en el script va con `T()`.

2. **El índice del buscador es un archivo aparte.** `scripts/search-index.js`
   tiene su gemelo `search-index-en.js`, con las urls de `/en/`. Si se
   regenera el índice en castellano, hay que regenerar el inglés (el bloque
   está al final de `en_gen.py`).

3. **Los rótulos de "ver más" viven en el HTML**, en `data-mas` y
   `data-menos`, justamente para que el generador los traduzca. Si se agrega
   una galería nueva, el botón tiene que traer esos dos atributos.
