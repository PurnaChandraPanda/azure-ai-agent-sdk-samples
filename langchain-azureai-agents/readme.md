## Create conda env
```
conda deactivate
conda deactivate
conda env create -f conda.yml
conda activate langchain_env
```

## Remove conda env
```
conda deactivate
conda env remove -n langchain_env -y
```

## Tests

Start the api server
```
./tests/start_api.sh
```

Test the api
```
./tests/test_langchain_api.sh
```

Test the langchain orchestrate engine directly
```
./tests/test_langchain_agents.sh
```

## Test in the docker

Build the docker instance
```
./dockers/start.sh
```

Test the api exposed in docker container
```
./tests/test_docker_api.sh
```

Stop the docker instance
```
./dockers/stop.sh
```

Prune the base image
```
docker image prune -f
docker images | grep langchain
docker rmi <image-id> -f
```

## Deploy as container app
- create acr with basic at least
- grant the current user at least contributor or acrpull+acrpush roles
- for container app deploy: `az provider register -n Microsoft.App`

az upgrade
./containerapp/containerapp_deploy.sh

## Test the container app endpoint
./tests/test_containerapp_api.sh
