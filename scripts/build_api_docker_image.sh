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

# Downloads a static copy of FFMPEG.
if [[ ! -f "${dist_dir}/ffmpeg/bin/ffmpeg" ]]; then
  echo "Downloading static FFMPEG files..."
  wget --no-check-certificate https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-arm64-static.tar.xz
  wget --no-check-certificate https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-arm64-static.tar.xz.md5
  md5sum -c ffmpeg-git-arm64-static.tar.xz.md5
  mkdir -p ${dist_dir}/ffmpeg/bin/
  tar -xf ffmpeg-git-arm64-static.tar.xz -C ${dist_dir}/ffmpeg/bin/ --strip-components=1
  rm ffmpeg-git-arm64-static.tar.xz ffmpeg-git-arm64-static.tar.xz.md5
fi

# Log in to ECR.
aws ecr get-login-password | docker login --username AWS --password-stdin ${ECR_URI}

# Builds the API Docker image.
docker build -t dpsh-api -f scripts/docker/Dockerfile.api .
docker tag dpsh-api:latest ${ECR_URI}:latest-api
docker push ${ECR_URI}:latest-api
if [[ $prune != false ]]; then
  echo "Pruning Docker images..."
  docker rmi dpsh-api:latest
  docker rmi ${ECR_URI}:latest-api
  docker system prune -f
fi

# Updates the Lambda function.
aws lambda update-function-code \
    --function-name ${LAMBDA_FUNCTION_NAME} \
    --image-uri ${ECR_URI}:latest-api \
    --no-cli-pager
