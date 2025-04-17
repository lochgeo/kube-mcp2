import pytest
from unittest.mock import MagicMock
from openshift_mcp_server.tools import (
    list_namespaces, list_pods, get_pod_logs, list_deployments, get_cluster_info,
    list_routes, get_route, list_services, get_service, get_all_services,
    create_deployment, validate_openshift_manifest, list_configmaps, list_secrets,
    list_jobs, list_pvcs, list_ingresses, list_rolebindings
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

def test_list_configmaps(ctx):
    cm1 = MagicMock()
    cm1.metadata.name = 'cm1'
    ctx.request_context.lifespan_context.k8s_api.list_namespaced_config_map.return_value.items = [cm1]
    assert list_configmaps('ns', ctx) == ['cm1']
    ctx.request_context.lifespan_context.k8s_api.list_namespaced_config_map.side_effect = Exception('fail')
    out = list_configmaps('ns', ctx)
    assert isinstance(out, dict) and 'error' in out

def test_list_secrets(ctx):
    s1 = MagicMock()
    s1.metadata.name = 's1'
    s1.type = 'Opaque'
    ctx.request_context.lifespan_context.k8s_api.list_namespaced_secret.return_value.items = [s1]
    out = list_secrets('ns', ctx)
    assert out == [{'name': 's1', 'type': 'Opaque'}]
    ctx.request_context.lifespan_context.k8s_api.list_namespaced_secret.side_effect = Exception('fail')
    out = list_secrets('ns', ctx)
    assert isinstance(out, dict) and 'error' in out

def test_list_jobs(ctx):
    job1 = MagicMock()
    job1.metadata.name = 'job1'
    ctx.request_context.lifespan_context.batch_api.list_namespaced_job.return_value.items = [job1]
    out = list_jobs('ns', ctx)
    assert out == ['job1']
    ctx.request_context.lifespan_context.batch_api.list_namespaced_job.side_effect = Exception('fail')
    out = list_jobs('ns', ctx)
    assert isinstance(out, dict) and 'error' in out

def test_list_pvcs(ctx):
    pvc1 = MagicMock()
    pvc1.metadata.name = 'pvc1'
    ctx.request_context.lifespan_context.k8s_api.list_namespaced_persistent_volume_claim.return_value.items = [pvc1]
    out = list_pvcs('ns', ctx)
    assert out == ['pvc1']
    ctx.request_context.lifespan_context.k8s_api.list_namespaced_persistent_volume_claim.side_effect = Exception('fail')
    out = list_pvcs('ns', ctx)
    assert isinstance(out, dict) and 'error' in out

def test_list_ingresses(ctx):
    ing1 = MagicMock()
    ing1.metadata.name = 'ing1'
    ctx.request_context.lifespan_context.networking_api.list_namespaced_ingress.return_value.items = [ing1]
    out = list_ingresses('ns', ctx)
    assert out == ['ing1']
    ctx.request_context.lifespan_context.networking_api.list_namespaced_ingress.side_effect = Exception('fail')
    out = list_ingresses('ns', ctx)
    assert isinstance(out, dict) and 'error' in out

def test_list_rolebindings(ctx):
    rb1 = MagicMock()
    rb1.metadata.name = 'rb1'
    ctx.request_context.lifespan_context.rbac_api.list_namespaced_role_binding.return_value.items = [rb1]
    out = list_rolebindings('ns', ctx)
    assert out == ['rb1']
    ctx.request_context.lifespan_context.rbac_api.list_namespaced_role_binding.side_effect = Exception('fail')
    out = list_rolebindings('ns', ctx)
    assert isinstance(out, dict) and 'error' in out
