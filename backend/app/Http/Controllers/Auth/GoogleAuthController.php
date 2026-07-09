<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Schema;
use Laravel\Socialite\Facades\Socialite;

class GoogleAuthController extends Controller
{
    public function redirect()
    {
        return Socialite::driver('google')->stateless()->redirect();
    }

    public function callback()
    {
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

            $token = $user->createToken('auth_token')->plainTextToken;

            // Redirect back to frontend with the token
            $frontendUrl = env('FRONTEND_URL', 'http://localhost:5173');
            return redirect()->away($frontendUrl . '/login?token=' . $token);

        } catch (\Exception $e) {
            Log::error('Google Login Error: ' . $e->getMessage(), [
                'trace' => $e->getTraceAsString()
            ]);
            $frontendUrl = env('FRONTEND_URL', 'http://localhost:5173');
            return redirect()->away($frontendUrl . '/login?error=GoogleLoginFailed');
        }
    }
}

