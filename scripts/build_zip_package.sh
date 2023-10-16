#!/bin/bash
# Packages the Python project for AWS Lambda deployment.
# Usage:
#   ./scripts/package_for_lambda.sh <dev/prod>

set -e

home_dir=$(pwd)

# Checks that the home directory is the root of the project.
if [[ ! -f "bot/requirements.txt" ]]; then
  echo "Error: Please run this script from the root of the project."
  exit 1
fi

# Checks CLI arguments.
if [[ $# -ne 1 ]]; then
  echo "Error: Invalid number of arguments."
  echo "Usage: ./scripts/package_for_lambda.sh <dev/prod>"
  exit 1
fi

# Gets the mode (either "dev" or "prod").
mode=${1}
if [[ $mode != "dev" && $mode != "prod" ]]; then
  echo "Error: Invalid mode. Please specify either 'dev' or 'prod'."
  exit 1
fi

# Create the dist directory if it doesn't exist.
dist_dir=${home_dir}/dist/package/${mode}
mkdir -p $dist_dir

# Installs build dependencies.
python -m pip install --upgrade pip
python -m pip install --upgrade build wheel setuptools

# Builds the project.
pip wheel --wheel-dir ${dist_dir}/wheels -r bot/requirements.txt
python -m build --wheel --outdir ${dist_dir}/wheels .

# Zips the project.
zip -r ${dist_dir}/lambda.zip ${dist_dir}/wheels

# Cleans up.
rm -rf ${dist_dir}/wheels

# Uploads the project to S3.
aws s3 cp ${dist_dir}/lambda.zip s3://dpsh-data-${mode}/lambda/package-$(date +%Y%m%d%H%M%S).zip

echo "Done."
