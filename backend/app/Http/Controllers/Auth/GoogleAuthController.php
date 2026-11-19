<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Str;
use Laravel\Socialite\Facades\Socialite;

class GoogleAuthController extends Controller
{
    /**
     * Vigencia del código de un solo uso que el frontend canjea por el token (SEC-03 / V-05).
     */
    public const LOGIN_CODE_TTL_SECONDS = 60;

    public function redirect()
    {
        return Socialite::driver('google')->stateless()->redirect();
    }

    public function callback()
    {
        $frontendUrl = rtrim((string) config('app.frontend_url'), '/');

        try {
            $googleUser = Socialite::driver('google')->stateless()->user();

            // Check if the google_id column exists (migration might not have run)
            $hasGoogleId = Schema::hasColumn('users', 'google_id');

            // Find user by email first to avoid unique constraint violations
            $user = User::where('email', $googleUser->email)->first();

            if ($user) {
                // Update existing user with Google info
                $user->name = $googleUser->name;
                if ($hasGoogleId) {
                    $user->google_id = $googleUser->id;
                }
                if ($googleUser->avatar && Schema::hasColumn('users', 'avatar')) {
                    $user->avatar = $googleUser->avatar;
                }
                $user->save();
            } else {
                // Create new user
                $userData = [
                    'name' => $googleUser->name,
                    'email' => $googleUser->email,
                ];
                if ($hasGoogleId) {
                    $userData['google_id'] = $googleUser->id;
                }
                if ($googleUser->avatar && Schema::hasColumn('users', 'avatar')) {
                    $userData['avatar'] = $googleUser->avatar;
                }

                $user = User::create($userData);
            }

            // Create default settings if new user
            $settingsExist = DB::table('settings')->where('user_id', $user->id)->exists();
            if (!$settingsExist) {
                DB::table('settings')->insert([
                    'user_id'        => $user->id,
                    'currency'       => 'MXN',
                    'monthly_income' => 0,
                    'created_at'     => now(),
                    'updated_at'     => now()
                ]);
                DB::table('accounts')->insert([
                    'user_id'    => $user->id,
                    'name'       => 'Cartera',
                    'balance'    => 0,
                    'created_at' => now(),
                    'updated_at' => now()
                ]);
            }

            // El token ya no viaja en la URL: se entrega un código de un solo uso que
            // el frontend canjea en POST /api/auth/google/exchange.
            $code = Str::random(64);
            Cache::put(self::loginCodeCacheKey($code), $user->id, now()->addSeconds(self::LOGIN_CODE_TTL_SECONDS));

            return redirect()->away($frontendUrl . '/login?code=' . $code);

        } catch (\Exception $e) {
            Log::error('Google Login Error: ' . $e->getMessage(), [
                'trace' => $e->getTraceAsString()
            ]);
            return redirect()->away($frontendUrl . '/login?error=GoogleLoginFailed');
        }
    }

    /**
     * Canjea el código de un solo uso por un token de Sanctum.
     */
    public function exchange(Request $request)
    {
        $validated = $request->validate([
            'code' => 'required|string|size:64',
        ]);

        $userId = Cache::pull(self::loginCodeCacheKey($validated['code']));
        $user = $userId ? User::find($userId) : null;

        if (!$user) {
            return response()->json(['message' => 'Invalid or expired login code'], 401);
        }

        $token = $user->createToken('auth_token')->plainTextToken;

        return response()->json([
            'message' => 'Logged in successfully',
            'access_token' => $token,
            'token_type' => 'Bearer',
            'user' => $user,
        ]);
    }

    /**
     * En caché se guarda el hash del código, no el código.
     */
    public static function loginCodeCacheKey(string $code): string
    {
        return 'google_login_code:' . hash('sha256', $code);
    }
}
