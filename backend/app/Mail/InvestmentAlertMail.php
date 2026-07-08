<?php

namespace App\Mail;

use App\Models\InvestmentAlert;
use Illuminate\Bus\Queueable;
use Illuminate\Mail\Mailable;
use Illuminate\Queue\SerializesModels;

class InvestmentAlertMail extends Mailable
{
    use Queueable, SerializesModels;

    public $alert;
    public $currentPrice;

    public function __construct(InvestmentAlert $alert, $currentPrice)
    {
        $this->alert = $alert;
        $this->currentPrice = $currentPrice;
    }

    public function build()
    {
        $directionWord = $this->alert->direction === 'up' ? 'subido' : 'bajado';
        $emoji = $this->alert->direction === 'up' ? '📈' : '📉';

        return $this->subject("{$emoji} Alerta: {$this->alert->symbol} ha {$directionWord} a \$" . number_format($this->currentPrice, 2))
                    ->html($this->buildHtml());
    }

    private function buildHtml()
    {
        $directionWord = $this->alert->direction === 'up' ? 'subido' : 'bajado';
        $color = $this->alert->direction === 'up' ? '#1da1f2' : '#e02424';

        return "
        <div style='font-family: Arial, sans-serif; max-w-md; margin: 0 auto; background: #121212; color: #fff; padding: 20px; border-radius: 8px;'>
            <h2 style='text-align: center; color: {$color};'>¡Meta Alcanzada!</h2>
            <p>Hola <strong>{$this->alert->user->name}</strong>,</p>
            <p>Tu alerta para <strong>{$this->alert->symbol}</strong> se ha activado.</p>
            
            <div style='background: #1e1e1e; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid {$color};'>
                <p style='margin: 0;'>El precio ha {$directionWord} más del <strong>{$this->alert->target_percent}%</strong> desde que creaste la alerta.</p>
                <p style='font-size: 24px; font-weight: bold; margin: 10px 0;'>Precio Actual: $" . number_format($this->currentPrice, 2) . "</p>
                <p style='color: #888; font-size: 12px; margin: 0;'>Precio cuando creaste la alerta: $" . number_format($this->alert->base_price, 2) . "</p>
            </div>
            
            <p style='text-align: center; font-size: 12px; color: #666;'>Esta alerta ha sido desactivada. Puedes crear una nueva en tu panel de SmartBudget.</p>
        </div>
        ";
    }
}
