<?php

namespace App\Services\Ai;

use Illuminate\Http\JsonResponse;
use RuntimeException;

/**
 * El usuario desactivó la IA (settings.ai_enabled = false): no se llama al servicio.
 */
class AiDisabledForUser extends RuntimeException
{
    public function __construct()
    {
        parent::__construct('AI is disabled for this user');
    }

    public function report(): void {}

    public function render(): JsonResponse
    {
        return response()->json([
            'message' => 'El asistente de IA está desactivado en tu configuración.',
            'error' => ['code' => 'ai_disabled'],
        ], 403);
    }
}
