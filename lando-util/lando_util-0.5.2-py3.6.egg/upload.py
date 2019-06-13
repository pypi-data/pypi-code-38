import click
import json
from ddsc.sdk.client import Client as DukeDSClient, KindType
from ddsc.core.upload import ProjectUpload
from ddsc.core.remotestore import RemoteStore, ProjectNameOrId
from ddsc.core.d4s2 import D4S2Project
from urllib.parse import urlparse


class Settings(object):
    def __init__(self, cmdfile):
        data = json.load(cmdfile)
        self.destination = data['destination']
        self.readme_file_path = data['readme_file_path']
        self.paths = data['paths']
        share = data.get('share', {})
        self.share_dds_user_ids = share['dds_user_ids']
        self.share_auth_role = share.get('auth_role', 'project_admin')
        self.share_user_message = share.get('user_message', 'Bespin job results.')
        self.activity_settings = ActivitySettings(data['activity'])


class ActivitySettings(object):
    def __init__(self, data):
        self.name = data['name']
        self.description = data['description']
        self.started_on = data['started_on']
        self.ended_on = data['ended_on']
        self.input_file_versions_json_path = data['input_file_versions_json_path']
        self.workflow_output_json_path = data['workflow_output_json_path']


class UploadedFilesInfo(object):
    """
    Copied from https://github.com/Duke-GCB/lando/blob/76f981ebff4ae0abbabbc4461308e9e5ea0bc830/lando/worker/
    provenance.py#L58
    """
    def __init__(self, project):
        """
        Contains file_id_lookup that goes from an absolute path -> file_id for files in project
        :param project: ddsc.core.localproject.LocalProject: LocalProject that was uploaded to DukeDS
        """
        self.file_id_lookup = self._build_file_id_lookup(project)

    @staticmethod
    def _build_file_id_lookup(project):
        """
        Creates dictionary from an absolute path to a file_id
        :param project: ddsc.core.localproject.LocalProject: LocalProject that was uploaded to DukeDS
        :return: dict: local_file_path -> duke_ds_file_id
        """
        lookup = {}
        for local_file in UploadedFilesInfo._gather_files(project):
            lookup[local_file.path] = local_file.remote_id
        return lookup

    @staticmethod
    def _gather_files(project_node):
        """
        Fetch all files within project_node.
        :param project_node: container or file, if container returns children
        :return: [LocalFile]: list of files
        """
        if KindType.is_file(project_node):
            return [project_node]
        else:
            children_files = []
            for child in project_node.children:
                children_files.extend(UploadedFilesInfo._gather_files(child))
            return children_files


class DukeDSActivity(object):
    def __init__(self, dds_client, settings, uploaded_files_info):
        self.dds_client = dds_client
        self.data_service = dds_client.dds_connection.data_service
        self.activity_settings = settings.activity_settings
        self.file_id_lookup = uploaded_files_info.file_id_lookup

    def create(self):
        click.echo("Creating activity {}.".format(self.activity_settings.name))
        activity_id = self._create_activity()

        input_file_version_ids = self._get_input_file_version_ids()
        click.echo("Attaching {} used relations.".format(len(input_file_version_ids)))
        for input_file_version_id in input_file_version_ids:
            self._create_activity_used_relation(activity_id, input_file_version_id)

        output_file_paths = self._get_output_file_paths()
        click.echo("Attaching {} generated relations.".format(len(output_file_paths)))
        for output_file_path in output_file_paths:
            output_file_version_id = self._get_file_version_id_for_path(output_file_path)
            self._create_activity_generated_relation(activity_id, output_file_version_id)

    def _create_activity(self):
        resp = self.data_service.create_activity(
            self.activity_settings.name,
            self.activity_settings.description,
            self.activity_settings.started_on,
            self.activity_settings.ended_on)
        return resp.json()["id"]

    def _create_activity_used_relation(self, activity_id, file_version_id):
        self.data_service.create_used_relation(activity_id, KindType.file_str, file_version_id)

    def _create_activity_generated_relation(self, activity_id, file_version_id):
        self.data_service.create_was_generated_by_relation(activity_id, KindType.file_str, file_version_id)

    def _get_file_version_id_for_path(self, output_file_path):
        file_id = self.file_id_lookup[output_file_path]
        duke_ds_file = self.dds_client.get_file_by_id(file_id)
        return duke_ds_file.current_version['id']

    def _get_output_file_paths(self):
        file_paths = []
        with open(self.activity_settings.workflow_output_json_path, 'r') as infile:
            data = json.load(infile)
            for value in data.values():
                DukeDSActivity._recursive_add_cwl_file_paths(value, file_paths)
            return file_paths

    def _get_input_file_version_ids(self):
        with open(self.activity_settings.input_file_versions_json_path) as infile:
            data = json.load(infile)
            return [file_metadata["current_version"]["id"] for file_metadata in data["items"]]

    @staticmethod
    def _recursive_add_cwl_file_paths(dict_or_array, file_paths):
        if isinstance(dict_or_array, dict):
            if dict_or_array.get('class') == "File":
                if 'location' in dict_or_array:
                    file_location = dict_or_array['location']
                    file_path = urlparse(file_location).path
                    file_paths.append(file_path)
                if 'secondaryFiles' in dict_or_array:
                    secondary_files = dict_or_array['secondaryFiles']
                    DukeDSActivity._recursive_add_cwl_file_paths(secondary_files, file_paths)
        else:
            for elem in dict_or_array:
                DukeDSActivity._recursive_add_cwl_file_paths(elem, file_paths)


