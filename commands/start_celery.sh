#!/bin/sh
export PYTHONPATH=/wms/src

celery -A config worker --loglevel="${CELERY_LOG_LEVEL:-DEBUG}" -c "${CELERY_WORKERS_COUNT:-4}" &
celery -A config beat --loglevel="${CELERY_LOG_LEVEL:-DEBUG}" &
celery -A config flower --port=5555 --broker="${CELERY_BROKER_URL}" &

wait
