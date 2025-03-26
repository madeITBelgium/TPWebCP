#!/bin/bash
set -e

# Gebruik opgegeven UID en GID
TARGET_UID=${UID:-33}
TARGET_GID=${GID:-33}

# Pas de groep aan
if [ "$(id -g www-data)" != "$TARGET_GID" ]; then
    groupmod -g "$TARGET_GID" www-data
fi

# Pas de gebruiker aan
if [ "$(id -u www-data)" != "$TARGET_UID" ]; then
    usermod -u "$TARGET_UID" www-data
fi

# Zorg dat de rechten correct zijn
chown -R www-data:www-data /var/www/public
chown -R www-data:www-data /var/log/apache2