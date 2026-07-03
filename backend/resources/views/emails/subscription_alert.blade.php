<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Subscription Alert</title>
    <style>
        body {
            font-family: 'Inter', Helvetica, Arial, sans-serif;
            background-color: #09090b;
            color: #ffffff;
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }
        .container {
            max-width: 600px;
            margin: 40px auto;
            background-color: #18181b;
            border-radius: 12px;
            border: 1px solid #27272a;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        }
        .header {
            background-color: #10b981;
            color: #000000;
            padding: 24px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .content {
            padding: 32px 24px;
        }
        .service-card {
            background-color: #09090b;
            border: 1px solid #27272a;
            border-radius: 8px;
            padding: 20px;
            margin: 24px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .service-info h2 {
            margin: 0;
            font-size: 20px;
            color: #ffffff;
        }
        .service-info p {
            margin: 4px 0 0;
            color: #a1a1aa;
            font-size: 14px;
        }
        .price {
            font-size: 28px;
            font-weight: bold;
            color: #10b981;
            text-align: right;
        }
        .alert-box {
            background-color: rgba(16, 185, 129, 0.1);
            border-left: 4px solid #10b981;
            padding: 16px;
            border-radius: 4px;
            margin-bottom: 24px;
        }
        .alert-box p {
            margin: 0;
            color: #d1d5db;
        }
        .alert-box strong {
            color: #10b981;
        }
        .footer {
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #71717a;
            border-top: 1px solid #27272a;
        }
        .btn {
            display: inline-block;
            background-color: #10b981;
            color: #000000;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-weight: 600;
            margin-top: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Recordatorio de Cobro</h1>
        </div>
        <div class="content">
            <p style="color: #ffffff; font-size: 16px;">Hola <strong style="color: #ffffff;">{{ $user->email }}</strong>,</p>
            
            <div class="alert-box">
                <p>⚠️ Tienes un cargo programado en las próximas <strong>24 horas</strong>. Aún estás a tiempo de cancelar esta suscripción si ya no la utilizas.</p>
            </div>

            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #09090b; border: 1px solid #27272a; border-radius: 8px; margin: 24px 0;">
                @php
                    $logos = [
                        'NETFLIX' => 'netflix', 'TEFLIX' => 'netflix',
                        'SPOTIFY' => 'spotify', 'SPOTIFFY' => 'spotify',
                        'CRUNCHYROLL' => 'crunchyroll', 'RUNCHYROLL' => 'crunchyroll',
                        'ICLOUD' => 'icloud', 'APPLE' => 'apple',
                        'YOUTUBE' => 'youtube',
                        'AMAZON' => 'amazon', 'AMAZON PRIME' => 'primevideo',
                        'HBO' => 'hbo', 'HBO MAX' => 'hbomax', 'MAX' => 'hbomax',
                        'XBOX' => 'xbox', 'GAME PASS' => 'xbox',
                        'PLAYSTATION' => 'playstation', 'PS PLUS' => 'playstation',
                        'NINTENDO' => 'nintendo'
                    ];
                    $nameKey = strtoupper(trim($subscription->name));
                    $slug = $logos[$nameKey] ?? null;
                @endphp
                <tr>
                    <td class="service-info" style="padding: 20px; text-align: left;">
                        <h2 style="margin: 0; font-size: 22px; color: #ffffff; display: flex; align-items: center;">
                            @if($slug)
                                <img src="https://cdn.simpleicons.org/{{ $slug }}" width="28" height="28" style="margin-right: 12px; vertical-align: middle;" alt="Logo">
                            @endif
                            {{ $subscription->name }}
                        </h2>
                        <p style="margin: 4px 0 0; color: #a1a1aa; font-size: 14px;">
                            @if($slug) <span style="margin-left: 40px;"></span> @endif Renovación automática
                        </p>
                    </td>
                    <td class="price" style="padding: 20px; text-align: right; font-size: 28px; font-weight: bold; color: #10b981; white-space: nowrap;">
                        ${{ number_format($subscription->amount, 2) }}
                    </td>
                </tr>
            </table>

            <p style="text-align: center; margin-top: 32px;">
                <a href="{{ config('app.url') }}/subscriptions" class="btn">Gestionar Mis Suscripciones</a>
            </p>
        </div>
        <div class="footer">
            &copy; {{ date('Y') }} SmartBudget AI. Todos los derechos reservados.<br>
            Has recibido este correo porque tienes activadas las alertas de suscripciones.
        </div>
    </div>
</body>
</html>
