#!/bin/sh

# Use the PORT environment variable provided by Render, or default to 8000
PORT=${PORT:-8000}

# Run database migrations
echo "Running migrations..."
php artisan migrate --force

# Cache configuration, routes, and views for production performance
echo "Caching config and routes..."
php artisan config:cache
php artisan route:cache
php artisan view:cache

# Start Laravel Octane with RoadRunner
echo "Starting Laravel Octane on port $PORT..."
php artisan octane:start --server=roadrunner --host=0.0.0.0 --port=$PORT --workers=auto
