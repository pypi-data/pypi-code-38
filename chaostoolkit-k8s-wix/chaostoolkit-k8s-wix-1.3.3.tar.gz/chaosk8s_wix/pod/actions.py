# -*- coding: utf-8 -*-
import random
import re

from chaoslib.types import Secrets, Configuration
from kubernetes import client
from logzero import logger
from chaosk8s_wix.slack.client import post_message
from chaosk8s_wix.slack.logger_handler import SlackHanlder

from chaosk8s_wix import create_k8s_api_client

__all__ = ["terminate_pods", "label_random_pod_in_ns",
           "remove_label_by_label_from_pod"]

slack_handler = SlackHanlder()
slack_handler.attach(logger)


def get_not_empty_ns(secret: Secrets = None, ns_ignore_list: str = "", label_selector: str = "com.wix.lifecycle=true"):
    api = create_k8s_api_client(secret)

    v1 = client.CoreV1Api(api)
    ret = v1.list_namespace()

    good_ns_list = [
        ns.metadata.name for ns in ret.items if ns.metadata.name not in ns_ignore_list]

    retval = None
    count = 100
    if len(good_ns_list) > 0:
        while retval is None and count > 0:
            count -= 1
            selected_ns = random.choice(good_ns_list)
            ret_pods = v1.list_namespaced_pod(
                selected_ns, label_selector=label_selector)
            if len(ret_pods.items) > 1:
                retval = selected_ns
                logger.debug("Found {} non-empty namespace".format(retval))
                break
    else:
        retval = 'default'
    return retval


def terminate_pods(label_selector: str = None, name_pattern: str = None,
                   all: bool = False, rand: bool = False,
                   ns: str = "default", secrets: Secrets = None,
                   configuration: Configuration = {}):
    """
    Terminate a pod gracefully. Select the appropriate pods by label and/or
    name patterns. Whenever a pattern is provided for the name, all pods
    retrieved will be filtered out if their name do not match the given
    pattern.

    If neither `label_selector` nor `name_pattern` are provided, all pods
    in the namespace will be terminated.

    If `all` is set to `True`, all matching pods will be terminated.
    If `rand` is set to `True`, one random pod will be terminated.
    Otherwise, the first retrieved pod will be terminated.
    """

    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)

    ns_to_check = ns
    if ns == "default":
        ns_to_check = get_not_empty_ns(secrets, configuration.get(
            'ns-ignore-list', []), label_selector)

    logger.info("Selected '{}' for experiment".format(ns_to_check))
    ret = v1.list_namespaced_pod(ns_to_check, label_selector=label_selector)

    logger.debug("Found {d} pods labelled '{s}'".format(
        d=len(ret.items), s=label_selector))

    pods = []
    if name_pattern:
        pattern = re.compile(name_pattern)
        for p in ret.items:
            if pattern.match(p.metadata.name):
                pods.append(p)
                logger.debug("Pod '{p}' match pattern".format(
                    p=p.metadata.name))
    else:
        pods = ret.items

    if rand:
        pods = [random.choice(pods)]
        logger.debug("Picked pod '{p}' (rand) to be terminated".format(
            p=pods[0].metadata.name))
    elif not all:
        pods = [pods[0]]
        logger.debug("Picked pod '{p}' to be terminated".format(
            p=pods[0].metadata.name))

    body = client.V1DeleteOptions()
    for p in pods:
        logger.warning("Killing pod " + p.metadata.name)
        res = v1.delete_namespaced_pod(
            name=p.metadata.name, namespace=ns_to_check, body=body)
