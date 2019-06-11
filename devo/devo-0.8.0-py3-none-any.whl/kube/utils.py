import sys
import subprocess
import shlex

from devo.config import read_config

CREATE_NAMESPACE = """kubectl create namespace {namespace}"""

CREATE_IMAGE_PULL_SECRET = """
kubectl create --namespace {namespace} secret docker-registry {name} \
--docker-server={url} \
--docker-username={user} \
--docker-password={password}
"""

EXECUTE_TESTS = """kubectl exec --namespace {namespace} {pod} -- /scripts/test"""

DELETE_NAMESPACE = """kubectl delete namespaces {namespace}"""

GET_POD_NAME = """kubectl get pods --namespace {namespace} -l app.kubernetes.io/component=app -o name"""

SET_CLUSTER = """kubectl config set-cluster {name} --server {url}"""

SET_CREDENTIALS = """kubectl config set-credentials {user} --token {token}"""

SET_CONTEXT = """kubectl config set-context {name} --cluster={name} --user={user}"""

USE_CONTEXT = """kubectl config use-context {name}"""

WAIT_FOR_DEPLOYMENT = """kubectl wait --namespace {namespace} deployment {deployment} --for condition=available --timeout={timeout}s"""


def create_namespace(namespace):
    command = shlex.split(CREATE_NAMESPACE.format(namespace=namespace))
    subprocess.call(command)


def create_image_pull_secret(namespace, name, url, user, password):
    command = shlex.split(CREATE_IMAGE_PULL_SECRET.format(namespace=namespace,
                                                          name=name,
                                                          url=url,
                                                          user=user,
                                                          password=password))
    subprocess.call(command)


def cleanup_test_env(namespace):
    command = shlex.split(DELETE_NAMESPACE.format(namespace=namespace))
    subprocess.call(command)


def get_pod_name(namespace):
    command = shlex.split(GET_POD_NAME.format(namespace=namespace))
    pod_name = subprocess.run(command, encoding='ascii', check=True, stdout=subprocess.PIPE).stdout[4:].strip()
    return pod_name


def execute_tests(namespace, timeout=300):
    wait_for_deployment(namespace, timeout)
    pod = get_pod_name(namespace)
    command = shlex.split(EXECUTE_TESTS.format(namespace=namespace,
                                               pod=pod))
    returncode = subprocess.call(command)
    sys.exit(returncode)


def wait_for_deployment(namespace, timeout=300):
    config = read_config()
    deployment = config['project_name'] + '-app'
    command = shlex.split(WAIT_FOR_DEPLOYMENT.format(namespace=namespace,
                                                     deployment=deployment,
                                                     timeout=timeout))
    subprocess.call(command)


def set_cluster(name, url):
    command = shlex.split(SET_CLUSTER.format(name=name, url=url))
    subprocess.call(command)


def set_credentials(user, token):
    command = shlex.split(SET_CREDENTIALS.format(user=user, token=token))
    subprocess.call(command)


def set_context(name, user):
    command = shlex.split(SET_CONTEXT.format(name=name, user=user))
    subprocess.call(command)


def use_context(name):
    command = shlex.split(USE_CONTEXT.format(name=name))
    subprocess.call(command)


def init_kubectl(name, url, user, token):
    set_cluster(name, url)
    set_credentials(user, token)
    set_context(name, user)
    use_context(name)
