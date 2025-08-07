#!/bin/bash

set -e

# Set the PATH to discover src directory
ROOT_DIR="$(cd "$(dirname "$0")/.."; pwd)"
SRC_DIR="${ROOT_DIR}/src"
export PYTHONPATH="${SRC_DIR}:${PYTHONPATH}"

python tests/test_foundry_client.py

echo "done"