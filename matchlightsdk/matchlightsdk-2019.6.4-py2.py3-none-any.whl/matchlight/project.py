"""An interface for creating and retrieving Matchlight projects."""
from __future__ import absolute_import

import datetime
try:
    import collections.abc as collections_abc
except ImportError:
    import collections as collections_abc

import json

import six

import matchlight.error
import matchlight.utils


class Project(object):
    """A Matchlight Fingerprint Monitoring Project.

    Attributes:
        name (:obj:`str`): The project name.
        project_type (:obj:`str`): The project type.
        upload_token (:obj:`str`): The project upload token.
        last_date_modified (:obj:`int`): The Unix timestamp of the last
            modification.
        number_of_records (:obj:`int`): The number of total records in
            the project.
        number_of_unseen_alerts (:obj:`int`): The number of unread
            alerts.

    """

    def __init__(self, name, project_type, upload_token,
                 last_date_modified, number_of_records,
                 number_of_unseen_alerts):
        """Initializes a new project.

        Args:
            name (:obj:`str`): The project name.
            project_type (:obj:`str`): The project type.
            upload_token (:obj:`str`): The project upload token.
            last_date_modified (:obj:`int`): The Unix timestamp of the
                last modification.
            number_of_records (:obj:`int`): The number of total records
                in the project.
            number_of_unseen_alerts (:obj:`int`): The number of unread
                alerts.

        """
        self.name = name
        self.project_type = project_type
        self.upload_token = upload_token
        self.last_date_modified = last_date_modified
        self.number_of_records = number_of_records
        self.number_of_unseen_alerts = number_of_unseen_alerts

    @classmethod
    def from_mapping(cls, mapping):
        """Creates a new project instance from the given mapping."""
        return cls(
            name=mapping['project_name'],
            project_type=mapping['project_type'],
            upload_token=mapping['project_upload_token'],
            last_date_modified=mapping['last_date_modified'],
            number_of_records=mapping['number_of_records'],
            number_of_unseen_alerts=mapping['number_of_unseen_alerts'],
        )

    @property
    def last_modified(self):
        """:class:`datetime.datetime`: The last modified timestamp."""
        return datetime.datetime.fromtimestamp(self.last_date_modified)

    @property
    def details(self):
        """:obj:`dict`: Returns the project details as a mapping."""
        return {
            'name': self.name,
            'project_type': self.project_type,
            'upload_token': self.upload_token,
            'last_date_modified': self.last_date_modified,
            'number_of_records': self.number_of_records,
            'number_of_unseen_alerts': self.number_of_unseen_alerts,
        }

    def __repr__(self):  # pragma: no cover
        return '<Project(name="{}", project_type="{}")>'.format(
            self.name, self.project_type)


class ProjectMethods(collections_abc.Iterable):
    """Provides methods for interfacing with the feeds API.

    Examples:
        Get project from upload token::
            >>> ml.projects.get('3ef85448c-d244-431e-a207-cf8d37ae3bfe')
            <Project(name='Customer Database May 2016',
            project_type='pii')>

        Filter on project types::
            >>> ml.projects.filter(project_type='pii')
            [<Project(name='...', project_type='pii'),
            <Project(name='...', project_type='pii'),
            <Project(name='...', project_type='pii')]
            >>> ml.projects.filter()
            [<Project(name='...', project_type='pii'),
            <Project(name='...', project_type='document'),
            <Project(name='...', project_type='source_code')]

        Create a new project::
            >>> project = ml.projects.add(
            ... name='Super secret algorithm',
            ... project_type='source_code')
            >>> project
            <Project(name='Super Secret Algorithm', type='source_code')>

        Edit a project::
            >>> project = ml.projects.edit(project,
            ... 'Updated Super Secret Algorithm')
            >>> project
            <Project(name='Updated Super Secret Algorithm',
            type='source_code'>

        Delete a project::
            >>> ml.projects.delete(project)
            >>> ml.projects.get(project.upload_token)
            None

        Get project details::
            >>> executives = ml.projects.add("Executive List 2016", "pii")
            >>> executives.details
            {'last_date_modified': 1472671877,
            'number_of_records': 0,
            'number_of_unseen_alerts': 0,
            'name': 'Executive List 2016',
            'project_type': 'pii',
            'upload_token': 'a1c7140a-17e5-4016-8f0a-ef4aa87619ce'}

    """

    def __init__(self, ml_connection):  # noqa: D205,D400
        """Initializes a project interface with the given Matchlight
        connection.

        Args:
            ml_connection (:class:`~.Connection`): A Matchlight
                connection instance.

        """
        self.conn = ml_connection

    def all(self):
        """Returns all projects associated with the account."""
        return self.filter()

    def add(self, name, project_type):
        """Creates a new project or group.

        Arguments:
            name (:obj:`str`): The name of the project to be created.
            project_type (:obj:`str`): The type of project to be
                created.

        Returns:
            :class:`~.Project` : Created project with upload token.

        """
        data = json.dumps({'name': name, 'type': project_type})
        r = self.conn.request('/project/add', data=data)
        return Project.from_mapping(r.json()['data'])

    def delete(self, project):
        """Deletes a project and all associated records.

        Args:
            project (:class:`~.Project` or :obj:`str`): The project
                object or upload token to be deleted.

        """
        if isinstance(project, six.string_types):
            upload_token = project
        else:
            upload_token = project.upload_token
        self.conn.request('/project/{upload_token}/delete'.format(
            upload_token=upload_token), data='{}')

    def edit(self, project, updated_name):
        """Renames a project.

        Arguments:
            project (:class:`~.Project` or :obj:`str`): A project
                instance or upload token.
            updated_name (:obj:`str`): New project name.

        Returns:
            :class:`~.Project`: Updated project instance with new name.

            Note that this method mutates any project instances passed.

        """
        if not isinstance(project, Project):
            project = self.get(project)
        data = json.dumps({'name': updated_name})
        self.conn.request('/project/{}/edit'.format(
            project.upload_token), data=data)
        project.name = updated_name
        return project

    def filter(self, project_type=None):
        """Returns a list of projects associated with the account.

        Providing an optional **project_type** keyword argument will
        only return projects of the specified type: ``source_code``,
        ``document`` or ``pii``.

        Arguments:
            project_type (:obj:`str`, optional): The project type to
                filter on. If not provided or ``None``, returns all
                projects.

        Returns:
            list of :class:`~.Project`: List of filtered projects.

        """
        response = self.conn.request('/projects', params={
            'project_type': project_type})
        projects = []
        for payload in response.json().get('data', []):
            if project_type and payload['project_type'] != project_type:
                continue
            projects.append(Project.from_mapping(payload))
        return projects

    def get(self, upload_token):
        """Returns a project by the given upload token.

        Args:
            upload_token (:obj:`str`): The project upload token.

        Returns:
           :class: `~.Project`: A Matchlight project.

        """
        try:
            response = self.conn.request('/project/{}'.format(upload_token))
            return Project.from_mapping(response.json())
        # for consistency since records.get() returns None if not found.
        except matchlight.error.APIError as err:
            if err.args[0] == 404:
                return
            else:
                raise

    def __iter__(self):
        return (project for project in self.filter())
