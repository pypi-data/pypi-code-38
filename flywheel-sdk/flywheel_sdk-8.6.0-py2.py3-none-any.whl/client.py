import json
import os
import sys

from .util import params_to_dict
from .flywheel import Flywheel
from .view_builder import ViewBuilder

def get_api_key_from_cli(path):
    try:
        with open(path) as fp:
            api_key = json.load(fp).get('key')
    except FileNotFoundError:
        raise Exception('Must login with flywheel command-line interface')
    return api_key

class Client(object):
    def __init__(self, api_key=None, **kwargs):
        if not api_key:
            api_key = get_api_key_from_cli(os.path.expanduser('~/.config/flywheel/user.json'))

        self._fw = Flywheel(api_key, **kwargs)

    def add_user(self, *args, **kwargs):  # noqa: E501
        """Add a new user"""
        body = params_to_dict('add_user', args, kwargs)
        return self._fw.add_user(body)

    def add_group(self, *args, **kwargs):
        """Add a group"""
        body = params_to_dict('add_group', args, kwargs)
        return self._fw.add_group(body)

    def add_collection(self, *args, **kwargs):
        """Create a collection"""
        body = params_to_dict('add_collection', args, kwargs)
        return self._fw.add_collection(body, **kwargs)

    def add_gear(self, gear_name, body, **kwargs):
        """Create or update a gear.

        If no existing gear is found, one will be created Otherwise, the specified gear will be updated

        :param str gear_name: Name of the gear to interact with (required)
        :param GearDoc body: (required)
        :return: CollectionNewOutput
        """
        return self._fw.add_gear(gear_name, body, **kwargs)

    def add_job(self, body, **kwargs):
        """Add a job

        :param Job body: (required)
        :return: CommonObjectCreated
        """
        return self._fw.add_job(body, **kwargs)

    def get_config(self, **kwargs):
        """Return public Scitran configuration information

        :return: ConfigOutput
        """
        return self._fw.get_config(**kwargs)

    def get_gear(self, gear_id, **kwargs):
        """Return a gear referenced by gear_id

        :param str gear_id: (required) The id of the gear to lookup
        :return: Gear
        """
        return self._fw.get_gear(gear_id, **kwargs)

    def get_version(self, **kwargs):
        """Get server and database schema version info

        :return: VersionOutput
        """
        return self._fw.get_version(**kwargs)

    def get_current_user(self, **kwargs):
        """Get current logged-in user

        :return: User
        """
        return self._fw.get_current_user(**kwargs)

    def get_modality(self, modality_id, **kwargs):
        """Get a modality's classification specification

        :param str modality_id: (required)
        :return: Modality
        """
        return self._fw.get_modality(modality_id, **kwargs)

    def get(self, id, **kwargs):
        """Retrieve the specified object by id.

        Objects that can be retrieved in this way are:
            group, project, session, subject, acquisition, analysis and collection

        :param str id: The id of the object to retrieve
        :return: ContainerOutput
        """
        return self._fw.get(id, **kwargs)

    def resolve(self, path):
        """Perform a path based lookup of nodes in the Flywheel hierarchy.

        :param str path: (required) The path to resolve
        :return: ResolverOutput
        """
        return self._fw.resolve(path)

    def lookup(self, path):
        """Perform a path based lookup of a single node in the Flywheel hierarchy.

        :param str path: (required) The path to resolve
        :return: ResolverOutput
        """
        return self._fw.lookup(path)

    def file_url(self, path):
        """Perform a path based lookup of a file in the Flywheel hierarchy, and return a single-use download URL.

        :param str path: (required) The path to resolve
        :return: The file URL if found, otherwise raises an error
        """
        return self._fw.file_url(path)

    def download_tar(self, containers, dest_file, include_types=None, exclude_types=None):
        """Download the given set of containers as a tarball to dest_file.

        Supports downloading Projects, Sessions, Acquisitions and/or Analyses.

        :param containers: (required) The container, or list of containers to download.
        :param str dest_file: (required) The destination file on disk
        :param list include_types: The optional list of types to include in the download (e.g. ['nifti'])
        :param list exclude_types: The optional list of types to exclude from the download (e.g. ['dicom'])
        :return: A summary of the download
        """
        return self._fw.download_tar(containers, dest_file, include_types=include_types, exclude_types=exclude_types)

    @property
    def users(self):
        """Returns the users finder object"""
        return self._fw.users

    @property
    def groups(self):
        """Returns the groups finder object"""
        return self._fw.groups

    @property
    def projects(self):
        """Returns the projects finder object"""
        return self._fw.projects

    @property
    def subjects(self):
        """Returns the subjects finder object"""
        return self._fw.subjects

    @property
    def sessions(self):
        """Returns the sessions finder object"""
        return self._fw.sessions

    @property
    def acquisitions(self):
        """Returns the acquisitions finder object"""
        return self._fw.acquisitions

    @property
    def jobs(self):
        """Returns the jobs finder object"""
        return self._fw.jobs

    @property
    def gears(self):
        """Returns the gears finder object"""
        return self._fw.gears

    @property
    def collections(self):
        """Returns the collections finder object"""
        return self._fw.collections

    def View(self, **kwargs):
        """Short-hand for flywheel.ViewBuilder(\*\*kwargs).build()

        :param kwargs: The arguments to pass directly to ViewBuilder
        :return: The built data view
        """
        return ViewBuilder(**kwargs).build()

    def print_view_columns(self, file=sys.stdout):
        """Print a list of column aliases that can be used in data views.

        :param file-like file: The file to print to
        """
        return self._fw.print_view_columns(file=file)

    def read_view_data(self, view, container_id, decode=True, **kwargs):
        """Execute a data view against container, and return a file-like object that can be streamed.

        :param view: The view id or DataView object to execute.
        :type view: str or DataView
        :param str container_id: The id of the container to execute the view against
        :param bool decode: Whether or not to decode the stream to utf-8 (default is true)
        :param kwargs: Additional arguments to pass to the evaluate_view call. (e.g. format='csv')
        :return: A file-like object where the contents can be read
        """
        return self._fw.read_view_data(view, container_id, decode=decode, **kwargs)

    def read_view_dataframe(self, view, container_id, opts=None, **kwargs):
        """Execute a data view against container, and return a DataFrame.

        NOTE: This requires that the pandas module be installed on the system.

        :param view: The view id or DataView object to execute.
        :type view: str or DataView
        :param str container_id: The id of the container to execute the view against
        :param object opts: Additional options to pass to the pandas read_json function
        :param kwargs: Additional arguments to pass to the evaluate_view call.
        :return: A pandas DataFrame
        """
        return self._fw.read_view_dataframe(view, container_id, opts=opts, **kwargs)


    def save_view_data(self, view, container_id, dest_file, **kwargs):
        """Execute a data view against container, and save the results to disk.

        :param view: The view id or DataView object to execute.
        :type view: str or DataView
        :param str container_id: The id of the container to execute the view against
        :param str dest_file: The destination file path
        :param kwargs: Additional arguments to pass to the evaluate_view call. (e.g. format='csv')
        """
        return self._fw.save_view_data(view, container_id, dest_file, **kwargs)

    def __getattr__(self, name):
        # By default return flywheel attributes, but don't auto-complete them
        return getattr(self._fw, name)
