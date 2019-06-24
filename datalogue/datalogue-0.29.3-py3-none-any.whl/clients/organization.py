from typing import List, Union
from uuid import UUID

from datalogue.clients.http import _HttpClient, HttpMethod
from datalogue.models.organization import Organization, _organization_from_payload, User, _users_from_payload, Group, _group_from_payload, Domain, _domain_from_payload
from datalogue.errors import DtlError
from datalogue.utils import _parse_list


class _OrganizationClient:
    """
    Client to interact with the Organization objects
    """
    errorMsg = "you may not have permission to do the action or the organization was not found"

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client

    def create(self, name: str) -> Union[DtlError, Organization]:
        """
        Creates an organization

        :param name: Organization to be created
        :return: string with error message if failed, the organization otherwise
        """
        res = self.http_client.make_authed_request(
            "/organization", HttpMethod.POST, {
                "name": name
            })

        if isinstance(res, DtlError):
            return DtlError("Could not create the organization:", res)

        return _organization_from_payload(res)

    def get(self, org_id: UUID) -> Union[DtlError, Organization]:
        """
        From the provided id, get the corresponding Organization

        :param org_id: id of the organization to be retrieved
        :return: Error if it fails or Organization object otherwise
        """

        res = self.http_client.make_authed_request(
            f"/organization/{str(org_id)}/public", HttpMethod.GET)

        if isinstance(res, DtlError):
            return DtlError("Could not retreive the organization:", res)

        return _organization_from_payload(res)

    def get_all_users(self, org_id: UUID) -> Union[DtlError, List[User]]:
        """
        From the provided organization id, get all users in the Organization

        :param org_id: id of the organization
        :return: Error if it fails or list of all users in the organization otherwise
        """

        res = self.http_client.make_authed_request(
            f"/organization/{str(org_id)}/users", HttpMethod.GET)

        if isinstance(res, DtlError):
            return DtlError("Could not retreive all users of the organization:", _OrganizationClient.errorMsg)

        return _parse_list(_users_from_payload)(res)

    def get_groups(self, org_id: UUID) -> Union[DtlError, List[Group]]:
        """
        From the provided organization id, get all groups in the Organization in which the user is a member

        :param org_id: id of the organization
        :return: Error if it fails or list of all groups in the organization otherwise
        """

        res = self.http_client.make_authed_request(
            f"/groups?orgId={str(org_id)}", HttpMethod.GET)

        if isinstance(res, DtlError):
            return DtlError("Could not retreive your groups of the organization:")

        return _parse_list(_group_from_payload)(res)

    def get_all_groups(self, org_id: UUID) -> Union[DtlError, List[Group]]:
        """
        From the provided organization id, get all groups in the Organization (should be admin)

        :param org_id: id of the organization
        :return: Error if it fails or list of all groups in the organization otherwise
        """

        res = self.http_client.make_authed_request(
            f"/organization/{str(org_id)}/groups", HttpMethod.GET)

        if isinstance(res, DtlError):
            return DtlError("Could not retrieve all groups of the organization:", _OrganizationClient.errorMsg)

        return _parse_list(_group_from_payload)(res)

    def add_domain(self, org_id: UUID, domain: str) -> Union[DtlError, bool]:
        """
        Add domain to provided organization

        :param org_id: id of the organization
        :return: Error if it fails or true if it's added
        """

        res = self.http_client.make_authed_request(
            f"/organization/{str(org_id)}/domain", HttpMethod.POST, {
                "domain": domain
            })

        if isinstance(res, DtlError):
            return DtlError("Could not add domain to the organization:", _OrganizationClient.errorMsg)
        else:
            return True

    def remove_domain(self, org_id: UUID, domain: str) -> Union[DtlError, bool]:
        """
        Remove domain from provided organization

        :param org_id: id of the organization
        :return: Error if it fails or true if it's deleted
        """

        res = self.http_client.make_authed_request(
            f"/organization/{str(org_id)}/domain", HttpMethod.DELETE, {
                "domain": domain
            })

        if isinstance(res, DtlError):
            return DtlError("Could not delete domain:", _OrganizationClient.errorMsg)
        else:
            return True

    def get_all_domains(self, org_id: UUID) -> Union[DtlError, List[Domain]]:
        """
        Get all domains of the provided organization

        :param org_id: id of the organization
        :return: Error if it fails or list of domains
        """

        res = self.http_client.make_authed_request(
            f"/organization/{str(org_id)}/domains", HttpMethod.GET)

        if isinstance(res, DtlError):
            return DtlError("Could not retreive all domains:", _OrganizationClient.errorMsg)

        return _parse_list(_domain_from_payload)(res)

