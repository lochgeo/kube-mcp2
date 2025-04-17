from typing import List, Dict, Any
from openshift_mcp_server.logging_utils import logger

def check_host_network(pod_spec: Dict[str, Any], errors: List[str]) -> None:
    if pod_spec.get('hostNetwork'):
        errors.append("hostNetwork is disallowed for security reasons.")

def check_privileged_containers(pod_spec: Dict[str, Any], errors: List[str]) -> None:
    for c in pod_spec.get('containers', []):
        sc = c.get('securityContext', {})
        if sc.get('privileged'):
            errors.append(f"Container '{c.get('name', '')}' sets privileged=true, which is disallowed.")

def check_host_pid_ipc(pod_spec: Dict[str, Any], errors: List[str]) -> None:
    if pod_spec.get('hostPID'):
        errors.append("hostPID is disallowed for security reasons.")
    if pod_spec.get('hostIPC'):
        errors.append("hostIPC is disallowed for security reasons.")

def check_host_path_volumes(pod_spec: Dict[str, Any], errors: List[str]) -> None:
    for v in pod_spec.get('volumes', []):
        if 'hostPath' in v:
            errors.append(f"Volume '{v.get('name', '')}' uses hostPath which is disallowed.")

def validate_deployment_manifest_security(manifest: dict) -> List[str]:
    """Validate deployment manifest against security policies. Returns a list of error messages if found."""
    errors: List[str] = []
    spec = manifest.get('spec', {})
    template = spec.get('template', {})
    pod_spec = template.get('spec', {})

    check_host_network(pod_spec, errors)
    check_privileged_containers(pod_spec, errors)
    check_host_pid_ipc(pod_spec, errors)
    check_host_path_volumes(pod_spec, errors)

    if errors:
        logger.warning(f"Security checks failed: {errors}")
    return errors
