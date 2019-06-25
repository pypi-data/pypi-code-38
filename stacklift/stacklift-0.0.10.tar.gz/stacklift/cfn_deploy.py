#!/usr/bin/env python3

import boto3
import botocore
import json
import datetime
import logging
import asyncio
from enum import Enum, unique, auto
from stacklift.templates_config import StackDesiredState


# logging.basicConfig(format="[%(levelname)s][%(name)s] %(message)s")
logging.basicConfig(format="[%(name)s] %(message)s", level=logging.INFO)

# botocore.session.Session().set_debug_logger()
logging.getLogger('botocore').setLevel(logging.WARN)


class ChangeSetResourceChange:
    def __init__(self, action, resource_type, logical_resource_id):
        self.action = action
        self.resource_type = resource_type
        self.logical_resource_id = logical_resource_id

    def __str__(self):
        return '{0:<6} {1:<25} {2:<32}'.format(self.action, self.resource_type, self.logical_resource_id)


@unique
class DeployStatus(Enum):
    UNCHANGED = auto()
    CHANGESET_CREATED = auto()
    CHANGESET_EXECUTED = auto()
    CHANGESET_COMPLETED = auto()
    DELETED = auto()


class CloudFormationDeployResult:
    def __init__(self, stack_name, deploy_status, change_list=None):
        self.stack_name = stack_name
        self.deploy_status = deploy_status
        self.change_list = change_list or []

    def __str__(self):
        return "## {}: {}\n{}".format(self.stack_name, self.deploy_status.name,
                                      "\n".join(["* {}".format(x) for x in self.change_list]))

    def is_change_exists(self):
        return len(self.change_list) > 0


