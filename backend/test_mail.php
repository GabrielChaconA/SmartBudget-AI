<?php
require __DIR__.'/vendor/autoload.php';
$app = require_once __DIR__.'/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

try {
    $user = \App\Models\User::find(1);
    $sub = \Illuminate\Support\Facades\DB::table('subscriptions')->where('user_id', 1)->where('name', 'like', '%Spotify%')->first();
    if (!$sub) {
        $sub = (object) [
            'name' => 'Spotify Premium',
            'amount' => 115.00,
            'billing_cycle' => 'monthly',
            'next_billing_date' => date('Y-m-d', strtotime('+1 day')),
            'status' => 'active'
        ];
    }
    \Illuminate\Support\Facades\Mail::to($user->email)->send(new \App\Mail\SubscriptionAlertMail($user, $sub));
    echo "Success: Email sent to " . $user->email . "\n";
} catch (\Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
