""" Discovery of host lists from DNS e.g. Round robin hosts"""
import time
import logging
import yaml



def hosts(**kwargs):
    """ return hosts from file """
    logger = logging.getLogger(name=__name__)
    results = []
    starttime = time.time()
    try:
        with open(kwargs['name'], 'rt') as source_file:
            hosts = yaml.safe_load(source_file)
            print(hosts)
            for host in hosts:
                if 'key' in kwargs:
                    if 'enabled_key' in kwargs:
                        if host.get(kwargs['enabled_key'], True) == True:
                            results.append(host.get(kwargs['key']))
                    else:
                        results.append(host.get(kwargs['key']))
                else:
                    results.append(host)
    except FileNotFoundError:
        logger.error("File not found")
    elapsed = time.time() - starttime
    logger.info("Lookup from {} took {}".format(kwargs['name'], elapsed))
    if 'metrics' in kwargs and None != kwargs['metrics']:
        kwargs['metrics'].stage(
            'discovery_file.{}.time'.format(kwargs['name'].replace('.','_')), 
            elapsed)
    return results
