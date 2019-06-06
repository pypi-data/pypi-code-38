# -*- coding: utf-8 -*-
import random
import boto3
from chaoslib.types import Configuration, Secrets
from logzero import logger
from chaosk8s_wix.node import get_active_nodes, load_taint_list_from_dict
from fabric import api
import os
from chaosk8s_wix.slack.logger_handler import SlackHanlder

__all__ = [
    "tag_random_node_aws",
    "set_tag_to_aws_instance",
    "detach_sq_from_instance_by_tag",
    "attach_sq_to_instance_by_tag",
    "remove_tag_from_aws_instances",
    "iptables_block_port",
    "terminate_instance_by_tag",
    "run_shell_command_on_tag"
]

slack_handler = SlackHanlder()
slack_handler.attach(logger)


def get_aws_filters_from_configuration(configuration: Configuration = None):
    filters_to_set = []
    if configuration is not None and "aws-instance-filters" in configuration.keys() is not None:
        filters_to_set = configuration["aws-instance-filters"]
    return filters_to_set


def get_sg_id_by_name(name: str = ""):
    retval = ""
    if name != "":
        ec2 = boto3.client('ec2')
        security_groups = ec2.describe_security_groups(
            Filters=[
                {
                    "Name": "group-name",
                    "Values": [name]
                }
            ]
        )
        for sg in security_groups['SecurityGroups']:
            retval = sg['GroupId']
    return retval


def set_tag_to_aws_instance(k8s_node_name: str = "not_defined",
                            tag_name: str = "under_chaostest",
                            aws_instance_filter: list = []):
    """
    Set tag to aws node. k8s_node_name should be the same as PrivateDnsName parameter in aws
    :param k8s_node_name: k8s node name is the same as PrivateDnsName field in aws
    :param tag_name:  tag name to set
    :param aws_instance_filter: not all aws instances are included into chaos testing scope.
    :return: result of ec2.create_tags, None if instance with specified PrivateDnsName was not found
    """
    filters_to_set = []
    if aws_instance_filter is not None:
        filters_to_set = aws_instance_filter

    ec2 = boto3.client('ec2')
    retval = None
    response = ec2.describe_instances(Filters=filters_to_set)

    for reservation in (response["Reservations"]):
        for instance in reservation["Instances"]:
            if instance['PrivateDnsName'] == k8s_node_name:

                retval = ec2.create_tags(Resources=[instance['InstanceId']],
                                         Tags=[{'Key': tag_name, 'Value': tag_name}])
    return retval


def tag_random_node_aws(k8s_label_selector: str = None,
                        secrets: Secrets = None,
                        tag_name: str = "under_chaos_test",
                        configuration: Configuration = None,
                        ) -> (int, str):
    """
    This works for k8s in aws only. Tags aws instance with specific tag. nodes will be slected from k8s cluster, and
    linked by PrivateDnsName property.

    :param k8s_label_selector: label selector for k8s nodes "com.wix.lifecycle=true"
    :param secrets: secrets to connect to k8s
    :param tag_name: tag to set for aws instance that hosts selected node
    :return: 0 and name of marked node. error code and erro description otherwise
    """
    filters_to_set = get_aws_filters_from_configuration(configuration)

    retval = 0
    desc = ""
    ignore_list = []
    if configuration is not None:
        ignore_list = load_taint_list_from_dict(
            configuration["taints-ignore-list"])

    resp, k8s_api_v1 = get_active_nodes(
        k8s_label_selector, ignore_list, secrets)
    random_node = None
    if len(resp.items) > 0:
        random_node = random.choice(resp.items)
    if random_node is not None:
        logger.info("tag_random_node_aws selected node " +
                    random_node.metadata.name + " with label " + tag_name)
        aws_retval = set_tag_to_aws_instance(
            random_node.metadata.name, tag_name, filters_to_set)
        if aws_retval is None:
            retval = 1
            desc = "Failed to set tag on aws node " + random_node.metadata.name
        else:
            desc = random_node.metadata.name
    else:
        retval = 1
        desc = "No node selected"

    return retval, desc


def remove_tag_from_aws_instances(configuration: Configuration = None,
                                  tag_name: str = "under_chaos_test") -> (int, str):
    """
    Removes tag if its already exist from aws instance.
    :param tag_name: name of the tag to remove
    :return:
    """
    filters_to_set = get_aws_filters_from_configuration(configuration)

    filters_to_set.append({'Name': 'tag:'+tag_name, 'Values': [tag_name]})

    ec2 = boto3.client('ec2')
    retval = None
    response = ec2.describe_instances(Filters=filters_to_set)
    array_of_ids = []
    for reservation in (response["Reservations"]):
        for instance in reservation["Instances"]:
            array_of_ids.append(instance.get('InstanceId'))
    if len(array_of_ids) > 0:
        ec2.delete_tags(Resources=array_of_ids, Tags=[{"Key": tag_name}])
    else:
        logger.warning('No aws instances found with tag {}'.format(tag_name))
    return retval


