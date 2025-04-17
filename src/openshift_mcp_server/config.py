import os

def get_env_variable(name: str, default=None):
    return os.environ.get(name, default)

OPENSHIFT_SERVER = get_env_variable('OPENSHIFT_SERVER')
OPENSHIFT_USERNAME = get_env_variable('OPENSHIFT_USERNAME')
OPENSHIFT_PASSWORD = get_env_variable('OPENSHIFT_PASSWORD')
