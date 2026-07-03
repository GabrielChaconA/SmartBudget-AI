<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});

Route::get('/test-mail', function () {
    $user = \App\Models\User::find(1);
    $subscription = \Illuminate\Support\Facades\DB::table('subscriptions')
        ->where('user_id', $user->id)
        ->first();
    \Illuminate\Support\Facades\Mail::to($user->email)->send(new \App\Mail\SubscriptionAlertMail($user, $subscription));
    return 'Sent';
});
