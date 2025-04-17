# OpenShift MCP Server

This is a Model Context Protocol (MCP) server that provides tools for interacting with OpenShift/Kubernetes clusters.

## Features

- Modular codebase for maintainability (all core logic is under `src/openshift_mcp_server/`)
- Security checks for deployment manifests (enforced during deployment creation)
- Standardized error handling and logging
- List namespaces, pods, deployments, services, and routes
- Get pod logs and service/route details
- Validate OpenShift manifests for best practices
- Get cluster information and resources

## Project Structure

- `src/openshift_mcp_server/`: Main server and tool modules
    - `server.py`: MCP server setup and tool/resource registration
    - `tools.py`: All tool/resource implementations
    - `config.py`: Environment variable and configuration management
    - `errors.py`: Standardized error responses
    - `logging_utils.py`: Logging configuration
    - `security.py`: Security validation for manifests
- `tests/`: Test suite (pytest-based)
- `.gitignore`: Excludes venvs, caches, and local configs

## Setup

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2. Configure cluster access:
    - Via `~/.kube/config` (default)
    - Or set these environment variables:
      - `OPENSHIFT_SERVER` (API URL)
      - `OPENSHIFT_USERNAME` / `OPENSHIFT_PASSWORD`

## Usage

From the project root:

To run the server in development mode:
```bash
PYTHONPATH=src mcp dev src/openshift_mcp_server/server.py
```

To install the server in Claude Desktop:
```bash
PYTHONPATH=src mcp install src/openshift_mcp_server/server.py
```

## Available Tools

- `list_namespaces(ctx)`: Lists all namespaces
- `list_pods(namespace, ctx)`: Lists pods in a namespace
- `get_pod_logs(namespace, pod_name, ctx, container=None)`: Gets logs from a pod
- `list_deployments(namespace, ctx)`: Lists deployments in a namespace
- `list_services(namespace, ctx)`: Lists services in a namespace
- `get_service(namespace, service_name, ctx)`: Gets details for a service
- `list_routes(namespace, ctx)`: Lists OpenShift routes
- `get_route(namespace, route_name, ctx)`: Gets details for a route
- `create_deployment(namespace, deployment_manifest, ctx)`: Creates a deployment (with security checks)
- `validate_openshift_manifest(manifest, ctx)`: Validates a deployment manifest for best practices

## Available Resources

- `cluster://info`: Get basic cluster information
- `cluster://services`: List all services across namespaces

## Security & Error Handling

- All deployments are validated for dangerous fields (e.g., `hostNetwork`, `privileged`, `hostPath`, etc.)
- Standardized error responses and logging for all tools

## Testing

Run all tests using:
```bash
PYTHONPATH=src pytest tests/
```

## Notes
- Ensure your environment variables or kubeconfig are set up before running the server.
- For local development, activate your virtual environment and install requirements first.
