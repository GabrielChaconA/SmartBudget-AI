FROM php:8.3-cli-alpine

# Install system dependencies required for PostgreSQL and RoadRunner
RUN apk add --no-cache \
    curl \
    git \
    libpq-dev \
    postgresql-dev \
    linux-headers

# Install PHP extensions
RUN docker-php-ext-install pdo pdo_pgsql pcntl sockets

# Install Composer
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install dependencies (no-dev for production)
RUN composer install --no-dev --optimize-autoloader --no-interaction

# Download RoadRunner binary
RUN ./vendor/bin/rr get --no-interaction

# Set permissions for Laravel directories
RUN chmod -R 777 storage bootstrap/cache

# Make the start script executable
RUN chmod +x start.sh

# The start.sh script will handle migrations and starting the server
CMD ["./start.sh"]
