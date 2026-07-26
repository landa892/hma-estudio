# Auditoría de seguridad, buenas prácticas y rendimiento — HMA Estudio

**Fecha:** 2026-07-26 · **Alcance analizado:** repositorio `landa892/hma-estudio`, configuración de GitHub, dependencias locales (MCP shadcn), código del sitio (`index.html`) y la máquina de desarrollo desde la que se opera.

## 0. Contexto real del proyecto (importante)

Este proyecto **es un sitio estático de una sola página** (`index.html` + `/assets`), sin backend, sin base de datos, sin sistema de usuarios/contraseñas y sin servidor propio en el repo. Por eso varias categorías clásicas de un audit de infraestructura (servidores, APIs, auth, DB) **no aplican** — se documentan como "N/A" en vez de inventar riesgo donde no lo hay. Lo que sí es real y se auditó a fondo:

- El repositorio en GitHub (código fuente, historial, permisos).
- Las dependencias de herramientas de desarrollo (MCP de shadcn).
- El código del frontend (`index.html`, JS inline, recursos externos).
- La máquina local desde donde se hacen los commits/push (puertos, firewall, credenciales de git).
- El futuro hosting estático (no configurado todavía — se dejan cabeceras listas para cuando se elija).

## 1. Hallazgos por capa

### 1.1 Infraestructura / cuenta de GitHub

| # | Hallazgo | Severidad | Evidencia |
|---|---|---|---|
| G1 | Rama `main` **sin protección**: se puede pushear directo o forzar sin PR/revisión. | 🔴 Alta | `gh api repos/.../branches/main/protection` → 404 "Branch not protected" |
| G2 | **Dependabot / alertas de vulnerabilidad desactivadas** en el repo. | 🟠 Media | `gh api .../vulnerability-alerts` → "disabled" |
| G3 | Repo **público** — correcto para un sitio de marketing, pero implica que cualquier commit futuro con datos sensibles queda expuesto para siempre en el historial. | 🟡 Info | `visibility: PUBLIC` |
| G4 | Autenticación de `git`/`gh` vía Git Credential Manager y Windows Credential Keyring (no hay tokens en texto plano en el repo ni en `.git/config`). | ✅ OK | revisado `credential.helper`, remotes, historial completo |

### 1.2 Dependencias (toolchain local, no el sitio en sí)

| # | Hallazgo | Severidad | Evidencia |
|---|---|---|---|
| D1 | 3 vulnerabilidades **moderadas** (path traversal vía backslash codificado en Windows) en `@hono/node-server`, dependencia transitiva del servidor MCP de `shadcn`. | 🟠 Media | `npm audit` → GHSA-frvp-7c67-39w9 |
| D2 | Mitigante real: el servidor MCP usa `StdioServerTransport` (stdin/stdout), **no abre ningún puerto TCP/HTTP** — el path traversal de un servidor HTTP no aplica a este uso concreto. | ✅ Mitigado | grep en `node_modules/shadcn/dist` confirma stdio, no `createServer`/`listen` |
| D3 | `node_modules/` nunca se commiteó (verificado en todo el historial); ya está en `.gitignore`. | ✅ OK | `git log --all --diff-filter=A` |

### 1.3 Código del sitio (frontend — no hay backend)

| # | Hallazgo | Severidad | Evidencia |
|---|---|---|---|
| C1 | **Sin cabeceras de seguridad** (CSP, X-Frame-Options, HSTS, etc.) porque no había config de hosting. | 🟠 Media | no existía `_headers`/`netlify.toml`/`vercel.json` |
| C2 | Fuentes cargadas desde Google Fonts (`fonts.googleapis.com`) sin aviso de privacidad — transfiere la IP del visitante a Google en cada carga. | 🟡 Info | uso estándar, bajo riesgo, pero es un dato a declarar si hay política de privacidad |
| C3 | Email de contacto en texto plano (`mailto:`) — expuesto a scraping de spam. | 🟢 Baja | aceptable para un sitio de contacto público |
| C4 | Sin `usuarios/contraseñas`: no hay login, formularios que posteen datos, ni cookies — **superficie de ataque de auth = 0** porque no existe. | ✅ N/A | revisión de código completa |
| C5 | Sin inputs de usuario ni `innerHTML` con datos externos — el único uso de `innerHTML`/`textContent` dinámico toma contenido ya presente en el propio HTML, no datos de terceros. Riesgo de XSS clásico: prácticamente nulo. | ✅ OK | revisión de `index.html` |

### 1.4 Máquina local (desde donde se administra el repo)

| # | Hallazgo | Severidad | Evidencia |
|---|---|---|---|
| M1 | **Puerto 445 (SMB)** y **139 (NetBIOS)** escuchando en la interfaz de red LAN (`0.0.0.0` / `192.168.1.8`), no solo en loopback. Riesgo real si se conecta a redes no confiables (wifi público, coworking). | 🟠 Media | `Get-NetTCPConnection -State Listen` |
| M2 | `spacedeskService` (puerto 28252) y `EpicGamesLauncher` (24563) escuchando en **todas las interfaces** (`0.0.0.0`) en vez de solo loopback/LAN de confianza. | 🟡 Baja | idem |
| M3 | Firewall de Windows **activo** en los 3 perfiles (Dominio/Privado/Público). | ✅ OK | `Get-NetFirewallProfile` |
| M4 | Microsoft Defender **activo** con protección en tiempo real y firmas actualizadas. | ✅ OK | `Get-MpComputerStatus` |
| M5 | Estado de **BitLocker no verificable** sin privilegios de administrador — no se pudo confirmar si el disco está cifrado. | ⚪ Pendiente | `manage-bde` requirió elevación |

