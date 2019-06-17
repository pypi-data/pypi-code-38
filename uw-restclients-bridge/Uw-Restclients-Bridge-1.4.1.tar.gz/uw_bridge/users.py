"""
Interacte with Bridge Users API.
You only need a single Users object in your app.
"""

from datetime import datetime
import json
import logging
import re
from dateutil.parser import parse
from restclients_core.exceptions import InvalidNetID
from uw_bridge.models import BridgeUser, BridgeCustomField, BridgeUserRole
from uw_bridge.custom_fields import CustomFields
from uw_bridge.user_roles import UserRoles
from uw_bridge import (
    get_resource, patch_resource, post_resource, delete_resource)


logger = logging.getLogger(__name__)
ADMIN_URL_PREFIX = "/api/admin/users"
AUTHOR_URL_PREFIX = "/api/author/users"
INCLUDES = "includes%5B%5D="
CUSTOM_FIELD = "{0}custom_fields".format(INCLUDES)
COURSE_SUMMARY = "{0}course_summary".format(INCLUDES)
MANAGER = "{0}manager".format(INCLUDES)
PAGE_MAX_ENTRY = "limit=1000"
RESTORE_SUFFIX = "restore"


class Users:

    def __init__(self):
        self.custom_fields = CustomFields()
        self.user_roles = UserRoles()

    def _add_custom_field_to_url(self, base_url, no_custom_fields):
        if no_custom_fields is True:
            return base_url
        return "{0}?{1}".format(base_url, CUSTOM_FIELD)

    def admin_id_url(self, bridge_id, no_custom_fields=True):
        url = ADMIN_URL_PREFIX
        if bridge_id:
            url = "{0}/{1:d}".format(url, bridge_id)
        return self._add_custom_field_to_url(url, no_custom_fields)

    def admin_uid_url(self, uwnetid, no_custom_fields=True):
        url = ADMIN_URL_PREFIX
        if uwnetid is not None:
            url = "{0}/uid%3A{1}%40uw%2Eedu".format(url, uwnetid)
        return self._add_custom_field_to_url(url, no_custom_fields)

    def author_id_url(self, bridge_id, no_custom_fields=True):
        url = AUTHOR_URL_PREFIX
        if bridge_id:
            url = "{0}/{1:d}".format(url, bridge_id)
        return self._add_custom_field_to_url(url, no_custom_fields)

    def author_uid_url(self, uwnetid, no_custom_fields=True):
        url = AUTHOR_URL_PREFIX
        if uwnetid is not None:
            url = "{0}/uid%3A{1}%40uw%2Eedu".format(url, uwnetid)
        return self._add_custom_field_to_url(url, no_custom_fields)

    def add_user(self, bridge_user):
        """
        Add the given bridge_user
        :param bridge_user: the BridgeUser object to be created
        Return the BridgeUser object created
        """
        url = self.admin_uid_url(None)
        body = json.dumps(bridge_user.to_json_post(), separators=(',', ':'))
        resp = post_resource(url, body)
        return self._get_obj_from_list(
            "add_user ({0})".format(bridge_user),
            self._process_json_resp_data(resp, no_custom_fields=True))

    def _upd_uid_req_body(self, new_uwnetid):
        return "{0}{1}@uw.edu{2}".format(
            '{"user":{"uid":"', new_uwnetid, '"}}')

    def change_uid(self, bridge_id, new_uwnetid, no_custom_fields=True):
        """
        :param bridge_id: integer
        :param no_custom_fields: specify if you want custom_fields
                                 in the response.
        Return a BridgeUser object
        """
        url = self.author_id_url(bridge_id, no_custom_fields=no_custom_fields)
        resp = patch_resource(url, self._upd_uid_req_body(new_uwnetid))
        return self._get_obj_from_list(
            "change_uid({0})".format(new_uwnetid),
            self._process_json_resp_data(resp,
                                         no_custom_fields=no_custom_fields))

    def replace_uid(self, old_uwnetid, new_uwnetid, no_custom_fields=True):
        """
        :param old_uwnetid, new_uwnetid: UwNetID strings
        :param no_custom_fields: specify if you want custom_fields
                                 in the response.
        Return a BridgeUser object
        """
        url = self.author_uid_url(old_uwnetid,
                                  no_custom_fields=no_custom_fields)
        resp = patch_resource(url, self._upd_uid_req_body(new_uwnetid))
        return self._get_obj_from_list(
            "replace_uid({0}->{1})".format(old_uwnetid, new_uwnetid),
            self._process_json_resp_data(resp,
                                         no_custom_fields=no_custom_fields))

    def delete_user(self, uwnetid):
        """
        Return True when the HTTP repsonse status is 204 -
        the user is deleted successfully
        """
        resp = delete_resource(self.admin_uid_url(uwnetid))
        return resp.status == 204

    def delete_user_by_id(self, bridge_id):
        """
        :param bridge_id: integer
        Return True when the HTTP repsonse status is 204 -
        the user is deleted successfully
        """
        resp = delete_resource(self.admin_id_url(bridge_id))
        return resp.status == 204

    def _add_includes_to_url(self, url,
                             include_manager,
                             include_course_summary):
        if include_course_summary:
            url = "{0}&{1}".format(url, COURSE_SUMMARY)
        if include_manager:
            url = "{0}&{1}".format(url, MANAGER)
        return url

    def get_user(self, uwnetid,
                 include_course_summary=True,
                 include_manager=True):
        """
        :param include_course_summary: specify if you want course
                                       data in the response.
        :param include_manager: specify if you want manager data
                                in the response.
        Return a BridgeUser object
        """
        url = self._add_includes_to_url(
            self.author_uid_url(uwnetid, no_custom_fields=False),
            include_manager, include_course_summary)
        resp = get_resource(url)
        return self._get_obj_from_list(
            "get_user by netid('{0}')".format(uwnetid),
            self._process_json_resp_data(resp))

    def get_user_by_id(self, bridge_id,
                       include_course_summary=True,
                       include_manager=True,
                       include_deleted=True):
        """
        :param bridge_id: integer
        :param include_course_summary: specify if you want course
                                       data in the response.
        :param include_manager: specify if you want manager data
                                in the response.
        :param include_deleted: specify if you want to include
                                terminated user record in the response.
        Return a BridgeUser object
        """
        url = self._add_includes_to_url(
            self.author_id_url(bridge_id, no_custom_fields=False),
            include_manager, include_course_summary)
        if include_deleted:
            url = "{0}&{1}".format(url, "with_deleted=true")
        resp = get_resource(url)
        return self._get_obj_from_list(
            "get_user by bridge_id('{0}')".format(bridge_id),
            self._process_json_resp_data(resp))

    def _get_all_users_url(self,
                           include_course_summary,
                           no_custom_fields):
        if not include_course_summary and no_custom_fields:
            url = "{0}?{1}".format(self.author_uid_url(None), INCLUDES)
        else:
            url = self.author_uid_url(None, no_custom_fields=no_custom_fields)
            if include_course_summary:
                url = "{0}&{1}".format(url, COURSE_SUMMARY)
        return "{0}&{1}".format(url, PAGE_MAX_ENTRY)

    def get_all_users(self,
                      include_course_summary=False,
                      no_custom_fields=True):
        """
        :param no_custom_fields: specify if you want custom_fields
                                 in the response.
        Return a list of BridgeUser objects of the active user records.
        """
        resp = get_resource(self._get_all_users_url(include_course_summary,
                                                    no_custom_fields))
        return self._process_json_resp_data(
            resp, no_custom_fields=no_custom_fields)

    def _restore_user_url(self, base_url, include_manager):
        return self._add_includes_to_url(
            "{0}/{1}?{2}".format(base_url, RESTORE_SUFFIX, CUSTOM_FIELD),
            include_manager, False)

    def restore_user(self,
                     uwnetid,
                     include_manager=True,
                     no_custom_fields=False):
        """
        :param include_manager: specify if you want manager data
                                 in the response.
        :param no_custom_fields: specify if you want custom_fields
                                 in the response.
        Return a BridgeUser object
        """
        url = self._restore_user_url(self.author_uid_url(uwnetid),
                                     include_manager)
        resp = post_resource(url, '{}')
        return self._get_obj_from_list(
            "restore_user by netid({0})".format(uwnetid),
            self._process_json_resp_data(
                resp, no_custom_fields=no_custom_fields))

    def restore_user_by_id(self,
                           bridge_id,
                           include_manager=True,
                           no_custom_fields=False):
        """
        :param bridge_id: integer
        :param include_manager: specify if you want manager_id
                                 in the response.
        :param no_custom_fields: specify if you want custom_fields
                                 in the response.
        return a BridgeUser object
        """
        url = self._restore_user_url(self.author_id_url(bridge_id),
                                     include_manager)
        resp = post_resource(url, '{}')
        return self._get_obj_from_list(
            "restore_user by bridge_id({0})".format(bridge_id),
            self._process_json_resp_data(
                resp, no_custom_fields=no_custom_fields))

    def update_user(self,
                    bridge_user,
                    no_custom_fields=True):
        """
        Update only the user attributes provided.
        :param no_custom_fields: specify if you want custom_fields
                                 in the response.
        Return a BridgeUser object
        """
        if bridge_user.bridge_id:
            url = self.author_id_url(bridge_user.bridge_id,
                                     no_custom_fields=no_custom_fields)
        else:
            url = self.author_uid_url(bridge_user.netid,
                                      no_custom_fields=no_custom_fields)
        body = json.dumps(bridge_user.to_json_patch(), separators=(',', ':'))
        resp = patch_resource(url, body)
        return self._get_obj_from_list(
            "update_user ({0})".format(bridge_user.to_json()),
            self._process_json_resp_data(resp,
                                         no_custom_fields=no_custom_fields))

    def _process_json_resp_data(self, resp,
                                no_custom_fields=False):
        """
        process the response and return a list of BridgeUser
        """
        bridge_users = []
        while True:
            resp_data = json.loads(resp)
            link_url = None
            if (resp_data.get("meta") is not None and
                    resp_data["meta"].get("next") is not None):
                link_url = resp_data["meta"]["next"]

            try:
                bridge_users = self._process_apage(resp_data,
                                                   bridge_users,
                                                   no_custom_fields)
            except Exception as err:
                logger.error("{0} in {1}".format(str(err), resp_data))

            if link_url is None:
                break
            resp = get_resource(link_url)
        return bridge_users

    def _process_apage(self,
                       resp_data,
                       bridge_users,
                       no_custom_fields):
        custom_fields_value_dict = self._get_custom_fields_dict(
            resp_data["linked"], no_custom_fields)
        # a dict of {custom_field_value_id: BridgeCustomField}

        for user_data in resp_data["users"]:
            user = BridgeUser(
                bridge_id=int(user_data["id"]),
                netid=re.sub('@uw.edu', '', user_data["uid"]),
                email=user_data.get("email", ""),
                full_name=user_data.get("full_name", ""),
                first_name=user_data.get("first_name", None),
                last_name=user_data.get("last_name", None),
                department=user_data.get("department", None),
                job_title=user_data.get("job_title", None),
                locale=user_data.get("locale", "en"),
                is_manager=user_data.get("is_manager", None),
                deleted_at=parse_date(user_data.get("deleted_at")),
                logged_in_at=parse_date(user_data.get("loggedInAt")),
                updated_at=parse_date(user_data.get("updated_at")),
                unsubscribed=parse_date(user_data.get("unsubscribed", None)),
                next_due_date=parse_date(user_data.get("next_due_date")),
                completed_courses_count=user_data.get(
                    "completed_courses_count", -1))

            if user_data.get("manager_id") is not None:
                user.manager_id = int(user_data["manager_id"])

            if (no_custom_fields is False and
                    "links" in user_data and len(user_data["links"]) > 0 and
                    "custom_field_values" in user_data["links"]):
                values = user_data["links"]["custom_field_values"]
                for custom_field_value in values:
                    if custom_field_value in custom_fields_value_dict:
                        custom_field = custom_fields_value_dict[
                            custom_field_value]
                        user.custom_fields[custom_field.name] = custom_field

            if user_data.get("roles") is not None:
                for role_data in user_data["roles"]:
                    user.roles.append(
                        self.user_roles.new_user_role_by_id(role_data))
            bridge_users.append(user)
        return bridge_users

    def _get_custom_fields_dict(self, linked_data, no_custom_fields):
        """
        :except KeyError:
        """
        custom_fields_value_dict = {}
        # a dict of {value_id: BridgeCustomField}

        if no_custom_fields is True:
            return custom_fields_value_dict

        custom_fields_name_dict = {}
        # a dict of {custom_field_id: name}

        for id_name_pair in linked_data["custom_fields"]:
            field_id = id_name_pair.get("id")
            name = id_name_pair.get("name")
            if field_id is not None and name is not None:
                custom_fields_name_dict[field_id] = name.lower()

        for value in linked_data["custom_field_values"]:
            custom_field = BridgeCustomField(
                value_id=value.get("id"),
                value=value.get("value"),
                field_id=value["links"]["custom_field"]["id"])
            custom_field.name = custom_fields_name_dict[custom_field.field_id]
            custom_fields_value_dict[custom_field.value_id] = custom_field
        return custom_fields_value_dict

    def _get_obj_from_list(self, action, rlist):
        if len(rlist) == 0:
            return None

        if len(rlist) > 1:
            data = []
            for u in rlist:
                data.append(u.to_json())
            logger.error(
                "{0} returns multiple Bridge user accounts: {1}".format(
                    action, data))
        return rlist[0]


def parse_date(date_str):
    if date_str is not None:
        return parse(date_str)
    return None