def attach_sq_to_instance_by_tag(tag_name: str = "not_set",
                                 sg_name: str = "not_set",
                                 configuration: Configuration = None):
    """
    Attaches security group to all instances with specific tag set.

    :param tag_name: tag to filter aws instances
    :param sg_name: security group name to attach
    :param configuration: injected by chaostoolkit framework
    :return: result of modify_attribute call
    """
    retval = None
    ec2 = boto3.resource('ec2')

    filters_to_set = get_aws_filters_from_configuration(configuration)
    filters_to_set.append({'Name': 'tag:' + tag_name, 'Values': [tag_name]})
    response = ec2.instances.filter(Filters=filters_to_set)
    sg_id = get_sg_id_by_name(sg_name)
    for instance in response:
        all_sg_ids = []
        all_sg_ids.append(sg_id)

        logger.warning('Attach {} to instance {} {}'.format(
            sg_id, instance.id, instance.private_dns_name))
        for interface in instance.network_interfaces:
            retval = interface.modify_attribute(Groups=all_sg_ids)
    return retval


def detach_sq_from_instance_by_tag(tag_name: str = "not_set",
                                   sg_name: str = "not_set",
                                   configuration: Configuration = None):
    """
    Detaches security group from instances market with specified tag.
    :param tag_name: tag to filter aws instances
    :param sg_name: security group name to attach
    :param configuration: configuration: injected by chaostoolkit framework
    :return: result of modify_attribute call
    """
    retval = None
    ec2 = boto3.resource('ec2')
    filters_to_set = get_aws_filters_from_configuration(configuration)
    filters_to_set.append({'Name': 'tag:' + tag_name, 'Values': [tag_name]})
    response = ec2.instances.filter(Filters=filters_to_set)

    target_sg_id = get_sg_id_by_name(sg_name)
    for instance in response:
        all_sg_ids = [sg['GroupId']
                      for sg in instance.security_groups if sg['GroupId'] != target_sg_id]
        logger.warning('Detach {} from instance {} {}'.format(target_sg_id,
                                                              instance.id,
                                                              instance.private_dns_name))

        retval = instance.modify_attribute(Groups=all_sg_ids)
    return retval


def terminate_instance_by_tag(tag_name: str = "not_set",
                              configuration: Configuration = None):
    """
    Terminates instance marked with specified tag in aws
    :param tag_name: tag to filter aws instances
    :param configuration: configuration: injected by chaostoolkit framework
    :return: result of modify_attribute call
    """
    retval = None

    ec2 = boto3.resource('ec2')
    filters_to_set = get_aws_filters_from_configuration(configuration)
    filters_to_set.append({'Name': 'tag:' + tag_name, 'Values': [tag_name]})
    filters_to_set.append(
        {'Name': 'instance-state-name', 'Values': ['running']})

    response = ec2.instances.filter(Filters=filters_to_set)

    for instance in response:
        logger.warning('Terminate instance {} {}'.format(
            instance.id, instance.private_dns_name))
        retval = instance.terminate()
    return retval


def iptables_block_port(tag_name: str = "under_chaos_test",
                        port: int = 0,
                        protocols: [] = None,
                        configuration: Configuration = None):
    """
    Block specific port on aws instance. SSH key should be provided with SHH_KEY env variable. Full text of the key

    :param tag_name: tag to filter aws instances
    :param port: port to block
    :param configuration: injected by chaostoolkit framework
    :param protocols: udp/tcp
    :return: result of shh command on host
    """

    retval = None
    ec2 = boto3.resource('ec2')

    filters_to_set = get_aws_filters_from_configuration(configuration)
    filters_to_set.append({'Name': 'tag:' + tag_name, 'Values': [tag_name]})
    response = ec2.instances.filter(Filters=filters_to_set)

    api.env.key = os.getenv("SSH_KEY")
    api.env.user = os.getenv("SSH_USER")
    api.env.port = 22
    text_format = "iptables -I PREROUTING  -t nat -p {} --dport {} -j DNAT --to-destination 0.0.0.0:1000"
    for instance in response:
        if instance.private_ip_address is not None:
            for protocol in protocols:
                command_text = text_format.format(protocol, port)

                api.env.host_string = instance.private_ip_address
                logger.warning("Run sudo {} \r\n on {}({})".format(command_text,
                                                                   instance.private_dns_name,
                                                                   instance.private_ip_address))
                retval = api.sudo(command_text).return_code
    return retval


def run_shell_command_on_tag(tag_name: str = "under_chaos_test",
                             command: str = "",
                             sudo: bool = False,
                             configuration: Configuration = None):
    """
    Block specific port on aws instance. SSH key should be provided with SHH_KEY env variable. Full text of the key

    :param tag_name: tag to filter aws instances
    :param command: command to execute
    :param configuration: injected by chaostoolkit framework
    :param sudo: True to run command in as sudo, False otherwise
    :return: result of ssh command on host
    """

    retval = None
    ec2 = boto3.resource('ec2')

    filters_to_set = get_aws_filters_from_configuration(configuration)
    filters_to_set.append({'Name': 'tag:' + tag_name, 'Values': [tag_name]})
    response = ec2.instances.filter(Filters=filters_to_set)

    api.env.key = os.getenv("SSH_KEY")
    api.env.user = os.getenv("SSH_USER")
    api.env.port = 22
    for instance in response:
        command_text = command
        api.env.host_string = instance.private_ip_address
        if sudo:
            logger.warning("Run sudo {} \r\n on {}({})".format(command_text,
                                                               instance.private_dns_name,
                                                               instance.private_ip_address))
            retval = api.sudo(command_text).return_code
        else:
            logger.warning("Run {} \r\n on {}({})".format(command_text,
                                                          instance.private_dns_name,
                                                          instance.private_ip_address))
            retval = api.run(command_text).return_code
    return retval
