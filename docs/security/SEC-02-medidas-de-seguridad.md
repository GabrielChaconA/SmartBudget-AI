# SEC-02 – Medidas de seguridad propuestas (SBI-6)

Basado en [SEC-01](SEC-01-reporte-vulnerabilidades.md). Cada medida usa primero mecanismos
nativos de Laravel/Sanctum/Vite (sin dependencias nuevas), es compatible con la arquitectura
actual (Laravel + Sanctum + Octane/RoadRunner, Vue 3 SPA, PostgreSQL en Render) y evita
duplicar lógica.

## Prioridades

| Prioridad | Significado |
|---|---|
| **P0** | Inmediata: explotable hoy sin requisitos o secreto ya expuesto |
| **P1** | En este sprint (SEC-03) |
| **P2** | En este sprint si no hay regresión; si no, siguiente |
| **P3** | Requiere historia propia (cambio de arquitectura) |

## Medidas

| Hallazgo | Medida | Prioridad | Dónde |
|---|---|---|---|
| V-01 | Solo `Hash::check` (y solo si el valor guardado es un hash); migración que aplica `Hash::make` a contraseñas sin hash; `seed.sql` con hash bcrypt | P0 | SEC-03 |
| V-02 | Verificar que el fondo pertenece al usuario antes de crear/borrar asignaciones (404 si no); no modificar categorías globales existentes | P0 | SEC-03 |
| V-03 | Eliminar `GET /test-mail` y `POST /api/test-subscription-email` | P0 | SEC-03 |
| V-04 | **Rotar ya** todas las llaves `VITE_*` en los proveedores. Después, mover las llamadas a un proxy en el backend (llaves en `config/services.php`) | P0 rotación / P3 proxy | Acción manual + historia propia |
| V-05 | Login con Google con **código de un solo uso** (60 s, en caché) que el frontend canjea por el token vía `POST /api/auth/google/exchange`; `sanctum.expiration` configurable (7 días por defecto) | P1 | SEC-03 |
| V-05 (b) | Migrar de token en `localStorage` a sesión con cookie `HttpOnly` (Sanctum SPA) | P3 | Historia propia |
| V-06 | `RateLimiter` nativo: `throttle:auth` (5/min por email+IP, 20/min por IP) en login, registro y canje de Google; contraseña mínima de 8 (`Password::min(8)`) | P1 | SEC-03 |
| V-07 | Validar `key` (máx. 150) y `url` (https y host de API-Sports o Sportmonks), limitar el tamaño de la caché y aplicar `throttle` | P1 | SEC-03 |
| V-08 | Orígenes CORS explícitos: `FRONTEND_URL` + `CORS_ALLOWED_ORIGINS`; `localhost` solo fuera de producción; sin patrones comodín | P2 | SEC-03 |
| V-09 | Mover a `config/` (`app.frontend_url`, `services.cloudinary`, `services.finnhub`) y leer con `config()` | P1 | SEC-03 |
| V-10 | Borrar `test-cloud.js` y scripts de un solo uso; **eliminar el upload preset en Cloudinary**; `.dockerignore` para que `run_all.php`/`run_seed.php`/SQL no lleguen a la imagen; `chmod -R ug+rwX` en lugar de `777` | P0 preset / P2 resto | Acción manual + SEC-03 |
| V-11 | `npm audit fix` + mover `shadcn-vue` a `devDependencies`; `composer audit` en CI (SBI-31) | P2 | Siguiente (requiere validar el build del frontend) |
| V-12 | Mensaje genérico al cliente y registro del status en logs | P1 | SEC-03 |
| V-13 | `increment('balance', $amount)` del query builder | P2 | SEC-03 |
| V-14 | Quitar la ruta `exchange-rate` (no existe el controlador ni hay consumidores); consultar la inversión con el query builder en `InvestmentAlertController` | P2 | SEC-03 |
| V-15 | `exists:categories,id` | P2 | SEC-03 |
| V-16 | Policies/FormRequests al reorganizar el backend en controladores y servicios | P3 | Historia de arquitectura |

## Justificación de las decisiones principales

- **V-01 – migración en lugar de "doble verificación":** mantener la comparación en texto plano
  para no romper las cuentas del seed perpetúa el problema. La migración se ejecuta sola en el
  despliegue (`start.sh` corre `migrate --force`) y conserva la misma contraseña para el usuario.
- **V-02 – 404 y no 403:** no revela si el fondo existe para otro usuario. Se coordina con la
  historia de arquitectura: la verificación es una consulta acotada a la ruta, fácil de mover a una
  Policy cuando exista el controlador.
- **V-05 – código de un solo uso:** es el patrón estándar para devolver credenciales tras un
  redirect OAuth. El código caduca en 60 s, se consume una vez (`Cache::pull`) y el token ya no
  aparece en la URL, el historial ni el `Referer`. No requiere cambios en Socialite.
- **V-05 – expiración de 7 días:** el frontend ya maneja el 401 (borra el token y manda a
  `/login`), así que no requiere cambios adicionales.
- **V-06 – límite por email+IP y por IP:** el primero frena la fuerza bruta a una cuenta, el
  segundo el *credential stuffing* desde una IP. Ambos son nativos (`RateLimiter::for`).
- **V-04 – por qué no se implementa ahora:** el proxy afecta seis proveedores (incluido un
  WebSocket de Finnhub) y casi todos los servicios del frontend; necesita su propia historia y
  pruebas de UI. La **rotación de llaves no depende del código** y debe hacerse ya.

## Acciones manuales (fuera del código)

1. Rotar las llaves de Binance, Finnhub, FMP, The Odds API, API-Sports y Sportmonks.
2. Eliminar en Cloudinary el *upload preset* sin firmar que aparece en `test-cloud.js`
   (sigue en el historial de git aunque se borre el archivo).
3. Configurar en Render: `SANCTUM_EXPIRATION` (opcional), `CORS_ALLOWED_ORIGINS` (si hay más de un
   frontend), `FINNHUB_API_KEY` (backend), `CLOUDINARY_*`.
