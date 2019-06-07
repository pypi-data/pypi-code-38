from docker import DockerClient
from docker.errors import NotFound

from riptide_engine_docker.container_builder import get_network_name, RIPTIDE_DOCKER_LABEL_IS_RIPTIDE


def start(client: DockerClient, project_name: str):
    net_name = get_network_name(project_name)
    try:
        client.networks.get(net_name)
    except NotFound:
        client.networks.create(net_name, driver="bridge", attachable=True, labels={RIPTIDE_DOCKER_LABEL_IS_RIPTIDE: "1"})


