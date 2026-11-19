<?php

namespace App\Services\Ai;

interface AiSettingsRepository
{
    /**
     * Indica si el usuario tiene la IA activada (settings.ai_enabled).
     */
    public function aiEnabled(int $userId): bool;
}
