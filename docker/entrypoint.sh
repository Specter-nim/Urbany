#!/usr/bin/env sh
set -e

echo "[entrypoint] Esperando servicios dependientes..."

# Espera a Postgres si USE_POSTGRES=true
if [ "${USE_POSTGRES}" = "true" ]; then
  until nc -z "${DB_HOST}" "${DB_PORT}"; do
    echo "[entrypoint] Esperando Postgres en ${DB_HOST}:${DB_PORT}..."
    sleep 2
  done
fi

# Espera a Redis
until nc -z "${REDIS_HOST}" "${REDIS_PORT}"; do
  echo "[entrypoint] Esperando Redis en ${REDIS_HOST}:${REDIS_PORT}..."
  sleep 2
done

echo "[entrypoint] Aplicando migraciones y collectstatic..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "[entrypoint] Iniciando aplicación: $@"
exec "$@"