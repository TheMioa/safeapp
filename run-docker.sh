#!/bin/sh
docker build --no-cache -t safeapp:latest .
docker run --name safeapp -d -p 8000:5000 --rm safeapp:latest
echo Aplikacja działa pod adresem https://localhost:8000/