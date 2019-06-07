# coding=utf-8
from __future__ import print_function

import json
import os
import re
import time
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from ibm_ai_openscale_cli.utility_classes.utils import executeCommand, executeCommandWithResult

logger = FastpathLogger(__name__)

def getOrg(cf_org):
    return executeCommandWithResult('bx account org "{}"'.format(cf_org))


def targetOrg(cf_org):
    return executeCommand('bx target -o "{}"'.format(cf_org))


def createOrg(cf_org):
    return executeCommand('bx account org-create "{}"'.format(cf_org))


def deleteOrg(cf_org):
    return executeCommand('bx account org-delete "{}"'.format(cf_org))


def getSpace(cf_space):
    return executeCommandWithResult('bx account space "{}"'.format(cf_space))


def targetSpace(cf_space):
    return executeCommand('bx target -s "{}"'.format(cf_space))


def createSpace(cf_space):
    return executeCommand('bx account space-create "{}"'.format(cf_space))


def deleteSpace(cf_org):
    return executeCommand('bx account space-delete "{}"'.format(cf_org))


def getCFInstanceCredentials(instance_params):
    '''
    Returns the credentials for the instance of the service specified.
    If there is no instance available, a new one is provisioned. If there is no
    existing key, a new one is created.
    '''
    service_name = instance_params['service_name']
    instance_name = instance_params['instance_name']
    service_plan_name = instance_params['service_plan_name']
    key_name = instance_params['key_name']

    logger.log_info('\t - Looking for existing instances of service "{}"'.format(service_name))
    existingInstances = getCFServiceInstances()
    existingInstanceName = None
    for instance in existingInstances:
        if instance['service'] == service_name:
            logger.log_info('\t - Found existing instance "{}" of "{}"'.format(instance['name'], service_name))
            if existingInstanceName is None:
                existingInstanceName = instance['name']
    if existingInstanceName is not None:
        logger.log_info('\t - Using instance {}'.format(existingInstanceName))
        instance_name = existingInstanceName
    else:
        logger.log_info('\t - No existing instance of "{}" found.'.format(service_name))
        logger.log_info('\t - Creating a new instance "{}" for service "{}"'.format(instance_name, service_name))
        instanceList = createCFServiceInstance(
            service_name, service_plan_name, instance_name)
        for instance in instanceList:
            logger.log_info('\t - Created instance "{}" of "{}"'.format(instance['name'], service_name))
            existingInstanceName = instance['name']

    logger.log_info('\t - Looking for existing credentials with name "{}"'.format(key_name))
    credentials = getCFServiceKey(instance_name, key_name)

    if credentials is None:
        logger.log_info('\t - Existing credentials with name "{}" not found'.format(key_name))
        logger.log_info('\t - Generating credentials with name "{}"'.format(key_name))
        createCFServiceKey(instance_name, key_name)
        credentials = getCFServiceKey(instance_name, key_name)
        logger.log_info('\t - Generated "{}" for "{}"'.format(key_name, instance_name))
    else:
        logger.log_info('\t - Existing credentials with name "{}" for instance "{}" found, reusing'.format(key_name, instance_name))

    return credentials


def getCFServiceInstances():
    '''
    Gets a dictionary of all instances of CF services
    '''
    cmd = 'bx service list'
    result = executeCommandWithResult(cmd)
    headers = []
    instances = []
    ignoreLine = True
    for line in result.splitlines():
        if ignoreLine and (line.startswith('name')):
            ignoreLine = False
            headers = re.split(r'\s{2,}', line)[0:3]
            continue
        if line.strip() and not ignoreLine:
            instances.append(dict(zip(headers, re.split(r'\s{2,}', line)[0:3])))
    return instances


def getCFServiceInstanceMetadata(service_instance_name):
    '''
    If a service is specified, returns a map of metadata properties of all its instances else returns None
    If an instance is specidied, returns a map of its metadata properties
    '''
    cmd = 'bx service show "{}"'.format(service_instance_name)
    result = executeCommandWithResult(cmd)
    if result is not None:
        i = -1
        metadataMapList = []
        for line in result.splitlines():
            if line.strip() and ':' in line:
                key, value = line.split(':', 1)
                if key == 'name':
                    metadataMapList.append({})
                    i += 1
                metadataMapList[i][key] = value.strip()
        return metadataMapList
    return None


def createCFServiceInstance(service_name, service_plan, service_instance_name):
    '''
    Create a CF Service instance using the specified values
    '''
    cmd = 'bx service create "{}" "{}" "{}"'.format(service_name, service_plan, service_instance_name)
    executeCommand(cmd)
    metadataMapList = getCFServiceInstanceMetadata(service_instance_name)
    # If instance details are not retrievable, give some time to create the instance
    if metadataMapList is None:
        for _ in range(30):
            time.sleep(2)
            metadataMapList = getCFServiceInstanceMetadata(
                service_instance_name)
            if metadataMapList is not None:
                break
            logger.log_info('\t\tWaiting for provision request to finish ...')
    return metadataMapList


def createCFServiceKey(service_instance_name, service_key_name):
    '''
    Creates a service key with the specified name for the specified instance
    with the specified role
    '''
    cmd = 'bx service key-create "{}" "{}"'.format(service_instance_name, service_key_name)
    executeCommand(cmd)


def getCFServiceKey(service_instance_name, service_key_name):
    '''
    Creates a service key with the specified name for the specified instance
    with the specified role
    '''
    cmd = 'bx service key-show "{}" "{}"'.format(service_instance_name, service_key_name)
    result = executeCommandWithResult(cmd)
    if result is not None:
        credentials = os.linesep.join([s for s in result.splitlines() if s and not s.startswith('Getting') and not s.startswith('Invoking')])
        credentials = json.loads(credentials)
        return credentials
    return None
