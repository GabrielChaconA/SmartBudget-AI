<?php

namespace Tests\Concerns;

use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * Crea en la base de pruebas las tablas que hoy solo existen en schema.sql (no tienen
 * migración). Cuando SBI-31 agregue migraciones y factories, este trait se elimina.
 */
trait CreatesLegacyTables
{
    protected function createLegacyTables(): void
    {
        Schema::create('settings', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id');
            $table->string('currency', 10)->default('MXN');
            $table->string('language', 10)->default('es');
            $table->string('theme', 20)->default('dark');
            $table->decimal('monthly_income', 15, 2)->default(0);
            $table->integer('payday')->default(15);
            $table->boolean('ai_enabled')->default(true);
            $table->timestamps();
        });

        Schema::create('accounts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id');
            $table->string('name');
            $table->decimal('balance', 15, 2)->default(0);
            $table->string('color', 20)->nullable();
            $table->string('icon', 100)->nullable();
            $table->string('type', 50)->nullable();
            $table->string('currency', 10)->default('MXN');
            $table->timestamps();
        });

        Schema::create('funds', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id');
            $table->string('name');
            $table->decimal('balance', 15, 2)->default(0);
            $table->string('color', 20)->nullable();
            $table->string('icon', 100)->nullable();
            $table->timestamps();
        });

        Schema::create('categories', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('type', 50);
            $table->string('color', 20)->nullable();
            $table->string('icon', 100)->nullable();
            $table->timestamps();
        });

        Schema::create('fund_allocations', function (Blueprint $table) {
            $table->id();
            $table->foreignId('fund_id');
            $table->foreignId('category_id');
            $table->decimal('amount', 15, 2)->default(0);
            $table->timestamps();
        });

        Schema::create('transactions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id');
            $table->foreignId('account_id')->nullable();
            $table->foreignId('category_id')->nullable();
            $table->string('type', 50);
            $table->decimal('amount', 15, 2);
            $table->text('description')->nullable();
            $table->text('notes')->nullable();
            $table->timestamp('date');
            $table->timestamps();
        });

        Schema::create('subscriptions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id');
            $table->string('name');
            $table->decimal('amount', 15, 2);
            $table->string('billing_cycle', 50);
            $table->date('next_billing_date')->nullable();
            $table->foreignId('category_id')->nullable();
            $table->foreignId('account_id')->nullable();
            $table->timestamps();
        });

        Schema::create('investments', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id');
            $table->foreignId('account_id')->nullable();
            $table->string('symbol', 50);
            $table->decimal('quantity', 24, 12);
            $table->decimal('average_price', 24, 12);
            $table->string('currency', 10)->default('MXN');
            $table->string('type', 50);
            $table->timestamps();
        });
    }
}
