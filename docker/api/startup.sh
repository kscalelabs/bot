#!/bin/bash

# Create the database, if it doesn't exist.
python3.11 -m bot.api.db

# Run Aerich migrations.
aerich upgrade

# Start FastAPI application.
gunicorn --bind 0.0.0.0:8000 bot.api.app.main:app --worker-class uvicorn.workers.UvicornWorker
