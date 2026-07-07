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
            'deduct_amount' => 'nullable|numeric',
        ]);

        $userId = $request->user()->id;
        
        $investmentData = collect($validated)->except('deduct_amount')->toArray();
        $investmentData['user_id'] = $userId;
        
        if (empty($investmentData['currency'])) {
            $investmentData['currency'] = 'MXN';
        }

        $id = DB::table('investments')->insertGetId($investmentData);
        $investmentData['id'] = $id;

        return response()->json($investmentData, 201);
    }

    /**
     * Update the specified investment.
     */
    public function update(Request $request, $id)
    {
        $validated = $request->validate([
            'symbol' => 'sometimes|string|max:50',
            'quantity' => 'sometimes|numeric',
            'currency' => 'nullable|string|max:10',
            'type' => 'sometimes|string|max:50',
            'diff_amount' => 'nullable|numeric', // Difference to apply to Cartera
        ]);

        $userId = $request->user()->id;

        $investment = DB::table('investments')
            ->where('id', $id)
            ->where('user_id', $userId)
            ->first();

        if (!$investment) {
            return response()->json(['success' => false, 'message' => 'Investment not found'], 404);
        }

        $updateData = collect($validated)->except('diff_amount')->toArray();
        if (isset($validated['currency']) && empty($validated['currency'])) {
            $updateData['currency'] = 'MXN';
        }

        if (!empty($updateData)) {
            DB::table('investments')
                ->where('id', $id)
                ->update($updateData);
        }

        $updatedInvestment = DB::table('investments')->where('id', $id)->first();
        return response()->json($updatedInvestment);
    }

    /**
     * Remove the specified investment.
     */
    public function destroy(Request $request, $id)
    {
        $validated = $request->validate([
            'refund_amount' => 'nullable|numeric', // Amount to refund to Cartera
        ]);

        $userId = $request->user()->id;

        $investment = DB::table('investments')
            ->where('id', $id)
            ->where('user_id', $userId)
            ->first();

        if (!$investment) {
            return response()->json(['success' => false, 'message' => 'Investment not found'], 404);
        }

        DB::table('investments')->where('id', $id)->delete();

        return response()->json(['success' => true]);
    }
}
