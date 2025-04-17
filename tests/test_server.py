import pytest
from unittest.mock import MagicMock, patch
from openshift_mcp_server.tools import (
    list_namespaces, list_pods, get_pod_logs, list_deployments, get_cluster_info,
    list_routes, get_route, list_services, get_service, get_all_services,
    list_tools_and_resources, create_deployment, validate_openshift_manifest
)

class DummyContext:
    def __init__(self):
        self.request_context = MagicMock()
        self.request_context.lifespan_context = MagicMock()

@pytest.fixture
def ctx():
    return DummyContext()

def test_list_namespaces(ctx):
    ns1 = MagicMock()
    ns1.metadata.name = 'ns1'
    ns2 = MagicMock()
    ns2.metadata.name = 'ns2'
    ctx.request_context.lifespan_context.k8s_api.list_namespace.return_value.items = [ns1, ns2]
    result = list_namespaces(ctx)
    assert result == ['ns1', 'ns2']

def test_list_pods(ctx):
    pod1 = MagicMock()
    pod1.metadata.name = 'pod1'
    pod2 = MagicMock()
    pod2.metadata.name = 'pod2'
    ctx.request_context.lifespan_context.k8s_api.list_namespaced_pod.return_value.items = [pod1, pod2]
    result = list_pods('ns', ctx)
    assert result == ['pod1', 'pod2']

def test_get_pod_logs(ctx):
    ctx.request_context.lifespan_context.k8s_api.read_namespaced_pod_log.return_value = 'logs'
    assert get_pod_logs('ns', 'pod', ctx) == 'logs'
    ctx.request_context.lifespan_context.k8s_api.read_namespaced_pod_log.side_effect = Exception('fail')
    result = get_pod_logs('ns', 'pod', ctx)
    assert isinstance(result, dict) and 'error' in result and 'Failed to get pod logs' in result['error']

def test_list_deployments(ctx):
    dep1 = MagicMock()
    dep1.metadata.name = 'dep1'
    ctx.request_context.lifespan_context.apps_api.list_namespaced_deployment.return_value.items = [dep1]
    assert list_deployments('ns', ctx) == ['dep1']

def test_get_cluster_info(ctx):
    ctx.request_context.lifespan_context.k8s_api.get_api_versions.return_value.versions = ['v1']
    result = get_cluster_info(ctx)
    assert 'v1' in result['api_versions']
    ctx.request_context.lifespan_context.k8s_api.read_namespace.return_value.status.phase = 'Active'
    result = get_cluster_info(ctx, namespace='ns')
    assert result['namespace_status'] == 'Active'

def test_list_routes(ctx):
    ctx.request_context.lifespan_context.route_api.list_namespaced_custom_object.return_value = {
        'items': [{'metadata': {'name': 'route1'}}]
    }
    assert list_routes('ns', ctx) == ['route1']

def test_get_route(ctx):
    ctx.request_context.lifespan_context.route_api.get_namespaced_custom_object.return_value = {'metadata': {'name': 'route1'}}
    assert get_route('ns', 'route1', ctx)['metadata']['name'] == 'route1'
    ctx.request_context.lifespan_context.route_api.get_namespaced_custom_object.side_effect = Exception('fail')
    assert 'error' in get_route('ns', 'route1', ctx)

def test_list_services(ctx):
    svc1 = MagicMock()
    svc1.metadata.name = 'svc1'
    ctx.request_context.lifespan_context.k8s_api.list_namespaced_service.return_value.items = [svc1]
    assert list_services('ns', ctx) == ['svc1']

def test_get_service(ctx):
    svc = MagicMock()
    svc.to_dict.return_value = {'metadata': {'name': 'svc1'}}
    ctx.request_context.lifespan_context.k8s_api.read_namespaced_service.return_value = svc
    assert get_service('ns', 'svc1', ctx)['metadata']['name'] == 'svc1'
    ctx.request_context.lifespan_context.k8s_api.read_namespaced_service.side_effect = Exception('fail')
    assert 'error' in get_service('ns', 'svc1', ctx)

def test_get_all_services(ctx):
    svc1 = MagicMock()
    svc1.metadata.namespace = 'ns1'
    svc1.metadata.name = 'svc1'
    svc2 = MagicMock()
    svc2.metadata.namespace = 'ns2'
    svc2.metadata.name = 'svc2'
    ctx.request_context.lifespan_context.k8s_api.list_service_for_all_namespaces.return_value.items = [svc1, svc2]
    out = get_all_services(ctx)
    assert 'ns1' in out and 'ns2' in out
    assert out['ns1'] == ['svc1']
    assert out['ns2'] == ['svc2']
    ctx.request_context.lifespan_context.k8s_api.list_namespaced_service.return_value.items = [svc1]
    out = get_all_services(ctx, namespace='ns1')
    assert out['ns1'] == ['svc1']

# def test_list_tools_and_resources(ctx):
#     # Just check it returns a dict with 'tools' and 'resources'
#     out = list_tools_and_resources(ctx)
#     assert 'tools' in out and 'resources' in out

def test_create_deployment(ctx):
    dep = MagicMock()
    dep.to_dict.return_value = {'metadata': {'name': 'dep1'}}
    ctx.request_context.lifespan_context.apps_api.create_namespaced_deployment.return_value = dep
    assert create_deployment('ns', {'kind': 'Deployment'}, ctx)['metadata']['name'] == 'dep1'
    ctx.request_context.lifespan_context.apps_api.create_namespaced_deployment.side_effect = Exception('fail')
    assert 'error' in create_deployment('ns', {'kind': 'Deployment'}, ctx)

def test_validate_openshift_manifest(ctx):
    manifest = {
        'kind': 'Deployment',
        'metadata': {'name': 'foo', 'labels': {'app': 'foo'}},
        'spec': {'template': {'spec': {'containers': [{'name': 'c', 'resources': {'limits': {}, 'requests': {}}}]}}}
    }
    result = validate_openshift_manifest(manifest, ctx)
    assert 'errors' in result and 'warnings' in result
    # Test non-compliant
    bad_manifest = {}
    result = validate_openshift_manifest(bad_manifest, ctx)
    assert result['errors']
