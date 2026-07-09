<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Support\Facades\Auth;
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
            
            $user = User::updateOrCreate([
                'google_id' => $googleUser->id,
            ], [
                'name' => $googleUser->name,
                'email' => $googleUser->email,
                'avatar' => $googleUser->avatar,
            ]);

            // Create default settings if new user
            $settingsExist = \Illuminate\Support\Facades\DB::table('settings')->where('user_id', $user->id)->exists();
            if (!$settingsExist) {
                \Illuminate\Support\Facades\DB::table('settings')->insert([
                    'user_id' => $user->id,
                    'currency' => 'MXN',
                    'monthly_income' => 0,
                    'created_at' => now(),
                    'updated_at' => now()
                ]);
                \Illuminate\Support\Facades\DB::table('accounts')->insert([
                    'user_id' => $user->id,
                    'name' => 'Cartera',
                    'balance' => 0,
                    'created_at' => now(),
                    'updated_at' => now()
                ]);
            }

            $token = $user->createToken('auth_token')->plainTextToken;

            // Redirect back to frontend with the token
            $frontendUrl = env('FRONTEND_URL', 'http://localhost:5173');
            return redirect()->away($frontendUrl . '/login?token=' . $token);

        } catch (\Exception $e) {
            \Log::error('Google Login Error: ' . $e->getMessage());
            $frontendUrl = env('FRONTEND_URL', 'http://localhost:5173');
            return redirect()->away($frontendUrl . '/login?error=GoogleLoginFailed');
        }
    }
}
