<?php

namespace App\Providers;

use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\ServiceProvider;

/**
 * Configuración de seguridad transversal (SEC-03). Se mantiene separada de
 * AppServiceProvider para que cada proveedor tenga una sola responsabilidad.
 */
class SecurityServiceProvider extends ServiceProvider
{
    public const AUTH_ATTEMPTS_PER_ACCOUNT = 5;

    public const AUTH_ATTEMPTS_PER_IP = 20;

    public function boot(): void
    {
        // V-06: frena fuerza bruta a una cuenta (email + IP) y credential stuffing (IP).
        RateLimiter::for('auth', function (Request $request) {
            $email = strtolower(trim((string) $request->input('email')));

            return [
                Limit::perMinute(self::AUTH_ATTEMPTS_PER_ACCOUNT)->by('auth:account:' . $email . '|' . $request->ip()),
                Limit::perMinute(self::AUTH_ATTEMPTS_PER_IP)->by('auth:ip:' . $request->ip()),
            ];
        });
    }
}
