<?php
use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;

Schema::dropIfExists('notifications');
Schema::create('notifications', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained()->onDelete('cascade');
    $table->string('type');
    $table->string('title');
    $table->text('message');
    $table->boolean('is_read')->default(false);
    $table->timestamps();
});
echo "Notifications table created.\n";
