<?php

namespace App\Services\Ai;

use App\Models\User;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\Client\PendingRequest;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use stdClass;

/**
 * Único punto de Laravel que llama al servicio interno de IA (ai-service).
 * Los controladores (SBI-11, SBI-14) usan esta clase; nunca llaman al servicio
 * Python directamente.
 *
 * - Si settings.ai_enabled es false para el usuario, lanza AiDisabledForUser sin llamar.
 * - Errores 503/504, conexión rechazada o timeout -> AiServiceUnavailable (se responde 503).
 * - Nunca registra el contexto financiero ni los mensajes del usuario.
 */
class AiServiceClient
{
    public function __construct(
        private readonly AiSettingsRepository $settings,
        private readonly string $baseUrl,
        private readonly string $token,
        private readonly int $timeout = 150,
        private readonly int $connectTimeout = 5,
    ) {}

    /**
     * @param  array<string, mixed>  $context  Contexto de FinancialContextBuilder (SBI-10)
     * @param  array<int, array{role: string, content: string}>  $history
     * @return array{status: string, reply: string, intent: string, prompt_version: string, model: ?string, purchase?: ?array}
     */
    public function chat(User|int $user, array $context, array $history, string $message, string $language = 'es'): array
    {
        return $this->post($user, '/v1/chat', [
            'context' => $this->object($context),
            'history' => array_values($history),
            'message' => $message,
            'language' => $language,
        ]);
    }

    /**
     * @param  array<string, mixed>  $context
     * @return array{status: string, insights: array<int, array>, reason: ?string, prompt_version: string, model: ?string}
     */
    public function insights(User|int $user, array $context, string $language = 'es'): array
    {
        return $this->post($user, '/v1/insights', [
            'context' => $this->object($context),
            'language' => $language,
        ]);
    }

    /**
     * @param  array<string, mixed>  $context
     * @return array{status: string, verdict: ?string, reasons: array, metrics: array, message: string, prompt_version: string}
     */
    public function purchaseCheck(
        User|int $user,
        array $context,
        int|float|string $amount,
        ?string $description = null,
        string $language = 'es',
    ): array {
        return $this->post($user, '/v1/purchase-check', [
            'context' => $this->object($context),
            'amount' => $amount,
            'description' => $description,
            'language' => $language,
        ]);
    }

    /**
     * @param  array<string, mixed>  $payload
     * @return array<string, mixed>
     */
    private function post(User|int $user, string $path, array $payload): array
    {
        $userId = $user instanceof User ? (int) $user->getKey() : $user;

        if (! $this->settings->aiEnabled($userId)) {
            throw new AiDisabledForUser;
        }

        try {
            $response = $this->request()->post($path, $payload);
        } catch (ConnectionException $e) {
            $exception = AiServiceUnavailable::connectionFailed($e);
            Log::warning('ai_service.request_failed', ['path' => $path, 'reason' => $exception->reason]);

            throw $exception;
        }

        if ($response->failed()) {
            $exception = AiServiceUnavailable::fromResponse($response);
            $level = in_array($response->status(), [503, 504], true) ? 'warning' : 'error';
            Log::log($level, 'ai_service.request_failed', [
                'path' => $path,
                'status' => $response->status(),
                'code' => $response->json('error.code'),
            ]);

            throw $exception;
        }

        return $response->json() ?? [];
    }

    private function request(): PendingRequest
    {
        return Http::baseUrl(rtrim($this->baseUrl, '/'))
            ->withHeaders(['X-AI-Service-Token' => $this->token])
            ->acceptJson()
            ->asJson()
            ->timeout($this->timeout)
            ->connectTimeout($this->connectTimeout);
    }

    /**
     * Un array vacío se serializa como [] y el servicio espera un objeto {}.
     *
     * @param  array<string, mixed>  $context
     */
    private function object(array $context): array|stdClass
    {
        return $context === [] ? new stdClass : $context;
    }
}
