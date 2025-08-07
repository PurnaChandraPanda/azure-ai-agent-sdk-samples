## Create conda env
```
conda deactivate
conda deactivate
conda env create -f conda.yml
conda activate langgraph_env
```

## Remove conda env
```
conda deactivate
conda env remove -n langgraph_env -y
```

## 0.1 Test

Test the langgraph orchestrate engine directly
```
./tests/test_langgraph_agents.sh
```

## 0.2 Test

Start the api server
```
./tests/start_api.sh
```

Test the api
```
./tests/test_langgraph_api.sh
```

## 0.3 Test in the docker
Update the docker/.env file SP credential details.

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
docker images | grep langgraph
docker rmi <image-id> -f
```

## Deploy as container app
- create acr with basic at least
- grant the current user at least contributor or acrpull+acrpush roles
- for container app deploy: `az provider register -n Microsoft.App`

```
az upgrade
./containerapp/containerapp_deploy.sh
```

Test the container app endpoint
```
./tests/test_containerapp_api.sh
```

