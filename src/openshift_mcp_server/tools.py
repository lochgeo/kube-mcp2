from typing import List, Optional, Dict
from kubernetes import client
from kubernetes.client import CustomObjectsApi
from openshift_mcp_server.errors import error_response
from openshift_mcp_server.logging_utils import logger
from openshift_mcp_server.security import validate_deployment_manifest_security


def list_namespaces(ctx) -> List[str]:
    k8s_api = ctx.request_context.lifespan_context.k8s_api
    namespaces = k8s_api.list_namespace()
    return [ns.metadata.name for ns in namespaces.items]


def list_pods(namespace: str, ctx) -> List[str]:
    k8s_api = ctx.request_context.lifespan_context.k8s_api
    pods = k8s_api.list_namespaced_pod(namespace)
    return [pod.metadata.name for pod in pods.items]


def get_pod_logs(namespace: str, pod_name: str, ctx, container: Optional[str] = None) -> str:
    k8s_api = ctx.request_context.lifespan_context.k8s_api
    try:
        logs = k8s_api.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            container=container
        )
        return logs
    except Exception as e:
        logger.error(f"Failed to get logs for pod {pod_name} in {namespace}: {e}")
        return error_response("Failed to get pod logs", str(e))


def list_deployments(namespace: str, ctx) -> List[str]:
    apps_api = ctx.request_context.lifespan_context.apps_api
    deployments = apps_api.list_namespaced_deployment(namespace)
    return [dep.metadata.name for dep in deployments.items]


def list_routes(namespace: str, ctx) -> List[str]:
    route_api = ctx.request_context.lifespan_context.route_api
    routes = route_api.list_namespaced_custom_object(
        group="route.openshift.io",
        version="v1",
        namespace=namespace,
        plural="routes"
    )
    return [item["metadata"]["name"] for item in routes.get("items", [])]


def get_route(namespace: str, route_name: str, ctx) -> dict:
    route_api = ctx.request_context.lifespan_context.route_api
    try:
        route = route_api.get_namespaced_custom_object(
            group="route.openshift.io",
            version="v1",
            namespace=namespace,
            plural="routes",
            name=route_name
        )
        return route
    except Exception as e:
        logger.error(f"Failed to get route {route_name} in {namespace}: {e}")
        return error_response(f"Failed to get route {route_name}", str(e))


def list_services(namespace: str, ctx) -> List[str]:
    k8s_api = ctx.request_context.lifespan_context.k8s_api
    services = k8s_api.list_namespaced_service(namespace)
    return [svc.metadata.name for svc in services.items]


def get_service(namespace: str, service_name: str, ctx) -> dict:
    k8s_api = ctx.request_context.lifespan_context.k8s_api
    try:
        svc = k8s_api.read_namespaced_service(service_name, namespace)
        return svc.to_dict()
    except Exception as e:
        logger.error(f"Failed to get service {service_name} in {namespace}: {e}")
        return error_response(f"Failed to get service {service_name}", str(e))


def list_configmaps(namespace: str, ctx) -> list:
    """List all ConfigMaps in the given namespace."""
    k8s_api = ctx.request_context.lifespan_context.k8s_api
    try:
        cms = k8s_api.list_namespaced_config_map(namespace)
        return [cm.metadata.name for cm in cms.items]
    except Exception as e:
        logger.error(f"Failed to list ConfigMaps in {namespace}: {e}")
        return error_response(f"Failed to list ConfigMaps in {namespace}", str(e))


def list_secrets(namespace: str, ctx) -> list:
    """List all Secrets in the given namespace (only names and types, not data)."""
    k8s_api = ctx.request_context.lifespan_context.k8s_api
    try:
        secrets = k8s_api.list_namespaced_secret(namespace)
        # Only return name and type, not secret data
        return [{"name": s.metadata.name, "type": s.type} for s in secrets.items]
    except Exception as e:
        logger.error(f"Failed to list Secrets in {namespace}: {e}")
        return error_response(f"Failed to list Secrets in {namespace}", str(e))


def list_jobs(namespace: str, ctx) -> list:
    """List all Jobs in the given namespace."""
    batch_api = ctx.request_context.lifespan_context.batch_api
    try:
        jobs = batch_api.list_namespaced_job(namespace)
        return [job.metadata.name for job in jobs.items]
    except Exception as e:
        logger.error(f"Failed to list Jobs in {namespace}: {e}")
        return error_response(f"Failed to list Jobs in {namespace}", str(e))


def list_pvcs(namespace: str, ctx) -> list:
    """List all PersistentVolumeClaims in the given namespace."""
    k8s_api = ctx.request_context.lifespan_context.k8s_api
    try:
        pvcs = k8s_api.list_namespaced_persistent_volume_claim(namespace)
        return [pvc.metadata.name for pvc in pvcs.items]
    except Exception as e:
        logger.error(f"Failed to list PVCs in {namespace}: {e}")
        return error_response(f"Failed to list PVCs in {namespace}", str(e))


