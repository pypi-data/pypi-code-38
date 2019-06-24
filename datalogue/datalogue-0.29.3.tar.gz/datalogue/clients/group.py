from typing import List, Union
from uuid import UUID

from datalogue.clients.http import _HttpClient, HttpMethod
from datalogue.models.organization import User, _users_from_payload, Group, _group_from_payload, Domain, _domain_from_payload
from datalogue.errors import DtlError
from datalogue.utils import _parse_list


class _GroupClient:
    """
    Client to interact with the Group objects
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client

    def create(self, name: str, org_id: UUID) -> Union[DtlError, Group]:
        """
        Creates a group

        :param name: Group to be created
        :param org_id: Organization in which the group will be created
        :return: string with error message if failed, the group otherwise
        """
        res = self.http_client.make_authed_request(
            "/group", HttpMethod.POST, {
                "name": name,
                "organizationId": str(org_id)
            })

        if isinstance(res, DtlError):
            return DtlError("Could not create the group:", res)

        return _group_from_payload(res)

    def delete(self, group_id: UUID) -> Union[DtlError, bool]:
        """
        Delete group

        :param group_id: id of the group
        :return: Error if it fails or true if it's deleted
        """

        res = self.http_client.make_authed_request(
            f"/group/{str(group_id)}", HttpMethod.DELETE)

        if isinstance(res, DtlError):
            return DtlError("Could not delete the group", res)
        else:
            return True

    def get_users(self, group_id: UUID) -> Union[DtlError, List[User]]:
        """
        From the provided group id, get all users in the group

        :param group_id: id of the group
        :return: Error if it fails or list of all users in the group otherwise
        """

        res = self.http_client.make_authed_request(
            f"/group/{str(group_id)}/users", HttpMethod.GET)

        if isinstance(res, DtlError):
            return DtlError("Could not retreive all users of the group:", res)

        return _parse_list(_users_from_payload)(res)

    def get_list(self) -> Union[DtlError, List[Group]]:
        """
        Get only a list of groups in which the user is a member (the whole database)

        :return: Error if it fails or list of groups otherwise
        """

        res = self.http_client.make_authed_request(
            "/groups", HttpMethod.GET)

        if isinstance(res, DtlError):
            return DtlError("Could not retreive all groups of the organization:", res)

        return _parse_list(_group_from_payload)(res)

    def add_user(self, user_id: UUID, group_id: UUID) -> Union[DtlError, bool]:
        """
        Add provided user to provided group

        :param group_id: id of the group
        :param user_id: id of the user
        :return: Error if it fails or true if it's added
        """

        res = self.http_client.make_authed_request(
            f"/group/{str(group_id)}/user/{str(user_id)}", HttpMethod.POST)

        if isinstance(res, DtlError):
            return DtlError("Could not add user to the group:", res)
        else:
            return True

    def remove_user(self, user_id: UUID, group_id: UUID) -> Union[DtlError, bool]:
        """
        Remove user from provided group

        :param group_id: id of the group 
        :param user_id: id of the user
        :return: Error if it fails or true if it's deleted
        """

        res = self.http_client.make_authed_request(
            f"/group/{str(group_id)}/user/{str(user_id)}", HttpMethod.DELETE)

        if isinstance(res, DtlError):
            return DtlError("Could not delete user:", res)
        else:
            return True

    def add_right(self, group_id: UUID) -> Union[DtlError, bool]:
        """
        Add right to provided group : should have the right ManageOrganization

        :param group_id: id of the group
        :return: Error if it fails or true if it's added
        """

        res = self.http_client.make_authed_request(
            f"/group/{str(group_id)}/permission?name=ManageOrganization", HttpMethod.POST)

        if isinstance(res, DtlError):
            return DtlError("You may not have permission to do the action. ", res)
        else:
            return True

    def remove_right(self, group_id: UUID) -> Union[DtlError, bool]:
        """
        Remove right from provided group: should have the right ManageOrganization

        :param group_id: id of the group
        :return: Error if it fails or true if it's deleted
        """

        res = self.http_client.make_authed_request(
            f"/group/{str(group_id)}/permission?name=ManageOrganization", HttpMethod.DELETE)

        if isinstance(res, DtlError):
            return DtlError("You may not have permission to do the action.", res)
        else:
            return True
