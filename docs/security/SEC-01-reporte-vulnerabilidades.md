# SEC-01 – Reporte de verificación y análisis de vulnerabilidades (SBI-5)

- **Fecha:** 2026-11-19
- **Alcance:** backend Laravel (`backend/`: rutas, controladores, configuración, despliegue),
  frontend Vue (`frontend/`: manejo de credenciales y dependencias), scripts del repositorio y
  comunicación entre servicios.
- **Base revisada:** rama `develop` @ `8f5a729`.
- **Método:** revisión manual de código, verificación de los 11 hallazgos preliminares de la
  planeación, búsqueda de patrones (`env(`, `DB::raw`, `VITE_*`, rutas sin dueño) y `npm audit`.
  `composer audit` no pudo ejecutarse en el equipo de la auditoría (PHP bloqueado por la política
  de Device Guard); queda como pendiente en SEC-02.
- **Regla:** este documento no incluye correcciones; las medidas se definen en SEC-02 (SBI-6) y se
  implementan en SEC-03 (SBI-7).

## Escala de criticidad

| Nivel | Criterio |
|---|---|
| Crítica | Compromiso directo de cuentas o datos de cualquier usuario, sin requisitos previos |
| Alta | Acceso o modificación de datos de otros usuarios, o exposición de secretos |
| Media | Abuso del servicio, debilita controles de autenticación o afecta disponibilidad |
| Baja | Exposición menor de información, malas prácticas sin explotación directa hoy |
| Info | Causa raíz / deuda técnica que facilita otros hallazgos |

## Resumen

| ID | Hallazgo | Criticidad | Componente |
|---|---|---|---|
| V-01 | Login acepta la contraseña en texto plano y el seed guarda contraseñas sin hash | **Crítica** | `AuthController::login`, `seed.sql` |
| V-02 | IDOR en asignaciones de fondos + modificación de categorías globales | **Alta** | `POST/DELETE /api/funds/{id}/allocations` |
| V-03 | Endpoints de prueba de correo en producción (uno público) | **Alta** | `GET /test-mail`, `POST /api/test-subscription-email` |
| V-04 | Llaves de APIs de terceros expuestas en el bundle del frontend | **Alta** | `frontend/src/services/*` (`VITE_*`) |
| V-05 | Token de Sanctum en la URL, sin expiración y en `localStorage` | **Alta** | `GoogleAuthController::callback`, `config/sanctum.php` |
| V-06 | Sin límite de intentos en login/registro; contraseña mínima de 6 | Media | `POST /api/login`, `POST /api/register` |
| V-07 | Caché global de logos escribible por cualquier usuario | Media | `POST /api/sports/logos` |
| V-08 | CORS acepta cualquier subdominio `*.onrender.com` | Media | `config/cors.php` |
| V-09 | `env()` fuera de `config/` con `config:cache` activo | Media | Google, Cloudinary, Finnhub |
| V-10 | Scripts sueltos, *upload preset* de Cloudinary en el repo y `chmod -R 777` | Media | raíz y `backend/`, `Dockerfile` |
| V-11 | Dependencias del frontend con vulnerabilidades conocidas | Media | `frontend/package-lock.json` |
| V-12 | `uploadAvatar` devuelve el detalle de error de Cloudinary | Baja | `ProfileController::uploadAvatar` |
| V-13 | SQL construido por concatenación en `add-money` | Baja | `POST /api/accounts/add-money` |
| V-14 | Rutas rotas que responden 500 | Baja | `GET /api/exchange-rate`, `POST /api/investment-alerts` |
| V-15 | `category_id` de suscripciones sin validar | Baja | `POST /api/subscriptions` |
| V-16 | Lógica de negocio y autorización en closures de rutas | Info | `routes/api.php` |

Los 11 hallazgos preliminares se confirmaron (V-01 a V-10 y V-12). V-11, V-13, V-14, V-15 y V-16
son nuevos.

---

## Detalle

### V-01 – Contraseña aceptada en texto plano (Crítica)
- **Evidencia:** `backend/app/Http/Controllers/AuthController.php:63`
  `if ($user->password === $request->password) { $isValidPassword = true; }` antes de `Hash::check`.
  `seed.sql` inserta los 10 usuarios con `password = 'password'` sin hash.
