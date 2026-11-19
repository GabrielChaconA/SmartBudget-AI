<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\ProfileController;

// Límite de intentos definido en App\Providers\SecurityServiceProvider (SEC-03 / V-06).
Route::middleware('throttle:auth')->group(function () {
    Route::post('/login', [AuthController::class, 'login']);
    Route::post('/register', [AuthController::class, 'register']);
    Route::post('/auth/google/exchange', [\App\Http\Controllers\Auth\GoogleAuthController::class, 'exchange']);
});

Route::get('/auth/google/redirect', [\App\Http\Controllers\Auth\GoogleAuthController::class, 'redirect']);
Route::get('/auth/google/callback', [\App\Http\Controllers\Auth\GoogleAuthController::class, 'callback']);

Route::middleware('auth:sanctum')->group(function () {
    Route::post('/logout', [AuthController::class, 'logout']);
    Route::put('/user/profile', [ProfileController::class, 'update']);
    Route::post('/user/avatar', [ProfileController::class, 'uploadAvatar']);
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
            ->select('fund_allocations.*', 'categories.name as category_name', 'categories.icon as category_icon')
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

    Route::post('/accounts/add-money', function (Request $request) {
        $validated = $request->validate([
            'amount' => 'required|numeric|not_in:0'
        ]);

        $userId = $request->user()->id;
        $amount = $validated['amount'];

        $account = \Illuminate\Support\Facades\DB::table('accounts')
            ->where('user_id', $userId)
            ->where('name', 'Cartera')
            ->first();

        if ($account) {
            \Illuminate\Support\Facades\DB::table('accounts')
                ->where('id', $account->id)
                ->increment('balance', $amount);
        } else {
            $accountId = \Illuminate\Support\Facades\DB::table('accounts')->insertGetId([
                'user_id' => $userId,
                'name' => 'Cartera',
                'type' => 'cash',
                'balance' => $amount,
                'created_at' => now(),
                'updated_at' => now()
            ]);
            $account = (object)['id' => $accountId];
        }

        if ($amount < 0) {
            \Illuminate\Support\Facades\DB::table('transactions')->insert([
                'user_id' => $userId,
                'account_id' => $account->id,
                'type' => 'expense',
                'amount' => abs($amount),
                'description' => 'Retiro de Dinero Libre',
                'date' => now(),
                'created_at' => now(),
                'updated_at' => now()
            ]);
        }

        return response()->json(['message' => 'Money added successfully']);
    });

    // Resets Cartera balance to exactly match sum of funds (so free money = 0)
    Route::post('/reset-free-money', function (Request $request) {
        $userId = $request->user()->id;
        $fundsTotal = \Illuminate\Support\Facades\DB::table('funds')->where('user_id', $userId)->sum('balance');
        $account = \Illuminate\Support\Facades\DB::table('accounts')
            ->where('user_id', $userId)
            ->where('name', 'Cartera')
            ->first();
        if ($account) {
            \Illuminate\Support\Facades\DB::table('accounts')
                ->where('id', $account->id)
                ->update(['balance' => $fundsTotal]);
        } else {
            \Illuminate\Support\Facades\DB::table('accounts')->insert([
                'user_id' => $userId,
                'name' => 'Cartera',
                'type' => 'cash',
                'balance' => $fundsTotal,
                'created_at' => now(),
                'updated_at' => now()
            ]);
        }
        return response()->json(['message' => 'Free money reset', 'balance' => $fundsTotal]);
    });

    Route::get('/notifications', function (Request $request) {
        $notifications = \Illuminate\Support\Facades\DB::table('notifications')
            ->where('user_id', $request->user()->id)
            ->orderBy('created_at', 'desc')
            ->take(50)
            ->get();
        return response()->json($notifications);
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
        $fund = \Illuminate\Support\Facades\DB::table('funds')
            ->where('id', $id)
            ->where('user_id', $request->user()->id)
            ->first();

        if (!$fund) {
            return response()->json(['success' => false, 'message' => 'Fund not found'], 404);
        }

        \Illuminate\Support\Facades\DB::table('funds')
            ->where('id', $id)
            ->where('user_id', $request->user()->id)
            ->update($validated);

        if (isset($validated['balance']) && $validated['balance'] != $fund->balance) {
            $diff = $validated['balance'] - $fund->balance;
            $action = $diff > 0 ? 'agregado a' : 'retirado de';
            $absAmount = abs($diff);
            $title = $diff > 0 ? 'Dinero Agregado' : 'Dinero Retirado';

            \Illuminate\Support\Facades\DB::table('notifications')->insert([
                'user_id' => $request->user()->id,
                'type' => 'fund_update',
                'title' => $title,
                'message' => "Has {$action} \${$absAmount} la caja '{$fund->name}'.",
                'created_at' => now(),
                'updated_at' => now()
            ]);
        }

        return response()->json(['success' => true]);
    });

    Route::post('/funds/{id}/allocations', function (Request $request, $id) {
        $validated = $request->validate([
            'category_name' => 'required|string|max:100',
            'amount' => 'required|numeric',
            'icon' => 'nullable|string|max:5',
        ]);

        // SEC-03 / V-02: el fondo debe pertenecer al usuario autenticado.
        $fund = \Illuminate\Support\Facades\DB::table('funds')
            ->where('id', $id)
            ->where('user_id', $request->user()->id)
            ->first();
        if (!$fund) {
            return response()->json(['success' => false, 'message' => 'Fund not found'], 404);
        }

        // Simple logic to find or create category.
        // `categories` es global: una categoría existente no se modifica desde aquí.
        $category = \Illuminate\Support\Facades\DB::table('categories')
            ->where('name', $validated['category_name'])
            ->first();
        if (!$category) {
            $categoryId = \Illuminate\Support\Facades\DB::table('categories')->insertGetId([
                'name' => $validated['category_name'],
                'type' => 'expense',
                'icon' => $validated['icon'] ?? null
            ]);
        } else {
            $categoryId = $category->id;
        }

        $existing = \Illuminate\Support\Facades\DB::table('fund_allocations')
            ->where('fund_id', $id)
            ->where('category_id', $categoryId)
            ->first();

        if ($existing) {
            \Illuminate\Support\Facades\DB::table('fund_allocations')
                ->where('id', $existing->id)
                ->update(['amount' => $validated['amount']]);
        } else {
            \Illuminate\Support\Facades\DB::table('fund_allocations')->insert([
                'fund_id' => $id,
                'category_id' => $categoryId,
                'amount' => $validated['amount']
            ]);
        }

        $absAmount = abs($validated['amount']);
        $title = 'Asignación de Caja';

        \Illuminate\Support\Facades\DB::table('notifications')->insert([
            'user_id' => $request->user()->id,
            'type' => 'fund_allocation',
            'title' => $title,
            'message' => "Has asignado \${$absAmount} a '{$validated['category_name']}' en la caja '{$fund->name}'.",
            'created_at' => now(),
            'updated_at' => now()
        ]);

        return response()->json(['success' => true]);
    });

    Route::delete('/funds/{id}/allocations/{categoryName}', function (Request $request, $id, $categoryName) {
        // SEC-03 / V-02: el fondo debe pertenecer al usuario autenticado.
        $ownsFund = \Illuminate\Support\Facades\DB::table('funds')
            ->where('id', $id)
            ->where('user_id', $request->user()->id)
            ->exists();
        if (!$ownsFund) {
            return response()->json(['success' => false, 'message' => 'Fund not found'], 404);
        }

        $category = \Illuminate\Support\Facades\DB::table('categories')
            ->where('name', $categoryName)
            ->first();

        if ($category) {
            \Illuminate\Support\Facades\DB::table('fund_allocations')
                ->where('fund_id', $id)
                ->where('category_id', $category->id)
                ->delete();
        }

        return response()->json(['success' => true]);
    });

    Route::get('/user/transaction-stats', function (Request $request) {
        $userId = $request->user()->id;

        $transactions = \Illuminate\Support\Facades\DB::table('transactions')
            ->where('user_id', $userId)
            ->whereIn('type', ['income', 'expense'])
            ->select('amount', 'date', 'type')
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
            'category_id' => 'nullable|integer|exists:categories,id'
        ]);

        $validated['user_id'] = $request->user()->id;
        $id = \Illuminate\Support\Facades\DB::table('subscriptions')->insertGetId($validated);

        $validated['id'] = $id;
        return response()->json($validated);
    });

    Route::get('/investments', [\App\Http\Controllers\InvestmentController::class, 'index']);
    Route::post('/investments', [\App\Http\Controllers\InvestmentController::class, 'store']);
    Route::put('/investments/{id}', [\App\Http\Controllers\InvestmentController::class, 'update']);
    Route::delete('/investments/{id}', [\App\Http\Controllers\InvestmentController::class, 'destroy']);
    
    Route::post('/investment-alerts', [\App\Http\Controllers\InvestmentAlertController::class, 'store']);

    // Sports Logo Server Cache (compartida entre usuarios)
    Route::get('/sports/logos', function () {
        return response()->json(\Illuminate\Support\Facades\Cache::get('sports_logos', []));
    });
    // SEC-03 / V-07: solo URLs https de los CDNs de logos, tamaño acotado y límite de peticiones.
    Route::post('/sports/logos', function (Request $request) {
        $validated = $request->validate([
            'key' => 'required|string|max:150',
            'url' => [
                'nullable',
                'string',
                'max:500',
                'url:https',
                function (string $attribute, mixed $value, \Closure $fail) {
                    if (!is_string($value)) {
                        return; // la regla 'string' ya reporta el error
                    }
                    $host = strtolower((string) parse_url($value, PHP_URL_HOST));
                    if (!preg_match('/(^|\.)(api-sports\.io|sportmonks\.com)$/', $host)) {
                        $fail('The logo URL host is not allowed.');
                    }
                },
            ],
        ]);

        $maxEntries = 5000;
        $logos = \Illuminate\Support\Facades\Cache::get('sports_logos', []);
        if (!array_key_exists($validated['key'], $logos) && count($logos) >= $maxEntries) {
            return response()->json(['success' => true, 'stored' => false]);
        }

        $logos[$validated['key']] = $validated['url'] ?? null;
        \Illuminate\Support\Facades\Cache::put('sports_logos', $logos, 60*60*24*30); // 30 days
        return response()->json(['success' => true, 'stored' => true]);
    })->middleware('throttle:60,1');
});
