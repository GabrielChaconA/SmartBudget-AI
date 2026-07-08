<?php
namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class FixDb extends Command
{
    protected $signature = 'fix:db';
    protected $description = 'Fix investments decimals';

    public function handle()
    {
        DB::statement('ALTER TABLE investments ALTER COLUMN quantity TYPE DECIMAL(24,12);');
        DB::statement('ALTER TABLE investments ALTER COLUMN average_price TYPE DECIMAL(24,12);');
        $this->info('DB Altered Successfully');
    }
}