- **Impacto:** cualquier contraseña guardada sin hash (seed, inserciones manuales) es válida tal
  cual; una filtración de la tabla `users` da acceso inmediato. Además, si alguien conoce el *hash*
  bcrypt de un usuario, puede enviarlo como contraseña y la comparación estricta lo acepta
  (*pass-the-hash*).
- **Afecta:** todas las cuentas.

### V-02 – IDOR en asignaciones de fondos (Alta)
- **Evidencia:** `backend/routes/api.php:180-236` (`POST /api/funds/{id}/allocations`) y
  `:238-251` (`DELETE /api/funds/{id}/allocations/{categoryName}`) usan `$id` sin comprobar que el
  fondo pertenezca a `$request->user()`. En contraste, `PUT /api/funds/{id}` (`:147-150`) sí filtra
  por `user_id`.
- **Impacto:** un usuario autenticado puede crear, modificar o borrar asignaciones de fondos de
  otros usuarios enumerando IDs. La notificación que se genera incluye el **nombre del fondo
  ajeno** (`:230`), lo que además filtra información. Con un `{id}` inexistente la ruta lanza 500.
- **Agravante:** `:198-202` actualiza el icono de una fila de `categories`, tabla **global**
  compartida por todos los usuarios: cualquier usuario cambia el icono que ven los demás.

### V-03 – Endpoints de prueba de correo (Alta)
- **Evidencia:** `backend/routes/web.php:9-16` `GET /test-mail` es **público**, busca al usuario 1
  y le envía un correo. `backend/routes/api.php:292-306` `POST /api/test-subscription-email`.
- **Impacto:** cualquiera en internet puede disparar correos ilimitados (abuso de la cuota de
  correo, posible bloqueo del remitente y spam al usuario 1). Si el usuario 1 no existe responde
  500 con traza si `APP_DEBUG` estuviera activo.

### V-04 – Llaves de APIs en el bundle público (Alta)
- **Evidencia:** `frontend/src/services/` lee `VITE_BINANCE_API_KEY`, `VITE_FINNHUB_API_KEY`
  (también en la URL del WebSocket, `finnhub.ts:46`), `VITE_FMP_API_KEY`, `VITE_ODDS_API_KEY`,
  `VITE_API_SPORTS_KEY`, `VITE_SPORTMONKS_API_KEY` / `VITE_SPORTMONKS_KEY`. Vite incrusta todas las
  variables `VITE_*` en el JavaScript público.
- **Impacto:** cualquiera puede extraer las llaves del sitio y consumir las cuotas o planes de
  pago asociados. Las llaves deben considerarse **ya comprometidas**.

### V-05 – Manejo del token de sesión (Alta)
- **Evidencia:** `GoogleAuthController.php:80` redirige a `FRONTEND_URL/login?token=<token>`;
  `config/sanctum.php:53` `'expiration' => null`; `frontend/src/views/LoginView.vue:32-34` y
  `composables/useAuth.ts` guardan el token en `localStorage`.
- **Impacto:** el token queda en el historial del navegador, en logs de proxies/servidores y puede
  filtrarse por `Referer`. Al no expirar, un token filtrado sirve indefinidamente. En
  `localStorage` es legible por cualquier script que logre ejecutarse en el sitio (XSS).

### V-06 – Fuerza bruta en autenticación (Media)
- **Evidencia:** `routes/api.php:8-9` sin middleware `throttle`; `AuthController.php:16`
  `min:6`.
- **Impacto:** permite *credential stuffing* y fuerza bruta sin freno; contraseñas débiles.

### V-07 – Caché global de logos (Media)
- **Evidencia:** `routes/api.php:322-331`: cualquier usuario autenticado escribe `key => url`
  arbitrarios en la entrada de caché `sports_logos`, que se sirve a **todos** los usuarios por
  `GET /api/sports/logos`. Sin validación de URL ni de tamaño.
- **Impacto:** otro usuario puede inyectar URLs de imágenes externas (rastreo de IPs, contenido
  ofensivo o *phishing* visual) y hacer crecer la caché sin límite (disponibilidad).

### V-08 – CORS permisivo (Media)
- **Evidencia:** `config/cors.php:26-29` patrón `/^https:\/\/.*\.onrender\.com$/`.
- **Impacto:** cualquier sitio alojado en Render puede invocar la API desde el navegador. El daño
  está acotado porque la autenticación es por *Bearer token* (no cookies,
  `supports_credentials=false`), pero amplía innecesariamente la superficie.

