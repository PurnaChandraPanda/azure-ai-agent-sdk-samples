## Create conda env
```
cd agents-webapp-ui (if not already in this folder)
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
cd agents-webapp-ui (if not already in this folder)
./dockers/start.sh
```

Test the api exposed in docker container
```
cd agents-webapp-ui (if not already in this folder)
./tests/test_docker_api.sh
```

Stop the docker instance
```
cd agents-webapp-ui (if not already in this folder)
./dockers/stop.sh
```

## Deplpy the conatiner app
Pre-requisite
- Get local docker app running first for a test
- Have resources pre-created: 1) ACR, 2) AI Foundry
- Remember to feed in the variables defined in `containerapp_deploy.sh`
- Run the script to perform container app deploy action

```
cd agents-webapp-ui (if not already in this folder)
az upgrade
./containerapp/containerapp_deploy.sh
```

flowchart TD
  A --> B

flowchart TD
    %% Local build and push
    A[Start] --> B[Read Dockerfile<br/>and note EXPOSE port]
    B --> C[Build local Docker image]
    C --> D[Login to Azure Container Registry (ACR)]
    D --> E[Tag image with ACR login server<br/>(acrName.azurecr.io/repo:tag)]
    E --> F[Push tagged image to ACR]
    F --> G[Delete local image (cleanup)]

    %% Azure resource setup
    G --> H{Container App Environment exists?}
    H -- "No" --> I[Create Container App Environment]
    H -- "Yes" --> J[Reuse existing Environment]
    I --> K
    J --> K

    K{User Assigned Managed Identity (UAI)<br/>exists in Entra ID?}
    K -- "No" --> L[Create UAI]
    K -- "Yes" --> M[Reuse UAI]
    L --> N
    M --> N

    %% Role assignments
    N --> O[Assign UAI 'AcrPull' role on ACR<br/>(if missing)]
    O --> P[Assign UAI 'Azure AI User' on AI Foundry<br/>(if missing)]

    %% Container App creation/update
    P --> Q[Create/Update Azure Container App<br/>(if not already)]
    Q --> R[Parameters:<br