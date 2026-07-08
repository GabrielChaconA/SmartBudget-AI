<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class InvestmentAlert extends Model
{
    use HasFactory;

    protected $fillable = [
        'user_id',
        'symbol',
        'target_percent',
        'base_price',
        'target_price',
        'direction',
        'is_active',
    ];

    public function user()
    {
        return $this->belongsTo(User::class);
    }
}
