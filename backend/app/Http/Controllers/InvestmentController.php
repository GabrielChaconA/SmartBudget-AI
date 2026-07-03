<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class InvestmentController extends Controller
{
    /**
     * Store a newly created investment.
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'symbol' => 'required|string|max:50',
            'quantity' => 'required|numeric',
            'average_price' => 'required|numeric',
            'currency' => 'nullable|string|max:10',
            'type' => 'required|string|max:50',
        ]);

        $validated['user_id'] = $request->user()->id;
        
        if (empty($validated['currency'])) {
            $validated['currency'] = 'MXN';
        }

        $id = DB::table('investments')->insertGetId($validated);
        $validated['id'] = $id;

        return response()->json($validated, 201);
    }
}
