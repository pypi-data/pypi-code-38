# -*- coding: utf-8 -*-
import json
import os
import random
from chaoslib.exceptions import FailedActivity
from chaoslib.types import MicroservicesStatus, Secrets, Configuration
from logzero import logger
from kubernetes import client
from kubernetes.client.rest import ApiException
import yaml
from chaosk8s_wix import create_k8s_api_client
from chaosk8s_wix.slack.logger_handler import SlackHanlder

__all__ = ["start_microservice", "kill_microservice", "scale_microservice",
           "remove_service_endpoint", "kill_microservice_by_label", "get_random_namespace"]


slack_handler = SlackHanlder()
slack_handler.attach(logger)


def start_microservice(spec_path: str, ns: str = "default",
                       secrets: Secrets = None):
    """
    Start a microservice described by the deployment config, which must be the
    path to the JSON or YAML representation of the deployment.
    """
    api = create_k8s_api_client(secrets)

    with open(spec_path) as f:
        p, ext = os.path.splitext(spec_path)
        if ext == '.json':
            deployment = json.loads(f.read())
        elif ext in ['.yml', '.yaml']:
            deployment = yaml.load(f.read())
        else:
            raise FailedActivity(
                "cannot process {path}".format(path=spec_path))

    v1 = client.AppsV1beta1Api(api)
    resp = v1.create_namespaced_deployment(ns, body=deployment)
    return resp


def kill_microservice(name: str, ns: str = "default",
                      label_selector: str = "name in ({name})",
                      secrets: Secrets = None):
    """
    Kill a microservice by `name` in the namespace `ns`.

    The microservice is killed by deleting the deployment for it without
    a graceful period to trigger an abrupt termination.

    The selected resources are matched by the given `label_selector`.
    """
    label_selector = label_selector.format(name=name)
    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1beta1Api(api)
    ret = v1.list_namespaced_deployment(ns, label_selector=label_selector)

    logger.debug("Found {d} deployments named '{n}'".format(
        d=len(ret.items), n=name))

    body = client.V1DeleteOptions()
    for d in ret.items:
        res = v1.delete_namespaced_deployment(
            name=d.metadata.name, namespace=ns, body=body)

    v1 = client.ExtensionsV1beta1Api(api)
    ret = v1.list_namespaced_replica_set(ns, label_selector=label_selector)

    logger.debug("Found {d} replica sets named '{n}'".format(
        d=len(ret.items), n=name))

    body = client.V1DeleteOptions()
    for r in ret.items:
        res = v1.delete_namespaced_replica_set(
            name=r.metadata.name, namespace=ns, body=body)

    v1 = client.CoreV1Api(api)
    ret = v1.list_namespaced_pod(ns, label_selector=label_selector)

    logger.debug("Found {d} pods named '{n}'".format(
        d=len(ret.items), n=name))

    body = client.V1DeleteOptions()
    for p in ret.items:
        res = v1.delete_namespaced_pod(
            name=p.metadata.name, namespace=ns, body=body)


def kill_microservice_by_label(label_selector: str = "name in ({name})",
                               secrets: Secrets = None):
    """
    Kill a microservice by `label_selector` in the namespace `ns`.

    The microservice is killed by deleting the deployment for it without
    a graceful period to trigger an abrupt termination.

    The selected resources are matched by the given `label_selector`.
    """

    api = create_k8s_api_client(secrets)

    v1 = client.AppsV1beta1Api(api)

    ret = v1.list_deployment_for_all_namespaces(label_selector=label_selector)

    logger.debug("Found {d} deployments labeled '{n}'".format(
        d=len(ret.items), n=label_selector))

    body = client.V1DeleteOptions()
    for d in ret.items:
        logger.debug("Delete deployment {}".format(d.metadata.name))
        res = v1.delete_namespaced_deployment(
            name=d.metadata.name, namespace=d.metadata.namespace, body=body)

    v1 = client.ExtensionsV1beta1Api(api)
    ret = v1.list_replica_set_for_all_namespaces(label_selector=label_selector)
    logger.debug("Found {d} replica sets labeled '{n}'".format(
        d=len(ret.items), n=label_selector))

    v1 = client.ExtensionsV1beta1Api(api)
    body = client.V1DeleteOptions()
    for r in ret.items:
        logger.warning("Delete replicaset {}".format(r.metadata.name))
        res = v1.delete_namespaced_replica_set(
            name=r.metadata.name, namespace=r.metadata.namespace, body=body)

    v1 = client.CoreV1Api(api)
    ret = v1.list_pod_for_all_namespaces(label_selector=label_selector)

    logger.debug("Found {d} pods labeled '{n}'".format(
        d=len(ret.items), n=label_selector))

    body = client.V1DeleteOptions()
    for p in ret.items:
        logger.warning("Delete pod {}".format(p.metadata.name))
        res = v1.delete_namespaced_pod(
            name=p.metadata.name, namespace=p.metadata.namespace, body=body)


def remove_service_endpoint(name: str, ns: str = "default",
                            secrets: Secrets = None):
    """
    Remove the service endpoint that sits in front of microservices (pods).
    """
    api = create_k8s_api_client(secrets)

    v1 = client.CoreV1Api(api)
    v1.delete_namespaced_service(name, namespace=ns)


def scale_microservice(name: str, replicas: int, ns: str = "default",
                       secrets: Secrets = None):
    """
    Scale a deployment up or down. The `name` is the name of the deployment.
    """
    api = create_k8s_api_client(secrets)

    v1 = client.ExtensionsV1beta1Api(api)
    body = {"spec": {"replicas": replicas}}
    try:
        v1.patch_namespaced_deployment_scale(name, namespace=ns, body=body)
    except ApiException as e:
        raise FailedActivity(
            "failed to scale '{s}' to {r} replicas: {e}".format(
                s=name, r=replicas, e=str(e)))


def get_random_namespace(configuration: Configuration = None, secrets: Secrets = None):
    """
    Get random namespace from cluster.
    Supports ns-ignore-list value in configuration
    :param secrets: chaostoolkit will inject this dictionary
    :param configuration: chaostoolkit will inject this dictionary
    :return: random namespace
    """
    ns_ignore_list = []
    if configuration is not None:
        ns_ignore_list = configuration.get("ns-ignore-list", [])

    api = create_k8s_api_client(secrets)
    v1 = client.CoreV1Api(api)
    ret = v1.list_namespace()
    namespace = None

    clean_ns = [
        namespace for namespace in ret.items if namespace.metadata.name not in ns_ignore_list]

    if len(clean_ns) > 0:
        namespace = random.choice(clean_ns)
    return namespace


def deploy_service_in_random_namespace(spec_path: str,
                                       configuration: Configuration = None,
                                       secrets: Secrets = None):
    """
    Start a microservice described by the deployment config, which must be the
    path to the JSON or YAML representation of the deployment.microservice will be
    started in random namespace.
    """
    api = create_k8s_api_client(secrets)

    with open(spec_path) as f:
        p, ext = os.path.splitext(spec_path)
        if ext == '.json':
            deployment = json.loads(f.read())
        elif ext in ['.yml', '.yaml']:
            deployment = yaml.safe_load(f.read())
        else:
            raise FailedActivity(
                "cannot process {path}".format(path=spec_path))

    v1 = client.AppsV1beta1Api(api)
    ns = get_random_namespace(configuration=configuration, secrets=secrets)
    logger.warning(
        "Deploy test deployment to {ns} namespace".format(ns=ns.metadata.name))
    v1.create_namespaced_deployment(ns.metadata.name, body=deployment)
