#!/bin/sh
source .env
docker build --no-cache -t safeapp:latest .
docker run --name safeapp -d -p 8000:5000 --rm  -e APP_SECRET_KEY=$APP_SECRET_KEY -e DB_URL=$DB_URL safeapp:latest
echo Aplikacja działa pod adresem https://localhost:8000/