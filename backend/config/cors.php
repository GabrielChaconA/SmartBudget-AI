<?php

/*
|--------------------------------------------------------------------------
| Cross-Origin Resource Sharing (CORS) Configuration
|--------------------------------------------------------------------------
|
| SEC-03 / V-08: solo orígenes explícitos, sin comodines.
| - FRONTEND_URL: frontend de producción.
| - CORS_ALLOWED_ORIGINS: orígenes extra separados por comas (p. ej. previews).
| - localhost solo fuera de producción.
|
*/

$localOrigins = [
    'http://localhost:5173',
    'http://localhost:3000',
    'http://127.0.0.1:5173',
];

$extraOrigins = array_map('trim', explode(',', (string) env('CORS_ALLOWED_ORIGINS', '')));

return [

    'paths' => ['api/*', 'sanctum/csrf-cookie'],

    'allowed_methods' => ['*'],

    'allowed_origins' => array_values(array_unique(array_filter(array_merge(
        env('APP_ENV', 'production') === 'production' ? [] : $localOrigins,
        [env('FRONTEND_URL')],
        $extraOrigins,
    )))),

    'allowed_origins_patterns' => [],

    'allowed_headers' => ['*'],

    'exposed_headers' => [],

    'max_age' => 0,

    'supports_credentials' => false,

];
