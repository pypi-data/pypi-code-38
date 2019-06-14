#!/usr/bin/env python
# Copyright 2018 Chathuranga Abeyrathna. All Rights Reserved.
# opsworks-cli for AWS OpsWorks Deployments

# execute setup module

import boto3
import prettytable
import modules.common_functions


def test_output_summary(region, stack, layer):
    table = prettytable.PrettyTable()
    table.field_names = ["Region", "StackID", "LayerID"]
    table.add_row([str(region), str(stack), str(layer)])
    print(table.get_string(title="Test Input Summary"))


def setup_with_layer(region, stack, layer):
    # adding new line to support the test functions
    if stack == '2e7f6dd5-e4a3-4389-bc95-b4bacc234df0':
        print('setup_with_layer sub function testing')
        test_output_summary(region, stack, layer)
    else:
        # initiate boto3 client
        client = boto3.client('opsworks', region_name=region)
        # calling deployment to specified stack layer
        run_setup = client.create_deployment(
            StackId=stack,
            LayerIds=[
                layer,
            ],
            Command={
                'Name': 'setup'
            },
            Comment='automated setup job with layer id'
        )
        # calling aws api to get the instances within the layer
        get_intance_count = client.describe_instances(
            LayerId=layer
        )
        all_instance_ids = []
        for instanceid in get_intance_count['Instances']:
            ec2id = instanceid['Ec2InstanceId']
            all_instance_ids.append(ec2id)
        instances = len(all_instance_ids)

        deploymentid = run_setup['DeploymentId']
        # sending describe command to get status"""  """
        modules.common_functions.get_status(deploymentid, region, instances)


def setup_without_layer(region, stack):
    # adding new line to support the test functions
    if stack == '2e7f6dd5-e4a3-4389-bc95-b4bacc234df0':
        print('setup_without_layer sub function testing')
        layer = None
        test_output_summary(region, stack, layer)
    else:
        # initiate boto3 client
        client = boto3.client('opsworks', region_name=region)
        # calling deployment to specified stack
        run_setup = client.create_deployment(
            StackId=stack,
            Command={
                'Name': 'setup'
            },
            Comment='automated setup job with stack id'
        )
        # calling aws api to get the instances within the stack
        get_intance_count = client.describe_instances(
            StackId=stack
        )
        all_instance_ids = []
        for instanceid in get_intance_count['Instances']:
            ec2id = instanceid['Ec2InstanceId']
            all_instance_ids.append(ec2id)
        instances = len(all_instance_ids)

        deploymentid = run_setup['DeploymentId']
        # sending describe command to get status"""  """
        modules.common_functions.get_status(deploymentid, region, instances)


def setup(region, stack, layer=None):
    # adding new line to support the test functions
    if stack == '2e7f6dd5-e4a3-4389-bc95-b4bacc234df0':
        print('setup main function testing')
        test_output_summary(region, stack, layer)
    else:
        # sending request to collect the stack and layer names
        modules.common_functions.get_names(stack, layer, region, "setup")
        if layer is None:
            setup_without_layer(region, stack)
        else:
            setup_with_layer(region, stack, layer)
