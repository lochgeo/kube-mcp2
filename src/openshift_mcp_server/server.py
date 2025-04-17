from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Optional
import requests

from kubernetes.client import CustomObjectsApi
from kubernetes import client, config
from mcp.server.fastmcp import FastMCP, Context
from openshift_mcp_server.config import OPENSHIFT_SERVER, OPENSHIFT_USERNAME, OPENSHIFT_PASSWORD
from openshift_mcp_server.tools import (
    list_namespaces, list_pods, get_pod_logs, list_deployments, list_routes,
    get_route, list_services, get_service, get_all_services, get_cluster_info,
    list_tools_and_resources, create_deployment, validate_openshift_manifest
)

@dataclass
class AppContext:
    k8s_api: client.CoreV1Api
    apps_api: client.AppsV1Api
    route_api: CustomObjectsApi

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Initialize Kubernetes/OpenShift client with username/password if provided via env vars, else use kube config."""
    server_url = OPENSHIFT_SERVER
    username = OPENSHIFT_USERNAME
    password = OPENSHIFT_PASSWORD
    if server_url and username and password:
        oauth_url = f"{server_url}/oauth/authorize?response_type=token&client_id=openshift-challenging-client"
        session = requests.Session()
        session.get(oauth_url, verify=False)
        auth = requests.auth.HTTPBasicAuth(username, password)
        response = session.post(oauth_url, auth=auth, allow_redirects=False, verify=False)
        location = response.headers.get("Location", "")
        token = None
        if "access_token=" in location:
            token = location.split("access_token=")[1].split("&")[0]
        if not token:
            raise Exception("Failed to obtain OpenShift token via OAuth")
        configuration = client.Configuration()
        configuration.host = server_url
        configuration.verify_ssl = False
        configuration.api_key = {"authorization": f"Bearer {token}"}
        api_client = client.ApiClient(configuration)
        k8s_api = client.CoreV1Api(api_client)
        apps_api = client.AppsV1Api(api_client)
        route_api = CustomObjectsApi(api_client)
    else:
        config.load_kube_config()
        k8s_api = client.CoreV1Api()
        apps_api = client.AppsV1Api()
        route_api = CustomObjectsApi()
    try:
        yield AppContext(k8s_api=k8s_api, apps_api=apps_api, route_api=route_api)
    finally:
        pass

# Create an MCP server for OpenShift operations with lifespan
mcp = FastMCP("OpenShift MCP Server", lifespan=app_lifespan)

# Register tools and resources
mcp.tool()(list_namespaces)
mcp.tool()(list_pods)
mcp.tool()(get_pod_logs)
mcp.tool()(list_deployments)
mcp.tool()(list_routes)
mcp.tool()(get_route)
mcp.tool()(list_services)
mcp.tool()(get_service)
mcp.resource("cluster://services")(get_all_services)
mcp.resource("cluster://info")(get_cluster_info)
mcp.tool()(create_deployment)
mcp.tool()(validate_openshift_manifest)
