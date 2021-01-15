#!/bin/bash
source venv/bin/activate
flask db upgrade
exec gunicorn -c config.py --certfile=./certs/cert.pem --keyfile=./certs/key.pem -b :5000 --access-logfile - --error-logfile - safeapp:app