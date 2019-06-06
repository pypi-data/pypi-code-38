from chaoslib.types import Configuration
import consul
import requests
from logzero import logger

__all__ = ['damage_quorum']


def kill_instance(node, seconds_to_be_dead: int = 10):
    address = node['ServiceAddress']
    port = node['ServicePort']
    # logger.warning("Make pod play dead {s} for {t} seconds".format(
    #    s=address, t=seconds_to_be_dead))
    url = "http://{a}:{p}/health/play_dead/{t}".format(
        a=address, p=port, t=seconds_to_be_dead)
    r = requests.put(url)


def damage_quorum(service_name: str,
                  dc: str,
                  num_of_instances_to_kill: int,
                  seconds_to_be_dead: int,
                  configuration: Configuration):
    """
    Works only for specific service that supports play dead command

    :param service_name: service to kill
    :param dc: in wich dc to kill instances
    :param num_of_instances_to_kill: how much instances to kill
    :param seconds_to_be_dead: number of seconds to play dead
    :param configuration: chaostoolkit will inject this parameter
    :return:
    """
    consul_host = configuration.get('consul_host')
    consul_client = consul.Consul(host=consul_host)
    service_name = service_name.replace('.', '--')
    try:
        nodes = consul_client.catalog.service(service_name, dc=dc)[1]
        if nodes:
            if len(nodes) < num_of_instances_to_kill:
                num_of_instances_to_kill = len(nodes)
            for i in range(0, num_of_instances_to_kill):
                kill_instance(nodes[i], seconds_to_be_dead)
    except (ValueError, IndexError) as e:
        logger.error(e)
        pass
