<?php

namespace App\Providers;

use App\Services\Ai\AiServiceClient;
use App\Services\Ai\AiSettingsRepository;
use App\Services\Ai\DatabaseAiSettingsRepository;
use Illuminate\Contracts\Foundation\Application;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        $this->app->bind(AiSettingsRepository::class, DatabaseAiSettingsRepository::class);

        // bind (no singleton): seguro con Octane y lee la config vigente en cada resolución.
        $this->app->bind(AiServiceClient::class, fn (Application $app) => new AiServiceClient(
            $app->make(AiSettingsRepository::class),
            (string) config('services.ai.url'),
            (string) config('services.ai.token'),
            (int) config('services.ai.timeout', 150),
            (int) config('services.ai.connect_timeout', 5),
        ));
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        //
    }
}
