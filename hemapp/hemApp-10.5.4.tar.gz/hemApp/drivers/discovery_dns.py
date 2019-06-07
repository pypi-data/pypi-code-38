""" Discovery of host lists from DNS e.g. Round robin hosts"""
import time
import logging
import dns.resolver



def hosts(**kwargs):
    """ return hosts for passed hostname """
    logger = logging.getLogger(name=__name__)
    results = []
    starttime = time.time()
    try:
        answers = dns.resolver.query(kwargs['name'], 'A')
        for rdata in answers:
            results.append(rdata.address)
    except dns.resolver.NXDOMAIN:
        logger.error("DNS name {} not found".format(kwargs['name']))
    elapsed = time.time() - starttime
    logger.info("Lookup of {} took {}".format(kwargs['name'], elapsed))
    if 'metrics' in kwargs and None != kwargs['metrics']:
        kwargs['metrics'].stage(
            'discovery_dns.{}.time'.format(kwargs['name'].replace('.','_')), 
            elapsed)
    return results
