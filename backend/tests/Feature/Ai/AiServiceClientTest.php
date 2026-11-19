<?php

namespace Tests\Feature\Ai;

use App\Services\Ai\AiDisabledForUser;
use App\Services\Ai\AiServiceClient;
use App\Services\Ai\AiServiceUnavailable;
use App\Services\Ai\AiSettingsRepository;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\Client\Request;
use Illuminate\Support\Facades\Http;
use Tests\TestCase;

/**
 * IAL-06: AiServiceClient. El servicio Python siempre se simula con Http::fake();
 * no requiere servicios externos ni base de datos (compatible con el CI de SBI-31).
 */
class AiServiceClientTest extends TestCase
{
    private const TOKEN = 'test-token-0123456789abcdef';

    private object $settings;

    protected function setUp(): void
    {
        parent::setUp();

        config([
            'services.ai.url' => 'http://ai.test',
            'services.ai.token' => self::TOKEN,
            'services.ai.timeout' => 7,
            'services.ai.connect_timeout' => 2,
        ]);

        $this->settings = new class implements AiSettingsRepository
        {
            public bool $enabled = true;

            /** @var array<int, int> */
            public array $checkedUsers = [];

            public function aiEnabled(int $userId): bool
            {
                $this->checkedUsers[] = $userId;

                return $this->enabled;
            }
        };
        $this->app->instance(AiSettingsRepository::class, $this->settings);

        Http::preventStrayRequests();
    }

    private function client(): AiServiceClient
    {
        return $this->app->make(AiServiceClient::class);
    }

    /** @return array<string, mixed> */
    private function context(): array
    {
        return ['currency' => 'MXN', 'monthly_income' => '18217.65', 'payday' => 15];
    }

    // ------------------------------------------------------------- éxito

    public function test_chat_posts_payload_with_internal_token_and_returns_response(): void
    {
        Http::fake([
            'ai.test/v1/chat' => Http::response([
                'status' => 'ok',
                'reply' => '¡Hola! Vas bien este mes.',
                'intent' => 'general',
                'prompt_version' => 'chat@1.0',
                'model' => 'qwen3:8b',
            ]),
        ]);

        $result = $this->client()->chat(
            7,
            $this->context(),
            [['role' => 'user', 'content' => 'hola'], ['role' => 'assistant', 'content' => '¡hola!']],
            '¿Cómo voy?',
            'es',
        );

        $this->assertSame('¡Hola! Vas bien este mes.', $result['reply']);
        $this->assertSame('chat@1.0', $result['prompt_version']);
        $this->assertSame([7], $this->settings->checkedUsers);

        Http::assertSent(fn (Request $request) => $request->url() === 'http://ai.test/v1/chat'
            && $request->method() === 'POST'
            && $request->hasHeader('X-AI-Service-Token', self::TOKEN)
            && $request['message'] === '¿Cómo voy?'
            && $request['language'] === 'es'
            && count($request['history']) === 2
            && $request['context']['payday'] === 15);
    }

    public function test_insights_returns_service_response(): void
    {
        Http::fake([
            'ai.test/v1/insights' => Http::response([
                'status' => 'ok',
                'insights' => [['title' => 'Comida', 'message' => 'Vas al 67 %.', 'category' => 'budget', 'priority' => 'medium']],
                'reason' => null,
                'prompt_version' => 'insights@1.0',
                'model' => 'qwen3:8b',
            ]),
        ]);

        $result = $this->client()->insights(7, $this->context(), 'en');

        $this->assertCount(1, $result['insights']);
        Http::assertSent(fn (Request $request) => $request->url() === 'http://ai.test/v1/insights'
            && $request['language'] === 'en');
    }

    public function test_purchase_check_sends_amount_and_description(): void
    {
        Http::fake([
            'ai.test/v1/purchase-check' => Http::response([
                'status' => 'ok',
                'verdict' => 'precaucion',
                'reasons' => [['code' => 'high_income_share', 'severity' => 'caution', 'message' => '...']],
                'metrics' => ['amount' => 8000.0],
                'message' => 'Con cuidado. Es solo una sugerencia: la decisión es tuya.',
                'message_source' => 'model',
                'prompt_version' => 'purchase_check@1.0',
                'model' => 'qwen3:8b',
                'missing_data' => [],
            ]),
        ]);

        $result = $this->client()->purchaseCheck(7, $this->context(), 8000, 'TV');

        $this->assertSame('precaucion', $result['verdict']);
        Http::assertSent(fn (Request $request) => $request->url() === 'http://ai.test/v1/purchase-check'
            && $request['amount'] === 8000
            && $request['description'] === 'TV');
    }

