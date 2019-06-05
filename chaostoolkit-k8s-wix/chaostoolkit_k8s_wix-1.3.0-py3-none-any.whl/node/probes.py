# -*- coding: utf-8 -*-
import json
from chaoslib.types import Configuration, Secrets
from kubernetes import client

from logzero import logger
from chaosk8s_wix import create_k8s_api_client
from . import get_active_nodes, load_taint_list_from_dict, is_equal_V1Taint
import datetime
from chaosk8s_wix.slack.logger_handler import SlackHanlder

__all__ = ["get_nodes", "all_nodes_are_ok",
           "have_new_node", "check_min_nodes_exist"]


slack_handler = SlackHanlder()
slack_handler.attach(logger)


def get_nodes(label_selector: str = None,
              secrets: Secrets = None):
    """
    List all Kubernetes worker nodes in your cluster. You may filter nodes
    by specifying a label selector.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    if label_selector:
        ret = v1.list_node(
            label_selector=label_selector, _preload_content=False)
    else:
        ret = v1.list_node(_preload_content=False)

    return json.loads(ret.read().decode('utf-8'))


def check_containers_for_node(client, nodename):
    """
       Helper function.
       Checks that all pods on specific container are in running state

    """
    pods = client.list_pod_for_all_namespaces(
        watch=False, field_selector="spec.nodeName=" + nodename)
    retval = True
    for i in pods.items:
        if i.status.container_statuses is not None:
            for status in i.status.container_statuses:
                if status.state.running is None:
                    logger.info("%s\t%s\t%s \t%s is not good" % (
                        nodename, i.metadata.namespace, i.metadata.name, i.status.container_statuses[0].state))
                    retval = False
    if not retval:
        logger.error("%s\tis NOT OK" % nodename)
    else:
        logger.info("%s\tis OK" % nodename)
    return retval


def all_nodes_are_ok(label_selector: str = None,
                     configuration: Configuration = None,
                     secrets: Secrets = None):
    """
    List all Kubernetes worker nodes in your cluster. You may filter nodes
    by specifying a label selector.
    """
    retval = True
    ignore_list = []
    if configuration is not None:
        ignore_list = load_taint_list_from_dict(
            configuration.get("taints-ignore-list", {}))
    resp, k8s_api_v1 = get_active_nodes(label_selector, ignore_list, secrets)

    for item in resp.items:
        localresult = True
        for condition in item.status.conditions:
            if condition.type == "Ready" and condition.status == "False":
                logger.debug("{p} Ready=False  ".format(
                    p=item.metadata.name))
                localresult = False
        if item.spec.unschedulable:
            logger.debug("{p} unschedulable ' ".format(
                p=item.metadata.name))
            localresult = False

        # if item.spec.taints and len(item.spec.taints) > 0:
        #     logger.debug("{p} Tainted node ' ".format(
        #         p=item.metadata.name))
        #     localresult = False

        if not localresult:
            logger.debug("{p} Is not healthy ' ".format(
                p=item.metadata.name))
        if localresult is False:
            retval = localresult

    return retval


def have_new_node(k8s_label_selector: str = None,
                  age_limit: int = 600,
                  configuration: Configuration = None,
                  secrets: Secrets = None):
    """
    Check that there is at least one new node created at time interval
    defined by age_limit, that matches k8s_label_selector
    :param k8s_label_selector: k8s label selector to filter nodes
    :param age_limit: seconds, time interval to check for new nodes. If node was created
    at time that was before current time minus age_limit, it will be filtered out
    :param configuration: chaostoolkit will inject configuration
    :param secrets: chaostoolkit will inject secrets
    :return: True if at least one node was created, False otherwise
    """

    resp, k8s_api_v1 = get_active_nodes(k8s_label_selector, None, secrets)
    new_nodes = []
    for node in resp.items:
        now = datetime.datetime.now(tz=node.metadata.creation_timestamp.tzinfo)
        begining_of_time = now - datetime.timedelta(seconds=age_limit)
        if node.metadata.creation_timestamp > begining_of_time:
            logger.debug("New node found :" + node.metadata.name)
            new_nodes.append(node)
    return len(new_nodes) > 0


def check_min_nodes_exist(k8s_label_selector: str = None,
                          min_limit: int = 2,
                          configuration: Configuration = None,
                          secrets: Secrets = None):
    """
    Check that there are least min_limit new node that matches k8s_label_selector
    :param k8s_label_selector: k8s label selector to filter nodes
    :param min_limit: minimum amount of nodes that have matching k8s_label_selector
    :param configuration: chaostoolkit will inject configuration
    :param secrets: chaostoolkit will inject secrets
    :return: True if there are at least min_limit nodes exists, False otherwise
    """

    resp, k8s_api_v1 = get_active_nodes(k8s_label_selector, None, secrets)

    return len(resp.items) >= min_limit


def get_tainted_nodes(key: str = None, value: str = None, effect: str = None,
                      secrets: Secrets = None):
    """
    Get nodes that are tainted with specific taint.
    :param key: Taint key
    :param value: Taint value
    :param effect: Taint effect
    :param secrets: chaostoolkit will inject secrets
    :return: array of nodes with specific taint
    """
    all_nodes, k8s_api_v1 = get_active_nodes(
        label_selector="", taints_ignore_list=None, secrets=secrets)
    taint_to_find = client.V1Taint(
        effect=effect, key=key, time_added=None, value=value)
    retval = []
    for node in all_nodes.items:
        if node.spec is not None and node.spec.taints is not None:
            for taint in node.spec.taints:
                if is_equal_V1Taint(taint, taint_to_find):
                    retval.append(node)
    return retval
