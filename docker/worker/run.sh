#!/bin/bash
# Runs the worker Docker image locally.
# Usage:
#   ./docker/worker/run.sh

set -e

# Checks that the home directory is the root of the project.
if [[ ! -f "bot/__init__.py" ]]; then
  echo "Error: Please run this script from the root of the project."
  exit 1
fi

# Rebuilds the worker Docker image, if necessary.
docker build -t dpsh-worker -f docker/worker/Dockerfile .

# Runs the worker Docker image.
docker run -p 8000:8000 --env-file docker/.env.local dpsh-worker:latest