    public function test_empty_context_is_sent_as_json_object(): void
    {
        Http::fake(['ai.test/*' => Http::response(['status' => 'insufficient_data', 'insights' => []])]);

        $this->client()->insights(7, []);

        Http::assertSent(fn (Request $request) => str_contains($request->body(), '"context":{}'));
    }

    // ------------------------------------------------------- servicio caído

    public function test_service_unavailable_503_throws_ai_service_unavailable(): void
    {
        Http::fake(['ai.test/*' => Http::response(
            ['error' => ['code' => 'model_unavailable', 'message' => 'Ollama no está disponible', 'retryable' => true]],
            503,
        )]);

        try {
            $this->client()->chat(7, $this->context(), [], 'hola');
            $this->fail('Se esperaba AiServiceUnavailable');
        } catch (AiServiceUnavailable $e) {
            $this->assertSame('unavailable', $e->reason);
            $this->assertSame(503, $e->upstreamStatus);
        }
    }

    public function test_connection_refused_throws_ai_service_unavailable(): void
    {
        Http::fake(fn () => throw new ConnectionException('cURL error 7: Failed to connect to ai.test port 80: Connection refused'));

        try {
            $this->client()->insights(7, $this->context());
            $this->fail('Se esperaba AiServiceUnavailable');
        } catch (AiServiceUnavailable $e) {
            $this->assertSame('connection', $e->reason);
        }
    }

    // ------------------------------------------------------------- timeout

    public function test_model_timeout_504_throws_ai_service_unavailable(): void
    {
        Http::fake(['ai.test/*' => Http::response(['error' => ['code' => 'model_timeout']], 504)]);

        try {
            $this->client()->chat(7, $this->context(), [], 'hola');
            $this->fail('Se esperaba AiServiceUnavailable');
        } catch (AiServiceUnavailable $e) {
            $this->assertSame('timeout', $e->reason);
        }
    }

    public function test_client_timeout_throws_ai_service_unavailable(): void
    {
        Http::fake(fn () => throw new ConnectionException('cURL error 28: Operation timed out after 7001 milliseconds'));

        try {
            $this->client()->purchaseCheck(7, $this->context(), 500);
            $this->fail('Se esperaba AiServiceUnavailable');
        } catch (AiServiceUnavailable $e) {
            $this->assertSame('timeout', $e->reason);
        }
    }

    // ------------------------------------------------------ respuesta 503

    public function test_unavailable_exception_renders_503_without_internal_details(): void
    {
        $response = AiServiceUnavailable::connectionFailed(
            new ConnectionException('cURL error 7: Failed to connect to 10.0.0.5 port 8001')
        )->render();

        $this->assertSame(503, $response->getStatusCode());
        $this->assertSame('ai_unavailable', $response->getData(true)['error']['code']);
        $this->assertStringNotContainsString('10.0.0.5', $response->getContent());
        $this->assertStringNotContainsString('cURL', $response->getContent());
    }

    // ------------------------------------------------------ ai_enabled=false

    public function test_does_not_call_service_when_ai_disabled_for_user(): void
    {
        Http::fake();
        $this->settings->enabled = false;

        try {
            $this->client()->chat(7, $this->context(), [], 'hola');
            $this->fail('Se esperaba AiDisabledForUser');
        } catch (AiDisabledForUser $e) {
            $this->assertSame(403, $e->render()->getStatusCode());
        }

        Http::assertNothingSent();
    }

    // ------------------------------------------------------------- config

    public function test_client_is_resolved_from_container_with_services_config(): void
    {
        config(['services.ai.url' => 'http://otro-host:9000/']);
        Http::fake(['otro-host:9000/v1/insights' => Http::response(['status' => 'ok', 'insights' => []])]);

        $this->client()->insights(7, $this->context());

        Http::assertSent(fn (Request $request) => $request->url() === 'http://otro-host:9000/v1/insights'
            && $request->hasHeader('X-AI-Service-Token', self::TOKEN));
    }
}
