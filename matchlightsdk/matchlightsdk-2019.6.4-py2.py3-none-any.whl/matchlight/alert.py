"""An interface for creating and retrieving alerts in Matchlight."""
from __future__ import absolute_import

import calendar
import datetime
import json

import matchlight.error


__all__ = (
    'Alert',
    'AlertMethods',
)


class Alert(object):
    """Represents an alert.

    Attributes:
        id (:obj:`str`): A 128-bit UUID.
        number (:obj:`int`): The account specific alert number.
        type (:obj:`str`): The type of the associated Record.
        url (:obj:`str`): The url where the match was found.
        url_metadata (:obj:`dict`): additional information about the url.
        ctime (:obj:`int`): A Unix timestamp of the alert creation
            timestamp.
        mtime (:obj:`int`): A Unix timestamp of the alert last
            modification date timestamp.
        seen (:obj:`bool`): User specific flag.
        archived (:obj:`bool`): User specific flag.
        upload_token (:obj:`str`): The upload_token of the associated Project.
        details (:obj:`dict`): Additional information about the Alert.
        project_name (:obj:`str`): The name of the associated Project
        record_name (:obj:`str`): The name of the associated Record.

    """

    def __init__(self, id, number, type, url, url_metadata, ctime, mtime, seen,
                 archived, upload_token, details, project_name, record_name):
        """Initializes a new alert.

        Args:
            id (:obj:`str`): A 128-bit UUID.
            number (:obj:`int`): The account specific alert number.
            type (:obj:`str`): The type of the associated Record.
            url (:obj:`str`): The url where the match was found.
            ctime (:obj:`int`): A Unix timestamp of the
                alert creation timestamp.
            mtime (:obj:`int`): A Unix timestamp of the
                alert last modification date timestamp.
            seen (:obj:`bool`): User specific flag.
            archived (:obj:`bool`): User specific flag.
            upload_token (:obj:`str`): The upload_token of the associated
                record.
            details (:obj:`dict`): details about the Alert.
            project_name (:obj:`str`): The name of the associated Project
            record_name (:obj:`str`): The name of the associated Record.

        """
        self.id = id
        self.number = number
        self.type = type
        self.url = url
        self.url_metadata = url_metadata
        self.ctime = ctime
        self.mtime = mtime
        self.seen = seen
        self.archived = archived
        self.upload_token = upload_token
        self.details = details
        self.project_name = project_name
        self.record_name = record_name

    @classmethod
    def from_mapping(cls, mapping):
        """Creates a new alert instance from the given mapping."""
        return cls(
            id=mapping['id'],
            number=mapping['alert_number'],
            type=mapping['type'],
            url=mapping['url'],
            url_metadata=mapping['url_metadata'],
            ctime=mapping['ctime'],
            mtime=mapping['mtime'],
            seen=True if mapping['seen'] == 'true' else False,
            archived=True if mapping['archived'] == 'true' else False,
            upload_token=mapping['upload_token'],
            details=mapping['details'],
            project_name=mapping['project_name'],
            record_name=mapping['asset_name']
        )

    @property
    def last_modified(self):
        """:class:`datetime.datetime`: The last modified timestamp."""
        if self.mtime is None:
            return None
        return datetime.datetime.fromtimestamp(self.mtime)

    @property
    def date(self):
        """:class:`datetime.datetime`: The date created timestamp."""
        if self.ctime is None:
            return None
        return datetime.datetime.fromtimestamp(self.ctime)

    @property
    def score(self):
        """:obj:`int`: Represents how much of the record appeared on the page.

        Scores range from 1 to 800, with 800 representing that the entire
        record was found on the page. PII records will always have a score
        of 800.
        """
        if self.type == 'pii':
            return 800
        if self.type == 'document':
            return self.details['document'].get('score', None)
        if self.type == 'source_code':
            return self.details['source_code'].get('score', None)

    @property
    def fields(self):
        """:obj:`list`: PII records will match on one or more 'fields'."""
        if self.type == 'pii':
            return self.details['pii'].get('fields', [])

        return None

    def __repr__(self):  # pragma: no cover
        return '<Alert(number="{}", id="{}")>'.format(
            self.number,
            self.id
        )