## 2. Plan de remediación (priorizado por sensibilidad real)

### Prioridad 1 — Gobernanza del repo (más sensible: previene pérdida de código/histórico)
1. **Proteger la rama `main`**: requerir PR antes de mergear, exigir que el status quede verde, prohibir force-push. *(Requiere tu OK porque cambia configuración de la cuenta de GitHub — decime y lo activo con `gh api`.)*
2. **Activar Dependabot / vulnerability alerts** en el repo. *(Idem, requiere tu OK.)*

### Prioridad 2 — Higiene de dependencias
3. Ya identificado: `npm audit fix --force` resuelve D1 pero **desinstala la versión actual de `shadcn` a `3.8.3`** (cambio breaking). Como es una herramienta de desarrollo local (no corre en producción ni abre puertos), lo recomendable es *esperar* al próximo `shadcn@latest` que ya traiga el fix, en vez de forzar un downgrade. Si preferís forzarlo ahora, decímelo.

### Prioridad 3 — Cabeceras de seguridad del sitio (ya aplicado)
4. ✅ Agregado `/_headers` con CSP, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`, `Strict-Transport-Security` y cache inmutable para `/assets/*`. Se activa automáticamente si el hosting es Netlify (u otro compatible); si eligen otro proveedor, hay que trasladar estas reglas a su formato (`vercel.json`, `.htaccess`, etc. — avisen qué hosting usan y lo adapto).
5. ✅ Agregado el mismo CSP como `<meta http-equiv>` en el `<head>` — funciona como respaldo sin importar el hosting.
6. ✅ Agregado `robots.txt` básico.

### Prioridad 4 — Higiene de la máquina local
7. Restringir el alcance de SMB/NetBIOS a la red privada de confianza (o desactivar "Compartir archivos e impresoras" si no se usa realmente entre dispositivos de la LAN).
8. Revisar si `spacedesk` necesita estar accesible desde toda interfaz o puede limitarse a la LAN de confianza.
9. Verificar cifrado de disco (BitLocker) con una sesión de administrador.

### Prioridad 5 — Rendimiento (ver sección 3)
10. Optimizar y comprimir imágenes (impacto más alto en performance real).

## 3. Análisis de rendimiento (post-cambios)

- **Peso de `/assets`: ~22 MB** en JPG sin variantes WebP/AVIF ni compresión agresiva — es, por lejos, el mayor cuello de botella de carga (ej. `manduca.jpg` 1.4 MB, `moshu.jpg` 1.3 MB).
- Ya en la sesión anterior se agregó `loading="lazy"` + `decoding="async"` a toda imagen fuera del viewport inicial, `preload` con `fetchpriority="high"` para el hero, y ahora se suma `Cache-Control: immutable` de 1 año para `/assets/*` vía `_headers`.
- **Recomendación de mayor impacto:** convertir las imágenes a WebP (o AVIF) con `<picture>`/fallback, apuntando a ~150–250 KB por foto de portfolio y ~80 KB para las del marquee. Esto podría bajar el peso total de 22 MB a ~4–5 MB sin pérdida visual perceptible.
- El resto (fonts con `preconnect`, JS vanilla sin frameworks, CSS inline sin build step) ya es liviano — no hay más ganancia relevante ahí sin agregar un pipeline de build.

## 4. Recomendaciones de mantenimiento (ágil, recurrente)

| Frecuencia | Acción |
|---|---|
| Cada PR | Revisar el diff antes de mergear (ya no se puede pushear directo a `main` una vez activada la protección). |
| Mensual | `npm audit` sobre este repo y sobre cualquier tooling local nuevo. |
| Mensual | Revisar `gh api repos/.../vulnerability-alerts` / tab "Security" de GitHub. |
| Al agregar imágenes nuevas | Comprimir/convertir a WebP antes de subir (mantener el patrón de carpeta `assets/gallery/<slug>/1..6.jpg`). |
| Al cambiar de hosting | Portar las reglas de `/_headers` al formato del nuevo proveedor. |
| Semestral | Revisar si sigue sin haber BitLocker/cifrado de disco en la máquina de trabajo. |
| Semestral | Repasar permisos de colaboradores del repo (`gh api repos/.../collaborators`). |

## 5. Resumen ejecutivo

- **No hay backend, base de datos ni login que proteger** — el "ataque de infraestructura" real hoy es mínimo porque la superficie es un sitio estático.
- Los riesgos reales encontrados son de **gobernanza de repo** (rama sin protección) y de **higiene de red local** (SMB expuesto en LAN), no del código del sitio.
- El código del sitio ya estaba razonablemente bien escrito (sin XSS evidente, sin inputs de usuario); se le sumaron cabeceras de seguridad como capa adicional preventiva de cara a un futuro hosting/CMS.
- El cuello de botella de performance real es el **peso de las imágenes**, no el código.
