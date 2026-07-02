<?php
require __DIR__.'/vendor/autoload.php';
$app = require_once __DIR__.'/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use Illuminate\Support\Facades\DB;

try {
    $sql = file_get_contents('/var/www/html/seed.sql');
    if (!$sql) throw new Exception("Could not read seed.sql");
    DB::unprepared($sql);
    echo "Seed executed successfully.\n";
} catch (\Exception $e) {
    echo "Error executing seed: " . $e->getMessage() . "\n";
}
