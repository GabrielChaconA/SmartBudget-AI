<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Models\InvestmentAlert;
use Illuminate\Support\Facades\Mail;
use App\Mail\InvestmentAlertMail;
use Illuminate\Support\Facades\Http;

class CheckInvestmentAlerts extends Command
{
    protected $signature = 'alerts:check';
    protected $description = 'Check active investment alerts against current prices (simulated logic for API)';

    public function handle()
    {
        $alerts = InvestmentAlert::where('is_active', true)->with('user')->get();
        if ($alerts->isEmpty()) {
            return;
        }

        // Group by symbol to optimize API calls
        $symbols = $alerts->pluck('symbol')->unique()->values()->all();

        // Very basic mock API fetching to avoid hard-coding Binance/Finnhub logic in Laravel without a service wrapper
        // In a real scenario, this would use Finnhub API for stocks and Binance API for crypto
        // For the sake of this implementation, we will query Binance for crypto and Finnhub for stocks

        // We'll separate them by checking if it ends in USDT for Binance, else Finnhub
        // Note: The frontend normalizes crypto symbols to lower case 'bitcoin' etc, but let's assume 
        // the frontend sent the proper Coingecko ID or Ticker.
        
        $prices = [];

        foreach ($symbols as $symbol) {
            // Simple heuristic: if it has more than 5 chars, it's likely a crypto ID like 'bitcoin'
            // We use CoinGecko here just to get the price reliably in USD
            if (strlen($symbol) > 5 || in_array($symbol, ['btc', 'eth', 'sol', 'ada'])) {
                try {
                    $response = Http::get("https://api.coingecko.com/api/v3/simple/price?ids={$symbol}&vs_currencies=usd");
                    if ($response->successful()) {
                        $prices[$symbol] = $response->json()[$symbol]['usd'] ?? null;
                    }
                } catch (\Exception $e) {}
            } else {
                // Finnhub for stocks
                try {
                    $token = env('VITE_FINNHUB_API_KEY');
                    $response = Http::get("https://finnhub.io/api/v1/quote?symbol={$symbol}&token={$token}");
                    if ($response->successful()) {
                        $prices[$symbol] = $response->json()['c'] ?? null;
                    }
                } catch (\Exception $e) {}
            }
        }

        foreach ($alerts as $alert) {
            $currentPrice = $prices[$alert->symbol] ?? null;
            if (!$currentPrice) continue;

            $triggered = false;
            
            if ($alert->direction === 'up' && $currentPrice >= $alert->target_price) {
                $triggered = true;
            } else if ($alert->direction === 'down' && $currentPrice <= $alert->target_price) {
                $triggered = true;
            }

            if ($triggered) {
                Mail::to($alert->user->email)->send(new InvestmentAlertMail($alert, $currentPrice));
                $alert->update(['is_active' => false]);
            }
        }
    }
}
