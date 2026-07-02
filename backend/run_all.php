<?php
require __DIR__.'/vendor/autoload.php';
$app = require_once __DIR__.'/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use Illuminate\Support\Facades\DB;

try {
    echo "Running schema.sql...\n";
    $schema = file_get_contents('/var/www/html/schema.sql');
    if (!$schema) throw new Exception("Could not read schema.sql");
    DB::unprepared($schema);
    echo "Schema executed successfully.\n";

    echo "Running seed.sql...\n";
    $seed = file_get_contents('/var/www/html/seed.sql');
    if (!$seed) throw new Exception("Could not read seed.sql");
    DB::unprepared($seed);
    echo "Seed executed successfully.\n";
} catch (\Exception $e) {
    echo "Error executing: " . $e->getMessage() . "\n";
}
