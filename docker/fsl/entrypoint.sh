#!/usr/bin/env sh

if [[ -z $1 ]]; then
    echo "[ERROR] Provide at least a command!"
    exit 1
fi

source /usr/.venv/bin/activate

case $1 in

  start)
    /usr/.venv/bin/python -O -m alembic upgrade head && \
    /usr/.venv/bin/python -O -m uvicorn src.main:app --host 0.0.0.0 --port 8000
    ;;

  init-db)
    /usr/.venv/bin/python -m alembic upgrade head
    ;;

  start-dev)
    /usr/.venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    ;;

  *)
    exec "$@"
    ;;
esac