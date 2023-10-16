#!/bin/bash
# Builds the Docker image for the AWS Lambda deployment.
# Usage:
#   ./scripts/build_docker_image.sh

set -e

home_dir=$(pwd)

# Checks that the home directory is the root of the project.
if [[ ! -f "bot/requirements.txt" ]]; then
  echo "Error: Please run this script from the root of the project."
  exit 1
fi

# Checks CLI arguments.
if [[ $# -ne 0 ]]; then
  echo "Error: Invalid number of arguments."
  echo "Usage: ./scripts/build_docker_image.sh"
  exit 1
fi

# Creates the dist directory if it doesn't exist.
dist_dir=${home_dir}/dist/deployment/
mkdir -p $dist_dir

# Installs build dependencies.
python -m pip install --upgrade pip
python -m pip install --upgrade build wheel setuptools

# Builds the configuration file.
python configs/build.py aws -o ${dist_dir}/config.yaml

# Builds the project.
python -m build --wheel --outdir ${dist_dir} .

# Gets a unique JWT secret.
export JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Builds the API Docker image.
docker build -t dpsh-api -f scripts/docker/Dockerfile.api ${dist_dir}

# Pushes the API Docker image to ECR.
aws ecr get-login-password | docker login --username AWS --password-stdin ${ECR_URI}
docker tag dpsh-api:latest ${ECR_URI}:latest-api
docker push ${ECR_URI}:latest-api

# Builds the worker Docker image.
docker build -t dpsh-worker -f scripts/docker/Dockerfile.worker ${dist_dir}

# Pushes the worker Docker image to ECR.
aws ecr get-login-password | docker login --username AWS --password-stdin ${ECR_URI}
docker tag dpsh-worker:latest ${ECR_URI}:latest-worker
docker push ${ECR_URI}:latest-worker