class CloudFormationDeployer:
    def __init__(self,
                 region_name,
                 stack_name,
                 logger_name,
                 template_file,
                 template_parameters,
                 changeset_desired_state,
                 stack_desired_state,
                 role_arn,
                 capabilities):
        self.client = boto3.client('cloudformation', region_name=region_name)
        self.stack_name = stack_name
        self.change_set_name = "{:}-{:%Y%m%d%H%M%S}".format(stack_name, datetime.datetime.utcnow())

        self.logger = logging.getLogger(logger_name)

        self.template_file = template_file
        self.template_parameters = template_parameters
        self.changeset_desired_state = changeset_desired_state
        self.stack_desired_state = stack_desired_state
        self.role_arn = role_arn
        self.capabilities = capabilities

    def describe_stack_or_none(self):
        try:
            response = self.client.describe_stacks(StackName=self.stack_name)
        except botocore.exceptions.ClientError as e:
            if "Stack with id {0} does not exist".format(self.stack_name) in str(e):
                return None
            raise
        return response

    def check_stack_exists(self):
        response = self.describe_stack_or_none()
        if not response:
            return False

        status = response['Stacks'][0]['StackStatus']
        return status != "REVIEW_IN_PROGRESS"

    async def wait_waiter_once(self, waiter, delay, waiter_kwargs, raise_max_attempts=False):
        await asyncio.sleep(delay)
        try:
            waiter.wait(WaiterConfig={'MaxAttempts': 1}, **waiter_kwargs)
            return True
        except botocore.exceptions.WaiterError as ex:
            if raise_max_attempts:
                raise

            reason = ex.kwargs["reason"]
            if reason == "Max attempts exceeded":
                return False

            raise

    async def wait_waiter(self, waiter, delay, max_attempts, waiter_kwargs):
        for i in range(max_attempts - 1):
            if await self.wait_waiter_once(waiter, delay, waiter_kwargs):
                return

        await self.wait_waiter_once(waiter, delay, waiter_kwargs, raise_max_attempts=True)

    async def create_change_set(self,
                                is_update):
        create_or_update = "UPDATE" if is_update else "CREATE"

        with open(self.template_file) as fp:
            template_body = fp.read()

        args = {
            'StackName': self.stack_name,
            'TemplateBody': template_body,
            'ChangeSetType': create_or_update,
            'ChangeSetName': self.change_set_name,
            'Parameters': [{'ParameterKey': k, 'ParameterValue': self.template_parameters[k]}
                           for k in self.template_parameters]
        }

        if self.role_arn:
            args['RoleARN'] = self.role_arn

        if self.capabilities:
            args['Capabilities'] = [self.capabilities]

        result = self.client.create_change_set(**args)
        stack_id = result["StackId"]

        waiter = self.client.get_waiter("change_set_create_complete")
        try:
            await self.wait_waiter(waiter, 3, 120, {
                "StackName": stack_id,
                "ChangeSetName": self.change_set_name
            })
        except botocore.exceptions.WaiterError as ex:
            res = ex.last_response
            status = res.get("Status")
            reason = res.get("StatusReason")
            if status == "FAILED" and reason and (
                "The submitted information didn't contain changes." in reason or
                "No updates are to be performed" in reason):
                return None
            else:
                raise RuntimeError("Failed to create a changeset: {0}: {1}".format(status, reason))
        return stack_id

    def get_change_list(self):
        response = self.client.describe_change_set(StackName=self.stack_name, ChangeSetName=self.change_set_name)
        return [
            ChangeSetResourceChange(action=x["ResourceChange"]["Action"],
                                    resource_type=x["ResourceChange"]["ResourceType"],
                                    logical_resource_id=x["ResourceChange"]["LogicalResourceId"])
            for x in response["Changes"]
        ]

    def execute_changeset(self):
        self.client.execute_change_set(StackName=self.stack_name, ChangeSetName=self.change_set_name)

    def try_describe_stack_events(self, stack_name_or_id, next_token=None):
        stack_events_args = {"StackName": stack_name_or_id}
        if next_token:
            stack_events_args["NextToken"] = next_token

        try:
            response = self.client.describe_stack_events(**stack_events_args)
            return response["StackEvents"], response.get("NextToken")
        except botocore.exceptions.ClientError as ex:
            if "does not exist" in ex.response["Error"]["Message"]:
                return [], None
            raise

    def get_unrelated_stack_event_id(self):
        events, _ = self.try_describe_stack_events(self.stack_name)
        if events:
            return events[0]["EventId"]
        else:
            return None

    def get_stack_events_until(self, stack_name_or_id, boundary_event_id):
        result_events = []
        next_token = None
        while True:
            events, next_token = self.try_describe_stack_events(stack_name_or_id, next_token)

            for event in events:
                if boundary_event_id == event["EventId"]:
                    return result_events

                result_events.append(event)

            if not next_token:
                break

        return result_events

    def print_stack_events(self, stack_events):
        for event in reversed(stack_events):
            time = "{0:%Y-%m-%d %H:%M:%S}".format(event["Timestamp"])

            line = '{0:<20} {1:<20} {2:<32} {3} {4}'.format(
                time,
                event["ResourceStatus"],
                event["ResourceType"],
                event["LogicalResourceId"],
                event.get("ResourceStatusReason") or "")
            self.logger.info(line)

    def get_finish_waiter(self, is_update):
        if is_update:
            return self.client.get_waiter("stack_update_complete")
        else:
            return self.client.get_waiter("stack_create_complete")

    async def wait_waiter_with_events(self, waiter, stack_id, unrelated_stack_event_id):
        last_event_id = unrelated_stack_event_id
        for i in range(720):
            try:
                if await self.wait_waiter_once(waiter, 5, {"StackName": stack_id}):
                    return
            except botocore.exceptions.WaiterError as ex:
                res = ex.last_response
                stack = res["Stacks"][0]
                status = stack["StackStatus"]
                raise RuntimeError("Waiter detected a failure: {0}".format(status))
            finally:
                events = self.get_stack_events_until(stack_id, last_event_id)
                if events:
                    last_event_id = events[0]["EventId"]
                    self.print_stack_events(events)

    async def deploy(self):
        if self.stack_desired_state == StackDesiredState.DELETED:
            return await self.delete_stack()
        else:
            return await self.change_stack()

    async def change_stack(self):
        is_update = self.check_stack_exists()
        self.logger.info("Creating a change set {} ...".format(self.change_set_name))

        unrelated_stack_event_id = self.get_unrelated_stack_event_id()
        stack_id = await self.create_change_set(is_update=is_update)
        if not stack_id:
            self.logger.info("The changeset does not contain changes.")
            return CloudFormationDeployResult(stack_name=self.stack_name,
                                              deploy_status=DeployStatus.UNCHANGED)

        change_list = self.get_change_list()
        for c in change_list:
            self.logger.info("> " + str(c))

        if self.changeset_desired_state == "created":
            return CloudFormationDeployResult(stack_name=self.stack_name,
                                              deploy_status=DeployStatus.CHANGESET_CREATED,
                                              change_list=change_list)

        self.logger.info("Executing the change set...")
        self.execute_changeset()

        if self.changeset_desired_state == "executed":
            return CloudFormationDeployResult(stack_name=self.stack_name,
                                              deploy_status=DeployStatus.CHANGESET_EXECUTED,
                                              change_list=change_list)

        waiter = self.get_finish_waiter(is_update)
        await self.wait_waiter_with_events(waiter, stack_id, unrelated_stack_event_id)
        self.logger.info("Finished.")

        return CloudFormationDeployResult(stack_name=self.stack_name,
                                          deploy_status=DeployStatus.CHANGESET_COMPLETED,
                                          change_list=change_list)

    async def delete_stack(self):
        response = self.describe_stack_or_none()
        if not response:
            return CloudFormationDeployResult(stack_name=self.stack_name,
                                              deploy_status=DeployStatus.UNCHANGED)

        stack_id = response["Stacks"][0]["StackId"]

        # TODO: handle imported stacks
        unrelated_stack_event_id = self.get_unrelated_stack_event_id()

        self.logger.info("Deleting a stack {} ...".format(self.stack_name))
        self.client.delete_stack(StackName=self.stack_name)

        waiter = self.client.get_waiter("stack_delete_complete")
        await self.wait_waiter_with_events(waiter, stack_id, unrelated_stack_event_id)
        self.logger.info("Deleted.")

        return CloudFormationDeployResult(stack_name=self.stack_name,
                                          deploy_status=DeployStatus.DELETED)


class CloudFormationDeployerOptions:
    def __init__(self):
        self.stack_name = None
        self.template_file = None
        self.params_file = None
        self.region = None
        self.role_arn = None
        self.capabilities = None
        self.stack_desired_state = None
        self.changeset_desired_state = "completed"

def load_params(file):
    with open(file) as fp:
        return json.load(fp)


def deploy(opts: CloudFormationDeployerOptions):
    deployer = CloudFormationDeployer(
        region_name=opts.region,
        stack_name=opts.stack_name,
        logger_name=opts.stack_name,
        template_file=opts.template_file,
        template_parameters=load_params(opts.params_file),
        stack_desired_state=opts.stack_desired_state,
        changeset_desired_state=opts.changeset_desired_state,
        role_arn=opts.role_arn,
        capabilities=opts.capabilities)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(deployer.deploy())
