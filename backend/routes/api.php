<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\ProfileController;

Route::post('/login', [AuthController::class, 'login']);

Route::middleware('auth:sanctum')->group(function () {
    Route::post('/logout', [AuthController::class, 'logout']);
    Route::put('/user/profile', [ProfileController::class, 'update']);
    Route::get('/user', function (Request $request) {
        $user = $request->user();
        $settings = \Illuminate\Support\Facades\DB::table('settings')->where('user_id', $user->id)->first();
        $accounts = \Illuminate\Support\Facades\DB::table('accounts')->where('user_id', $user->id)->get();
        $goals = \Illuminate\Support\Facades\DB::table('goals')->where('user_id', $user->id)->get();
        $subscriptions = \Illuminate\Support\Facades\DB::table('subscriptions')->where('user_id', $user->id)->get();
        $investments = \Illuminate\Support\Facades\DB::table('investments')->where('user_id', $user->id)->get();
        
        $funds = \Illuminate\Support\Facades\DB::table('funds')->where('user_id', $user->id)->get();
        $fundIds = $funds->pluck('id')->toArray();
        $allocations = \Illuminate\Support\Facades\DB::table('fund_allocations')
            ->join('categories', 'fund_allocations.category_id', '=', 'categories.id')
            ->select('fund_allocations.*', 'categories.name as category_name')
            ->whereIn('fund_allocations.fund_id', $fundIds)
            ->get();
            
        foreach ($funds as $fund) {
            $fund->allocations = $allocations->where('fund_id', $fund->id)->values()->toArray();
        }
        
        $userData = $user->toArray();
        if ($settings) {
            $userData['currency'] = $settings->currency;
            $userData['monthlyIncome'] = $settings->monthly_income;
        }
        $userData['accounts'] = $accounts;
        $userData['goals'] = $goals;
        $userData['funds'] = $funds;
        $userData['subscriptions'] = $subscriptions;
        $userData['investments'] = $investments;
        return $userData;
    });

    Route::post('/funds', function (Request $request) {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'balance' => 'required|numeric',
            'color' => 'nullable|string|max:20',
            'icon' => 'nullable|string|max:100',
        ]);
        $validated['user_id'] = $request->user()->id;
        $id = \Illuminate\Support\Facades\DB::table('funds')->insertGetId($validated);
        return response()->json(['id' => $id]);
    });

    Route::put('/funds/{id}', function (Request $request, $id) {
        $validated = $request->validate([
            'name' => 'sometimes|string|max:255',
            'balance' => 'sometimes|numeric',
        ]);
        \Illuminate\Support\Facades\DB::table('funds')
            ->where('id', $id)
            ->where('user_id', $request->user()->id)
            ->update($validated);
        return response()->json(['success' => true]);
    });

    Route::post('/funds/{id}/allocations', function (Request $request, $id) {
        $validated = $request->validate([
            'category_name' => 'required|string|max:100',
            'amount' => 'required|numeric',
        ]);
        // Simple logic to find or create category
        $category = \Illuminate\Support\Facades\DB::table('categories')
            ->where('user_id', $request->user()->id)
            ->where('name', $validated['category_name'])
            ->first();
        if (!$category) {
            $categoryId = \Illuminate\Support\Facades\DB::table('categories')->insertGetId([
                'user_id' => $request->user()->id,
                'name' => $validated['category_name'],
                'type' => 'expense'
            ]);
        } else {
            $categoryId = $category->id;
        }
        
        \Illuminate\Support\Facades\DB::table('fund_allocations')->insert([
            'fund_id' => $id,
            'category_id' => $categoryId,
            'amount' => $validated['amount']
        ]);
        
        // Increment the total fund balance
        \Illuminate\Support\Facades\DB::table('funds')->where('id', $id)->increment('balance', $validated['amount']);

        return response()->json(['success' => true]);
    });

    Route::get('/user/income-stats', function (Request $request) {
        $userId = $request->user()->id;
        
        $transactions = \Illuminate\Support\Facades\DB::table('transactions')
            ->where('user_id', $userId)
            ->where('type', 'income')
            ->select('amount', 'date')
            ->orderBy('date', 'asc')
            ->get();
            
        return response()->json($transactions);
    });
    Route::get('/subscription-catalog', function (Request $request) {
        $query = $request->query('query');
        $catalogQuery = \Illuminate\Support\Facades\DB::table('subscription_catalog');
        
        if ($query) {
            $catalogQuery->where('name', 'ilike', '%' . $query . '%');
        }
        
        return response()->json($catalogQuery->take(20)->get());
    });

    Route::post('/subscriptions', function (Request $request) {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'amount' => 'required|numeric',
            'billing_cycle' => 'required|string|max:50',
            'next_billing_date' => 'required|date',
            'category_id' => 'nullable|integer'
        ]);
        
        $validated['user_id'] = $request->user()->id;
        $id = \Illuminate\Support\Facades\DB::table('subscriptions')->insertGetId($validated);
        
        $validated['id'] = $id;
        return response()->json($validated);
    });

    Route::post('/test-subscription-email', function (Request $request) {
        $user = $request->user();
        
        // Find one subscription that is active (e.g. Netflix that we just inserted)
        $subscription = \Illuminate\Support\Facades\DB::table('subscriptions')
            ->where('user_id', $user->id)
            ->first();

        if ($subscription) {
            \Illuminate\Support\Facades\Mail::to($user->email)->send(new \App\Mail\SubscriptionAlertMail($user, $subscription));
            return response()->json(['success' => true, 'message' => 'Test email sent successfully to ' . $user->email]);
        }
        
        return response()->json(['success' => false, 'message' => 'No subscriptions found to test with.'], 404);
    });

    Route::post('/investments', [\App\Http\Controllers\InvestmentController::class, 'store']);
});

