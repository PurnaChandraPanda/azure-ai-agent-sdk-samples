#!/bin/bash

compose_file="dockers/docker-compose.yml"

# Stop the Docker containers using docker-compose
docker-compose -f dockers/docker-compose.yml down