def list_ingresses(namespace: str, ctx) -> list:
    """List all Ingresses in the given namespace."""
    networking_api = ctx.request_context.lifespan_context.networking_api
    try:
        ingresses = networking_api.list_namespaced_ingress(namespace)
        return [ing.metadata.name for ing in ingresses.items]
    except Exception as e:
        logger.error(f"Failed to list Ingresses in {namespace}: {e}")
        return error_response(f"Failed to list Ingresses in {namespace}", str(e))


def list_rolebindings(namespace: str, ctx) -> list:
    """List all RoleBindings in the given namespace."""
    rbac_api = ctx.request_context.lifespan_context.rbac_api
    try:
        rbs = rbac_api.list_namespaced_role_binding(namespace)
        return [rb.metadata.name for rb in rbs.items]
    except Exception as e:
        logger.error(f"Failed to list RoleBindings in {namespace}: {e}")
        return error_response(f"Failed to list RoleBindings in {namespace}", str(e))


def get_all_services(ctx, namespace: Optional[str] = None) -> dict:
    k8s_api = ctx.request_context.lifespan_context.k8s_api
    try:
        if namespace:
            svcs = k8s_api.list_namespaced_service(namespace)
            return {namespace: [svc.metadata.name for svc in svcs.items]}
        else:
            svcs = k8s_api.list_service_for_all_namespaces()
            ns_services = {}
            for svc in svcs.items:
                ns = svc.metadata.namespace
                name = svc.metadata.name
                ns_services.setdefault(ns, []).append(name)
            return ns_services
    except Exception as e:
        logger.error(f"Failed to get services: {e}")
        return error_response("Failed to get services", str(e))


def get_cluster_info(ctx, namespace: Optional[str] = None) -> dict:
    k8s_api = ctx.request_context.lifespan_context.k8s_api
    try:
        if namespace:
            ns_obj = k8s_api.read_namespace(namespace)
            return {"namespace_status": ns_obj.status.phase}
        version = k8s_api.get_api_versions()
        return {"api_versions": version.versions}
    except Exception as e:
        logger.error(f"Failed to get cluster info: {e}")
        return error_response("Failed to get cluster info", str(e))


def list_tools_and_resources(ctx) -> dict:
    from inspect import signature, getdoc
    from openshift_mcp_server.server import mcp
    def get_func_info(f):
        sig = signature(f)
        return {"parameters": [str(p) for p in sig.parameters.values()], "doc": getdoc(f)}
    tools = {name: get_func_info(func) for name, func in mcp.tools.items()}
    resources = {name: get_func_info(func) for name, func in mcp.resources.items()}
    return {"tools": tools, "resources": resources}


def create_deployment(namespace: str, deployment_manifest: dict, ctx) -> dict:
    # Security validation
    sec_errors = validate_deployment_manifest_security(deployment_manifest)
    if sec_errors:
        logger.error(f"Security validation errors for deployment in {namespace}: {sec_errors}")
        return error_response("Security validation failed", "; ".join(sec_errors))
    apps_api = ctx.request_context.lifespan_context.apps_api
    try:
        deployment = apps_api.create_namespaced_deployment(namespace=namespace, body=deployment_manifest)
        return deployment.to_dict()
    except Exception as e:
        logger.error(f"Failed to create deployment in {namespace}: {e}")
        return error_response("Failed to create deployment", str(e))


def validate_openshift_manifest(manifest: dict, ctx) -> dict:
    errors = []
    warnings = []
    if manifest.get("kind") != "Deployment":
        errors.append("Manifest kind must be 'Deployment'.")
    metadata = manifest.get("metadata", {})
    if not metadata.get("name"):
        errors.append("metadata.name is required.")
    spec = manifest.get("spec", {})
    template = spec.get("template", {})
    spec_containers = template.get("spec", {}).get("containers", [])
    if not spec_containers:
        errors.append("At least one container must be defined in spec.template.spec.containers.")
    if "hostNetwork" in template.get("spec", {}):
        warnings.append("hostNetwork is discouraged in OpenShift unless absolutely required.")
    for container in spec_containers:
        resources = container.get("resources", {})
        limits = resources.get("limits")
        requests = resources.get("requests")
        if not limits or not requests:
            warnings.append(f"Container '{container.get('name','')}' should specify resource requests and limits.")
    security_ctx = template.get("spec", {}).get("securityContext", {})
    if security_ctx.get("runAsUser") == 0:
        warnings.append("Running as root (runAsUser: 0) is discouraged in OpenShift.")
    for container in spec_containers:
        if container.get("imagePullPolicy") == "Always":
            warnings.append(f"Container '{container.get('name','')}' uses imagePullPolicy: Always. Make sure this is intended.")
    if "serviceAccountName" not in template.get("spec", {}):
        warnings.append("No serviceAccountName specified. OpenShift recommends using dedicated service accounts.")
    labels = metadata.get("labels", {})
    if not labels.get("app"):
        warnings.append("metadata.labels.app is recommended for OpenShift apps.")
    return {"errors": errors, "warnings": warnings}
