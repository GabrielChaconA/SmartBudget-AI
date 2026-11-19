<?php

namespace App\Services\Ai;

use Illuminate\Http\Client\Response;
use Illuminate\Http\JsonResponse;
use RuntimeException;
use Throwable;

/**
 * El servicio de IA no respondió (503/504, conexión rechazada, timeout u otro error).
 * Laravel la convierte automáticamente en una respuesta 503 sin detalles internos.
 */
class AiServiceUnavailable extends RuntimeException
{
    public function __construct(
        public readonly string $reason,
        public readonly ?int $upstreamStatus = null,
        ?Throwable $previous = null,
    ) {
        parent::__construct("AI service unavailable ({$reason})", 0, $previous);
    }

    public static function fromResponse(Response $response): self
    {
        $reason = match ($response->status()) {
            504 => 'timeout',
            503 => 'unavailable',
            401 => 'unauthorized',
            default => 'error',
        };

        return new self($reason, $response->status());
    }

    public static function connectionFailed(Throwable $previous): self
    {
        $timedOut = str_contains(strtolower($previous->getMessage()), 'timed out')
            || str_contains($previous->getMessage(), 'cURL error 28');

        return new self($timedOut ? 'timeout' : 'connection', null, $previous);
    }

    /**
     * Ya se registra un warning en AiServiceClient; no se reporta como error.
     */
    public function report(): void {}

    public function render(): JsonResponse
    {
        return response()->json([
            'message' => 'El asistente de IA no está disponible en este momento. Intenta de nuevo más tarde.',
            'error' => ['code' => 'ai_unavailable'],
        ], 503);
    }
}
