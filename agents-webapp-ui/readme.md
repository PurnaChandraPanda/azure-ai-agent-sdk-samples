## Create conda env
```
conda env create -f conda.yml
conda activate sk_ui_env
```

## Remove conda env
```
conda deactivate
conda env remove -n sk_ui_env -y
```

## Confirm that the code can be run fine in local docker
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

## Deplpy the conatiner app
Pre-requisite
- Get local docker app running first for a test
- Have resources pre-created: 1) ACR, 2) AI Foundry
- Remember to feed in the variables defined in `containerapp_deploy.sh`
- Run the script to perform container app deploy action

```
az upgrade
./containerapp/containerapp_deploy.sh
```