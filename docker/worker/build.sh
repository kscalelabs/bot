#!/bin/bash
# Builds the Docker image for the AWS Lambda deployment.
# Usage:
#   ./docker/build_worker.sh

set -e

home_dir=$(pwd)

# Checks that the home directory is the root of the project.
if [[ ! -f "bot/__init__.py" ]]; then
  echo "Error: Please run this script from the root of the project."
  exit 1
fi

# Builds the worker Docker image.
docker build -t dpsh-worker -f docker/worker/Dockerfile .

# Log in to ECR.
aws ecr get-login-password | docker login --username AWS --password-stdin ${ECR_URI}

# Pushes the Docker image to ECR.
docker tag dpsh-worker:latest ${ECR_URI}:latest-worker
docker push ${ECR_URI}:latest-worker

# Triggers the AWS ECS deployment.
aws ecs update-service \
  --cluster dpsh-dev-cluster \
  --service dpsh-dev-worker \
  --force-new-deployment
