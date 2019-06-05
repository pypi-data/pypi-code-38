# -*- coding: utf-8 -*-
from kubernetes import client
from chaosk8s_wix import create_k8s_api_client
from chaoslib.types import Secrets
from logzero import logger
from chaosk8s_wix.slack.logger_handler import SlackHanlder
__all__ = ["get_active_nodes", "node_should_be_ignored_by_taints",
           "is_equal_V1Taint", "load_taint_list_from_dict"]

slack_handler = SlackHanlder()
slack_handler.attach(logger)


def load_taint_list_from_dict(list_of_objects):
    """
    Convert list of dictionaries loaded from configuration to V1Taint objects
    :param list_of_objects: array of objects. Usually loaded from configuration
    :return: array of V1Taint objects
    """
    retval = []
    for obj in list_of_objects:
        taint = client.V1Taint(effect=obj.get("effect"),
                               value=obj.get("value"),
                               key=obj.get("key"),
                               time_added=obj.get("time_added"))
        retval.append(taint)
    return retval


def is_equal_V1Taint(taint1: client.V1Taint, taint2: client.V1Taint) -> bool:
    """
    Compares 2 V1Taint objects. returns True if effect, value and key properties are equal, False otherwise
    :param taint1: first object to compare
    :param taint2: second object to compare
    :return:  True if effect, value and key properties are equal, False otherwise
    """
    return taint1 is not None \
        and taint2 is not None \
        and taint1.effect == taint2.effect \
        and taint1.key == taint2.key \
        and taint1.value == taint2.value


def node_should_be_ignored_by_taints(node_taints, taint_ignore_list) -> bool:
    """
    Check is node shoudl be excluded from selection for chaos tests.
    Returns True if one of node taints matches taint in ignore list.
    """
    retval = False
    for node_taint in node_taints:
        taint_ignored = False
        for taint_from_ignore in taint_ignore_list:
            if is_equal_V1Taint(node_taint, taint_from_ignore):
                taint_ignored = True
                break
        if taint_ignored:
            retval = True
            break
    return retval


def get_active_nodes(label_selector: str = None, taints_ignore_list=None,
                     secrets: Secrets = None):
    """
    List all nodes, that are not tainted by known taints. You may filter nodes
    by specifying a label selector.
    """
    if taints_ignore_list is None:
        taints_ignore_list = []

    api = create_k8s_api_client(secrets)
    v1 = client.CoreV1Api(api)
    if label_selector:
        ret = v1.list_node_with_http_info(label_selector=label_selector,
                                          _preload_content=True,
                                          _return_http_data_only=True)
    else:
        ret = v1.list_node_with_http_info(_preload_content=True,
                                          _return_http_data_only=True)
    node_list = ret.items
    retval = client.V1NodeList(items=[])
    for node in node_list:
        node_ignored = False
        if node.spec.taints is not None:
            node_ignored = node_should_be_ignored_by_taints(
                node.spec.taints, taints_ignore_list)
        if not node_ignored:
            retval.items.append(node)
    return retval, v1
