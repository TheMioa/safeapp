#!/bin/sh
docker build -t safeapp:latest .
docker run --name safeapp -d -p 8000:5000 --rm safeapp:latest