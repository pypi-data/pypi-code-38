#!/usr/bin/env python
# Copyright 2018 Chathuranga Abeyrathna. All Rights Reserved.
# opsworks-cli for AWS OpsWorks Deployments

# execute deploy module

import boto3
import prettytable
import modules.common_functions


def test_output_summary(region, stack, layer, app, custom_json=None):
    table = prettytable.PrettyTable()
    table.field_names = ["Region", "StackID", "LayerID", "ApplicationID", "CustomJSON"]
    table.add_row([str(region), str(stack), str(layer), str(app), str(custom_json)])
    print(table.get_string(title="Test Input Summary"))


def deploy_with_layer(region, stack, layer, app, custom_json=None):
    if stack == '2e7f6dd5-e4a3-4389-bc95-b4bacc234df0':
        print('deploy_with_layer sub function')
        test_output_summary(region, stack, layer, app, custom_json)
    else:
        try:
            custom_json
        except NameError:
            custom_json = str({})
        custom_json = custom_json
        if custom_json is None:
            custom_json = str({})
        # initiate boto3 client
        client = boto3.client('opsworks', region_name=region)
        # calling deployment to specified stack layer
        run_recipes = client.create_deployment(
            StackId=stack,
            AppId=app,
            LayerIds=[
                layer,
            ],
            Command={
                'Name': 'deploy',
            },
            Comment='automated deploy job',
            CustomJson=custom_json
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

        deploymentid = run_recipes['DeploymentId']
        # sending describe command to get status"""  """
        modules.common_functions.get_status(deploymentid, region, instances)


def deploy_without_layer(region, stack, app, custom_json=None):
    if stack == '2e7f6dd5-e4a3-4389-bc95-b4bacc234df0':
        print('deploy_without_layer sub function')
        layer = None
        test_output_summary(region, stack, app, custom_json)
    else:
        try:
            custom_json
        except NameError:
            custom_json = str({})
        custom_json = custom_json
        if custom_json is None:
            custom_json = str({})
        # initiate boto3 client
        client = boto3.client('opsworks', region_name=region)
        # calling deployment to specified stack
        run_recipes = client.create_deployment(
            StackId=stack,
            AppId=app,
            Command={
                'Name': 'deploy',
            },
            Comment='automated deploy job',
            CustomJson=custom_json
        )

        # calling aws api to get the instances within the
        get_intance_count = client.describe_instances(
            StackId=stack
        )
        all_instance_ids = []
        for instanceid in get_intance_count['Instances']:
            ec2id = instanceid['Ec2InstanceId']
            all_instance_ids.append(ec2id)
        instances = len(all_instance_ids)

        deploymentid = run_recipes['DeploymentId']
        # sending describe command to get status"""  """
        modules.common_functions.get_status(deploymentid, region, instances)


def deploy(region, stack, app, layer=None, custom_json=None):
    # adding new line to support the test functions
    if stack == '2e7f6dd5-e4a3-4389-bc95-b4bacc234df0':
        print('deploy main function')
        test_output_summary(region, stack, layer, app, custom_json)
    else:
        # sending request to collect the stack and layer names
        modules.common_functions.get_names(stack, layer, region, "deploy")
        if layer is None:
            deploy_without_layer(region, stack, app, custom_json)
        else:
            deploy_with_layer(region, stack, layer, app, custom_json)
