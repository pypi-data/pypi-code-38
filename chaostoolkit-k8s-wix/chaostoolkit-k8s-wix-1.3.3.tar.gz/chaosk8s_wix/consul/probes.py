from chaoslib.types import Configuration
import consul
from logzero import logger

__all__ = ["check_quorum", "get_good_nodes"]


def get_good_nodes(nodes: [] = []):
    retval = []
    for node in nodes:
        heath_checks = [check for check in node['Checks']
                        if check['CheckID'] == 'serfHealth' and check['Status'] == 'passing']
        if len(heath_checks) > 0:
            retval.append(node)
    return retval


def check_quorum(dc: str, service_name: str, configuration: Configuration = None):
    """
    Check that service has more live endpoints than dead ones
    :param service_name: service name to check
    :param configuration: injected by chaostoolkit
    :return: True if more endpoins are passing healthcheck. False otherwise
    """
    retval = False
    consul_host = configuration.get('consul_host')
    consul_client = consul.Consul(host=consul_host)
    service_name = service_name.replace('.', '--')
    try:
        nodes = consul_client.health.service(service_name, dc=dc)[1]
        if nodes:

            total_nodes = len(nodes)
            good_nodes = get_good_nodes(nodes)
            total_good_nodes = len(good_nodes)
            if (total_nodes - total_good_nodes) < total_good_nodes:
                retval = True
    except (ValueError, IndexError) as e:
        logger.error(e)
        pass

    return retval
