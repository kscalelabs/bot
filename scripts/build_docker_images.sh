#!/bin/bash
# Builds the Docker image for the AWS Lambda deployment.
# Usage:
#   ./scripts/build_docker_images.sh <prune?>

set -e

home_dir=$(pwd)

# Checks that the home directory is the root of the project.
if [[ ! -f "bot/requirements.txt" ]]; then
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
prune=false
if [[ $# -eq 1 ]]; then
  if [[ $1 == "prune" ]]; then
    prune=true
  else
    echo "Error: Invalid argument."
    echo "Usage: ./scripts/build_docker_images.sh"
    exit 1
  fi
fi

# Creates the dist directory if it doesn't exist.
dist_dir=dist/
mkdir -p $dist_dir

# Gets a unique JWT secret.
export JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Builds the configuration file.
python configs/build.py aws -o ${dist_dir}/config.yaml

# Downloads a static copy of FFMPEG.
if [[ ! -f "${dist_dir}/ffmpeg/bin/ffmpeg" ]]; then
  echo "Downloading static FFMPEG files..."
  wget --no-check-certificate https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
  wget --no-check-certificate https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz.md5
  md5sum -c ffmpeg-release-amd64-static.tar.xz.md5
  mkdir -p ${dist_dir}/ffmpeg/bin/
  tar -xf ffmpeg-release-amd64-static.tar.xz -C ${dist_dir}/ffmpeg/bin/ --strip-components=1
  rm ffmpeg-release-amd64-static.tar.xz ffmpeg-release-amd64-static.tar.xz.md5
fi

# Log in to ECR.
aws ecr get-login-password | docker login --username AWS --password-stdin ${ECR_URI}

# Builds the API Docker image.
docker build -t dpsh-api -f scripts/docker/Dockerfile.api .
docker tag dpsh-api:latest ${ECR_URI}:latest-api
docker push ${ECR_URI}:latest-api
if [[ $prune == true ]]; then
  docker rmi dpsh-api:latest
  docker system prune -f
fi

# Updates the Lambda function.
aws lambda update-function-code \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --image-uri ${ECR_URI}:latest-api \
    --no-cli-pager

# Builds the worker Docker image.
docker build -t dpsh-worker -f scripts/docker/Dockerfile.worker .
docker tag dpsh-worker:latest ${ECR_URI}:latest-worker
docker push ${ECR_URI}:latest-worker
if [[ $prune == true ]]; then
  docker rmi dpsh-worker:latest
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
