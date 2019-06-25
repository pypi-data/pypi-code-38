# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from argparse import Namespace

from azureml._base_sdk_common.project_context import create_project_context
from azureml._base_sdk_common.cli_wrapper._common import get_default_subscription_id
from azureml.core.workspace import Workspace
from azureml.core.experiment import Experiment
from azureml.exceptions import UserErrorException
from azureml._base_sdk_common.cli_wrapper._common import get_workspace_or_default_name, \
    get_resource_group_or_default_name, _get_project_object

from azureml._history.jmespath_data_mapper import JmesPathDataMapper
from azureml._project.project import Project
import jmespath
from .run_history_service import RunHistoryService
import logging

logger = logging.getLogger(__name__)


# Uncomment this for testing on master deployment
# __SERVICE_URL__ = "https://master.experiments.azureml-test.net"
PROJECT_ASSETS_DIR = 'assets'
LOG_FILE_NAME = "driver_log"


def list_runs(context, args):
    service_facade = RunHistoryService(context, logger)

    if args.run_ids is not None:
        run_data = [service_facade.get_run(rid) for rid in args.run_ids]
    else:
        run_data = service_facade.get_runs()

    metrics = []
    for run in run_data:
        if isinstance(run, dict) and JmesPathDataMapper.RUN_ID in run.keys():
            run_metric = service_facade.list_metrics(
                run.get(JmesPathDataMapper.RUN_ID, None))
            if run_metric:
                metrics.extend(run_metric)

    run_data = JmesPathDataMapper().map_runs(
        run_data, metrics, status=args.status) if run_data is not None else []
    return run_data


def show_run_detail(context, args):
    service_facade = RunHistoryService(context, logger)
    run_data = service_facade.get_run(args.run_id)
    if run_data is not None:
        attachments = service_facade.list_attachments(
            args.run_id)

        names = _get_artifact_names(attachments)
        if args.attachment:
            if _validate_artifact(args.attachment, names, args.run_id) is True:
                print(service_facade.get_run_attachment_content(
                    args.run_id, args.attachment))
            return

        if args.output:
            if _validate_artifact(LOG_FILE_NAME, names, args.run_id) is True:
                print(service_facade.get_run_attachment_content(
                    args.run_id, LOG_FILE_NAME))
            return

        else:
            run_metrics = service_facade.list_metrics(args.run_id)

            return JmesPathDataMapper().map_run(run_data, attachments, run_metrics)
    else:
        logger.debug("Run history service returns no data")
        return []


def show_last_run(context, args):
    service_facade = RunHistoryService(context, logger)
    run_data = service_facade.get_runs(last=1)
    if run_data:
        last_data = run_data.pop()
        run_id = last_data.get(JmesPathDataMapper.RUN_ID)
        attachments = service_facade.list_attachments(run_id)

        if args.output:
            names = _get_artifact_names(attachments)
            if _validate_artifact(LOG_FILE_NAME, names, run_id) is True:
                print(service_facade.get_run_attachment_content(
                    run_id, LOG_FILE_NAME))
            return
        else:
            metrics = service_facade.list_metrics(run_id)
            return JmesPathDataMapper().map_run(last_data, attachments, metrics)
    else:
        logger.debug("Run history service returns no data")
        return []


def compare_runs(context, args):
    service_facade = RunHistoryService(context, logger)

    two_runs = [service_facade.get_run(rid) for rid in args.run_ids]

    if len(two_runs) != 2 or two_runs[0] is None or two_runs[1] is None:
        raise Exception("Cannot find runs of the provided run ids")

    metrics = []
    metrics.extend(service_facade.list_metrics(rid) for rid in args.run_ids)
    return JmesPathDataMapper().compare_runs(two_runs, metrics)


def download_artifact(context, args):
    if args.attachment:
        if not args.overwrite:
            if os.path.exists(os.path.join(args.destination, args.attachment)):
                print("There is a file name {0} existing in {1}, "
                      "please add '--overwrite' to overwrite"
                      .format(args.attachment, args.destination))
                return

    service_facade = RunHistoryService(context, logger)
    if args.last and not args.run_id:
        run_details = service_facade.get_runs(last=1)
        if not run_details:
            raise ValueError("Unable to get last run")
        last_run = run_details.pop()
        args.run_id = last_run["run_id"]
    attachments = service_facade.list_attachments(args.run_id)
    names = _get_artifact_names(attachments)
    if not names:
        print("There is no artifacts with this run_id {}".format(args.run_id))
        return

    if args.attachment:
        if _validate_artifact(args.attachment, names, args.run_id) is True:
            file_path = service_facade.download_run_attachment(
                args.run_id, args.attachment, args.destination, args.overwrite)
            if file_path:
                print('Artifact {0} has been downloaded to {1}'.format(
                    args.attachment, file_path))
        return

    if not args.overwrite:
        is_existing = False
        for name in names:
            if os.path.exists(os.path.join(args.destination, name)):
                is_existing = True
                print(
                    "There is a file name {0} existing in {1}, "
                    "please add '--overwrite' to overwrite"
                    .format(name, args.destination))
        if is_existing:
            return

    for name in names:
        file_path = service_facade.download_run_attachment(
            args.run_id, name, args.destination, args.overwrite)
        if file_path:
            print('Artifact {0} has been downloaded to {1}'.format(
                name, file_path))
        else:
            print("Cannot find the artifact {0} with run_id {1}".format(
                name, args.run_id))
    return


