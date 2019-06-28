from __future__ import absolute_import
from datetime import date, datetime
import logging
import requests
from typing import Dict, Iterable, List, Optional, Union, Generator
import warnings

from dateutil.parser import parse
from hockeyapp.exceptions import HockeyToGusError, PageNotFoundError, AuthenticationError, BadRequestError, RateLimitedError
from hockeyapp.models import App, AppStatistic, AppVersion, Crash, CrashAnnotation, CrashReason, CrashReasonStatus, HistogramPoint, User, UserRole
import hockeyapp.budgeter


class Hockeyapp:
    # Constants
    HOCKEY_BASE_URL = "https://rink.hockeyapp.net/api/2/apps/"

    def __init__(self, hockey_token: List[str], app_public_identifier: str=None, api_token_gen=None) -> None:
        """

        :param List[str] hockey_token: A List[str] or str representing your API token(s).
                                       They look like UUIDs.
        :param app_id: Your app's ID. If this isn't passed, most of these functions won't work.
                       App_id is a 32-char hex string.
        """
        self.app_public_identifier = app_public_identifier
        self.logger = logging.getLogger(__name__)
        self.api_key_gen = api_token_gen or hockeyapp.budgeter.APITokenBudgeter(hockey_token)

    @staticmethod
    def raise_for_status(response) -> None:
        if response.status_code == 200:
            pass
        elif response.status_code == 202:
            raise RateLimitedError('API call was successful, but further requests are rate limited')
        elif response.status_code == 404:
            raise PageNotFoundError('HockeyApp could not find URL. '
                                    'Make sure App ID is correct.')
        elif response.status_code == 400:
            raise AuthenticationError('HockeyApp token is incorrect.')
        else:
            raise HockeyToGusError('Something went wrong with HockeyApp.')

    def _headers(self) -> Dict[str, str]:
        return {'content-type': 'application/json',
                'X-HockeyAppToken': next(self.api_key_gen)}

    def list_apps(self) -> List[App]:
        resp = requests.get(self.HOCKEY_BASE_URL, headers=self._headers())
        self.raise_for_status(resp)
        resp_json = resp.json()
        if resp_json['status'].lower() == 'success':
            return [App(app) for app in resp_json['apps']]
        return []

    def get_app_by_id(self,
                      app_id: int) -> Union[None, App]:
        """
        Get information about an app by its ID.
        :param app_id: Application ID. Looks like a short integer.
        :return: The Application, if found, or None
        """
        all_apps = self.list_apps()
        id_to_app = {app.id : app for app in all_apps}
        return id_to_app.get(app_id, None)

    def convert_id_to_public_identifier(self, app_id: int) -> Optional[str]:
        all_apps = self.list_apps()
        idmap = {app.id: app.public_identifier for app in all_apps}
        return idmap.get(app_id, None)

    def lookup_hockeyapp_version_id(self, app_version: str, app_versioncode: str) -> Optional[int]:
        """
        Given an app version (1.0) and version code (1234), determine the ID of the HockeyApp AppVersion.
        :param app_version:
        :param str app_versioncode: typically a build number, like an integer, but could be a sematic version string.
        :return:
        :rtype Optional[str]
        """
        all_versions = self.get_versions()
        # note we don't do an exact match for app_version, since some teams like to decorate them
        # with code names (Godzilla etc)
        matches = filter(lambda each_version: each_version.version != 'null' and
                                              each_version.version == app_versioncode and
                                              app_version in each_version.shortversion,
                         all_versions)
        first_match = next(matches)
        if first_match:
            return first_match.id
        return None

    def lookup_version_from_versioncode(self, app_versioncode: str) -> Optional[str]:
        """
        Given a VersionCode (Android=Version Code, iOS=CFBundleVersion), find the corresponding
        version.
        :param app_id:
        :param app_versioncode:
        :return:
        """
        all_versions = self.get_versions()

        # note we don't do an exact match for app_version, since some teams like to decorate them
        # with code names (Godzilla etc)
        def filter_versions(version: AppVersion) -> bool:
            try:
                return version.version != 'null' and version.version == app_versioncode
            except ValueError:
                return False

        matches = filter(filter_versions,
                         all_versions)
        try:
            first_match = next(matches)
            if first_match:
                return first_match.shortversion
        except StopIteration:
            self.logger.warning('Cannot find a version label for version code %s', app_versioncode)
        return None

    def lookup_versioncode_from_version(self, app_version: str) -> Optional[str]:
        """
        Given a Version Label (e.g. "12.0"), find the corresponding
        build number.
        Note that in HockeyApp schema, the versioncode is always an integer.
        Windows apps do not have a versioncode. They only have versions.
        :param str app_version:
        :return:
        """
        all_versions = self.get_versions()

        # note we don't do an exact match for app_version, since some teams like to decorate them
        # with code names (Godzilla etc)
        def filter_versions(version: AppVersion) -> bool:
            try:
                return version.shortversion != 'null' and version.shortversion == app_version
            except ValueError:
                return False

        matches = filter(filter_versions,
                         all_versions)
        try:
            first_match = next(matches)
            if first_match:
                return first_match.version
        except StopIteration:
            self.logger.warning('Cannot find a versioncode for version label %s', app_version)
        return None

    def list_crash_groups(self,
                          version_id: int=0,
                          sort: str='date',
                          order: str='asc',
                          page: int=1) -> Iterable[CrashReason]:
        """
        List all crash groups for an app.
        :param version_id: the Version of the app (integer)
        :param sort: How to sort the crash groups. Valid options are: date, class, number_of_crashes, last_crash_at
        :param order: Sort order. Value is either 'asc' (default) or 'desc' for descending.
        :return: Yields `CrashGroup` objects.
        """
        if version_id != 0:
            url = self.HOCKEY_BASE_URL + self.app_public_identifier + "/app_versions/ " + str(version_id) + "/crash_reasons"
        else:
            url = self.HOCKEY_BASE_URL + self.app_public_identifier + "/crash_reasons"
        params = {'page': str(page),
                  'per_page': str(50),
                  # 'symbolicated': str(1),
                  'sort': sort, # optional, sort by "date" (default), "class", "number_of_crashes",
                  #  "last_crash_at"
                  'order': order, # 'asc' for ascending, 'desc' for descending
                  }
        resp = requests.get(url, params=params, headers=self._headers())
        self.raise_for_status(resp)
        # json keys include: 'crash_reasons', 'total_entries', 'total_pages','per_page','status','current_page'
        resp_json = resp.json()
        if resp_json['status'] == 'success':
            for reason in resp_json['crash_reasons']:
                yield CrashReason(reason)
            if resp_json['current_page'] < resp_json['total_pages']:
                yield from self.list_crash_groups(version_id, sort, order, page+1)
        else:
            self.logger.warning('Unsuccessful query. Status=%s', resp_json['status'])

    def crash_group_by_id(self,
                          crash_group_id: int) -> CrashReason:
        """
        Get info about a specific crash group.
        :param int crash_group_id: The crash group identifier. It's an integer, and it can uniquely identify a
                                   crash for a specific app in a specific version.
        """
        url = self.HOCKEY_BASE_URL + self.app_public_identifier + "/crash_reasons/" + str(crash_group_id)
        resp = requests.get(url, headers=self._headers())
        self.raise_for_status(resp)
        resp_json = resp.json()
        if resp_json['status'].lower() == 'success':
            if 'file' not in resp_json['crash_reason'] or resp_json['crash_reason']['file'] is None:
                resp_json['crash_reason']['file'] = 'None'
            if 'class' not in resp_json['crash_reason']:
                resp_json['crash_reason']['class'] = None
            if 'method' not in resp_json['crash_reason']:
                resp_json['crash_reason']['method'] = None
            if 'line' not in resp_json['crash_reason']:
                resp_json['crash_reason']['line'] = None
            return CrashReason(resp_json['crash_reason'])

    def top_crashes(self,
                    app_version_id: int) -> Iterable[CrashReason]:
        """get the top crashes from the most recent builds"""
        yield from self.list_crash_groups(app_version_id, sort='number_of_crashes', order='desc')

    def list_crashes_in_a_group(self, crash_group_id: int, page: int=1) -> Iterable[Crash]:
        """
        get number of crash reports in group, version id, and build name to query.
        """
        url = self.HOCKEY_BASE_URL + self.app_public_identifier + "/crash_reasons/" + str(crash_group_id)
        params = {'page': page}
        resp = requests.get(url, params=params, headers=self._headers())
        self.raise_for_status(resp)
        resp_json = resp.json()
        if resp_json['status'] == 'success':
            for crash in resp_json['crashes']:
                yield Crash(crash)
            if resp_json['current_page'] < resp_json['total_pages']:
                yield from self.list_crashes_in_a_group(crash_group_id, page + 1)

    # get stack trace log - get subject
    def fetch_stack_trace(self, crash_id: int) -> str:
        url = self.HOCKEY_BASE_URL + self.app_public_identifier + "/crashes/" + str(crash_id)
        params = {'format': 'log'}
        resp = requests.get(url, params=params, headers=self._headers())
        self.raise_for_status(resp)
        return resp.text

    # get stack trace log - get subject
    def fetch_crash_description(self, crash_id: int) -> str:
        url = self.HOCKEY_BASE_URL + self.app_public_identifier + "/crashes/" + str(crash_id)
        params = {'format': 'text'}
        resp = requests.get(url, params=params, headers=self._headers())
        self.raise_for_status(resp)
        return resp.text

    def histogram(self,
                  start_date: date,
                  end_date: date,
                  app_version: int=0,
                  crash_reason: int=0) -> Iterable[HistogramPoint]:
        """
        Get a histogram of the number of crashes between two given dates.
        For an app (don't pass app_version or crash_reason), or one or the other.

        The number of days between `start_date` and `end_date` should not be larger than 30 days.
        :param start_date:
        :param end_date:
        :param app_version:
        :param crash_reason:
        :return:
        """
        if app_version != 0 and crash_reason != 0:
            raise RuntimeError('can\'t specify both app version and crash reason at the same time. pick one')
        if app_version != 0:
            url = self.HOCKEY_BASE_URL + self.app_public_identifier + '/app_versions/' + str(app_version) + '/crashes/histogram'
        elif crash_reason != 0:
            url = self.HOCKEY_BASE_URL + self.app_public_identifier + '/crash_reasons/' + str(crash_reason) + '/histogram'
        else:
            url = self.HOCKEY_BASE_URL + self.app_public_identifier + '/crashes/histogram'
        params = {'start_date': start_date.strftime('%Y-%m-%d'),
                  'end_date': end_date.strftime('%Y-%m-%d')}
        resp = requests.get(url, params=params, headers=self._headers())
        self.raise_for_status(resp)
        resp_json = resp.json()
        if resp_json['status'] == 'success':
            for histogram_point in resp_json['histogram']:
                yield HistogramPoint(point_date=histogram_point[0],
                                     occurrences=histogram_point[1])

    def get_annotation(self, crash_reason_id: int) -> Optional[CrashAnnotation]:
        """
        Retrieve the annotation of a crash group

        :param crash_reason_id:
        :return: A namedtuple `CrashAnnotation`
        """
        # {
        #  "status": "success",
        #  "crash_annotations": [
        #   {
        #     "id": 192693,
        #     "crash_reason_id": 136174811,
        #     "text": "some text",
        #     "created_at": "2016-09-19T16:40:36Z",
        #     "updated_at": "2016-09-19T16:40:36Z"
        #   }
        #  ]
        # }
        url = self.HOCKEY_BASE_URL + self.app_public_identifier + "/crash_reasons/" + str(crash_reason_id) + "/crash_annotations"
        resp = requests.get(url, headers=self._headers())
        self.raise_for_status(resp)
        resp_data = resp.json()
        # if there is none, resp_data['status'] == 'empty'
        if 'status' in resp_data and resp_data['status'] == 'success':
            if len(resp_data['crash_annotations']) > 0:
                first = resp_data['crash_annotations'][0]
                return CrashAnnotation(id=first['id'],
                                       crash_reason_id=first['crash_reason_id'],
                                       text=first['text'],
                                       created_at=parse(first['created_at']),
                                       updated_at=parse(first['updated_at']))
        return None

    def set_annotation(self, crash_reason_id: int, text: Optional[str]) -> None:
        url = self.HOCKEY_BASE_URL + self.app_public_identifier + "/crash_reasons/" + str(crash_reason_id) + "/crash_annotations"
        if text:
            resp = requests.post(url, headers=self._headers(), params={'text':text})
        else:
            resp = requests.delete(url, headers=self._headers())
        self.raise_for_status(resp)
        return None

    def remove_annotation(self, crash_reason_id: int) -> None:
        warnings.warn('Call to deprecated function {}.'.format(__name__), category = DeprecationWarning)
        return self.set_annotation(crash_reason_id, text=None)

    def set_status_and_ticket(self,
                              crash_reason_id: int,
                              ticket_status: CrashReasonStatus,
                              ticket_url: str) -> None:
        url = self.HOCKEY_BASE_URL + self.app_public_identifier + "/crash_reasons/" + str(crash_reason_id)
        params = {'status': str(ticket_status.value),
                  'ticket_url': ticket_url}
        resp = requests.post(url, headers=self._headers(), params=params)
        self.raise_for_status(resp)
        return None

    def get_versions(self) -> Iterable[AppVersion]:
        # GET /api/2/apps/APP_ID/app_versions
        # Returns up to 500 on the first page (!!), newest first?
        url = self.HOCKEY_BASE_URL + self.app_public_identifier + "/app_versions"
        print("URL: ", url)
        print("Headers: ", self._headers())
        resp = requests.get(url, headers=self._headers())
        print("Response: ", resp)
        self.raise_for_status(resp)
        resp_json = resp.json()
        if resp_json['status'] != 'success':
            raise BadRequestError(resp_json['status'])

        for version in resp_json['app_versions']:
            yield AppVersion(version)

    def get_versions_statistics(self) -> Iterable[AppStatistic]:
        # GET /api/2/apps/APP_ID/app_versions
        # Returns up to 500 on the first page (!!), newest first?
        url = self.HOCKEY_BASE_URL + self.app_public_identifier + "/statistics"
        resp = requests.get(url, headers=self._headers())
        self.raise_for_status(resp)
        resp_json = resp.json()
        if resp_json['status'] == 'success':
            for version in resp_json['app_versions']:
                yield AppStatistic(version)

    def get_version_statistic(self, app_version: str) -> AppStatistic:
        match = filter(lambda stat: stat.version == app_version, self.get_versions_statistics())
        return next(match)

    def set_retention_policy(self, policy: Union[str,int]) -> None:
        """
        Set the data retention policy for this application.

        :param policy: one of "28", "90" [default], or "unlimited"
        :return: None
        :rtype None
        """
        url = self.HOCKEY_BASE_URL + self.app_public_identifier + '/retention'

        resp = requests.put(url, headers=self._headers(), params={'retention_days': str(policy)})
        self.raise_for_status(resp)
        resp_json = resp.json()
        assert resp_json['status'] == 'success'

    def invite_user_to_app(self, email: str,
                           first_name: str=None,
                           last_name: str=None,
                           message: str=None,
                           role: UserRole=UserRole.tester,
                           tags: List[str]=[]) -> None:
        """
        Invite a user to an Application.
        :param email: Required.
        :param first_name: First name. Only used if the user has no email record already on file at Hockeyapp.
        :param last_name: Last name. Only used if the user has no email record already on file at Hockeyapp.
        :param message: included in the email notification.
        :param role: The role of the user. See `UserRole`
        :param tags: tags to apply to the new user.
        :return:
        """
        url = self.HOCKEY_BASE_URL + self.app_public_identifier + '/app_users'
        params = {
            'email': email,
            'role': role.value
        }
        if first_name is not None:
            params['first_name'] = first_name
        if last_name is not None:
            params['last_name'] = last_name
        if message is not None:
            params['message'] = message
        if len(tags) > 0:
            params['tags'] = ','.join(tags)
        resp = requests.post(url, headers=self._headers(), params=params)
        self.raise_for_status(resp)
        return None

    def get_app_users(self, app_public_identifier: str) -> Generator[User, None, None]:
        """
        gets all the users assigned to the given app
        """
        url = '{}{}/app_users'.format(self.HOCKEY_BASE_URL, app_public_identifier)
        resp = requests.get(url, headers=self._headers())
        # self.raise_for_status(resp)
        resp_json = resp.json()

        # if app has users, generate User objects
        if resp_json and 'app_users' in resp_json:
            for user in resp_json['app_users']:
                user['app_id'] = app_public_identifier
                yield User(user)

    def delete_app_user(self, app_public_identifier: str, user_app_id: int) -> None:
        """
        remove a user from the given app
        """
        url = '{}{}/app_users/{}'.format(self.HOCKEY_BASE_URL, app_public_identifier, user_app_id)
        resp = requests.delete(url, headers=self._headers())
        self.raise_for_status(resp)
