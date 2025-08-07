#!/bin/bash

compose_file="dockers/docker-compose.yml"
# env_file="dockers/.env"

# Start the Docker containers using docker-compose
docker-compose -f $compose_file up -d

# Wait for the containers to be ready and print logs
docker-compose -f $compose_file logs -f sk_ui_api
