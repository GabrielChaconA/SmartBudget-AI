<?php
require 'vendor/autoload.php';
$app = require_once 'bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

$users = App\Models\User::all();
foreach ($users as $user) {
    $funds = Illuminate\Support\Facades\DB::table('funds')->where('user_id', $user->id)->sum('balance');
    $account = Illuminate\Support\Facades\DB::table('accounts')->where('user_id', $user->id)->where('name', 'Cartera')->first();
    if ($account) {
        Illuminate\Support\Facades\DB::table('accounts')->where('id', $account->id)->update(['balance' => $funds]);
        echo "Fixed money for user " . $user->id . " (" . $user->name . "). New balance: " . $funds . "\n";
    } else {
        echo "No Cartera found for user " . $user->id . "\n";
    }
}
