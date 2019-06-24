from uuid import UUID
from typing import List, Union

from datalogue.errors import DtlError


class Organization:
    def __init__(self, org_id: UUID, name: str):
        self.id = org_id
        self.name = name

    def __eq__(self, other: 'Organization'):
        if isinstance(self, other.__class__):
            return self.id == other.id and self.name == other.name
        return False

    def __repr__(self):
        return f'{self.__class__.__name__}(id: {self.id}, name: {self.name!r})'


def _organization_from_payload(json: dict) -> Union[DtlError, Organization]:
    org_id = json.get("id")
    if org_id is None:
        return DtlError("Organization object should have an 'id' property")
    else:
        try:
            org_id = UUID(org_id)
        except ValueError:
            return DtlError("'id' field was not a proper uuid")

    name = json.get("name")
    if name is None:
        return DtlError("Organization object should have a 'name' property")

    return Organization(org_id, name)


class Group:
    def __init__(self, group_id: UUID, org_id: UUID, name: str):
        self.id = group_id
        self.name = name
        self.org_id = org_id

    def __eq__(self, other: 'Group'):
        if isinstance(self, other.__class__):
            return self.id == other.id and self.name == other.name and self.org_id == other.org_id
        return False

    def __repr__(self):
        return f'{self.__class__.__name__}(id: {self.id}, name: {self.name!r}, org_id: {self.org_id!r})'


def _group_from_payload(json: dict) -> Union[DtlError, Group]:
    group_id = json.get("id")
    if group_id is None:
        return DtlError("Group object should have an 'id' property")
    else:
        try:
            group_id = UUID(group_id)
        except ValueError:
            return DtlError("'id' field was not a proper uuid")

    name = json.get("name")
    if name is None:
        return DtlError("Group object should have a 'name' property")

    org_id = json.get("orgId")
    if org_id is None:
        return DtlError("Group object should have a 'org_id' property")
    else:
        try:
            org_id = UUID(org_id)
        except ValueError:
            return DtlError("'orgId' field was not a proper uuid")

    return Group(group_id, org_id, name)


class User:
    def __init__(self, user_id: UUID, first_name: str, last_name: str, email: str, organization_ids: Union[None,List[str]], group_ids: Union[None,List[str]]):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.organization_ids = organization_ids
        self.group_ids = group_ids

    def __eq__(self, other: 'User'):
        if isinstance(self, other.__class__):
            return self.id == other.id and self.first_name == other.first_name and self.last_name == other.last_name and self.email == other.email
        return False

    def __repr__(self):
        return f'{self.__class__.__name__}(id: {self.id}, first_name: {self.first_name!r}, last_name: {self.last_name!r}, email: {self.email!r}, organization_ids: {self.organization_ids!r}, group_ids: {self.group_ids!r})'


def _user_from_payload(json: dict) -> Union[DtlError, User]:
    user_id = json.get("user").get("id")
    if user_id is None:
        return DtlError("User object should have an 'id' property")
    else:
        try:
            user_id = UUID(user_id)
        except ValueError:
            return DtlError("'id' field was not a proper uuid")

    first_name = json.get("user").get("firstName")
    if first_name is None:
        return DtlError("User object should have a 'firstName' property")

    last_name = json.get("user").get("lastName")
    if last_name is None:
        return DtlError("User object should have a 'lastName' property")

    email = json.get("user").get("email")
    if email is None:
        return DtlError("User object should have a 'email' property")

    organization_ids = json.get("organizationsIds")
    # if organization_ids is None:
    #     return DtlError("User object should have a 'organizationsIds' property")

    group_ids = json.get("groupsIds")
    if group_ids is None:
        return DtlError("User object should have a 'groupsIds' property")

    return User(user_id, first_name, last_name, email, organization_ids, group_ids)


def _users_from_payload(json: dict) -> Union[DtlError, User]:
    user_id = json.get("id")
    if user_id is None:
        return DtlError("User object should have an 'id' property")
    else:
        try:
            user_id = UUID(user_id)
        except ValueError:
            return DtlError("'id' field was not a proper uuid")

    first_name = json.get("firstName")
    if first_name is None:
        return DtlError("User object should have a 'firstName' property")

    last_name = json.get("lastName")
    if last_name is None:
        return DtlError("User object should have a 'lastName' property")

    email = json.get("email")
    if email is None:
        return DtlError("User object should have a 'email' property")

    return User(user_id, first_name, last_name, email, None, None)


class Domain:
    def __init__(self, org_id: UUID, domain: str):
        self.org_id = org_id
        self.domain = domain

    def __eq__(self, other: 'Domain'):
        if isinstance(self, other.__class__):
            return self.org_id == other.org_id and self.domain == other.domain
        return False

    def __repr__(self):
        return f'{self.__class__.__name__}(org_id: {self.org_id}, domain: {self.domain!r})'


def _domain_from_payload(json: dict) -> Union[DtlError, Domain]:
    org_id = json.get("orgId")
    if org_id is None:
        return DtlError("Domain object should have an 'orgId' property")
    else:
        try:
            org_id = UUID(org_id)
        except ValueError:
            return DtlError("'id' field was not a proper uuid")

    domain = json.get("domain")
    if domain is None:
        return DtlError("Domain object should have a 'domain' property")

    return Domain(org_id, domain)
