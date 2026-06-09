
## Packages used

```
@modelcontextprotocol/sdk  -> Actual MCP server/client SDK
zod                       -> Tool input schema validation
express                   -> HTTP server wrapper
cors                      -> Local/browser/API testing convenience
typescript                -> TS compilation
tsx                       -> Run TypeScript directly during development
@types/*                  -> Type definitions for TS
```

The SDK documentation recommends [McpServer](https://ts.sdk.modelcontextprotocol.io/documents/server.html) and Streamable HTTP for remote MCP servers.


## Dev run

- install packages
```
npm install
```

- it will get `package-lock.json` generated

- run locally
```
npm run build

npm start
```

- Test locally for mcp endpoint

```
curl http://127.0.0.1:3000/health
curl POST /mcp initialize
curl POST /mcp tools/list
curl POST /mcp tools/call
```

- For proper mcp lifecycle testing, following order is important

```
initialize
tools/list
tools/call
```

- run local tests for target host
```
./tests/local_mcp_test.sh
```

## Dev run/ docker

- build docker image
```
docker build -f dockers/Dockerfile -t node-mcp-http-server:local .
```

- create docker instance
```
docker run --rm \
  --name node-mcp-http-server-local \
  -p 3000:3000 \
  -e HOST=0.0.0.0 \
  -e PORT=3000 \
  -e LOG_LEVEL=debug \
  node-mcp-http-server:local
```

- run local tests for target docker host
```
./tests/local_mcp_test.sh
```

## Published instance/ azure container app

- Deploy container app
```
./containerapp/containerapp_deploy.sh
```

- Test contaner app

```
./tests/aca_mcp_test.sh
```

- Test container app on failure case

```
./tests/aca_mcp_handler_error_test.sh
```

