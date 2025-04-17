"""
Prompt handlers for OpenShift MCP Server.
These provide natural language access to common Kubernetes/OpenShift operations.
"""
from openshift_mcp_server.server import mcp
from openshift_mcp_server.tools import (
    list_namespaces, list_pods, get_pod_logs, list_deployments, list_services,
    get_service, list_routes, get_route, create_deployment, validate_openshift_manifest
)

@mcp.prompt()
def prompt_list_namespaces(input: str, ctx):
    """
    Prompt: List all namespaces.
    Input: str (not used)
    Output: List[str] of namespace names or error dict
    """
    return list_namespaces(ctx)

@mcp.prompt()
def prompt_list_pods(input: str, ctx, namespace: str = None):
    """
    Prompt: List all pods in a namespace.
    Input: str (namespace name) or None
    Output: List[str] of pod names or error dict
    """
    ns = namespace or input or "default"
    return list_pods(ns, ctx)

@mcp.prompt()
def prompt_get_pod_logs(input: str, ctx, namespace: str = None, pod_name: str = None, container: str = None):
    """
    Prompt: Get logs for a pod (optionally specify container).
    Input: str (pod name), optional namespace/container
    Output: dict with 'logs' or error dict
    """
    ns = namespace or "default"
    pod = pod_name or input
    return get_pod_logs(ns, pod, ctx, container)

@mcp.prompt()
def prompt_list_deployments(input: str, ctx, namespace: str = None):
    """
    Prompt: List all deployments in a namespace.
    Input: str (namespace name) or None
    Output: List[str] of deployment names or error dict
    """
    ns = namespace or input or "default"
    return list_deployments(ns, ctx)

@mcp.prompt()
def prompt_list_services(input: str, ctx, namespace: str = None):
    """
    Prompt: List all services in a namespace.
    Input: str (namespace name) or None
    Output: List[str] of service names or error dict
    """
    ns = namespace or input or "default"
    return list_services(ns, ctx)

@mcp.prompt()
def prompt_get_service(input: str, ctx, namespace: str = None, service_name: str = None):
    """
    Prompt: Get details for a service.
    Input: str (service name), optional namespace
    Output: dict with service details or error dict
    """
    ns = namespace or "default"
    svc = service_name or input
    return get_service(ns, svc, ctx)

@mcp.prompt()
def prompt_list_routes(input: str, ctx, namespace: str = None):
    """
    Prompt: List all routes in a namespace.
    Input: str (namespace name) or None
    Output: List[str] of route names or error dict
    """
    ns = namespace or input or "default"
    return list_routes(ns, ctx)

@mcp.prompt()
def prompt_get_route(input: str, ctx, namespace: str = None, route_name: str = None):
    """
    Prompt: Get details for a route.
    Input: str (route name), optional namespace
    Output: dict with route details or error dict
    """
    ns = namespace or "default"
    route = route_name or input
    return get_route(ns, route, ctx)

@mcp.prompt()
def prompt_create_deployment(input: str, ctx, namespace: str = None, deployment_manifest: dict = None):
    """
    Prompt: Create a deployment from a manifest.
    Input: dict (deployment manifest), optional namespace
    Output: dict with deployment details or error dict
    """
    ns = namespace or "default"
    manifest = deployment_manifest or input
    return create_deployment(ns, manifest, ctx)

@mcp.prompt()
def prompt_validate_manifest(input: str, ctx):
    """
    Prompt: Validate an OpenShift deployment manifest.
    Input: dict (deployment manifest)
    Output: dict with errors and warnings
    """
    return validate_openshift_manifest(input, ctx)