def download_snapshot(context, project_object, args):
    service_facade = RunHistoryService(context, logger)
    if args.last and not args.run_id:
        last_run = service_facade.get_runs(last=1)
        run_details = last_run.pop() if last_run else None
    else:
        run_details = service_facade.get_run(args.run_id)

    if run_details:
        if "properties" in run_details and "ContentSnapshotId" in run_details["properties"]:
            snapshot_id = run_details["properties"]["ContentSnapshotId"]
            return project_object._snapshot_restore(snapshot_id, args.destination)
        else:
            raise ValueError("Run does not have an associated SnapshotId")
    else:
        raise ValueError("Could not find run details")


def _validate_artifact(artifacts, names_in_server, run_id):
    is_validate = True

    if isinstance(artifacts, list):
        for artifact in artifacts:
            if artifact not in names_in_server:
                print("Cannot find the artifact '{0}' with run_id '{1}'".format(
                    artifact, run_id))
                return False

    if isinstance(artifacts, str):
        if artifacts not in names_in_server:
            print("Cannot find the artifact '{0}' with run_id '{1}'".format(
                artifacts, run_id))
            return False
    else:
        raise TypeError(
            "Argument 'artifacts' should be a string or list of strings.")

    return is_validate


def _get_artifact_names(artifacts):
    if not artifacts:
        return []

    names = jmespath.search(
        '[*].{0}'.format(JmesPathDataMapper.PATH), artifacts)

    # backward compatible if reference old version (<1.2.0) of azure.dmsclient
    if not names:
        names = jmespath.search(
            '[*].{0}'.format(JmesPathDataMapper.NAME), artifacts)
        if names:
            logger.debug(
                "Old azure.dmsclient is being used, please update to newer azure.dmsclient")
    if not names:
        names = []
    return names


def get_project_context(auth, subscription_id, resource_group=None, workspace_name=None, project_name=None,
                        project_path=None):
    # If everything is specified then that is the project context.
    if resource_group and workspace_name and project_name:
        workspace_object = Workspace(subscription_id, resource_group, workspace_name, auth=auth)
        project_context = create_project_context(
            workspace_object._auth_object,
            workspace_object.subscription_id,
            workspace_object.resource_group,
            workspace_object.name,
            project_name,
            workspace_object._workspace_id)
        return project_context
    else:
        # We check if we are in a project scope.
        project_object = _get_project_object(auth=auth, project_path=project_path)
        if project_object:
            project_context = create_project_context(
                auth,
                subscription_id,
                project_object.workspace.resource_group,
                project_object.workspace.name,
                project_object.history.name,
                project_object.workspace._workspace_id)
            return project_context
        else:
            # Try to get the CLI default values that might have been set using az configure command.
            if not project_name:
                raise UserErrorException("Experiment name cannot be none.")

            resource_group = get_resource_group_or_default_name(resource_group, throw_error=True, auth=auth,
                                                                project_path=project_path)
            workspace_name = get_workspace_or_default_name(workspace_name, throw_error=True, auth=auth,
                                                           project_path=project_path)

            workspace_object = Workspace(subscription_id, resource_group, workspace_name, auth=auth)
            project_context = create_project_context(
                workspace_object._auth_object,
                workspace_object.subscription_id,
                workspace_object.resource_group,
                workspace_object.name,
                project_name,
                workspace_object._workspace_id)
            return project_context


def receiver(
        auth,
        status=None,
        run_ids=None,
        run_id=None,
        attachment=None,
        destination=None,
        overwrite=False,
        artifact_path=None,
        name=None,
        outputs=None,
        subscription_id=None,
        project_path=None,
        subparser_name=None,
        resource_group=None,
        workspace=None,
        project=None,
        last=None):
    # TODO check if receiver is used with named param,
    # if not change project to experiment_name

    # Setting default subscription id.
    if not subscription_id:
        subscription_id = get_default_subscription_id(auth)

    args = Namespace()
    args.subparser_name = subparser_name
    args.status = status
    args.run_ids = run_ids
    args.run_id = run_id
    args.attachment = attachment
    args.destination = destination
    args.overwrite = overwrite
    args.output = outputs
    args.name = name
    args.artifact_path = artifact_path
    args.last = last

    # Special case for listing run histories for a workspace, which
    # doesn't require a project to exist locally.
    if args.subparser_name == "list_run_histories":
        resource_group = get_resource_group_or_default_name(resource_group, throw_error=True, auth=auth)
        workspace = get_workspace_or_default_name(workspace, throw_error=True, auth=auth)

        workspace_object = Workspace(subscription_id=subscription_id,
                                     resource_group=resource_group,
                                     workspace_name=workspace,
                                     auth=auth)

        experiments = Experiment.list(workspace_object)
        experiments_list_serialized = [experiment._serialize_to_dict() for experiment in experiments]

        return experiments_list_serialized

    curr_dir = os.getcwd()

    if project_path:
        if not os.path.isdir(project_path):
            raise UserErrorException("Project path {path} does not exist".format(
                path=project_path))
    else:
        project_path = curr_dir
    args.project_path = project_path

    project_context = get_project_context(auth, subscription_id, resource_group=resource_group,
                                          workspace_name=workspace, project_name=project,
                                          project_path=project_path)

    if args.destination and not os.path.isabs(args.destination):
            args.destination = os.path.abspath(os.path.join(project_path, args.destination))

    if args.subparser_name == "list_runs":
        return list_runs(project_context, args)
    elif args.subparser_name == "info":
        return show_run_detail(project_context, args)
    elif args.subparser_name == "last":
        return show_last_run(project_context, args)
    elif args.subparser_name == "compare":
        return compare_runs(project_context, args)
    elif args.subparser_name == "download":
        return download_artifact(project_context, args)
    elif args.subparser_name == "snapshot":
        project_object = Project(auth=auth, directory=project_path)
        return download_snapshot(project_context, project_object, args)
    else:
        raise Exception(
            "Unsupported command: {0}".format(args.subparser_name))
