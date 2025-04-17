from typing import List
from openshift_mcp_server.logging_utils import logger

def validate_deployment_manifest_security(manifest: dict) -> List[str]:
    """Validate deployment manifest against security policies. Returns a list of error messages if found."""
    errors: List[str] = []
    spec = manifest.get('spec', {})
    template = spec.get('template', {})
    pod_spec = template.get('spec', {})
    # Disallow hostNetwork
    if pod_spec.get('hostNetwork'):
        errors.append("hostNetwork is disallowed for security reasons.")
    # Disallow privileged containers
    for c in pod_spec.get('containers', []):
        sc = c.get('securityContext', {})
        if sc.get('privileged'):
            errors.append(f"Container '{c.get('name', '')}' sets privileged=true, which is disallowed.")
    # Disallow hostPID and hostIPC
    if pod_spec.get('hostPID'):
        errors.append("hostPID is disallowed for security reasons.")
    if pod_spec.get('hostIPC'):
        errors.append("hostIPC is disallowed for security reasons.")
    # Disallow hostPath volumes
    for v in pod_spec.get('volumes', []):
        if 'hostPath' in v:
            errors.append(f"Volume '{v.get('name', '')}' uses hostPath which is disallowed.")
    if errors:
        logger.warning(f"Security checks failed: {errors}")
    return errors
