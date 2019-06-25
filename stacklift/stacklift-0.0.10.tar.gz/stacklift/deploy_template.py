#!/usr/bin/env python3

from stacklift.read_config import ConfigReader
from stacklift.cfn_deploy import CloudFormationDeployer
from stacklift.templates_config import StackDesiredState
import boto3
import os
import zipfile
import contextlib
import hashlib
import uuid
import tempfile
import botocore
import re


def update_hash(hasher, file_name):
    block_size = 4096
    with open(file_name, "rb") as fp:
        buf = fp.read(block_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fp.read(block_size)


def zip_dir(temp_archive_path, target_dir):
    hasher = hashlib.md5()

    target_root = os.path.abspath(target_dir)
    with open(temp_archive_path, 'wb') as f:
        zip_file = zipfile.ZipFile(f, 'w', zipfile.ZIP_DEFLATED)
        with contextlib.closing(zip_file) as z:
            for root, _, files in os.walk(target_root):
                for filename in files:
                    full_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(full_path, target_root)
                    z.write(full_path, relative_path)

                    update_hash(hasher, full_path)

    digest = hasher.hexdigest()
    return "{}.zip".format(digest)


@contextlib.contextmanager
def archive(target_dir):
    temp_archive_path = os.path.join(tempfile.gettempdir(), "archive-{}.zip".format(uuid.uuid4().hex))

    try:
        candidate_filename = zip_dir(temp_archive_path, target_dir)
        yield (temp_archive_path, candidate_filename)
    finally:
        if os.path.exists(temp_archive_path):
            os.remove(temp_archive_path)


class DeployTemplate:
    def __init__(self, template_file, config_file, section_name, stack_desired_state):
        self.template_file = template_file
        self.config_reader = ConfigReader(config_file)
        self.section_name = section_name
        self.stack_desired_state = stack_desired_state
        self.region = self.config_reader.get_value(self.section_name, "Region")
        self.client = boto3.client('cloudformation', region_name=self.region)
        self.s3 = boto3.client('s3')

    def get_export_value(self, export_name):
        paginator = self.client.get_paginator('list_exports')
        page_iterator = paginator.paginate()

        for page in page_iterator:
            for export in page["Exports"]:
                if export["Name"] == export_name:
                    return export["Value"]

        raise RuntimeError("Failed to get a export value: {}".format(export_name))

    def get_parameter_names(self, template_file):
        with open(template_file) as fp:
            response = self.client.validate_template(TemplateBody=fp.read())

        return [parameter["ParameterKey"] for parameter in response["Parameters"]]

    def upload_function(self, deploy_bucket_name, function_root):
        # TODO: share the same function_root archives
        with archive(function_root) as (temp_path, candidate_filename):
            key_name = "function/{}".format(candidate_filename)
            if not self.check_file_exists(deploy_bucket_name, key_name):
                self.s3.upload_file(temp_path, deploy_bucket_name, key_name)

            return key_name

    async def deploy(self, function_root):
        if self.stack_desired_state == StackDesiredState.DELETED:
            params = {}
        else:
            parameter_names = self.get_parameter_names(self.template_file)
            params = self.config_reader.get_parameters(self.section_name, parameter_names)

            if function_root:
                deploy_bucket_name = self.config_reader.get_value(self.section_name, "DeployBucketName")
                deploy_code_key = self.upload_function(deploy_bucket_name=deploy_bucket_name,
                                                       function_root=function_root)
            else:
                deploy_bucket_name = ""
                deploy_code_key = ""

            for name in parameter_names:
                value = params[name]
                value = re.sub(r'%DeployBucketName%', deploy_bucket_name, value)
                value = re.sub(r'%DeployCodeKey%', deploy_code_key, value)
                params[name] = value

        stack_name = self.config_reader.get_value(self.section_name, "StackName")
        changeset_desired_state = self.config_reader.get_value_or_default(self.section_name, "ChangesetDesiredState",
                                                                          "completed")
        capabilities = self.config_reader.get_value_or_default(self.section_name, "Capabilities", "CAPABILITY_IAM")
        role_export_name = self.config_reader.get_value_or_default(self.section_name, "CloudFormationRoleExport")
        role_arn = self.get_export_value(role_export_name) if role_export_name else None

        deployer = CloudFormationDeployer(region_name=self.region,
                                          stack_name=stack_name,
                                          logger_name=self.section_name,
                                          template_file=self.template_file,
                                          changeset_desired_state=changeset_desired_state,
                                          stack_desired_state=self.stack_desired_state,
                                          capabilities=capabilities,
                                          role_arn=role_arn,
                                          template_parameters=params)
        change_list = await deployer.deploy()
        return change_list

    def check_file_exists(self, bucket_name, key_name):
        try:
            self.s3.head_object(Bucket=bucket_name, Key=key_name)
            return True
        except botocore.exceptions.ClientError:
            return False
