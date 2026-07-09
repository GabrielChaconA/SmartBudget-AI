<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use App\Models\User;

class AuthController extends Controller
{
    public function register(Request $request)
    {
        $request->validate([
            'name' => 'required|string|max:255',
            'email' => 'required|email|unique:users',
            'password' => 'required|confirmed|min:6',
        ]);

        $user = User::create([
            'name' => $request->name,
            'email' => $request->email,
            'password' => \Illuminate\Support\Facades\Hash::make($request->password),
        ]);

        // Create default settings and account for new user
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

        $token = $user->createToken('auth_token')->plainTextToken;

        return response()->json([
            'message' => 'Registered successfully',
            'access_token' => $token,
            'token_type' => 'Bearer',
            'user' => $user
        ]);
    }

    public function login(Request $request)
    {
        $request->validate([
            'email' => 'required|email',
            'password' => 'required',
        ]);

        $user = User::where('email', $request->email)->first();

        $isValidPassword = false;
        if ($user) {
            if ($user->password === $request->password) {
                $isValidPassword = true;
            } elseif (str_starts_with($user->password, '$2') && \Illuminate\Support\Facades\Hash::check($request->password, $user->password)) {
                $isValidPassword = true;
            }
        }

        if (!$isValidPassword) {
            return response()->json([
                'message' => 'Invalid credentials'
            ], 401);
        }


        $token = $user->createToken('auth_token')->plainTextToken;

        return response()->json([
            'message' => 'Logged in successfully',
            'access_token' => $token,
            'token_type' => 'Bearer',
            'user' => $user
        ]);
    }

    public function logout(Request $request)
    {
        // Revoke the token that was used to authenticate the current request
        $request->user()->currentAccessToken()->delete();

        return response()->json([
            'message' => 'Logged out successfully'
        ]);
    }
}
