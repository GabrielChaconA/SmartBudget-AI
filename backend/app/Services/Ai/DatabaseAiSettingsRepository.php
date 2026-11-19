<?php

namespace App\Services\Ai;

use Illuminate\Support\Facades\DB;

class DatabaseAiSettingsRepository implements AiSettingsRepository
{
    public function aiEnabled(int $userId): bool
    {
        $value = DB::table('settings')->where('user_id', $userId)->value('ai_enabled');

        // Sin fila de settings se usa el default de la columna (ai_enabled DEFAULT true).
        return $value === null ? true : (bool) $value;
    }
}
