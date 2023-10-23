#!/bin/bash
# Builds the Docker image for the AWS Lambda deployment.
# Usage:
#   ./docker/api/build.sh

set -e

# Checks that the home directory is the root of the project.
if [[ ! -f "bot/__init__.py" ]]; then
  echo "Error: Please run this script from the root of the project."
  exit 1
fi

# Builds the API Docker image.
docker build -t dpsh-api -f docker/api/Dockerfile .

# Log in to ECR.
aws ecr get-login-password | docker login --username AWS --password-stdin ${ECR_URI}

# Pushes the Docker image to ECR.
docker tag dpsh-api:latest ${ECR_URI}:latest-api
docker push ${ECR_URI}:latest-api

# Triggers the AWS ECS deployment.
aws ecs update-service \
  --cluster dpsh-dev-cluster \
  --service dpsh-dev-api \
  --force-new-deployment
