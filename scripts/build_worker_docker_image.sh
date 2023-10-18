#!/bin/bash
# Builds the Docker image for the AWS Lambda deployment.
# Usage:
#   ./scripts/build_docker_images.sh <prune?>

set -e

home_dir=$(pwd)

# Checks that the home directory is the root of the project.
if [[ ! -f "bot/__init__.py" ]]; then
  echo "Error: Please run this script from the root of the project."
  exit 1
fi

# Checks CLI arguments.
if [[ $# -ne 0 ]] && [[ $# -ne 1 ]]; then
  echo "Error: Invalid number of arguments."
  echo "Usage: ./scripts/build_docker_images.sh"
  exit 1
fi

# Get the prune flag.
prune=${CLEANUP_DOCKER:-false}

# Creates the dist directory if it doesn't exist.
dist_dir=dist/
mkdir -p $dist_dir

# Builds the configuration file.
python configs/build.py aws -o ${dist_dir}/config.yaml

# Log in to ECR.
aws ecr get-login-password | docker login --username AWS --password-stdin ${ECR_URI}

# Builds the worker Docker image.
docker build -t dpsh-worker -f scripts/docker/Dockerfile.worker .
docker tag dpsh-worker:latest ${ECR_URI}:latest-worker
docker push ${ECR_URI}:latest-worker
if [[ $prune != false ]]; then
  echo "Pruning Docker images..."
  docker rmi dpsh-worker:latest
  docker rmi ${ECR_URI}:latest-worker
  docker system prune -f
fi

# Updates the ECS cluster.
# aws ecs update-service \
#     --cluster ${ECS_CLUSTER_NAME} \
#     --service dpsh-worker-service \
#     --task-definition dpsh-worker-task-definition \
#     --desired-count 1 \
#     --force-new-deployment \
#     --no-cli-pager
