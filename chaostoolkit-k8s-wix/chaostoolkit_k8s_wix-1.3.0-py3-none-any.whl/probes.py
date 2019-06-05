# -*- coding: utf-8 -*-
from typing import Dict, Union
import urllib3
import requests
from chaoslib.exceptions import FailedActivity
from chaoslib.types import MicroservicesStatus, Secrets, Configuration
from logzero import logger
from kubernetes import client, watch

from chaosk8s_wix import __version__, create_k8s_api_client
from chaosk8s_wix.pod.probes import read_pod_logs
from chaosk8s_wix.node import load_taint_list_from_dict, get_active_nodes
from chaosk8s_wix.node.probes import all_nodes_are_ok


__all__ = ["all_microservices_healthy", "microservice_available_and_healthy",
           "microservice_is_not_available", "service_endpoint_is_initialized",
           "deployment_is_not_fully_available", "read_microservices_logs",
           "all_pods_in_all_ns_are_ok", "nodes_super_healthy", "check_http"]


def all_microservices_healthy(
        ns: str = "default",
        secrets: Secrets = None,
        configuration: Configuration = None) -> MicroservicesStatus:
    """
    Check all microservices in the system are running and available.

    Raises :exc:`chaoslib.exceptions.FailedActivity` when the state is not
    as expected.
    """
    api = create_k8s_api_client(secrets)
    not_ready = []
    failed = []
    not_in_condition = []
    ns_ignore_list = []
    if configuration is not None:
        ns_ignore_list = configuration.get("ns-ignore-list", [])
    v1 = client.CoreV1Api(api)
    if ns == "":
        ret = v1.list_pod_for_all_namespaces()
    else:
        ret = v1.list_namespaced_pod(namespace=ns)
    total = 0
    for p in ret.items:
        phase = p.status.phase
        if p.metadata.namespace not in ns_ignore_list:
            total = total + 1
            if phase == "Failed" or phase == "Unknown":
                failed.append(p)
            elif phase != "Running":
                not_ready.append(p)

    logger.debug("Total pods {t}. Found {d} failed and {n} not ready pods".format(
        d=len(failed), n=len(not_ready), t=total))
    for srv in failed:
        logger.debug("Failed service {} on {} {}".format(
            srv.metadata.name, srv.spec.node_name, srv.status.phase))
    for srv in not_ready:
        logger.debug("Not ready service {} on {} {}".format(
            srv.metadata.name, srv.spec.node_name, srv.status.phase))

    # we probably should list them in the message
    if failed or not_ready:
        raise FailedActivity("the system is unhealthy")

    return True


def microservice_available_and_healthy(
        name: str, ns: str = "default",
        label_selector: str = "name in ({name})",
        secrets: Secrets = None) -> Union[bool, None]:
    """
    Lookup a deployment by `name` in the namespace `ns`.

    The selected resources are matched by the given `label_selector`.

    Raises :exc:`chaoslib.exceptions.FailedActivity` when the state is not
    as expected.
    """
    label_selector = label_selector.format(name=name)
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1beta1Api(api)
    ret = v1.list_namespaced_deployment(ns, label_selector=label_selector)

    logger.debug("Found {d} deployments named '{n}'".format(
        d=len(ret.items), n=name))

    if not ret.items:
        raise FailedActivity(
            "microservice '{name}' was not found".format(name=name))

    for d in ret.items:
        logger.debug("Deployment has '{s}' available replicas".format(
            s=d.status.available_replicas))

        if d.status.available_replicas != d.spec.replicas:
            raise FailedActivity(
                "microservice '{name}' is not healthy".format(name=name))

    return True


def microservice_is_not_available(name: str, ns: str = "default",
                                  label_selector: str = "name in ({name})",
                                  secrets: Secrets = None) -> bool:
    """
    Lookup pods with a `name` label set to the given `name` in the specified
    `ns`.

    Raises :exc:`chaoslib.exceptions.FailedActivity` when one of the pods
    with the specified `name` is in the `"Running"` phase.
    """
    label_selector = label_selector.format(name=name)
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    ret = v1.list_namespaced_pod(ns, label_selector=label_selector)

    logger.debug("Found {d} pod named '{n}'".format(
        d=len(ret.items), n=name))

    for p in ret.items:
        phase = p.status.phase
        logger.debug("Pod '{p}' has status '{s}'".format(
            p=p.metadata.name, s=phase))
        if phase == "Running":
            raise FailedActivity(
                "microservice '{name}' is actually running".format(name=name))

    return True


def service_endpoint_is_initialized(name: str, ns: str = "default",
                                    label_selector: str = "name in ({name})",
                                    secrets: Secrets = None):
    """
    Lookup a service endpoint by its name and raises :exc:`FailedProbe` when
    the service was not found or not initialized.
    """
    label_selector = label_selector.format(name=name)
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    ret = v1.list_namespaced_service(ns, label_selector=label_selector)

    logger.debug("Found {d} services named '{n}'".format(
        d=len(ret.items), n=name))

    if not ret.items:
        raise FailedActivity(
            "service '{name}' is not initialized".format(name=name))

    return True


