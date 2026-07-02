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
}