class AlertMethods(object):
    """Provides methods for interfacing with the alerts API."""

    def __init__(self, ml_connection):  # noqa: D205,D400
        """Initializes an alerts interface with the given Matchlight
        connection.

        Args:
            ml_connection (:class:`~.Connection`): A Matchlight
                connection instance.

        """
        self.conn = ml_connection

    def filter(self, limit, seen=None, archived=None, project=None,
               record=None, last_modified=None, last_alert=None):
        """Returns a list of alerts.

        Providing a **limit** keyword argument will limit the number of alerts
        returned. The request may time out if this is set too high, a limit of
        50 is recomended to avoid timeouts.

        Providing an optional **seen** keyword argument will only
        return alerts that match that property

        Providing an optional **archived** keyword argument will only
        return alerts that match that property

        Providing an optional **project** keyword argument will only
        return alerts that are associated with a specific project.

        Providing an optional **record** keyword argument will only
        return alerts that are associated with a specific record.

        Providing an optional **last_modified** keyword argument will only
        return alerts with a last_modifed less than the argument.

        Providing an optional **last_alert** keyword argument will only return
        results after this Alert

        Examples:
            Request all unseen alerts::

                >>> ml.alerts.filter(seen=False, limit=50)
                [<Alert(number="1024",
                id="625a732ad0f247beab18595z951c2088a3")>,
                Alert(number="1025",
                id="f9427dd5a24d4a98b2069004g04c2977")]

            Request all alerts for a project::

                >>> my_project
                <Project(name="Super Secret Algorithm", type="source_code")>
                >>> ml.alerts.filter(project=my_project, limit=50)
                [<Alert(number="1024",
                id="625a732ad0f247beab18595z951c2088a3")>,
                Alert(number="1025",
                id="f9427dd5a24d4a98b2069004g04c2977")]

            Request sets of alerts using pagination::

                >>> ml.alerts.filter(limit=50)
                [<Alert(number="1027",
                id="625a732ad247beab18595z951c2088a3")>,
                Alert(number="1026",
                id="f9427dd5a24d4a98b2069004g04c2977")...
                >>> ml.alerts.filter(limit=50, last_alert=50)
                [<Alert(number="977",
                id="59d5a791g8d4436aaffe64e4b15474a5")>,
                Alert(number="976",
                id="6b1001aaec5a48f19d17171169eebb56")...

        Args:
            limit (:obj:`int`):
                Don't return more than this number of alerts.
            seen (:obj:`bool`, optional):
            archived (:obj:`bool`, optional):
            project (:class:`~.Project`, optional): a project object.
                Defaults to all projects if not specified.
            record (:class:`~.Record`, optional): a record object.
                Defaults to all projects if not specified.
            last_modified (:obj:`datetime`, optional):
            last_alert (:obj:`int`):
                Only return Alerts after this one.

        Returns:
            :obj:`list` of :class:`~.Alert`: List of alerts that
                are associated with a project.

        """
        if seen is not None:
            seen_int = 1 if seen is True else 0
        else:
            seen_int = None

        if archived is not None:
            archived_int = 1 if archived is True else 0
        else:
            archived_int = None

        if project is not None:
            upload_token = project.upload_token
        else:
            upload_token = None

        if record is not None:
            record_id = record.id
        else:
            record_id = None

        if last_modified is not None:
            mtime = calendar.timegm(last_modified.timetuple())
        else:
            mtime = None

        response = self.conn.request(
            '/alerts',
            params={
                'limit': limit,
                'seen': seen_int,
                'archived': archived_int,
                'upload_token_filter': upload_token,
                'record_id_filter': record_id,
                'mtime': mtime,
                'last_alert': last_alert
            }
        )
        alerts = []
        for payload in response.json().get('alerts', []):
            alerts.append(Alert.from_mapping(payload))
        return alerts

    def edit(self, alert_id, seen=None, archived=None):
        """Edits an alert.

        Example:
            Archive an alert::

                >>> alert
                <Alert(number=1024,
                id="0760570a2c4a4ea68d526f58bab46cbd")>
                >>> ml.alerts.edit(alert, archived=True)
                {
                    'seen': True,
                    'archived': True
                }

        Arguments:
            alert (:obj:`str`): An alert id.
            seen (:obj:`bool`, optional):
            archived (:obj:`bool`, optional):

        Returns:
            :obj:`dict`: Updated alert metadata.

        """
        if isinstance(alert_id, Alert):
            alert_id = alert_id.id

        data = {}
        if seen is not None:
            data['seen'] = seen

        if archived is not None:
            data['archived'] = archived

        response = self.conn.request(
            '/alert/{}/edit'.format(alert_id),
            data=json.dumps(data)
        )
        response = response.json()
        return {
            'seen': response['seen'],
            'archived': response['archived']
        }

    def get_details(self, alert_id):
        """Returns details of an alert by the given alert ID.

        Args:
            alert_id (:obj:`str`): The alert identifier.

        Returns:
           :obj:`dict`: map of the alert details.

        """
        if isinstance(alert_id, Alert):
            alert_id = alert_id.id

        try:
            response = self.conn.request('/alert/{}/details'.format(alert_id))
            return response.json()
        except matchlight.error.APIError as err:
            if err.args[0] == 404:
                return
            else:
                raise
