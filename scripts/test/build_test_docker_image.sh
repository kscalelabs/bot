#!/bin/bash
# Builds the Docker image for the AWS Lambda deployment.
# Usage:
#   ./scripts/test/build_test_docker_image.sh

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
  echo "Usage: ./scripts/test/build_test_docker_image.sh"
  exit 1
fi


# Log in to ECR.
aws ecr get-login-password | docker login --username AWS --password-stdin ${ECR_URI}

# Builds the test Docker image.
docker build -t dpsh-test -f scripts/test/Dockerfile .
docker tag dpsh-test:latest ${ECR_URI}:latest-test
docker push ${ECR_URI}:latest-test
docker rmi dpsh-test:latest
docker system prune -f
