""" Discovery of host lists from Consul API over http"""
import time
import logging
import requests


def hosts(**kwargs):
    """ return hosts from consul api """
    logger = logging.getLogger(name=__name__)
    starttime = time.time()
    consul_server = kwargs.get("server","127.0.0.1")
    service = kwargs.get("name","consul")
    catalog = requests.get("http://{}:8500/v1/catalog/service/{}".format(consul_server, service)).json()
    results = []
    for node in catalog:
        results.append("{}:{}".format(node['Address'], node['ServicePort']))
    elapsed = time.time() - starttime
    logger.info("Lookup of {} took {}".format(service, elapsed))
    if 'metrics' in kwargs and None != kwargs['metrics']:
        
        kwargs['metrics'].stage(
            'discovery_consul.{}.time'.format(service.replace('.','_')), 
            elapsed)
    return results

if __name__ == "__main__":
    print(hosts(server="192.168.0.18", name="desklight"))
