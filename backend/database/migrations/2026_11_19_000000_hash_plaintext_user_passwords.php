<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;

/**
 * SEC-03 / V-01: aplica hash a las contraseñas guardadas en texto plano (p. ej. las del
 * seed) para que el login ya no tenga que compararlas en claro. El usuario conserva la
 * misma contraseña. Es idempotente: las contraseñas que ya son hash no se tocan.
 */
return new class extends Migration
{
    public function up(): void
    {
        DB::table('users')
            ->select(['id', 'password'])
            ->whereNotNull('password')
            ->orderBy('id')
            ->chunkById(200, function ($users) {
                foreach ($users as $user) {
                    if ($user->password === '' || Hash::isHashed($user->password)) {
                        continue;
                    }
                    DB::table('users')
                        ->where('id', $user->id)
                        ->update(['password' => Hash::make($user->password)]);
                }
            });
    }

    /**
     * Irreversible: no se puede (ni se debe) recuperar el texto plano.
     */
    public function down(): void
    {
        //
    }
};
