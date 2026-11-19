# SEC-03 – Implementación y validación de medidas de seguridad (SBI-7)

Implementa las medidas P0–P2 de [SEC-02](SEC-02-medidas-de-seguridad.md) que se resuelven en
código. Las pruebas de validación están en
`backend/tests/Feature/Security/RouteSecurityTest.php`.

## Cambios por hallazgo

| Hallazgo | Cambio | Archivos | Prueba |
|---|---|---|---|
| V-01 | El login solo acepta `Hash::check` contra un valor que sea hash; se eliminó la comparación en texto plano. Migración idempotente que aplica hash a las contraseñas en texto plano (las cuentas conservan su contraseña). `seed.sql` usa hash bcrypt | `AuthController`, `database/migrations/2026_11_19_000000_hash_plaintext_user_passwords.php`, `seed.sql`, `backend/seed.sql` | `test_login_rejects_password_stored_in_plaintext`, `test_login_rejects_the_stored_hash_sent_as_password`, `test_login_accepts_hashed_password`, `test_migration_hashes_plaintext_passwords_and_keeps_them_usable` |
| V-02 | `POST` y `DELETE /api/funds/{id}/allocations` verifican que el fondo sea del usuario (404 si no). Ya no se modifica el icono de una categoría global existente | `routes/api.php` | `test_cannot_create_allocation_in_another_users_fund`, `test_cannot_delete_allocation_in_another_users_fund`, `test_owner_can_*`, `test_allocation_does_not_modify_existing_global_category` |
| V-03 | Eliminados `GET /test-mail` y `POST /api/test-subscription-email` | `routes/web.php`, `routes/api.php` | `test_test_mail_routes_are_removed` |
| V-05 | Login con Google: el callback redirige con un **código de un solo uso** (60 s, hash en caché) y el frontend lo canjea en `POST /api/auth/google/exchange`. Tokens con expiración (`SANCTUM_EXPIRATION`, 7 días por defecto) y limpieza diaria `sanctum:prune-expired` | `GoogleAuthController`, `routes/api.php`, `config/sanctum.php`, `routes/console.php`, `frontend/src/views/LoginView.vue` | `test_google_callback_returns_one_time_code_instead_of_token`, `test_google_exchange_rejects_unknown_code`, `test_tokens_expire_by_default` |
| V-06 | `throttle:auth` (5/min por email+IP y 20/min por IP) en login, registro y canje de Google. Contraseña mínima de 8 | `app/Providers/SecurityServiceProvider.php`, `bootstrap/providers.php`, `routes/api.php`, `AuthController` | `test_login_is_rate_limited_per_account`, `test_register_requires_at_least_eight_characters`, `test_register_succeeds_with_valid_password` |
| V-07 | `POST /api/sports/logos`: `key` máx. 150, `url` https de `*.api-sports.io` o `*.sportmonks.com`, máximo 5000 entradas, `throttle:60,1` | `routes/api.php` | `test_sports_logo_rejects_untrusted_urls`, `test_sports_logo_accepts_known_cdn_urls` |
| V-08 | CORS sin comodines: `FRONTEND_URL` + `CORS_ALLOWED_ORIGINS`; `localhost` solo fuera de producción | `config/cors.php` | `test_cors_rejects_arbitrary_onrender_origin`, `test_cors_allows_local_frontend_outside_production` |
| V-09 | `FRONTEND_URL`, Cloudinary y Finnhub se leen con `config()` (`app.frontend_url`, `services.cloudinary`, `services.finnhub`) | `config/app.php`, `config/services.php`, `GoogleAuthController`, `ProfileController`, `CheckInvestmentAlerts` | cubierto por las pruebas de Google y avatar |
| V-10 | Eliminados `test-cloud.js`, `backend/fix.php`, `test_mail.php`, `create_table.php`, `create_tokens_table.php` (sustituidos por migraciones). `.dockerignore` deja fuera `.env`, `*.sql`, `run_all.php`, `run_seed.php` y `tests/`. `chmod -R ug+rwX` en lugar de `777` | raíz, `backend/.dockerignore`, `backend/Dockerfile` | — |
| V-12 | `uploadAvatar` responde un error genérico; el detalle del proveedor solo va a logs | `ProfileController` | `test_avatar_upload_error_does_not_leak_provider_details` |
| V-13 | `increment('balance', $amount)` en lugar de `DB::raw` concatenado | `routes/api.php` | `test_add_money_increments_cartera_balance` |
| V-14 | Quitada la ruta `GET /api/exchange-rate` (controlador inexistente, sin consumidores). `InvestmentAlertController` consulta la inversión con el query builder | `routes/api.php`, `InvestmentAlertController` | `test_broken_exchange_rate_route_is_removed`, `test_investment_alert_can_be_created` |
| V-15 | `category_id` con `exists:categories,id` | `routes/api.php` | `test_subscription_with_unknown_category_is_rejected` |

## Sin regresiones
- Las rutas mantienen sus respuestas de éxito; solo cambian los casos que antes eran inseguros
  (404 en fondos ajenos, 422 en datos inválidos, 429 por exceso de intentos).
- El frontend ya maneja el 401 por token vencido (`main.ts` borra el token y manda a `/login`).
- Las pruebas usan SQLite en memoria (`phpunit.xml`) y no dependen de servicios externos
  (`Http::fake()`, `Mail::fake()`, Socialite simulado). `tests/Concerns/CreatesLegacyTables.php`
  crea las tablas que aún no tienen migración; se elimina cuando SBI-31 agregue las migraciones.
- Validación de lógica en un solo lugar: el límite de intentos vive en `SecurityServiceProvider` y
  la verificación de propiedad del fondo es una sola consulta por ruta, lista para moverse a una
  Policy en la historia de arquitectura (V-16).

## Configuración necesaria en el despliegue
- `FRONTEND_URL` (ya existe en Render), `SANCTUM_EXPIRATION` opcional, `CORS_ALLOWED_ORIGINS`
  si hay más frontends, `FINNHUB_API_KEY`, `CLOUDINARY_*`.
- La migración de contraseñas corre sola con `php artisan migrate --force` (`start.sh`).

## Pendiente (fuera de este cambio)
- **V-04:** rotar las llaves `VITE_*` ya expuestas (acción manual inmediata) y crear la historia del
  proxy en el backend.
- **V-05 (b):** sesión con cookie `HttpOnly` en lugar de `localStorage` (historia propia).
- **V-10:** eliminar en Cloudinary el *upload preset* que estaba en `test-cloud.js` (sigue en el
  historial de git).
- **V-11:** `npm audit fix` y `composer audit` en CI (SBI-31).
- **V-16:** Policies/FormRequests en la reorganización del backend.
