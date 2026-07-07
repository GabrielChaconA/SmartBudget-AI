<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class ProfileController extends Controller
{
    /**
     * Update the user's profile information.
     * Only the name can be changed as requested.
     */
    public function update(Request $request)
    {
        $validated = $request->validate([
            'name' => 'sometimes|string|max:255',
            'avatar' => 'sometimes|string|url|max:2048',
        ]);

        $user = $request->user();
        if (isset($validated['name'])) {
            $user->name = $validated['name'];
        }
        if (isset($validated['avatar'])) {
            $user->avatar = $validated['avatar'];
        }
        $user->save();

        return response()->json([
            'message' => 'Profile updated successfully',
            'user' => $user
        ]);
    }
    public function uploadAvatar(Request $request)
    {
        $request->validate([
            'file' => 'required|image|max:5120',
        ]);

        $file = $request->file('file');
        $cloudName = env('CLOUDINARY_CLOUD_NAME');
        $apiKey = env('CLOUDINARY_API_KEY');
        $apiSecret = env('CLOUDINARY_API_SECRET');
        $timestamp = time();

        $stringToSign = "timestamp={$timestamp}" . $apiSecret;
        $signature = sha1($stringToSign);

        $response = \Illuminate\Support\Facades\Http::attach(
            'file', file_get_contents($file->path()), $file->getClientOriginalName()
        )->post("https://api.cloudinary.com/v1_1/{$cloudName}/image/upload", [
            'api_key' => $apiKey,
            'timestamp' => $timestamp,
            'signature' => $signature
        ]);

        if ($response->successful() && isset($response['secure_url'])) {
            $user = $request->user();
            $user->avatar = $response['secure_url'];
            $user->save();

            return response()->json([
                'message' => 'Avatar updated successfully',
                'secure_url' => $response['secure_url']
            ]);
        }

        return response()->json([
            'error' => 'Failed to upload to Cloudinary', 
            'details' => $response->json()
        ], 500);
    }
}
