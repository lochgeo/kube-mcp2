from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Optional
import requests

from kubernetes.client import CustomObjectsApi
from kubernetes import client, config
from mcp.server.fastmcp import FastMCP
from openshift_mcp_server.config import OPENSHIFT_SERVER, OPENSHIFT_USERNAME, OPENSHIFT_PASSWORD
from openshift_mcp_server.tools import (
    list_namespaces, list_pods, get_pod_logs, list_deployments, list_routes,
    get_route, list_services, get_service, get_all_services, get_cluster_info,
    create_deployment, validate_openshift_manifest,
    list_configmaps, list_secrets, list_jobs, list_pvcs, list_ingresses, list_rolebindings,
    list_projects, list_serviceaccounts, list_resourcequotas, list_events
)

@dataclass
class AppContext:
    k8s_api: client.CoreV1Api
    apps_api: client.AppsV1Api
    route_api: CustomObjectsApi
    batch_api: client.BatchV1Api
    networking_api: client.NetworkingV1Api
    rbac_api: client.RbacAuthorizationV1Api

def get_api_client_with_token(server_url: str, username: str, password: str) -> client.ApiClient:
    """Authenticate with OpenShift and return an ApiClient using a Bearer token."""
    oauth_url = f"{server_url}/oauth/authorize?response_type=token&client_id=openshift-challenging-client"
    session = requests.Session()
    session.get(oauth_url, verify=False)
    auth = requests.auth.HTTPBasicAuth(username, password)
    response = session.post(oauth_url, auth=auth, allow_redirects=False, verify=False)
    location = response.headers.get("Location", "")
    if "access_token=" not in location:
        raise Exception("Failed to obtain OpenShift token via OAuth")
    token = location.split("access_token=")[1].split("&")[0]
    configuration = client.Configuration()
    configuration.host = server_url
    configuration.verify_ssl = False
    configuration.api_key = {"authorization": f"Bearer {token}"}
    return client.ApiClient(configuration)

def build_app_context(api_client: Optional[client.ApiClient] = None) -> AppContext:
    """Create an AppContext with or without a custom ApiClient."""
    return AppContext(
        k8s_api=client.CoreV1Api(api_client) if api_client else client.CoreV1Api(),
        apps_api=client.AppsV1Api(api_client) if api_client else client.AppsV1Api(),
        route_api=CustomObjectsApi(api_client) if api_client else CustomObjectsApi(),
        batch_api=client.BatchV1Api(api_client) if api_client else client.BatchV1Api(),
        networking_api=client.NetworkingV1Api(api_client) if api_client else client.NetworkingV1Api(),
        rbac_api=client.RbacAuthorizationV1Api(api_client) if api_client else client.RbacAuthorizationV1Api(),
    )

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Initialize Kubernetes/OpenShift client with username/password if provided via env vars, else use kube config."""
    server_url = OPENSHIFT_SERVER
    username = OPENSHIFT_USERNAME
    password = OPENSHIFT_PASSWORD

    if server_url and username and password:
        api_client = get_api_client_with_token(server_url, username, password)
        context = build_app_context(api_client)
    else:
        config.load_kube_config()
        context = build_app_context()

    yield context

# Create an MCP server for OpenShift operations with lifespan
mcp = FastMCP("OpenShift MCP Server", lifespan=app_lifespan)

# Register tools
for tool in [
    list_namespaces, list_pods, get_pod_logs, list_deployments, list_routes,
    get_route, list_services, get_service, create_deployment, validate_openshift_manifest
]:
    mcp.tool()(tool)

# Register resources
resource_map = {
    "cluster://services/{namespace}": get_all_services,
    "cluster://info": get_cluster_info,
    "cluster://routes/{namespace}": list_routes,
    "cluster://pods/{namespace}": list_pods,
    "cluster://deployments/{namespace}": list_deployments,
    "cluster://namespaces": list_namespaces,
    "cluster://configmaps/{namespace}": list_configmaps,
    "cluster://secrets/{namespace}": list_secrets,
    "cluster://jobs/{namespace}": list_jobs,
    "cluster://pvcs/{namespace}": list_pvcs,
    "cluster://ingresses/{namespace}": list_ingresses,
    "cluster://rolebindings/{namespace}": list_rolebindings,
    "cluster://projects": list_projects,
    "cluster://serviceaccounts/{namespace}": list_serviceaccounts,
    "cluster://resourcequotas/{namespace}": list_resourcequotas,
    "cluster://events/{namespace}": list_events,
}
for uri, func in resource_map.items():
    mcp.resource(uri)(func)
