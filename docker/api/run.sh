#!/bin/bash
# Re-builds and runs the API Docker image locally.
# Usage:
#   ./docker/api/run.sh

set -e

# Checks that the home directory is the root of the project.
if [[ ! -f "bot/__init__.py" ]]; then
  echo "Error: Please run this script from the root of the project."
  exit 1
fi

# Rebuilds the API Docker image, if necessary.
docker build -t dpsh-api -f docker/api/Dockerfile .

# Runs the API Docker image.
docker run -p 8000:8000 --env-file .env.local dpsh-api:latest
# docker run -p 8000:8000 --env-file .env.dev dpsh-api:latest
