<?php

namespace Tests\Feature\Security;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Mail;
use Laravel\Sanctum\Sanctum;
use Laravel\Socialite\Facades\Socialite;
use Laravel\Socialite\Two\GoogleProvider;
use Laravel\Socialite\Two\User as SocialiteUser;
use Mockery;
use Tests\Concerns\CreatesLegacyTables;
use Tests\TestCase;

/**
 * SEC-03: pruebas de validación de las vulnerabilidades corregidas en las rutas.
 * Los IDs (V-xx) corresponden a docs/security/SEC-01-reporte-vulnerabilidades.md.
 */
class RouteSecurityTest extends TestCase
{
    use CreatesLegacyTables;
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->createLegacyTables();
    }

    private function legacyUser(string $email, string $password): int
    {
        return DB::table('users')->insertGetId([
            'name' => 'Legacy',
            'email' => $email,
            'password' => $password,
            'created_at' => now(),
            'updated_at' => now(),
        ]);
    }

    private function fundFor(User $user, string $name = 'Comida'): int
    {
        return DB::table('funds')->insertGetId([
            'user_id' => $user->id,
            'name' => $name,
            'balance' => 1000,
        ]);
    }

    // ------------------------------------------------- V-01 contraseñas

    public function test_login_rejects_password_stored_in_plaintext(): void
    {
        $this->legacyUser('legacy@example.com', 'secret-plain');

        $this->postJson('/api/login', ['email' => 'legacy@example.com', 'password' => 'secret-plain'])
            ->assertStatus(401);
    }

    public function test_login_rejects_the_stored_hash_sent_as_password(): void
    {
        $user = User::factory()->create(['password' => Hash::make('correct-horse-battery')]);

        $this->postJson('/api/login', ['email' => $user->email, 'password' => $user->password])
            ->assertStatus(401);
    }

    public function test_login_accepts_hashed_password(): void
    {
        $user = User::factory()->create(['password' => Hash::make('correct-horse-battery')]);

        $this->postJson('/api/login', ['email' => $user->email, 'password' => 'correct-horse-battery'])
            ->assertOk()
            ->assertJsonStructure(['access_token', 'token_type', 'user']);
    }

    public function test_migration_hashes_plaintext_passwords_and_keeps_them_usable(): void
    {
        $plainId = $this->legacyUser('legacy@example.com', 'password');
        $hashed = Hash::make('other-password');
        $hashedId = $this->legacyUser('hashed@example.com', $hashed);

        $migration = require database_path('migrations/2026_11_19_000000_hash_plaintext_user_passwords.php');
        $migration->up();

        $stored = DB::table('users')->where('id', $plainId)->value('password');
        $this->assertTrue(Hash::isHashed($stored));
        $this->assertTrue(Hash::check('password', $stored));
        $this->assertSame($hashed, DB::table('users')->where('id', $hashedId)->value('password'));

        $this->postJson('/api/login', ['email' => 'legacy@example.com', 'password' => 'password'])
            ->assertOk();
    }

    // ------------------------------------------- V-06 fuerza bruta / registro

    public function test_login_is_rate_limited_per_account(): void
    {
        $user = User::factory()->create();

        for ($i = 0; $i < 5; $i++) {
            $this->postJson('/api/login', ['email' => $user->email, 'password' => 'wrong-password'])
                ->assertStatus(401);
        }

        $this->postJson('/api/login', ['email' => $user->email, 'password' => 'wrong-password'])
            ->assertStatus(429);
    }

    public function test_register_requires_at_least_eight_characters(): void
    {
        $this->postJson('/api/register', [
            'name' => 'Ana',
            'email' => 'ana@example.com',
            'password' => 'short7c',
            'password_confirmation' => 'short7c',
        ])->assertStatus(422)->assertJsonValidationErrors('password');
    }

    public function test_register_succeeds_with_valid_password(): void
    {
        $this->postJson('/api/register', [
            'name' => 'Ana',
            'email' => 'ana@example.com',
            'password' => 'long-enough-1',
            'password_confirmation' => 'long-enough-1',
        ])->assertOk()->assertJsonStructure(['access_token']);

        $this->assertTrue(Hash::check('long-enough-1', User::where('email', 'ana@example.com')->value('password')));
    }

    // ------------------------------------------------ V-02 IDOR en fondos

    public function test_cannot_create_allocation_in_another_users_fund(): void
    {
        $owner = User::factory()->create();
        $fundId = $this->fundFor($owner, 'Fondo secreto');
        Sanctum::actingAs(User::factory()->create());

        $this->postJson("/api/funds/{$fundId}/allocations", ['category_name' => 'Super', 'amount' => 100])
            ->assertNotFound();

        $this->assertSame(0, DB::table('fund_allocations')->count());
        $this->assertSame(0, DB::table('notifications')->count()); // no se filtra el nombre del fondo
    }

    public function test_owner_can_create_allocation(): void
    {
        $owner = User::factory()->create();
        $fundId = $this->fundFor($owner, 'Comida');
        Sanctum::actingAs($owner);

        $this->postJson("/api/funds/{$fundId}/allocations", ['category_name' => 'Super', 'amount' => 100])
            ->assertOk();

        $this->assertSame(1, DB::table('fund_allocations')->where('fund_id', $fundId)->count());
        $this->assertStringContainsString('Comida', DB::table('notifications')->value('message'));
    }

    public function test_cannot_delete_allocation_in_another_users_fund(): void
    {
        $owner = User::factory()->create();
        $fundId = $this->fundFor($owner);
        $categoryId = DB::table('categories')->insertGetId(['name' => 'Super', 'type' => 'expense']);
        DB::table('fund_allocations')->insert(['fund_id' => $fundId, 'category_id' => $categoryId, 'amount' => 50]);
        Sanctum::actingAs(User::factory()->create());

        $this->deleteJson("/api/funds/{$fundId}/allocations/Super")->assertNotFound();

        $this->assertSame(1, DB::table('fund_allocations')->count());
    }

    public function test_owner_can_delete_allocation(): void
    {
        $owner = User::factory()->create();
        $fundId = $this->fundFor($owner);
        $categoryId = DB::table('categories')->insertGetId(['name' => 'Super', 'type' => 'expense']);
        DB::table('fund_allocations')->insert(['fund_id' => $fundId, 'category_id' => $categoryId, 'amount' => 50]);
        Sanctum::actingAs($owner);

        $this->deleteJson("/api/funds/{$fundId}/allocations/Super")->assertOk();

        $this->assertSame(0, DB::table('fund_allocations')->count());
    }

    public function test_allocation_does_not_modify_existing_global_category(): void
    {
        $owner = User::factory()->create();
        $fundId = $this->fundFor($owner);
        DB::table('categories')->insert(['name' => 'Super', 'type' => 'expense', 'icon' => 'A']);
        Sanctum::actingAs($owner);

        $this->postJson("/api/funds/{$fundId}/allocations", ['category_name' => 'Super', 'amount' => 10, 'icon' => 'B'])
            ->assertOk();

        $this->assertSame('A', DB::table('categories')->where('name', 'Super')->value('icon'));
    }

    // ------------------------------------------ V-03 / V-14 rutas eliminadas

    public function test_test_mail_routes_are_removed(): void
    {
        Mail::fake();

        $this->get('/test-mail')->assertNotFound();
        Sanctum::actingAs(User::factory()->create());
        $this->postJson('/api/test-subscription-email')->assertNotFound();

        Mail::assertNothingSent();
    }

    public function test_broken_exchange_rate_route_is_removed(): void
    {
        Sanctum::actingAs(User::factory()->create());

        $this->getJson('/api/exchange-rate')->assertNotFound();
    }

    public function test_investment_alert_can_be_created(): void
    {
        $user = User::factory()->create();
        DB::table('investments')->insert([
            'user_id' => $user->id, 'symbol' => 'AAPL', 'quantity' => 1, 'average_price' => 100, 'type' => 'stock',
        ]);
        Sanctum::actingAs($user);

        $this->postJson('/api/investment-alerts', ['symbol' => 'AAPL', 'target_percent' => 10])
            ->assertCreated()
            ->assertJsonPath('direction', 'up');
    }

    // --------------------------------------------------- V-05 login Google

    public function test_google_callback_returns_one_time_code_instead_of_token(): void
    {
        config(['app.frontend_url' => 'https://app.example.com']);
        User::factory()->create(['email' => 'g@example.com']);

        $googleUser = (new SocialiteUser)->map([
            'id' => 'google-123', 'name' => 'G User', 'email' => 'g@example.com', 'avatar' => null,
        ]);
        $provider = Mockery::mock(GoogleProvider::class);
        $provider->shouldReceive('stateless')->andReturnSelf();
        $provider->shouldReceive('user')->andReturn($googleUser);
        Socialite::shouldReceive('driver')->with('google')->andReturn($provider);

        $location = $this->get('/api/auth/google/callback')->assertRedirect()->headers->get('Location');

        $this->assertStringStartsWith('https://app.example.com/login?code=', $location);
        $this->assertStringNotContainsString('token=', $location);

        parse_str((string) parse_url($location, PHP_URL_QUERY), $query);
        $this->postJson('/api/auth/google/exchange', ['code' => $query['code']])
            ->assertOk()
            ->assertJsonStructure(['access_token']);

        // un solo uso
        $this->postJson('/api/auth/google/exchange', ['code' => $query['code']])->assertStatus(401);
    }

    public function test_google_exchange_rejects_unknown_code(): void
    {
        $this->postJson('/api/auth/google/exchange', ['code' => str_repeat('a', 64)])->assertStatus(401);
    }

    public function test_tokens_expire_by_default(): void
    {
        $this->assertNotNull(config('sanctum.expiration'));
    }

    // ------------------------------------------------ V-07 caché de logos

    public function test_sports_logo_rejects_untrusted_urls(): void
    {
        Sanctum::actingAs(User::factory()->create());

        foreach (['https://evil.example.com/pixel.png', 'http://media.api-sports.io/x.png', 'javascript:alert(1)'] as $url) {
            $this->postJson('/api/sports/logos', ['key' => 'soccer_Team', 'url' => $url])->assertStatus(422);
        }

        $this->assertSame([], Cache::get('sports_logos', []));
    }

    public function test_sports_logo_accepts_known_cdn_urls(): void
    {
        Sanctum::actingAs(User::factory()->create());
        $url = 'https://media.api-sports.io/football/teams/33.png';

        $this->postJson('/api/sports/logos', ['key' => 'soccer_Team', 'url' => $url])->assertOk();
        $this->postJson('/api/sports/logos', ['key' => 'soccer_Unknown', 'url' => null])->assertOk();

        $this->getJson('/api/sports/logos')->assertExactJson(['soccer_Team' => $url, 'soccer_Unknown' => null]);
    }

    // ----------------------------------------------------------- V-08 CORS

    public function test_cors_rejects_arbitrary_onrender_origin(): void
    {
        $response = $this->withHeaders([
            'Origin' => 'https://evil-app.onrender.com',
            'Access-Control-Request-Method' => 'GET',
        ])->options('/api/user');

        $this->assertNull($response->headers->get('Access-Control-Allow-Origin'));
    }

    public function test_cors_allows_local_frontend_outside_production(): void
    {
        $response = $this->withHeaders([
            'Origin' => 'http://localhost:5173',
            'Access-Control-Request-Method' => 'GET',
        ])->options('/api/user');

        $this->assertSame('http://localhost:5173', $response->headers->get('Access-Control-Allow-Origin'));
    }

    // ----------------------------------------- V-12 errores de Cloudinary

    public function test_avatar_upload_error_does_not_leak_provider_details(): void
    {
        config(['services.cloudinary' => ['cloud_name' => 'demo', 'api_key' => 'key', 'api_secret' => 'secret']]);
        Http::fake(['api.cloudinary.com/*' => Http::response(['error' => ['message' => 'Invalid api_key key-123']], 401)]);
        Sanctum::actingAs(User::factory()->create());

        $response = $this->post(
            '/api/user/avatar',
            ['file' => UploadedFile::fake()->create('avatar.png', 10, 'image/png')],
            ['Accept' => 'application/json'],
        );

        $response->assertStatus(500)->assertExactJson(['error' => 'Failed to upload avatar']);
        $this->assertStringNotContainsString('key-123', $response->getContent());
    }

    // ------------------------------------------- V-13 / V-15 validaciones

    public function test_add_money_increments_cartera_balance(): void
    {
        $user = User::factory()->create();
        DB::table('accounts')->insert(['user_id' => $user->id, 'name' => 'Cartera', 'type' => 'cash', 'balance' => 100]);
        Sanctum::actingAs($user);

        $this->postJson('/api/accounts/add-money', ['amount' => 50.5])->assertOk();

        $this->assertEquals(150.5, (float) DB::table('accounts')->where('user_id', $user->id)->value('balance'));
    }

    public function test_subscription_with_unknown_category_is_rejected(): void
    {
        Sanctum::actingAs(User::factory()->create());

        $this->postJson('/api/subscriptions', [
            'name' => 'Netflix',
            'amount' => 299,
            'billing_cycle' => 'monthly',
            'next_billing_date' => '2026-12-01',
            'category_id' => 999,
        ])->assertStatus(422)->assertJsonValidationErrors('category_id');
    }
}
