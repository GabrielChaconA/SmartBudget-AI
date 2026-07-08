<?php

namespace App\Http\Controllers;

use App\Models\InvestmentAlert;
use Illuminate\Http\Request;

class InvestmentAlertController extends Controller
{
    public function store(Request $request)
    {
        $request->validate([
            'symbol' => 'required|string',
            'target_percent' => 'required|numeric',
        ]);

        $user = $request->user();
        
        // Find the user's investment to get the base price
        $investment = $user->investments()->where('symbol', $request->symbol)->first();
        if (!$investment) {
            return response()->json(['message' => 'Investment not found'], 404);
        }

        $basePrice = $investment->average_price;
        if ($basePrice <= 0) {
            // If we don't have a valid average price in DB, we can't reliably alert
            $basePrice = 1; // Fallback to avoid division by zero, though not ideal
        }

        $targetPrice = $basePrice * (1 + ($request->target_percent / 100));
        $direction = $request->target_percent > 0 ? 'up' : 'down';

        $alert = InvestmentAlert::create([
            'user_id' => $user->id,
            'symbol' => $request->symbol,
            'target_percent' => $request->target_percent,
            'base_price' => $basePrice,
            'target_price' => $targetPrice,
            'direction' => $direction,
            'is_active' => true,
        ]);

        return response()->json($alert, 201);
    }
}