class UploadUtil(object):
    def __init__(self, cmdfile):
        self.settings = Settings(cmdfile)
        self.dds_client = DukeDSClient()
        self.dds_config = self.dds_client.dds_connection.config

    def get_or_create_project(self):
        """
        Find or create a project with the name self.settings.destination
        :return: ddsc.sdk.client.Project
        """
        project_name = self.settings.destination
        for project in self.dds_client.get_projects():
            if project.name == project_name:
                return project
        return self.dds_client.create_project(project_name, description=project_name)

    def upload_files(self, project):
        """
        Upload files from local paths to the specified project
        :param project: ddsc.sdk.client.Project: project to upload files to
        :return: UploadedFileInfo: contains details about uploaded files
        """
        project_upload = ProjectUpload(self.dds_config,
                                       ProjectNameOrId.create_from_project_id(project.id),
                                       self.settings.paths)
        click.echo(project_upload.get_differences_summary())
        if project_upload.needs_to_upload():
            click.echo("Uploading")
            project_upload.run()
        return UploadedFilesInfo(project_upload.local_project)

    def create_provenance_activity(self, uploaded_files_info):
        """
        Create a provenance activity in DukeDS API for our project.
        :param uploaded_files_info: UploadedFilesInfo: contains details about uploaded files
        """
        activity = DukeDSActivity(self.dds_client, self.settings, uploaded_files_info)
        activity.create()

    def share_project(self, project):
        """
        Share the specified project with some users.
        :param project: ddsc.sdk.client.Project: project to share
        """
        remote_store = RemoteStore(self.dds_config)
        remote_project = remote_store.fetch_remote_project_by_id(project.id)
        d4s2_project = D4S2Project(self.dds_config, remote_store, print_func=print)
        for dds_user_id in self.settings.share_dds_user_ids:
            d4s2_project.share(remote_project,
                               remote_store.fetch_user(dds_user_id),
                               force_send=True,
                               auth_role=self.settings.share_auth_role,
                               user_message=self.settings.share_user_message)

    def create_annotate_project_details_script(self, project, outfile):
        """
        Create a script to annotat a pod with details about the uploaded project
        :param project: ddsc.sdk.client.Project: project to share
        :param outfile: output file to write script into
        """
        readme_file = project.get_child_for_path(self.settings.readme_file_path)
        click.echo("Writing annotate project details script project_id:{} readme_file_id:{} to {}".format(
            project.id, readme_file.id, outfile.name))
        contents = "kubectl annotate pod $MY_POD_NAME " \
                   "project_id={} readme_file_id={}".format(project.id, readme_file.id)
        outfile.write(contents)
        outfile.close()

    def create_json_project_details_file(self, project, outfile):
        readme_file = project.get_child_for_path(self.settings.readme_file_path)
        click.echo("Writing JSON project details project_id:{} readme_file_id:{} to {}".format(
            project.id, readme_file.id, outfile.name))
        outfile.write(json.dumps({
            "project_id": project.id, "readme_file_id": readme_file.id
        }))


@click.command()
@click.argument('cmdfile', type=click.File('r'))
@click.argument('outfile', type=click.File('w'))
@click.option('--outfile-format', type=click.Choice(['annotate_script', 'json']), default='annotate_script')
def main(cmdfile, outfile, outfile_format):
    util = UploadUtil(cmdfile)
    project = util.get_or_create_project()
    uploaded_files_info = util.upload_files(project)
    util.create_provenance_activity(uploaded_files_info)
    util.share_project(project)
    if outfile_format == 'annotate_script':
        util.create_annotate_project_details_script(project, outfile)
    elif outfile_format == 'json':
        util.create_json_project_details_file(project, outfile)


if __name__ == '__main__':
    main()