def deployment_is_not_fully_available(name: str, ns: str = "default",
                                      label_selector: str = "name in ({name})",
                                      timeout: int = 30,
                                      secrets: Secrets = None):
    """
    Wait until the deployment gets into an intermediate state where not all
    expected replicas are available. Once this state is reached, return `True`.
    If the state is not reached after `timeout` seconds, a
    :exc:`chaoslib.exceptions.FailedActivity` exception is raised.
    """
    label_selector = label_selector.format(name=name)
    api = create_k8s_api_client(secrets)
    v1 = client.AppsV1beta1Api(api)
    w = watch.Watch()
    timeout = int(timeout)

    try:
        logger.debug("Watching events for {t}s".format(t=timeout))
        for event in w.stream(v1.list_namespaced_deployment, namespace=ns,
                              label_selector=label_selector,
                              _request_timeout=timeout):
            deployment = event['object']
            status = deployment.status
            spec = deployment.spec

            logger.debug(
                "Deployment '{p}' {t}: "
                "Ready Replicas {r} - "
                "Unavailable Replicas {u} - "
                "Desired Replicas {a}".format(
                    p=deployment.metadata.name, t=event["type"],
                    r=status.ready_replicas,
                    a=spec.replicas,
                    u=status.unavailable_replicas))

            if status.ready_replicas != spec.replicas:
                w.stop()
                return True

    except urllib3.exceptions.ReadTimeoutError:
        logger.debug("Timed out!")
        raise FailedActivity(
            "microservice '{name}' failed to stop running within {t}s".format(
                name=name, t=timeout))


def get_value_from_configuration(conf: Configuration, field_name: str):
    """
    Extracts value from chaostoolkit Configuration object with check for None
    :param conf: chaostoolkit Configuration object
    :param field_name: name of field to extract from root of conf
    :return: Value of field named as field_name, None otherwise
    """

    retval = None
    if conf is not None and field_name in conf.keys():
        retval = conf[field_name]
    return retval


def all_pods_in_all_ns_are_ok(configuration: Configuration = None,
                              secrets: Secrets = None):
    """

    :param configuration: experiment configuration
    :param secrets: k8s credentials
    :return: True if all pods are in running state, False otherwise
    """

    ns_ignore_list = get_value_from_configuration(
        configuration, "ns-ignore-list")
    if ns_ignore_list is None:
        ns_ignore_list = []

    taint_ignore_list = []
    taints = get_value_from_configuration(configuration, "taints-ignore-list")
    if taints is not None:
        taint_ignore_list = load_taint_list_from_dict(taints)

    nodes, kubeclient = get_active_nodes(None, taint_ignore_list, secrets)

    active_nodes = [i.metadata.name for i in nodes.items]

    api = create_k8s_api_client(secrets)
    v1 = client.CoreV1Api(api)
    pods = v1.list_pod_for_all_namespaces(watch=False)
    retval = True
    for i in pods.items:
        if i.spec.node_name in active_nodes and i.status.container_statuses is not None:
            for status in i.status.container_statuses:
                if status.state.running is None:
                    if i.metadata.namespace not in ns_ignore_list:
                        logger.info("%s\t%s\t%s \t%s is not good" % (
                            i.status.host_ip,
                            i.metadata.namespace,
                            i.metadata.name,
                            i.status.container_statuses[0].state))
                        retval = False
                        break
                    else:
                        logger.info("%s\t%s\t%s \t%s is IGNORED" % (
                            i.status.host_ip,
                            i.metadata.namespace,
                            i.metadata.name,
                            i.status.container_statuses[0].state))
    return retval


def nodes_super_healthy(
        label_selector: str = "",
        ns: str = "",
        configuration: Configuration = None,
        secrets: Secrets = None) -> bool:
    """
    Super set of tests for nodes health. all_nodes_are_ok all_pods_in_all_ns_are_ok all_microservices_healthy
    :param ns: namespace to check microservices in
    :param configuration: experiment configuration
    :param secrets: k8s credentials
    :return: true if all test are ok. False otherwise
    """
    logger.debug(
        "========================Running all pods in all namespaces are ok check")

    retval = all_pods_in_all_ns_are_ok(
        configuration=configuration, secrets=secrets)
    if retval:
        logger.debug("========================Running all nodes are ok check")
        retval = all_nodes_are_ok(
            label_selector=label_selector,
            secrets=secrets,
            configuration=configuration)
    return retval


def check_http(url: str, timeout: int = 5) -> int:
    """
    Perfromts http get for given url.
    :param url: url to get results
    :param timeout: timeout to wait for response 5 sec defualt
    :return: retunrs status_code of request
    """
    r = requests.get(url, timeout=timeout)
    return r.status_code


# moved to pod/probes.py
read_microservices_logs = read_pod_logs
