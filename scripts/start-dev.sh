#!/bin/sh
pip install -r /app/requirements.txt
gunicorn --bind 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker app:app $*