### V-09 – `env()` fuera de configuración (Media)
- **Evidencia:** `GoogleAuthController.php:79,86` (`FRONTEND_URL`), `ProfileController.php:41-43`
  (Cloudinary), `Console/Commands/CheckInvestmentAlerts.php:49` (`VITE_FINNHUB_API_KEY`).
  `start.sh:18` ejecuta `php artisan config:cache`; con la configuración en caché, `env()` devuelve
  `null` fuera de `config/`.
- **Impacto:** en producción el login con Google redirige a `http://localhost:5173`, la firma de
  Cloudinary se calcula con secreto `null` y el comando de alertas consulta Finnhub sin llave.
  Fallos silenciosos que tientan a "parches" inseguros.

### V-10 – Scripts sueltos y permisos (Media)
- **Evidencia:** `test-cloud.js` contiene el *cloud name* y un *upload preset* de Cloudinary
  (subida sin firmar). `backend/fix.php`, `run_all.php`, `run_seed.php`, `test_mail.php`,
  `create_table.php`, `create_tokens_table.php` se copian a la imagen de producción
  (`Dockerfile` hace `COPY . /app` sin `.dockerignore`). `Dockerfile:31` `chmod -R 777`.
- **Impacto:** con el preset cualquiera puede subir archivos a la cuenta de Cloudinary. Los scripts
  ejecutan SQL masivo (`run_all.php` corre `schema.sql`, que hace `DROP TABLE`) si alguien los
  ejecuta en el contenedor. `777` permite a cualquier proceso modificar caché y logs.

### V-11 – Dependencias vulnerables del frontend (Media)
- **Evidencia:** `npm audit --omit=dev`: 41 vulnerabilidades (1 crítica, 29 altas, 11 moderadas).
  Relevantes en el navegador: `axios`, `vue`/`@vue/server-renderer`, `vue-i18n`. La mayoría
  (`vite`, `postcss`, `undici`, `hono`, `@modelcontextprotocol/sdk`…) llegan por herramientas de
  build y por `shadcn-vue`, declarado como dependencia de producción.
- **Impacto:** riesgo principalmente en build/desarrollo; las de `axios`/`vue-i18n` requieren
  actualización.

### V-12 – Detalle de errores de Cloudinary (Baja)
- **Evidencia:** `ProfileController.php:68-71` devuelve `'details' => $response->json()`.
- **Impacto:** expone información interna del proveedor (configuración, mensajes) al cliente.

### V-13 – SQL por concatenación (Baja)
- **Evidencia:** `routes/api.php:67` `DB::raw('balance + ' . $amount)`.
- **Impacto:** hoy no es explotable porque `amount` se valida como `numeric`, pero el patrón es
  frágil ante cambios de validación.

### V-14 – Rutas rotas (Baja)
- **Evidencia:** `routes/api.php:316` apunta a `ExchangeRateController`, que no existe en ninguna
  rama; el frontend no la usa. `InvestmentAlertController.php:20` llama `$user->investments()`,
  relación que no existe en `User`.
- **Impacto:** ambas rutas responden 500 siempre.

### V-15 – `category_id` sin validar (Baja)
- **Evidencia:** `routes/api.php:282` `'category_id' => 'nullable|integer'`.
- **Impacto:** un ID inexistente provoca error de llave foránea (500).

### V-16 – Autorización dispersa (Info, causa raíz)
- **Evidencia:** casi toda la lógica vive en closures de `routes/api.php`; cada ruta repite (u
  olvida, ver V-02) el filtro `where('user_id', …)`. No hay Policies ni FormRequests.
- **Impacto:** facilita nuevos IDOR. La historia de arquitectura «Reorganización del backend en
  controladores y servicios» debe absorber este punto.

## Revisado sin hallazgos relevantes
- `PUT /api/funds/{id}`, `PUT/DELETE /api/investments/{id}`, `/api/notifications`,
  `/api/user`, `/api/user/transaction-stats`: filtran por el usuario autenticado.
- `GET /api/subscription-catalog`: usa *bindings* del query builder (sin inyección).
- `render.yaml`: `APP_DEBUG=false` en producción.
- Comunicación Laravel ↔ servicio de IA (ramas SBI-32…37): token interno comparado en tiempo
  constante, servicio publicado solo en `127.0.0.1`. Recomendación: `AI_DOCS_ENABLED=false` en
  producción.
