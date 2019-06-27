# Copyright 2019 StreamSets Inc.

"""Classes for SCH-related models.

This module provides implementations of classes with which users may interact in the course of
writing tests that exercise SCH functionality.
"""

import collections
import copy
import json
import logging
import requests
import time
import urllib3
import uuid
from datetime import datetime
from functools import partial

import inflection

from .sdc import DataCollector as SdcDataCollector
from .sdc_models import PipelineBuilder as SdcPipelineBuilder, Stage
from .utils import SeekableList, MutableKwargs, update_acl_permissions, set_acl, get_params, reversed_dict

logger = logging.getLogger(__name__)

json_to_python_style = lambda x: inflection.underscore(x)
python_to_json_style = lambda x: inflection.camelize(x, uppercase_first_letter=False)

ModelCollectionResults = collections.namedtuple('ModelCollectionResults', ['results', 'kwargs'])


class BaseModel:
    """Base class for Control Hub models that essentially just wrap a dictionary.

    Args:
        data (:obj:`dict`): The underlying JSON representation of the model.
        attributes_to_ignore (:obj:`list`, optional): A list of string attributes to mask from being handled
            by this class' __setattr__ method. Default: ``None``.
        attributes_to_remap (:obj:`dict`, optional): A dictionary of attributes to remap with the desired attributes
            as keys and the corresponding property name in the JSON representation as values. Default: ``None``.
        repr_metadata (:obj:`list`, optional): A list of attributes to use in the model's __repr__ string.
            Default: ``None``.
    """

    def __init__(self, data, attributes_to_ignore=None, attributes_to_remap=None, repr_metadata=None):
        super().__setattr__('_data', data)
        super().__setattr__('_attributes_to_ignore', attributes_to_ignore or [])
        super().__setattr__('_attributes_to_remap', attributes_to_remap or {})
        super().__setattr__('_repr_metadata', repr_metadata or [])

    def __getattr__(self, name):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            return self._data[remapped_name]
        elif (name_ in self._data and
              name not in self._attributes_to_ignore and
              name not in self._attributes_to_remap.values()):
            return self._data[name_]
        raise AttributeError('Could not find attribute {}.'.format(name_))

    def __setattr__(self, name, value):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            self._data[remapped_name] = value
        elif (name_ in self._data and
              name not in self._attributes_to_ignore and
              name not in self._attributes_to_remap.values()):
            self._data[name_] = value
        else:
            super().__setattr__(name, value)

    def __dir__(self):
        return sorted(list(dir(object))
                      + list(self.__dict__.keys())
                      + list(json_to_python_style(key)
                             for key in self._data.keys()
                             if key not in (list(self._attributes_to_remap.values())
                                            + self._attributes_to_ignore))
                      + list(self._attributes_to_remap.keys()))

    def __eq__(self, other):
        return self._data == other._data

    def __repr__(self):
        return '<{} ({})>'.format(self.__class__.__name__,
                                  ', '.join('{}={}'.format(key, getattr(self, key)) for key in self._repr_metadata))


class UiMetadataBaseModel(BaseModel):
    def __getattr__(self, name):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            return self._data[remapped_name]['value']
        elif (name_ in self._data and
              name not in self._attributes_to_ignore and
              name not in self._attributes_to_remap.values()):
            return self._data[name_]['value']
        raise AttributeError('Could not find attribute {}.'.format(name_))

    def __setattr__(self, name, value):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            self._data[remapped_name]['value'] = value
        elif (name_ in self._data and
              name not in self._attributes_to_ignore and
              name not in self._attributes_to_remap.values()):
            self._data[name_]['value'] = value
        else:
            super().__setattr__(name, value)


class ModelCollection:
    """Base class wrapper with Abstractions.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
    """

    def __init__(self, control_hub):
        self._control_hub = control_hub
        self._id_attr = 'id'

    def _get_all_results_from_api(self, **kwargs):
        """Used to get multiple (all) results from api.

        Args:
            Optional arguments to be passed to filter the results.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of inherited instances of
                :py:class:`streamsets.sdk.sch_models.BaseModel` and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        pass

    def __iter__(self):
        """Enables the list enumeration or iteration."""
        for item in self._get_all_results_from_api().results:
            yield item

    def __getitem__(self, i):
        """Enables the user to fetch items by index.

        Args:
            i (:obj:`int`): Index of the item.

        Returns:
            An inherited instance of :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        return self._get_all_results_from_api().results[i]

    def __len__(self):
        """Provides length (count) of items.

        Returns:
            A :py:obj:`int` object.
        """
        return len(self._get_all_results_from_api().results)

    def __contains__(self, item_given):
        """Checks if given item is in the list of items by comparing the ids.

        Returns:
            A :py:obj:`boolean` object.
        """
        return self.contains(**{self._id_attr: getattr(item_given, self._id_attr)})

    def get(self, **kwargs):
        """
        Args:
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            An inherited instance of :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        result, new_kwargs = self._get_all_results_from_api(**kwargs)
        return result.get(**new_kwargs)

    def get_all(self, **kwargs):
        """
        Args:
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of inherited instances of
            :py:class:`streamsets.sdk.sch_models.BaseModel`.
        """
        result, new_kwargs = self._get_all_results_from_api(**kwargs)
        return result.get_all(**new_kwargs)

    def __repr__(self):
        return str(self._get_all_results_from_api().results)

    def contains(self, **kwargs):
        """
        Args:
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :py:obj:`boolean` object.
        """
        try:
            self.get(**kwargs)
        except ValueError:
            return False
        return True


class ACL(BaseModel):
    """Represents an ACL.

    Args:
        acl (:obj:`dict`): JSON representation of an ACL.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Control Hub object.

    Attributes:
        permissions (:py:class:`streamsets.sdk.sch_models.Permissions`): A Collection of Permissions.
    """
    _ATTRIBUTES_TO_REMAP = {'resource_id': 'resourceId',
                            'resource_owner': 'resourceOwner',
                            'resource_created_time': 'resourceCreatedTime',
                            'resource_type': 'resourceType',
                            'last_modified_by': 'lastModifiedBy',
                            'last_modified_on': 'lastModifiedOn'}
    _ATTRIBUTES_TO_IGNORE = ['permissions']
    _REPR_METADATA = ['resource_id', 'resource_type']

    def __init__(self, acl, control_hub):
        super().__init__(acl,
                         attributes_to_remap=ACL._ATTRIBUTES_TO_REMAP,
                         attributes_to_ignore=ACL._ATTRIBUTES_TO_IGNORE,
                         repr_metadata=ACL._REPR_METADATA)
        self.permissions = SeekableList(Permission(permission,
                                                   self.resource_type,
                                                   control_hub.api_client) for permission in self._data['permissions'])
        self._control_hub = control_hub

    def __getitem__(self, key):
        return getattr(self, key)

    def __len__(self):
        return len(self._data)

    @property
    def permission_builder(self):
        """Get a permission builder instance with which a pipeline can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACLPermissionBuilder`.
        """
        permission = {property: None
                      for property in self._control_hub._job_api['definitions']['PermissionJson']['properties']}

        return ACLPermissionBuilder(permission=permission, acl=self)

    def add_permission(self, permission):
        """Add new permission to the ACL.

        Args:
            permission (:py:class:`streamsets.sdk.sch_models.Permission`): A permission object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        self._data['permissions'].append(permission._data)
        return set_acl(self._control_hub.api_client, self.resource_type, self.resource_id, self._data)

    def remove_permission(self, permission):
        """Remove a permission from ACL.

        Args:
            permission (:py:class:`streamsets.sdk.sch_models.Permission`): A permission object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        permissions = self._data['permissions']
        self._data['permissions'] = [perm for perm in permissions if perm['subjectId'] != permission.subject_id]
        return set_acl(self._control_hub.api_client, self.resource_type, self.resource_id, self._data)


class ACLPermissionBuilder():
    """Class to help build the ACL permission.

    Args:
        permission (:py:class:`streamsets.sdk.sch_models.Permission`): A permission object.
        acl (:py:class:`streamsets.sdk.sch_models.ACL`): An ACL object.
    """

    def __init__(self, permission, acl):
        self._permission = permission
        self._acl = acl

    def build(self, subject_id, subject_type, actions):
        """Method to help build the ACL permission.

        Args:
            subject_id (:obj:`str`): Id of the subject e.g. 'test@test'.
            subject_type (:obj:`str`): Type of the subject e.g. 'USER'.
            actions (:obj:`list`): A list of actions of type :obj:`str` e.g. ['READ', 'WRITE', 'EXECUTE'].

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Permission`.
        """
        self._permission.update({'resourceId': self._acl.resource_id,
                                 'subjectId': subject_id,
                                 'subjectType': subject_type,
                                 'actions': actions})
        return Permission(self._permission, self._acl.resource_type, self._acl._control_hub.api_client)


class Permission(BaseModel):
    """A container for a permission.

    Args:
        permission (:obj:`dict`): A Python object representation of a permission.
        resource_type (:obj:`str`): String representing the type of resource e.g. 'JOB', 'PIPELINE'.
        api_client (:py:class:`streamsets.sdk.sch_api.ApiClient`): An instance of ApiClient.

    Attributes:
        resource_id (:obj:`str`): Id of the resource e.g. Pipeline or Job.
        subject_id (:obj:`str`): Id of the subject e.g. user id ``'admin@admin'``.
        subject_type (:obj:`str`): Type of the subject e.g. ``'USER'``.
        last_modified_by (:obj:`str`): User who last modified this permission e.g. ``'admin@admin'``.
        last_modified_on (:obj:`int`): Timestamp at which this permission was last modified e.g. ``1550785079811``.
    """
    _ATTRIBUTES_TO_REMAP = {'resource_id': 'resourceId',
                            'subject_id': 'subjectId',
                            'subject_type': 'subjectType',
                            'last_modified_by': 'lastModifiedBy',
                            'last_modified_on': 'lastModifiedOn'}
    _ATTRIBUTES_TO_IGNORE = ['resource_type', 'api_client']
    _REPR_METADATA = ['resource_id', 'subject_type', 'subject_id']

    def __init__(self, permission, resource_type, api_client):
        super().__init__(permission,
                         attributes_to_remap=Permission._ATTRIBUTES_TO_REMAP,
                         attributes_to_ignore=Permission._ATTRIBUTES_TO_IGNORE,
                         repr_metadata=Permission._REPR_METADATA)
        self._resource_type = resource_type
        self._api_client = api_client

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if key in {'actions', 'subject_id', 'subject_type'}:
            update_acl_permissions(self._api_client, self._resource_type, self._data)


class UserBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.User`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_user_builder`.

    Args:
        user (:obj:`dict`): Python object built from our Swagger UserJson definition.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
    """

    def __init__(self, user, roles):
        self._user = user
        self._roles = roles

    def build(self, id, display_name, email_address, saml_user_name=None):
        """Build the user.

        Args:
            id (:obj:`str`): User Id.
            display_name (:obj:`str`): User display name.
            email_address (:obj:`str`): User Email Address.
            saml_user_name (:obj:`str`, optional): Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.User`.
        """
        self._user.update({'id': id,
                           'name': display_name,
                           'email': email_address,
                           # Following logic from https://git.io/fNsoQ.
                           'nameInOrg': saml_user_name or id})
        return User(user=self._user, roles=self._roles)


class User(BaseModel):
    """Model for User.

    Args:
        user (:obj:`dict`): JSON representation of User.
        roles (:obj:`dict`): A mapping of role IDs to role labels.

    Attributes:
        active (:obj:`bool`): Whether the user is active or not.
        created_by (:obj:`str`): Creator of this user.
        created_on (:obj:`str`): Creation time of this user.
        display_name (:obj:`str`): Display name of this user.
        email_address (:obj:`str`): Email address of this user.
        id (:obj:`str`): Id of this user.
        groups (:obj:`list`): Groups this user belongs to.
        last_modified_by (:obj:`str`): User last modified by.
        last_modified_on (:obj:`str`): User last modification time.
        password_expires_on (:obj:`str`): User's password expiration time.
        password_system_generated (:obj:`bool`): Whether User's password is system generated or not.
        roles (:obj:`set`): A set of role labels.
        saml_user_name (:obj:`str`): SAML username of user.
    """
    _ATTRIBUTES_TO_IGNORE = ['destroyer', 'organization', 'roles', 'userDeleted']
    _ATTRIBUTES_TO_REMAP = {'created_by': 'creator',
                            'email_address': 'email',
                            'display_name': 'name',
                            'saml_user_name': 'nameInOrg',
                            'password_expires_on': 'passwordExpiryTime',
                            'password_system_generated': 'passwordGenerated'}
    _REPR_METADATA = ['id', 'display_name']

    # Jetty requires ever SCH user to have the 'user' role, which is hidden in the UI. We'll do the same.
    _ROLES_TO_HIDE = ['user']

    def __init__(self, user, roles):
        super().__init__(user,
                         attributes_to_ignore=User._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=User._ATTRIBUTES_TO_REMAP,
                         repr_metadata=User._REPR_METADATA)
        self._roles = roles

    @property
    def roles(self):
        return {self._roles[role] for role in self._data.get('roles', []) if role not in User._ROLES_TO_HIDE}

    @roles.setter
    def roles(self, value):
        # We reverse the _roles dictionary to let this setter deal with role labels while still writing role ids.
        role_label_to_id = {role_label: role_id for role_id, role_label in self._roles.items()}

        value_ = value if isinstance(value, list) else [value]
        self._data['roles'] = list({role_label_to_id[role] for role in value_} | set(User._ROLES_TO_HIDE))


class Users(ModelCollection):
    """Collection of :py:class:`streamsets.sdk.sch_models.User` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
        organization (:obj:`str`): Organization ID.
    """

    def __init__(self, control_hub, roles, organization):
        super().__init__(control_hub)
        self._roles = roles
        self._organization = organization

    def _get_all_results_from_api(self, id=None, organization=None, **kwargs):
        """
        Args:
            id (:obj:`str`)
            organization (:obj:`str`)
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.User` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        if organization is None:
            organization = self._organization
        if id is not None:
            try:
                return ModelCollectionResults(SeekableList([User(self._control_hub.api_client
                                                                     .get_user(org_id=organization,
                                                                               user_id=id).response.json(),
                                                                 self._roles)]),
                                              kwargs)
            except requests.exceptions.HTTPError:
                raise ValueError('User (id={}) not found'.format(id))
        return ModelCollectionResults(SeekableList(User(user, self._roles)
                                                   for user in
                                                   self._control_hub.api_client
                                                   .get_all_users(organization).response.json()),
                                      kwargs)


class Roles(list):
    """Wrapper class over the list of Roles.

    Args:
        values (:obj:`list`): List of roles.
        entity (:py:class:`streamsets.sdk.sch_models.Group`) or
              (:py:class:`streamsets.sdk.sch_models.User`): Group or User object.
        role_label_to_id (:obj:`dict`): Role label to Role ID mapping.
    """
    def __init__(self, values, entity, role_label_to_id):
        super().__init__(values)
        self._entity = entity
        self._role_label_to_id = role_label_to_id

    def append(self, value):
        # Use super().append() to throw corresponding exceptions when necessary.
        super().append(value)
        self._entity._data['roles'].append(self._role_label_to_id[value])

    def remove(self, value):
        # Use super().remove() to throw corresponding exceptions when necessary.
        super().remove(value)
        self._entity._data['roles'].remove(self._role_label_to_id[value])


class GroupBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Group`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_group_builder`.

    Args:
        group (:obj:`dict`): Python object built from our Swagger GroupJson definition.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
    """

    def __init__(self, group, roles):
        self._group = group
        self._roles = roles

    def build(self, id, display_name):
        """Build the group.

        Args:
            id (:obj:`str`): Group ID.
            display_name (:obj:`str`): Group display name.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Group`.
        """
        self._group.update({'id': id,
                            'name': display_name})
        return Group(group=self._group, roles=self._roles)


class Group(BaseModel):
    """Model for Group.

    Args:
        group (:obj:`dict`): A Python object representation of Group.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
    """
    _ATTRIBUTES_TO_IGNORE = ['destroyer', 'organization', 'roles', 'groupDeleted']
    _ATTRIBUTES_TO_REMAP = {'display_name': 'name'}
    _REPR_METADATA = ['id', 'display_name']

    # Jetty requires every SCH group to have the 'user' role, which is hidden in the UI. We'll do the same.
    _ROLES_TO_HIDE = ['user']

    def __init__(self, group, roles):
        super().__init__(group,
                         attributes_to_ignore=User._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=User._ATTRIBUTES_TO_REMAP,
                         repr_metadata=User._REPR_METADATA)
        self._roles = roles

    @property
    def roles(self):
        return Roles([self._roles[role] for role in self._data.get('roles', []) if role not in Group._ROLES_TO_HIDE],
                     self,
                     reversed_dict(self._roles))

    @roles.setter
    def roles(self, value):
        # We reverse the _roles dictionary to let this setter deal with role labels while still writing role ids.
        role_label_to_id = reversed_dict(self._roles)

        value_ = value if isinstance(value, list) else [value]
        self._data['roles'] = list({role_label_to_id[role] for role in value_} | set(Group._ROLES_TO_HIDE))


class Groups(ModelCollection):
    """Collection of :py:class:`streamsets.sdk.sch_models.Group` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        roles (:obj:`dict`): A mapping of role IDs to role labels.
        organization (:obj:`str`): Organization ID.
    """

    def __init__(self, control_hub, roles, organization):
        super().__init__(control_hub)
        self._roles = roles
        self._organization = organization

    def _get_all_results_from_api(self, id=None, organization=None, **kwargs):
        """
        Args:
            id (:obj:`str`)
            organization (:obj:`str`)
            kwargs: Other optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.Group` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        if organization is None:
            organization = self._organization
        if id is not None:
            try:
                return ModelCollectionResults(SeekableList([Group(self._control_hub.api_client
                                                                      .get_group(org_id=organization,
                                                                                 group_id=id).response.json(),
                                                                  self._roles)]),
                                              kwargs)
            except requests.exceptions.HTTPError:
                raise ValueError('Group (id={}) not found'.format(id))
        return ModelCollectionResults(SeekableList(Group(group, self._roles)
                                                   for group in
                                                   self._control_hub.api_client
                                                   .get_all_groups(organization).response.json()),
                                      kwargs)


class OrganizationBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Organization`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_organization_builder`.

    Args:
        organization (:obj:`dict`): Python object built from our Swagger UserJson definition.
    """

    def __init__(self, organization, organization_admin_user):
        self._organization = organization
        self._organization_admin_user = organization_admin_user

    def build(self, id, name,
              admin_user_id, admin_user_display_name, admin_user_email_address):
        """Build the organization.

        Args:
            id (:obj:`str`): Organization ID.
            name (:obj:`str`): Organization name.
            admin_user_id (:obj:`str`): User Id of the admin of this organization.
            admin_user_display_name (:obj:`str`): User display name of admin of this organization.
            admin_user_email_address (:obj:`str`): User email address of admin of this organization.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Organization`.
        """
        self._organization.update({'id': id,
                                   'name': name,
                                   'primaryAdminId': admin_user_id})
        self._organization_admin_user.update({'id': admin_user_id,
                                              'name': admin_user_display_name,
                                              'email': admin_user_email_address,
                                              'organization': id})
        return Organization(self._organization, self._organization_admin_user)


class Organization(BaseModel):
    """Model for Organization.

    Args:
        organization (:obj:`str`): Organization Id.
        organization_admin_user (:obj:`str`, optional): Default: ``None``.
        api_client (:py:obj:`streamsets.sdk.sch_api.ApiClient`, optional): Default: ``None``.
    """
    _ATTRIBUTES_TO_IGNORE = ['configuration', 'passwordExpiryTimeInMillis', ]
    _ATTRIBUTES_TO_REMAP = {'admin_user_id': 'primaryAdminId',
                            'created_by': 'creator',
                            'saml_intergration_enabled': 'externalAuthEnabled'}
    _REPR_METADATA = ['id', 'name']

    def __init__(self, organization, organization_admin_user=None, api_client=None):
        super().__init__(organization,
                         attributes_to_ignore=Organization._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=Organization._ATTRIBUTES_TO_REMAP,
                         repr_metadata=Organization._REPR_METADATA)
        self._organization_admin_user = organization_admin_user
        self._api_client = api_client

    @property
    def default_user_password_expiry_time_in_days(self):
        return self._data['passwordExpiryTimeInMillis'] / 86400000  # 1 d => ms

    @default_user_password_expiry_time_in_days.setter
    def default_user_password_expiry_time_in_days(self, value):
        self._data['passwordExpiryTimeInMillis'] = value * 86400000

    @property
    def configuration(self):
        configuration = self._api_client.get_organization_configuration(self.id).response.json()

        # Some of the config names are a bit long, so shorten them slightly...
        ID_TO_REMAP = {'accountType': 'Organization account type',
                       'contractExpirationTime': 'Timestamp of the contract expiration',
                       'trialExpirationTime': 'Timestamp of the trial expiration'}
        return Configuration(configuration=configuration,
                             update_callable=self._api_client.update_organization_configuration,
                             update_callable_kwargs=dict(org_id=self.id),
                             id_to_remap=ID_TO_REMAP)

    @configuration.setter
    def configuration(self, value):
        self._api_client.update_organization_configuration(self.id, value._data)


class Organizations(ModelCollection):
    """Collection of :py:class:`streamsets.sdk.sch_models.Organization` instances."""

    def _get_all_results_from_api(self, **kwargs):
        """
        Args:
            kwargs: optional arguments

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.Organization` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        return ModelCollectionResults(SeekableList(Organization(organization, api_client=self._control_hub.api_client)
                                                   for organization in
                                                   self._control_hub.api_client
                                                   .get_all_organizations().response.json()),
                                      kwargs)


class Configuration:
    """A dictionary-like container for getting and setting configuration values.

    Args:
        configuration (:obj:`dict`): JSON object representation of configuration.
        update_callable (optional): A callable to which ``self._data`` will be passed as part of ``__setitem__``.
        update_callable_kwargs (:obj:`dict`, optional): A dictionary of kwargs to pass (along with a body)
            to the callable.
        id_to_remap (:obj:`dict`, optional): A dictionary mapping configuration IDs to human-readable container keys.
    """

    def __init__(self, configuration, update_callable=None, update_callable_kwargs=None, id_to_remap=None):
        self._data = configuration
        self._update_callable = update_callable
        self._update_callable_kwargs = update_callable_kwargs or {}
        self._id_to_remap = id_to_remap or {}

    def __getitem__(self, key):
        for config in self._data:
            if config['name'] == key or self._id_to_remap.get(config.get('id')) == key:
                break
        else:
            raise KeyError(key)
        if 'type' not in config:
            return config['value']
        if config['type'] == 'boolean':
            return json.loads(config['value'])
        elif config['type'] == 'integer':
            return int(config['value'])
        else:
            return config['value']

    def __setitem__(self, key, value):
        for config in self._data:
            if config['name'] == key or self._id_to_remap.get(config.get('id')) == key:
                break
        else:
            raise KeyError(key)
        config['value'] = value
        if self._update_callable:
            kwargs = dict(body=[config])
            kwargs.update(self._update_callable_kwargs)
            self._update_callable(**kwargs)

    def __repr__(self):
        configs = {}
        for config in self._data:
            key = self._id_to_remap.get(config.get('id')) or config['name']
            if 'type' not in config:
                value = config['value']
            elif config['type'] == 'boolean':
                value = json.loads(config['value'])
            elif config['type'] == 'integer':
                value = int(config['value'])
            else:
                value = config['value']
            configs[key] = value
        return '{{{}}}'.format(', '.join("'{}': {}".format(k, v) for k, v in configs.items()))


class DataCollector(BaseModel):
    """Model for Data Collector.

    Attributes:
        execution_mode (:obj:`bool`): ``True`` for Edge and ``False`` for SDC.
        id (:obj:`str`): Data Collectort id.
        labels (:obj:`list`): Labels for Data Collector.
        last_validated_on (:obj:`str`): Last validated time for Data Collector.
        reported_labels (:obj:`list`): Reported labels for Data Collector.
        url (:obj:`str`): Data Collector's url.
        version (:obj:`str`): Data Collector's version.
    """
    _ATTRIBUTES_TO_IGNORE = ['offsetProtocolVersion', 'edge']
    _ATTRIBUTES_TO_REMAP = {'execution_mode': 'edge',
                            'last_validated_on': 'lastReportedTime',
                            'url': 'httpUrl'}
    _REPR_METADATA = ['id', 'url']

    def __init__(self, data_collector, control_hub):
        super().__init__(data_collector,
                         attributes_to_ignore=DataCollector._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=DataCollector._ATTRIBUTES_TO_REMAP,
                         repr_metadata=DataCollector._REPR_METADATA)
        self._control_hub = control_hub

    @property
    def accessible(self):
        """Returns a :obj:`bool` for whether the Data Collector instance is accessible."""
        try:
            # We disable InsecureRequestWarning and disable SSL certificate verification to enable self-signed certs.
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            requests.get(self.http_url, verify=False, timeout=5)
            return True
        except requests.exceptions.ConnectionError:
            return False

    @property
    def attributes(self):
        """Returns a :obj:`dict` of Data Collector attributes."""
        return self._component['attributes']

    @property
    def attributes_updated_on(self):
        return self._component['attributesUpdatedOn']

    @property
    def authentication_token_generated_on(self):
        return self._component['authTokenGeneratedOn']

    @property
    def instance(self):
        # Disable SSL cert verification to enable use of self-signed certs.
        SdcDataCollector.VERIFY_SSL_CERTIFICATES = False
        return SdcDataCollector(self.url, control_hub=self._control_hub)

    @property
    def registered_by(self):
        return self._component['registeredBy']

    @property
    def acl(self):
        """Get DataCollector ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client.get_sdc_acl(sdc_id=self.id).response.json(), self._control_hub)

    @acl.setter
    def acl(self, sdc_acl):
        """Update DataCollector ACL.

        Args:
            sdc_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The sdc ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self._control_hub.api_client.set_sdc_acl(sdc_id=self.id, sdc_acl_json=sdc_acl._data)


class DataCollectors(ModelCollection):
    """Collection of :py:class:`streamsets.sdk.sch_models.DataCollector` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Control Hub object.
    """

    def _get_all_results_from_api(self, id=None, **kwargs):
        """
        Args:
            id (:obj:`str`): id of DataCollector.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.DataCollector` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        if id is None:
            return ModelCollectionResults(SeekableList(DataCollector(data_collector, self._control_hub)
                                                       for data_collector in
                                                       self._control_hub.api_client
                                                       .get_all_registered_sdcs(organization=None,
                                                                                edge=None,
                                                                                label=None,
                                                                                version=None,
                                                                                offset=None,
                                                                                len_=None,
                                                                                order_by=None,
                                                                                order=None).response.json()),
                                          kwargs)
        try:
            return ModelCollectionResults(SeekableList([DataCollector(self._control_hub.api_client.get_sdc(id)
                                                                          .response.json(),
                                                                      self._control_hub)]),
                                          kwargs)
        except requests.exceptions.HTTPError:
            raise ValueError('DataCollector (id={}) not found'.format(id))


class PipelineBuilder(SdcPipelineBuilder):
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Pipeline`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_user_builder`.

    Args:
        pipeline (:obj:`dict`): Python object built from our Swagger PipelineJson definition.
        data_collector_pipeline_builder (:py:class:`streamsets.sdk.sdc_models.PipelineBuilder`): Data Collector Pipeline
                                                                                                 Builder object.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Default: ``None``.
        fragment (:obj:`boolean`, optional): Specify if a fragment builder. Default: ``False``.
    """
    def __init__(self, pipeline, data_collector_pipeline_builder, control_hub=None, fragment=False):
        super().__init__(data_collector_pipeline_builder._pipeline,
                         data_collector_pipeline_builder._definitions,
                         fragment=fragment)
        self._data_collector_pipeline_builder = data_collector_pipeline_builder
        self._sch_pipeline = pipeline
        self._control_hub = control_hub
        self._fragment = fragment
        self._config_key = 'pipelineFragmentConfig' if fragment else 'pipelineConfig'
        self._sch_pipeline['fragment'] = self._fragment

    def build(self, title='Pipeline', **kwargs):
        """Build the pipeline.

        Args:
            title (:obj:`str`): title of the pipeline.

        Returns:
            An instance of :py:class`streamsets.sdk.sch_models.Pipeline`.
        """
        if kwargs.get('build_from_imported'):
            return Pipeline(pipeline=self._sch_pipeline,
                            builder=self,
                            pipeline_definition=json.loads(self._sch_pipeline['pipelineDefinition']),
                            rules_definition=json.loads(self._sch_pipeline['currentRules']['rulesDefinition']),
                            control_hub=self._control_hub)
        sdc_pipeline = super().build(title=title)
        sch_pipeline = (_Pipeline)(pipeline=self._sch_pipeline,
                                   builder=self,
                                   pipeline_definition=sdc_pipeline._data[self._config_key],
                                   rules_definition=sdc_pipeline._data['pipelineRules'],
                                   control_hub=self._control_hub)
        sch_pipeline.name = title
        fragment_commit_ids = sdc_pipeline._data.get('fragmentCommitIds')
        sch_pipeline._data['fragmentCommitIds'] = fragment_commit_ids
        return sch_pipeline


class Pipeline(BaseModel):
    """Model for Pipeline.

    Args:
        pipeline (:obj:`dict`): Pipeline in JSON format.
        builder (:py:class:`streamsets.sdk.sch_models.PipelineBuilder`): Pipeline Builder object.
        pipeline_definition (:obj:`dict`): Pipeline Definition in JSON format.
        rules_definition (:obj:`dict`): Rules Definition in JSON format.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): ControlHub object.
    """
    _REPR_METADATA = ['pipeline_id', 'commit_id', 'name', 'version']
    _ATTRIBUTES_TO_REMAP = {'Labels': 'pipelineLabels'}

    def __init__(self, pipeline, builder, pipeline_definition, rules_definition, control_hub=None):
        super().__init__(pipeline,
                         repr_metadata=Pipeline._REPR_METADATA,
                         attributes_to_remap=Pipeline._ATTRIBUTES_TO_REMAP)
        self._builder = builder
        self._pipeline_definition = pipeline_definition
        self._rules_definition = rules_definition
        self._control_hub = control_hub
        self._parameters = None

    @property
    def configuration(self):
        """Get pipeline's configuration.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Configuration`.
        """
        return Configuration(configuration=self._pipeline_definition['configuration'])

    @property
    def acl(self):
        """Get pipeline ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client.get_pipeline_acl(pipeline_id=self.pipeline_id).response.json(),
                   self._control_hub)

    @acl.setter
    def acl(self, pipeline_acl):
        """Update pipeline ACL.

        Args:
            pipeline_acl (:py:class:`streamsets.sdk.sch_models.ACL`): Pipeline ACL in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdc_api.Command`.
        """
        return self._control_hub.api_client.set_pipeline_acl(pipeline_id=self.pipeline_id,
                                                             pipeline_acl_json=pipeline_acl._data)

    @property
    def stages(self):
        all_stages = {}
        if 'libraryDefinitions' in self._data and self._data['libraryDefinitions']:
            all_stages = SdcPipelineBuilder._generate_all_stages(json.loads(self._data['libraryDefinitions']))
        return SeekableList(all_stages.get(stage['stageName'],
                                           _Stage)(stage=stage, label=stage['stageName'])
                            for stage in self._pipeline_definition['stages']
                            if 'instanceName' in stage and 'stageName' in stage)

    @property
    def error_stage(self):
        all_stages = {}
        if 'libraryDefinitions' in self._data and self._data['libraryDefinitions']:
            all_stages = SdcPipelineBuilder._generate_all_stages(json.loads(self._data['libraryDefinitions']))
        error_stage = self._pipeline_definition['errorStage']
        return (all_stages.get(error_stage['stageName'],
                               _Stage)(stage=error_stage, label=error_stage['stageName'])
                if error_stage else None)

    @property
    def parameters(self):
        """Get the pipeline parameters.

        Returns:
            A dict like, :py:obj:`streamsets.sdk.sch_models.PipelineParameters` object of parameter key-value pairs.
        """
        if self._parameters is None:
            self._parameters = PipelineParameters(self)
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """Create new set of pipeline parameters by replacing existing ones if any.

        Args:
            parameters (:obj:`dict`): A dictionary of key-value parameters to set.
        """
        self.parameters._create(parameters)

    @property
    def stats_aggregator_stage(self):
        all_stages = {}
        if 'libraryDefinitions' in self._data and self._data['libraryDefinitions']:
            all_stages = SdcPipelineBuilder._generate_all_stages(json.loads(self._data['libraryDefinitions']))
        stats_aggregator_stage = self._pipeline_definition.get('statsAggregatorStage')
        return (all_stages.get(stats_aggregator_stage['stageName'],
                               _Stage)(stage=stats_aggregator_stage, label=stats_aggregator_stage['stageName'])
                if stats_aggregator_stage else None)


class PipelineParameters(collections.Mapping):
    """Parameters for pipelines.

    Args:
        pipeline (:py:obj:`streamsets.sdk.sch_models.Pipeline`): Pipeline Instance.
    """
    def __init__(self, pipeline):
        self._store = {parameter['key']: parameter['value'] for parameter in pipeline.configuration['constants']}
        self._pipeline = pipeline

    def update(self, parameters_dict):
        """Update existing parameters. Works similar to Python dictionary update.

        Args:
            parameters_dict (:obj:`dict`): Dictionary of key-value pairs to be used as parameters.
        """
        self._store.update(parameters_dict)
        self._create(self._store)

    def _create(self, parameters_dict):
        """Create a new set of parameters discarding existing ones.

        Args:
            parameters_dict (:obj:`dict`): Dictionary of key-value pairs to be used as parameters.
        """
        self._pipeline.configuration['constants'] = []
        self._store = parameters_dict.copy()
        for key, value in parameters_dict.items():
            self._pipeline.configuration['constants'].append({'key': key, 'value': value})
        self._pipeline._data['pipelineDefinition'] = json.dumps(self._pipeline.pipeline_definition)

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def __repr__(self):
        return str(self._store)


class Pipelines(ModelCollection):
    """Collection of :py:class:`streamsets.sdk.sch_models.Pipeline` instances.

    Args:
        control_hub: An instance of :py:class:`streamsets.sdk.sch.ControlHub`.
        organization (:obj:`str`): Organization Id.
    """

    def __init__(self, control_hub, organization):
        super().__init__(control_hub)
        self._organization = organization
        self._id_attr = 'pipeline_id'

    def _get_all_results_from_api(self, organization=None, label=None, template=False, fragment=False,
                                  using_fragment=None, **kwargs):
        """Args offset, len, order_by, order, system, filter_text, only_published, execution_modes are not exposed
        directly as arguments because of their limited use by normal users but, could still be specified just like any
        other args with the help of kwargs.

        Args:
            organization (:obj:`str`): Organization id of pipeline.
            label (:obj:`str`): Label of pipeline
            template (:obj:`boolean`): Indicate if requesting pipeline templates or pipelines.
            fragment (:obj:`boolean`, optional): Specify if querying for fragments. Default: ``False``.
            using_fragment (:py:obj:`streamsets.sdk.sch_models.Pipeline`, optional): Pipelines using this fragment.
                                                                                     Default: ``None``.
            **kwargs: Optional arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.Pipeline` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        kwargs_defaults = {'offset': None, 'len': None, 'order_by': None, 'order': None, 'system': None,
                           'filter_text': None, 'only_published': None, 'execution_modes': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if label is not None:
            label_id_org = self._organization if organization is None else organization
            pipeline_label_id = '{}:{}'.format(label, label_id_org)
        else:
            pipeline_label_id = None
        if using_fragment:
            fragment_commit_id = using_fragment.commit_id
            pipeline_commit_ids = [pipeline['commitId']
                                   for pipeline in self._control_hub.api_client.get_pipelines_using_fragment(
                                    fragment_commit_id=fragment_commit_id,
                                    offset=kwargs_unioned['offset'],
                                    len=kwargs_unioned['len'],
                                    order_by=kwargs_unioned['order_by'],
                                    order=kwargs_unioned['order']).response.json()['data']]
        elif template:
            pipeline_commit_ids = [pipeline['commitId']
                                   for pipeline in self._control_hub.api_client.return_all_pipeline_templates(
                                    pipeline_label_id=pipeline_label_id,
                                    offset=kwargs_unioned['offset'],
                                    len=kwargs_unioned['len'],
                                    order_by=kwargs_unioned['order_by'],
                                    order=kwargs_unioned['order'],
                                    system=kwargs_unioned['system'],
                                    filter_text=kwargs_unioned['filter_text'],
                                    execution_modes=kwargs_unioned['execution_modes']).response.json()['data']]
        elif fragment:
            pipeline_commit_ids = [pipeline['commitId']
                                   for pipeline in
                                   self._control_hub.
                                   api_client.return_all_pipeline_fragments(organization=organization,
                                                                   pipeline_label_id=pipeline_label_id,
                                                                   offset=kwargs_unioned['offset'],
                                                                   len=kwargs_unioned['len'],
                                                                   order_by=kwargs_unioned['order_by'],
                                                                   order=kwargs_unioned['order'],
                                                                   system=kwargs_unioned['system'],
                                                                   filter_text=kwargs_unioned['filter_text'],
                                                                   only_published=kwargs_unioned['only_published'],
                                                                   execution_modes=kwargs_unioned['execution_modes'])
                                                                   .response.json()['data']]
        else:
            pipeline_commit_ids = [pipeline['commitId']
                                   for pipeline in self._control_hub.api_client.return_all_pipelines(
                                    organization=organization,
                                    pipeline_label_id=pipeline_label_id,
                                    offset=kwargs_unioned['offset'],
                                    len=kwargs_unioned['len'],
                                    order_by=kwargs_unioned['order_by'],
                                    order=kwargs_unioned['order'],
                                    system=kwargs_unioned['system'],
                                    filter_text=kwargs_unioned['filter_text'],
                                    only_published=kwargs_unioned['only_published'],
                                    execution_modes=kwargs_unioned['execution_modes']).response.json()['data']]
        result = SeekableList()
        if pipeline_commit_ids:
            for pipeline in self._control_hub.api_client.get_pipelines_commit(body=pipeline_commit_ids).response.json():
                result.append(Pipeline(pipeline=pipeline,
                                       builder=None,
                                       pipeline_definition=json.loads(pipeline['pipelineDefinition']),
                                       rules_definition=json.loads(pipeline['currentRules']['rulesDefinition']),
                                       control_hub=self._control_hub))
        kwargs_unused = kwargs_instance.subtract()
        return ModelCollectionResults(result, kwargs_unused)


class JobBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Job`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_job_builder`.

    Args:
        job (:obj:`dict`): Python object built from our Swagger JobJson definition.
    """

    def __init__(self, job, control_hub):
        self._job = job
        self._control_hub = control_hub

    def build(self, job_name, pipeline, pipeline_commit_or_tag=None, job_template=False, runtime_parameters=None):
        """Build the job.

        Args:
            job_name (:obj:`str`): Name of the job.
            pipeline (:py:obj:`streamsets.sdk.sch_models.Pipeline`): Pipeline object.
            pipeline_commit_or_tag (:obj:`str`, optional): Default: ``None``, which resolves to the latest pipeline
                                                           commit.
            job_template (:obj:`boolean`, optional): Indicate if it is a Job Template. Default: ``False``.
            runtime_parameters (:obj:`dict`, optional): Runtime Parameters for the Job or Job Template.
                                                        Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        if job_template: assert runtime_parameters is not None, "Please specify atleast one runtime parameter."
        self._job.update({'name': job_name,
                          'pipelineCommitId': pipeline_commit_or_tag or pipeline.commit_id,
                          'pipelineCommitLabel': 'v{}'.format(pipeline.version),
                          'pipelineId': pipeline.pipeline_id,
                          'pipelineName': pipeline.name,
                          'rulesId': pipeline.current_rules['id'],
                          'jobTemplate': job_template,
                          'runtimeParameters': None if runtime_parameters is None else json.dumps(runtime_parameters)})
        return Job(job=self._job, control_hub=self._control_hub)


class JobOffset(BaseModel):
    """Model for offset.

    Args:
        offset (:obj:`dict`): Offset in JSON format.
    """
    _REPR_METADATA = ['sdc_id', 'pipeline_id']
    def __init__(self, offset):
        super().__init__(offset,
                         repr_metadata=JobOffset._REPR_METADATA)


class JobRunEvent(BaseModel):
    """Model for an event in a Job Run.

    Args:
        event (:obj:`dict`): Job Run Event in JSON format.
    """
    _REPR_METADATA = ['user', 'time', 'status']
    def __init__(self, event):
        super().__init__(event,
                         repr_metadata=JobRunEvent._REPR_METADATA)


class JobStatus(BaseModel):
    """Model for Job Status.

    Attributes:
        run_history (:py:class:`streamsets.sdk.utils.SeekableList`) of
                    (:py:class:`streamsets.sdk.utils.JobRunHistoryEvent`): History of a particular job run.
        offsets (:py:class:`streamsets.sdk.utils.SeekableList`) of
                (:py:class:`streamsets.sdk.utils.JobPipelineOffset`): Offsets after the job run.

    Args:
        status (:obj:`dict`): Job status in JSON format.
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Control Hub object.
    """
    _ATTRIBUTES_TO_IGNORE = ['pipeline_offsets']
    _REPR_METADATA = ['id', 'status', 'run_count']

    def __init__(self, status, control_hub):
        super().__init__(status,
                         repr_metadata=JobStatus._REPR_METADATA)
        self._control_hub = control_hub

    @property
    def run_history(self):
        return SeekableList(JobRunEvent(event)
                            for event in self._control_hub.api_client
                                             .get_job_status_history_for_run(self.id).response.json())

    @property
    def offsets(self):
        if 'pipelineOffsets' not in self._data or not self._data['pipelineOffsets']:
            return None
        return SeekableList(JobOffset(pipeline_offset) for pipeline_offset in self._data['pipelineOffsets'])


class JobMetrics(BaseModel):
    """Model for job metrics.

    Attributes:
        output_count (:obj:`dict`): Stage ID to output count map.
        error_count (:obj:`dict`): Stage ID to error count map.

    Args:
        metrics (:obj:`dict`): Metrics counts in JSON format.
    """
    _ATTRIBUTES_TO_REMAP = {'output_count': 'stageIdToOutputCountMap',
                            'error_count': 'stageIdToErrorCountMap'}
    _REPR_METADATA = ['output_count', 'error_count']

    def __init__(self, metrics):
        super().__init__(metrics,
                         repr_metadata=JobMetrics._REPR_METADATA,
                         attributes_to_remap=JobMetrics._ATTRIBUTES_TO_REMAP)


class JobTimeSeriesMetrics(BaseModel):
    """Model for job metrics.

    Attributes:
        input_records (:py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetric`): Appears when queried for
                                                                                   'Record Count Time Series' or
                                                                                   'Record Throughput Time Series'.
        output_records (:py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetric`): Appears when queried for
                                                                                    'Record Count Time Series' or
                                                                                    'Record Throughput Time Series'.
        error_records (:py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetric`): Appears when queried for
                                                                                   'Record Count Time Series' or
                                                                                   'Record Throughput Time Series'.
        batch_counter (:py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetric`): Appears when queried for
                                                                                   'Batch Throughput Time Series'.
        batch_processing_timer (:py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetric`): Appears when queried for
                                                                                            'Batch Processing Timer
                                                                                            seconds'.

    Args:
        metrics (:obj:`dict`): Metrics in JSON format.
    """
    _ATTRIBUTES_TO_REMAP = {'input_records': 'pipeline_batchInputRecords_meter',
                            'output_records': 'pipeline_batchOutputRecords_meter',
                            'error_records': 'pipeline_batchErrorRecords_meter',
                            'batch_counter': 'pipeline_batchCount_meter',
                            'batch_processing_timer': 'stage_batchProcessing_timer'}
    _METRIC_TYPE_ATTRS = {'Record Count Time Series': ['input_records', 'output_records', 'error_records'],
                          'Record Throughput Time Series': ['input_records', 'output_records', 'error_records'],
                          'Batch Throughput Time Series': ['batch_counter'],
                          'Stage Batch Processing Timer seconds': ['batch_processing_timer']}

    def __init__(self, metrics, metric_type):
        data = {}
        repr_metadata = []
        attributes_map_inverted = {v: k for k, v in JobTimeSeriesMetrics._ATTRIBUTES_TO_REMAP.items()}
        for metric in metrics:
            series = metric['series']
            if series:
                name = metric['series'][0]['name']
                remapped_name = attributes_map_inverted[name]
                data[name] = JobTimeSeriesMetric(metric, remapped_name)
                repr_metadata.append(remapped_name)
            else:
                data = {JobTimeSeriesMetrics._ATTRIBUTES_TO_REMAP[attr]: None
                        for attr in JobTimeSeriesMetrics._METRIC_TYPE_ATTRS[metric_type]}
        super().__init__(data,
                         attributes_to_remap=JobTimeSeriesMetrics._ATTRIBUTES_TO_REMAP,
                         repr_metadata=repr_metadata)


class JobTimeSeriesMetric(BaseModel):
    """Model for job metrics.

    Attributes:
        name (:obj:`str`): Name of measurement.
        values (:obj:`list`): Timeseries data.
        time_series (:obj:`dict`): Timeseries data with timestamp as key and metric value as value.

    Args:
        metric (:obj:`dict`): Metrics in JSON format.
    """
    _REPR_METADATA = ['name', 'time_series']
    _ATTRIBUTES_TO_IGNORE = ['columns', 'tags']

    def __init__(self, metric, metric_type):
        if metric.get('error'):
            # Not throwing an exception because if one metric fails, every other metric won't be displayed because of
            # __repr__ of JobTimeSeriesMetrics.
            logger.warning('Fetching metrics for %s failed with error %s', metric_type, metric.get('error'))
        super().__init__(metric['series'][0],
                         repr_metadata=JobTimeSeriesMetric._REPR_METADATA,
                         attributes_to_ignore=JobTimeSeriesMetric._ATTRIBUTES_TO_IGNORE)

    @property
    def time_series(self):
        time_series = {}
        for k, v in self.values:
            time_series[k] = v
        return time_series


class Job(BaseModel):
    """Model for Job.

    Attributes:
        commit_id (:obj:`str`): Pipeline commit id.
        commit_label (:obj:`str`): Pipeline commit label.
        created_by (:obj:`str`): User that created this job.
        created_on (:obj:`int`): Time at which this job was created.
        data_collector_labels (:obj:`list`): Labels of the data collectors.
        description (:obj:`str`): Job description.
        destroyer (:obj:`str`): Job destroyer.
        enable_failover (:obj:`bool`): Flag that indicates if failover is enabled.
        enable_time_series_analysis (:obj:`bool`): Flag that indicates if time series is enabled.
        execution_mode (:obj:`bool`): True for Edge and False for SDC.
        job_deleted (:obj:`bool`): Flag that indicates if this job is deleted.
        job_id (:obj:`str`): Id of the job.
        job_name (:obj:`str`): Name of the job.
        last_modified_by (:obj:`str`): User that last modified this job.
        last_modified_on (:obj:`int`): Time at which this job was last modified.
        number_of_instances (:obj:`int`): Number of instances.
        pipeline_force_stop_timeout (:obj:`int`): Timeout for Pipeline force stop.
        pipeline_id (:obj:`str`): Id of the pipeline that is running the job.
        pipeline_name (:obj:`str`): Name of the pipeline that is running the job.
        pipeline_rule_id (:obj:`str`): Rule Id of the pipeline that is running the job.
        read_policy (:py:obj:`streamsets.sdk.sch_models.ProtectionPolicy`): Read Policy of the job.
        runtime_parameters (:obj:`str`): Run-time parameters of the job.
        statistics_refresh_interval_in_millisecs (:obj:`int`): Refresh interval for statistics in milliseconds.
        status (:obj:`string`): Status of the job.
        write_policy (:py:obj:`streamsets.sdk.sch_models.ProtectionPolicy`): Write Policy of the job.
    """
    _ATTRIBUTES_TO_IGNORE = ['current_job_status', 'delete_time', 'destroyer', 'organization', 'parent_job_id',
                             'provenance_meta_data', 'runtime_parameters', 'system_job_id']
    _ATTRIBUTES_TO_REMAP = {'commit_id': 'pipelineCommitId',
                            'commit_label': 'pipelineCommitLabel',
                            'created_by': 'creator',
                            'created_on': 'createTime',
                            'data_collector_labels': 'labels',
                            'enable_failover': 'migrateOffsets',
                            'enable_time_series_analysis': 'timeSeries',
                            'execution_mode': 'edge',
                            'job_id': 'id',
                            'job_name': 'name',
                            'number_of_instances': 'numInstances',
                            'pipeline_rule_id': 'rulesId',
                            'pipeline_force_stop_timeout': 'forceStopTimeout',
                            'statistics_refresh_interval_in_millisecs': 'statsRefreshInterval',
                            'system_job_id': 'systemJobId'}
    _REPR_METADATA = ['job_id', 'job_name']

    # Container for details about the Data Collector running a job.
    JobDataCollector = collections.namedtuple('JobDataCollector', ['id', 'instance', 'pipeline'])

    def __init__(self, job, control_hub=None):
        super().__init__(job,
                         attributes_to_ignore=Job._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=Job._ATTRIBUTES_TO_REMAP,
                         repr_metadata=Job._REPR_METADATA)
        self._control_hub = control_hub
        self.read_policy = None
        self.write_policy = None

    def refresh(self):
        self._data = self._control_hub.api_client.get_job(self.job_id).response.json()

    @property
    def data_collectors(self):
        data_collectors = SeekableList()
        for pipeline_status in self.pipeline_status:
            id = pipeline_status.sdc_id
            data_collector = self._control_hub.data_collectors.get(id=id)
            id_separator = data_collector.id_separator
            pipeline_id = pipeline_status.name
            if id_separator == '__':
                pipeline_id = pipeline_status.name.replace(':', '__')
            pipeline = data_collector.instance.pipelines.get(id=pipeline_id)
            data_collectors.append(Job.JobDataCollector(id=id, instance=data_collector.instance, pipeline=pipeline))
        return data_collectors

    @property
    def status(self):
        # Newly added jobs have a currentJobStatus of None, so need to be handled accordingly.
        current_job_status = self.current_status
        return current_job_status.status if current_job_status is not None else None

    @property
    def current_status(self):
        current_job_status = self._data['currentJobStatus']
        return JobStatus(current_job_status, self._control_hub) if current_job_status is not None else None

    @property
    def history(self):
        job_statuses = self._control_hub.api_client.get_job_status_history(self.job_id)
        return SeekableList(JobStatus(job_status, self._control_hub) for job_status in job_statuses.response.json())

    @property
    def start_time(self):
        return datetime.fromtimestamp(self._data['currentJobStatus']['startTime']/1000)

    @property
    def pipeline_status(self):
        # We use type to create a trivial class as a container for the dictionaries we get from
        # SCH containing pipeline status.
        PipelineStatus = type('PipelineStatus', (BaseModel,), {})
        return SeekableList(PipelineStatus(pipeline_status, repr_metadata=['sdc_id', 'name'])
                            for pipeline_status in self._data['currentJobStatus']['pipelineStatus'])

    @property
    def runtime_parameters(self):
        return RuntimeParameters(self._data['runtimeParameters'], self)

    @runtime_parameters.setter
    def runtime_parameters(self, value):
        self._data['runtimeParameters'] = json.dumps(value)

    @property
    def acl(self):
        """Get job ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client.get_job_acl(job_id=self.job_id).response.json(), self._control_hub)

    @acl.setter
    def acl(self, job_acl):
        """Update job ACL.

        Args:
            job_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The job ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self._control_hub.api_client.set_job_acl(job_id=self.job_id, job_acl_json=job_acl._data)

    @property
    def system_job(self):
        """Get the sytem Job for this job if exists.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        system_job_id = self._control_hub.jobs.get(job_id=self.job_id).system_job_id
        if system_job_id is not None:
            return self._control_hub.jobs.get(job_id=system_job_id, system=True)

    @property
    def pipeline(self):
        """Get the pipeline object corresponding to this job."""
        return self._control_hub.pipelines.get(commit_id=self._data['pipelineCommitId'])

    def metrics(self, metric_type='RECORD_COUNT', pipeline_version=None, sdc_id=None, time_filter_condition='LATEST',
                include_error_count=False):
        """Get metrics for the job.

        Args:
            metric_type (:obj:`str`, optional): metric_type in {'RECORD_COUNT', 'RECORD_THROUGHPUT'}.
                                                Default: ``'RECORD_COUNT'``.
            pipeline_version (:obj:`str`, optional): Default: ``None``. If default, version is picked as the version of
                                                     the current commit of the pipeline.
            sdc_id (:obj:`str`, optional): Default: ``None``. If default, SDC ID is picked as the Id of the SDC with the
                                           current job run.
            time_filter_condition (:obj:`str`, optional): Default: `LATEST`.
            include_error_count (:obj:`boolean`, optional): Default: `False`.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.JobMetrics`.
        """
        if pipeline_version is None:
            pipeline_version = self.pipeline.version
        if sdc_id is None:
            sdc_id = self._data['currentJobStatus']['sdcIds'][0]
        return JobMetrics(self._control_hub
                              .api_client
                              .get_job_sankey_metrics(job_id=self.job_id,
                                                      metric_type=metric_type,
                                                      pipeline_version=pipeline_version,
                                                      sdc_id=sdc_id,
                                                      time_filter_condition=time_filter_condition,
                                                      include_error_count=include_error_count).response.json())

    def time_series_metrics(self, metric_type, time_filter_condition='LAST_5M', **kwargs):
        """Get historic time series metrics for the job.

        Args:
            time_filter_condition (:obj:`str`, optional): Default: ``'LAST_5M'``.
            metric_type (:obj:`str`): metric type in {'Record Count Time Series', 'Record Throughput Time Series',
                                                      'Batch Throughput Time Series',
                                                      'Stage Batch Processing Timer seconds'}.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.JobTimeSeriesMetrics`.
        """
        def generate_body(column, measurements, self):
            body = []
            for measurement in measurements:
                time_series_query_json = self._time_series_query_json.copy()
                time_series_query_json.update({'columns': [column],
                                               'jobId': self.job_id,
                                               'measurement': measurement,
                                               'pipelineVersion': self.pipeline.version,
                                               'sdcId': self._data['currentJobStatus']['sdcIds'][0]})
                body.append(time_series_query_json)
            return body

        # Swagger for time series does not exist yet (DPM-6328). So, using a static json here.
        self._time_series_query_json = {'columns': None,
                                        'jobId': None,
                                        'measurement': None,
                                        'pipelineVersion': None,
                                        'sdcId': None}
        record_meter_types = ['PIPELINE_BATCH_INPUT_RECORDS_METER', 'PIPELINE_BATCH_OUTPUT_RECORDS_METER',
                              'PIPELINE_BATCH_ERROR_RECORDS_METER']
        metric_type_to_body_params = {'Record Count Time Series': generate_body('count',
                                                                                record_meter_types,
                                                                                self),
                                      'Record Throughput Time Series': generate_body('m1_rate',
                                                                                     record_meter_types,
                                                                                     self),
                                      'Batch Throughput Time Series': generate_body('m1_rate',
                                                                                    ['PIPELINE_BATCH_COUNT_METER'],
                                                                                    self),
                                      'Stage Batch Processing Timer seconds': generate_body(
                                                                                       'mean',
                                                                                       ['STAGE_BATCH_PROCESSING_TIMER'],
                                                                                       self)}
        return JobTimeSeriesMetrics(self._control_hub
                                              .api_client
                                              .get_job_time_series_metrics(metric_type_to_body_params[metric_type],
                                                                          time_filter_condition,
                                                                          **kwargs).response.json(),
                                    metric_type)


class Jobs(ModelCollection):
    """Collection of :py:class:`streamsets.sdk.sch_models.Job` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Control Hub object.
    """

    def __init__(self, control_hub):
        self._control_hub = control_hub
        self._id_attr = 'job_id'

    def _get_all_results_from_api(self, id=None, organization=None, **kwargs):
        """Args order_by, order, removed, system, filter_text, job_status, job_label, edge, len, offset are not exposed
        directly as arguments because of their limited use by normal users but, could still be specified just like any
        other args with the help of kwargs.

        Args:
            id (:obj:`str`).
            organization (:obj:`str`): Organization ID.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.Job` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        kwargs_defaults = {'order_by': 'NAME', 'order': 'ASC', 'removed': False, 'system': False, 'filter_text': None,
                           'job_status': None, 'job_label': None, 'edge': False, 'offset': 0, 'len': -1}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if id is not None:
            try:
                job = self._control_hub.api_client.get_job(id).response.json()
                result = SeekableList([Job(job, self._control_hub)])
            except requests.exceptions.HTTPError:
                raise ValueError('Job (id={}) not found'.format(id))
        else:
            result = SeekableList(Job(job, self._control_hub)
                                  for job in
                                  self._control_hub.
                                  api_client.return_all_jobs(organization=organization,
                                                             order_by=kwargs_unioned['order_by'],
                                                             order=kwargs_unioned['order'],
                                                             removed=kwargs_unioned['removed'],
                                                             system=kwargs_unioned['system'],
                                                             filter_text=kwargs_unioned['filter_text'],
                                                             job_status=kwargs_unioned['job_status'],
                                                             job_label=kwargs_unioned['job_label'],
                                                             edge=kwargs_unioned['edge'],
                                                             offset=kwargs_unioned['offset'],
                                                             len=kwargs_unioned['len']
                                                             ).response.json())
        kwargs_unused = kwargs_instance.subtract()
        return ModelCollectionResults(result, kwargs_unused)


class RuntimeParameters:
    """Wrapper for Control Hub job runtime parameters.

    Args:
        runtime_parameters (:obj:`str`): Runtime parameter.
        job (:py:obj:`streamsets.sdk.sch_models.Job`): Job object.
    """

    def __init__(self, runtime_parameters, job):
        self._data = json.loads(runtime_parameters) if runtime_parameters else {}
        self._job = job

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        self._propagate()

    def update(self, runtime_parameters):
        self._data.update(runtime_parameters)
        self._propagate()

    def _propagate(self):
        self._job._data['runtimeParameters'] = json.dumps(self._data)

    def __repr__(self):
        return str(self._data)

    def __bool__(self):
        return bool(self._data)


class TopologyBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.Topology`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_topology_builder`.

    Args:
        topology (:obj:`dict`): Python object built from our Swagger TopologyJson definition.
    """

    def __init__(self, topology):
        self._topology = topology
        self._default_topology = topology

    def build(self, topology_name, description=None):
        """Build the topology.

        Args:
            topology_name (:obj:`str`): Name of the topology.
            description (:obj:`str`): Description of the topology.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Topology`.
        """
        self._topology.update({'name': topology_name,
                               'description': description})
        return Topology(topology=self._topology)


class Topology(BaseModel):
    """Model for Topology.

    Args:
        topology (:obj:`dict`): JSON representation of Topology.

    Attributes:
        commit_id (:obj:`str`): Pipeline commit id.
        commit_message (:obj:`str`): Commit Message.
        commit_time (:obj:`int`): Time at which commit was made.
        committed_by (:obj:`str`): User that made the commit.
        default_topology (:obj:`bool`): Default Topology.
        description (:obj:`str`): Topology description.
        draft (:obj:`bool`): Indicates whether this topology is a draft.
        last_modified_by (:obj:`str`): User that last modified this topology.
        last_modified_on (:obj:`int`): Time at which this topology was last modified.
        organization (:obj:`str`): Id of the organization.
        parent_version (:obj:`str`): Version of the parent topology.
        topology_definition (:obj:`str`): Definition of the topology.
        topology_id (:obj:`str`): Id of the topology.
        topology_name (:obj:`str`): Name of the topology.
        version (:obj:`str`): Version of this topology.
    """
    _ATTRIBUTES_TO_IGNORE = ['provenanceMetaData']
    _ATTRIBUTES_TO_REMAP = {'committed_by': 'committer',
                            'topology_name': 'name'}
    _REPR_METADATA = ['topology_id', 'topology_name']

    def __init__(self, topology):
        super().__init__(topology,
                         attributes_to_ignore=Topology._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=Topology._ATTRIBUTES_TO_REMAP,
                         repr_metadata=Topology._REPR_METADATA)


class Topologies(ModelCollection):
    """Collection of :py:class:`streamsets.sdk.sch_models.Topology` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): An instance of the Control Hub.
    """

    def __init__(self, control_hub):
        super().__init__(control_hub)
        self._id_attr = 'topology_id'

    def _get_all_results_from_api(self, commit_id=None, organization=None, **kwargs):
        """Args offset, len_, order_by, order are not exposed directly as arguments because of their limited use by
        normal users but, could still be specified just like any other args with the help of kwargs.

        Args:
            commit_id (:obj:`str`)
            organization (:obj:`str`, optional): Default: ``None``.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.Topology` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        kwargs_defaults = {'offset': 0, 'len_': -1, 'order_by': 'NAME', 'order': 'ASC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if commit_id is not None:
            try:
                result = SeekableList(Topology(self._control_hub.api_client
                                               .get_topology_for_commit_id(commit_id=commit_id).response.json()))
            except requests.exceptions.HTTPError:
                raise ValueError('Topology (commit_id={}) not found'.format(commit_id))
        result = SeekableList([Topology(topology)
                               for topology in
                               self._control_hub.api_client.return_all_topologies(organization=organization,
                                                                                  offset=kwargs_unioned['offset'],
                                                                                  len=kwargs_unioned['len_'],
                                                                                  order_by=kwargs_unioned['order_by'],
                                                                                  order=kwargs_unioned['order'])
                                                                                  .response.json()])
        kwargs_unused = kwargs_instance.subtract()
        return ModelCollectionResults(result, kwargs_unused)


class ClassificationRule(UiMetadataBaseModel):
    """Classification Rule Model.

    Args:
        classification_rule (:obj:`dict`): A Python dict representation of classification rule.
        classifiers (:obj:`list`): A list of :py:class:`streamsets.sdk.sch_models.Classifier` instances.
    """
    _ATTRIBUTES_TO_IGNORE = ['classifiers']
    _ATTRIBUTES_TO_REMAP = {}

    def __init__(self, classification_rule, classifiers):
        super().__init__(classification_rule,
                         attributes_to_ignore=ClassificationRule._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=ClassificationRule._ATTRIBUTES_TO_REMAP)
        self.classifiers = classifiers


class Classifier(UiMetadataBaseModel):
    """Classifier model.

    Args:
        classifier (:obj:`dict`): A Python dict representation of classifier.
    """
    _ATTRIBUTES_TO_IGNORE = ['patterns']
    _ATTRIBUTES_TO_REMAP = {'case_sensitive': 'sensitive',
                            'match_with': 'type',
                            'regular_expression_type': 'implementationClassValue', }

    # From https://git.io/fA0w2.
    MATCH_WITH_ENUM = {'Field Path': 'FIELD_PATH',
                       'Field Value': 'FIELD_VALUE'}

    # From https://git.io/fA0w4.
    REGULAR_EXPRESSION_TYPE_ENUM = {'RE2/J': 'RE2J_MATCHER',
                                    'Java Regular Expression': 'REGEX_MATCHER'}

    def __init__(self, classifier):
        super().__init__(classifier,
                         attributes_to_ignore=Classifier._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=Classifier._ATTRIBUTES_TO_REMAP)

    @property
    def patterns(self):
        return [pattern['value'] for pattern in self._data['patterns']]

    @patterns.setter
    def patterns(self, values):
        self._data['patterns'] = [{'messages': [],
                                   'type': 'RSTRING',
                                   'value': value,
                                   'scrubbed': False}
                                  for value in values]

    @property
    def _id(self):
        return self._data['id']

    @_id.setter
    def _id(self, value):
        self._data['id'] = value

    @property
    def _rule_uuid(self):
        return self._data['ruleUuid']

    @_rule_uuid.setter
    def _rule_uuid(self, value):
        self._data['ruleUuid'] = value

    @property
    def _uuid(self):
        return self._data['uuid']

    @_uuid.setter
    def _uuid(self, value):
        self._data['uuid'] = value


class ClassificationRuleBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.ClassificationRule`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_classification_rule_builder`.

    Args:
        classification_rule (:obj:`dict`): Python object defining a classification rule.
        classifier (:obj:`dict`): Python object defining a classifier.
    """

    def __init__(self, classification_rule, classifier):
        self._classification_rule = classification_rule
        self._classifier = classifier
        self.classifiers = []

    def add_classifier(self, patterns=None, match_with=None,
                       regular_expression_type='RE2/J', case_sensitive=False):
        """Add classifier to the classification rule.

        Args:
            patterns (:obj:`list`, optional): List of strings of patterns. Default: ``None``.
            match_with (:obj:`str`, optional): Default: ``None``.
            regular_expression_type (:obj:`str`, optional): Default: ``'RE2/J'``.
            case_sensitive (:obj:`bool`, optional): Default: ``False``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Classifier`.
        """
        classifier = Classifier(classifier=copy.deepcopy(self._classifier))
        classifier.patterns = patterns or ['.*']
        classifier.match_with = Classifier.MATCH_WITH_ENUM.get(match_with) or 'FIELD_PATH'
        classifier.regular_expression_type = Classifier.REGULAR_EXPRESSION_TYPE_ENUM.get(regular_expression_type)
        classifier.case_sensitive = case_sensitive

        classifier._uuid = str(uuid.uuid4())
        classifier._id = '{}:1'.format(classifier._uuid)
        classifier._rule_uuid = self._classification_rule['uuid']
        self.classifiers.append(classifier)
        return classifier

    def build(self, name, category, score):
        """Build the classification rule.

        Args:
            name (:obj:`str`): Classification Rule name.
            category (:obj:`str`): Classification Rule category.
            score (:obj:`float`): Classification Rule score.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ClassificationRule`.
        """
        classification_rule = ClassificationRule(classification_rule=self._classification_rule,
                                                 classifiers=self.classifiers)
        classification_rule.name = name
        classification_rule.category = category
        classification_rule.score = score
        return classification_rule


class ProtectionPolicy(UiMetadataBaseModel):
    """Model for Protection Policy.

    Args:
        protection_policy (:obj:`dict`): JSON representation of Protection Policy.
        procedures (:obj:`list`): A list of :py:class:`streamsets.sdk.sch_models.PolicyProcedure` instances,
                    Default: ``None``.
    """
    _ATTRIBUTES_TO_IGNORE = ['enactment', 'procedures']
    _ATTRIBUTES_TO_REMAP = {}
    _REPR_METADATA = ['name', 'enactment']

    ENACTMENT_ENUM = {'Read': 'READ',
                      'Write': 'WRITE'}

    def __init__(self, protection_policy, procedures=None):
        super().__init__(protection_policy,
                         attributes_to_ignore=ProtectionPolicy._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=ProtectionPolicy._ATTRIBUTES_TO_REMAP,
                         repr_metadata=ProtectionPolicy._REPR_METADATA)
        self.procedures = procedures

    @property
    def _id(self):
        return self._data['id']

    @_id.setter
    def _id(self, value):
        self._data['id'] = value

    @property
    def enactment(self):
        return next(k
                    for k, v in ProtectionPolicy.ENACTMENT_ENUM.items()
                    if v == self._data['enactment']['value'])

    @enactment.setter
    def enactment(self, value):
        self._data['enactment']['value'] = value


class ProtectionPolicies(ModelCollection):
    """Collection of :py:class:`streamsets.sdk.sch_models.ProtectionPolicy` instances."""

    def _get_all_results_from_api(self, **kwargs):
        """
        Args:
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.ProtectionPolicy` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        protection_policies = []
        response = self._control_hub.api_client.get_protection_policy_list().response.json()['response']
        for protection_policy in response:
            protection_policy['data'].pop('messages', None)
            protection_policies.append(ProtectionPolicy(protection_policy['data']))
        return ModelCollectionResults(SeekableList(protection_policies), kwargs)


class ProtectionPolicyBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.ProtectionPolicy`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_protection_policy_builder`.

    Args:
        protection_policy (:obj:`dict`): Python object defining a protection policy.
        policy_procedure (:obj:`dict`): Python object defining a policy procedure.
    """

    def __init__(self, protection_policy, policy_procedure):
        self._protection_policy = protection_policy
        self._policy_procedure = policy_procedure
        self.procedures = []

    def add_procedure(self, classification_score_threshold=0.5, procedure_basis='Category Pattern',
                      classification_category_pattern=None, field_path=None, protection_method=None):
        procedure = PolicyProcedure(policy_procedure=copy.deepcopy(self._policy_procedure))
        procedure.classification_score_threshold = classification_score_threshold
        procedure.procedure_basis = PolicyProcedure.PROCEDURE_BASIS_ENUM.get(procedure_basis)
        if procedure_basis == 'Category Pattern':
            procedure.classification_category_pattern = classification_category_pattern
        elif procedure_basis == 'Field Path':
            procedure.field_path = field_path
        # https://git.io/fAE0K
        procedure.protection_method = json.dumps({'issues': None,
                                                  'schemaVersion': 1,
                                                  'stageConfiguration': protection_method._data})

        self.procedures.append(procedure)

    def build(self, name, enactment):
        protection_policy = ProtectionPolicy(self._protection_policy, self.procedures)
        protection_policy.name = name
        protection_policy.enactment = ProtectionPolicy.ENACTMENT_ENUM.get(enactment)

        return protection_policy


class PolicyProcedure(UiMetadataBaseModel):
    """Model for Policy Procedure.

    Args:
        policy_procedure (:obj:`dict`): JSON representation of Policy Procedure.
    """
    PROCEDURE_BASIS_ENUM = {'Category Pattern': 'CATEGORY_PATTERN',
                            'Field Path': 'FIELD_PATH'}

    _ATTRIBUTES_TO_IGNORE = ['id', 'optimisticLockVersion', 'version']
    _ATTRIBUTES_TO_REMAP = {'classification_category_pattern': 'classificationCategory',
                            'classification_score_threshold': 'threshold',
                            'procedure_basis': 'subjectType',
                            'protection_method': 'transformerConfig'}

    def __init__(self, policy_procedure):
        super().__init__(policy_procedure,
                         attributes_to_ignore=PolicyProcedure._ATTRIBUTES_TO_IGNORE,
                         attributes_to_remap=PolicyProcedure._ATTRIBUTES_TO_REMAP)

    @property
    def _id(self):
        return self._data['id']

    @_id.setter
    def _id(self, value):
        self._data['id'] = value

    @property
    def _policy_id(self):
        return self._data['policyId']

    @_policy_id.setter
    def _policy_id(self, value):
        self._data['policyId'] = value


class ProtectionMethod(Stage):
    """Protection Method Model.

    Args:
        stage (:obj:`dict`): JSON representation of a stage.
    """
    STAGE_LIBRARY = 'streamsets-datacollector-dataprotector-lib'

    def __init__(self, stage):
        super().__init__(stage, label=stage['uiInfo']['label'])


class ProtectionMethodBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.ProtectionMethod`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_protection_method_builder`.

    Args:
        pipeline_builder (:py:class:`streamsets.sdk.sch_models.PipelineBuilder`): Pipeline Builder object.
    """

    def __init__(self, pipeline_builder):
        self._pipeline_builder = pipeline_builder

    def build(self, method):
        method_stage = self._pipeline_builder.add_stage(
            label=method, library=ProtectionMethod.STAGE_LIBRARY)
        # We generate a single output lane to conform to SDP's expectations for detached stages.
        method_stage.add_output()
        protection_method = type(method_stage.stage_name,
                                 (ProtectionMethod,),
                                 {'_attributes': method_stage._attributes})
        return protection_method(method_stage._data)


class ReportDefinitions(ModelCollection):
    """Collection of :py:class:`streamsets.sdk.sch_models.ReportDefinition` instances."""

    def _get_all_results_from_api(self, organization=None, **kwargs):
        """Args order_by, order, filter_text, len, offset are not exposed directly as arguments because of their limited
        use by normal users but, could still be specified just like any other args with the help of kwargs.

        Args:
            organization (:obj:`str`): Organization Id.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.ReportDefinition` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        kwargs_defaults = {'order_by': 'NAME', 'order': 'ASC', 'filter_text': None, 'offset': 0, 'len': -1}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        result = SeekableList(ReportDefinition(report_definition, self._control_hub)
                              for report_definition in
                              self._control_hub.api_client.
                              return_all_report_definitions(organization=organization,
                                                            offset=kwargs_unioned['offset'],
                                                            len=kwargs_unioned['len'],
                                                            order_by=kwargs_unioned['order_by'],
                                                            order=kwargs_unioned['order'],
                                                            filter_text=kwargs_unioned['filter_text'])
                                                            .response.json()['data'])
        kwargs_unused = kwargs_instance.subtract()
        return ModelCollectionResults(result, kwargs_unused)


class ReportDefinition(BaseModel):
    """Model for Report Definition.

    Args:
        report_definition (:obj:`dict`): JSON representation of Report Definition.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """
    _REPR_METADATA = ['id', 'name']

    def __init__(self, report_definition, control_hub):
        super().__init__(report_definition, repr_metadata=ReportDefinition._REPR_METADATA)
        self._control_hub = control_hub

    @property
    def reports(self):
        """Get Reports of the Report Definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Reports`.
        """
        return Reports(self._control_hub, self.id)

    @property
    def report_resources(self):
        """Get Report Resources of the Report Definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ReportResources`.
        """
        return ReportResources(self._data['reportArtifacts'], self)

    def generate_report(self):
        """Generate a Report for Report Definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Report`.
        """
        trigger_time = int(round(time.time() * 1000))
        return GenerateReportCommand(self._control_hub,
                                     self,
                                     self._control_hub.api_client
                                     .generate_report_for_report_definition(self.id, trigger_time).response.json())

    @property
    def acl(self):
        """Get Report Definition ACL.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ACL`.
        """
        return ACL(self._control_hub.api_client
                       .get_report_definition_acl(report_definition_id=self.id).response.json(), self._control_hub)

    @acl.setter
    def acl(self, report_definition_acl):
        """Update Report Definition ACL.

        Args:
            report_definition_acl (:py:class:`streamsets.sdk.sch_models.ACL`): The Report Definition ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return (self._control_hub.api_client
                    .set_report_definition_acl(report_definition_id=self.id,
                                               report_definition_acl_json=report_definition_acl._data))


class GenerateReportCommand:
    """Command to interact with the response from generate_report.

    Args:
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
        report_definition (:obj:`dict`): JSON representation of Report Definition.
        response (:obj:`dict`): Api response from generating the report.
    """
    def __init__(self, control_hub, report_defintion, response):
        self._control_hub = control_hub
        self._report_defintion = report_defintion
        self.response = response

    @property
    def report(self):
        report = self._report_defintion.reports.get(id=self.response['id'])
        self.response = report._data
        if report.report_status == 'REPORT_TO_BE_GENERATED':
            logger.warning('Report is still being generated...')
        elif report.report_status == 'REPORT_SUCCESS':
            return Report(report, self._control_hub, self._report_defintion.id)
        else:
            raise Exception('Report generation failed with status {}'.format(report.report_status))


class ReportResources:
    """Model for the collection of Report Resources.

    Args:
        report_resources (:obj:`list`): List of Report Resources.
        report_definition (:py:class:`streamsets.sdk.sch_models.ReportDefinition`): Report Definition object.
    """
    def __init__(self, report_resources, report_definition):
        self._report_resources = SeekableList(ReportResource(report_resource) for report_resource in report_resources)
        self._report_definition = report_definition

    def get(self, **kwargs):
        return self._report_resources.get(**kwargs)

    def get_all(self, **kwargs):
        return self._report_resources.get_all(**kwargs)

    def __iter__(self):
        for report_resource in self._report_resources:
            yield report_resource

    def __len__(self):
        return len(self._report_resources)

    def __getitem__(self, i):
        return self._report_resources[i]

    def __contains__(self, resource):
        """Check if given resource is in Report Definition resources.

        Args:
            resource (:py:class:streamsets.sdk.sch_models.Job) or (:py:class:streamsets.sdk.sch_models.Topology)

        Returns:
            A :obj:`boolean` indicating if the resource exists.
        """
        assert isinstance(resource, Job) or isinstance(resource, Topology), "Only Job and Topology are supported"
        if isinstance(resource, Job):
            resource_id = resource.job_id
            resource_type = 'JOB'
        else:
            resource_id = resource.commit_id
            resource_type = 'TOPOLOGY'
        for resource in self._report_resources:
            if resource.resource_id == resource_id and resource.resource_type == resource_type:
                return True
        return False

    def __repr__(self):
        return str(self._report_resources)


class ReportResource(BaseModel):
    """Model for Report Resource.

    Args:
        report_resource (:obj:`dict`): JSON representation of Report Resource.
    """
    _REPR_METADATA = ['resource_type', 'resource_id']

    def __init__(self, report_resource):
        super().__init__(report_resource, repr_metadata=ReportResource._REPR_METADATA)


class ReportDefinitionBuilder:
    """Class with which to build instances of :py:class:`streamsets.sdk.sch_models.ReportDefinition`.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_report_definition_builder`.

    Args:
        report_definition (:obj:`dict`): JSON representation of Report Definition.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """

    def __init__(self, report_definition, control_hub):
        self._report_definition = report_definition
        self._report_resources = SeekableList()
        self._control_hub = control_hub

    def import_report_definition(self, report_definition):
        """Import an existing Report Definition to update it.

        Args:
            report_definition (:py:class:`streamsets.sdk.sch_models.ReportDefinition`): Report Definition object.
        """
        self._report_definition = report_definition._data
        self._report_resources = SeekableList(ReportResource(report_resource)
                                              for report_resource in report_definition._data['reportArtifacts'])

    def set_data_retrieval_period(self, start_time, end_time):
        """Set Time range over which the report will be generated.

        Args:
            start_time (:obj:`str`) or (:obj:`int`): Absolute or relative start time for the Report.
            end_time (:obj:`str`) or (:obj:`int`): Absolute or relative end time for the Report.
        """
        self._report_definition.update({'startTime': start_time,
                                        'endTime': end_time})

    def add_report_resource(self, resource):
        """Add a given resource to Report Definition resources.

        Args:
            resource (:py:class:`streamsets.sdk.sch_models.Job`) or (:py:class:`streamsets.sdk.sch_models.Topology`)
        """
        if isinstance(resource, Job):
            self._report_resources.append(ReportResource({'resourceId': resource.job_id,
                                                          'resourceType': 'JOB'}))
        elif isinstance(resource, Topology):
            self._report_resources.append(ReportResource({'resourceId': resource.commit_id,
                                                          'resourceType': 'TOPOLOGY'}))
        if self._report_definition is not None:
            self._report_definition['reportArtifacts'] = SeekableList(report_resource._data
                                                                            for report_resource in
                                                                            self._report_resources)

    def remove_report_resource(self, resource):
        """Remove a resource from Report Definition Resources.

        Args:
            resource (:py:class:`streamsets.sdk.sch_models.Job`) or (:py:class:`streamsets.sdk.sch_models.Topology`)

        Returns:
            A resource of type :py:obj:`dict` that is removed from Report Definition Resources.
        """
        if isinstance(resource, Job):
            resource_type = 'JOB'
            resource_id = resource.job_id
        elif isinstance(resource, Topology):
            resource_type = 'TOPOLOGY'
            resource_id = resource.commit_id

        popped = self._report_resources.get(resource_type=resource_type,
                                            resource_id=resource_id)
        self._report_resources = SeekableList(i for i in self._report_resources if any(getattr(i, k) != v
                                              for k, v in popped._data.items()))
        if self._report_definition is not None:
            self._report_definition['reportArtifacts'] = SeekableList(report_resource._data
                                                                            for report_resource in
                                                                            self._report_resources)
        return popped

    def build(self, name, description=None):
        """Build the report definition.

        Args:
            name (:obj:`str`): Name of the Report Definition.
            description (:obj:`str`, optional): Description of the Report Definition. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ReportDefinition`.
        """
        self._report_definition.update({'name': name,
                                        'description': description})
        return ReportDefinition(self._report_definition, self._control_hub)


class Reports(ModelCollection):
    """Collection of :py:class:`streamsets.sdk.sch_models.Report` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Control Hub object.
        report_definition_id (:obj:`str`): Report Definition Id.
    """

    def __init__(self, control_hub, report_definition_id):
        self._control_hub = control_hub
        self._report_definition_id = report_definition_id

    def _get_all_results_from_api(self, id=None, **kwargs):
        """Get Reports belonging to a Report Definition. Args offset, len are not exposed directly as arguments because
        of their limited use by normal users but, could still be specified just like any other args with the help of
        kwargs.

        Args:
            id (:obj:`str`, optional): Report Id. Default: ``None``. If specified, only that particular report is
                                       fetched from control hub. If not, all reports belonging to this Report Definition
                                       will be fetched and other filters will be applied later.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.Report` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        kwargs_defaults = {'offset': 0, 'len': -1}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        if self._report_definition_id is not None:
            if id is None:
                report_ids = [report['id']
                              for report in
                              self._control_hub.api_client
                              .return_all_reports_from_definition(report_definition_id=self._report_definition_id,
                                                                  offset=kwargs_unioned['offset'],
                                                                  len=kwargs_unioned['len']).response.json()['data']]
            else:
                report_ids = [id]
            result = SeekableList(Report(self._control_hub.api_client
                                         .get_report_for_given_report_id(self._report_definition_id,
                                                                         report_id).response.json(),
                                         self._control_hub,
                                         self._report_definition_id)
                                  for report_id in report_ids)
        else:
            result = SeekableList()
        kwargs_unused = kwargs_instance.subtract()
        return ModelCollectionResults(result, kwargs_unused)


class Report(BaseModel):
    """Model for Report.

    Args:
        report (:obj:`dict`): JSON representation of Report.
    """
    _REPR_METADATA = ['id', 'name']

    def __init__(self, report, control_hub, report_definition_id):
        super().__init__(report, repr_metadata=Report._REPR_METADATA)
        self._control_hub = control_hub
        self._report_definition_id = report_definition_id

    def download(self):
        """Download the Report in PDF format

        Returns:
            An instance of :obj:`bytes`.
        """
        return self._control_hub.api_client.download_report(self._report_definition_id, self.id, 'PDF').response.content


class ScheduledTaskBaseModel(BaseModel):
    """Base Model for Scheduled Task related classes."""

    def __getattr__(self, name):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            return (self._data[remapped_name]['value']
                   if 'value' in self._data[remapped_name] else self._data[remapped_name])
        elif (name_ in self._data and
              name not in self._attributes_to_ignore and
              name not in self._attributes_to_remap.values()):
            return self._data[name_]['value'] if 'value' in self._data[name_] else self._data[name_]
        raise AttributeError('Could not find attribute {}.'.format(name_))

    def __setattr__(self, name, value):
        name_ = python_to_json_style(name)
        if name in self._attributes_to_remap:
            remapped_name = self._attributes_to_remap[name]
            if 'value' in self._data[remapped_name]:
                self._data[remapped_name]['value'] = value
            else:
                self._data[remapped_name] = value
        elif (name_ in self._data and
              name not in self._attributes_to_ignore and
              name not in self._attributes_to_remap.values()):
            if 'value' in self._data[name_]:
                self._data[name_]['value'] = value
            else:
                self._data[name_] = value
        else:
            super().__setattr__(name, value)


class ScheduledTaskBuilder:
    """Builder for Scheduled Task.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_scheduled_task_builder`.

    Args:
        job_selection_types (:py:obj:`dict`): JSON representation of job selection types.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """

    def __init__(self, job_selection_types, control_hub):
        self._job_selection_types = job_selection_types
        self._control_hub = control_hub

    def build(self, task_object, action='START', name=None, description=None, cron_expression='0 0 1/1 * ? *',
              time_zone='UTC', status='RUNNING', start_time=None, end_time=None, missed_execution_handling='IGNORE'):
        """Builder for Scheduled Task.

        Args:
            task_object (:py:class:`streamsets.sdk.sch_models.Job`) or
                        (:py:class:`streamsets.sdk.sch_models.ReportDefinition`): Job or ReportDefinition object.
            action (:obj:`str`, optional): One of the {'START', 'STOP', 'UPGRADE'} actions. Default: ``START``.
            name (:obj:`str`, optional): Name of the task. Default: ``None``.
            description (:obj:`str`, optional): Description of the task. Default: ``None``.
            crontab_mask (:obj:`str`, optional): Schedule in cron syntax. Default: ``"0 0 1/1 * ? *"``. (Daily at 12).
            time_zone (:obj:`str`, optional): Time zone. Default: ``"UTC"``.
            status (:obj:`str`, optional): One of the {'RUNNING', 'PAUSED'} statuses. Default: ``RUNNING``.
            start_time (:obj:`str`, optional): Start time of task. Default: ``None``.
            end_time (:obj:`str`, optional): End time of task. Default: ``None``.
            missed_trigger_handling (:obj:`str`, optional): One of {'IGNORE', 'RUN ALL', 'RUN ONCE'}.
                                                            Default: ``IGNORE``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ScheduledTask`.
        """
        assert isinstance(task_object, Job) or isinstance(task_object, ReportDefinition), \
               "Only Job and ReportDefinition are supported"
        params = get_params(parameters=locals(), exclusions=('self', 'task_object', 'action'))

        if isinstance(task_object, Job):
            self._job_selection_types['jobId']['value'] = task_object.job_id
            self._job_selection_types['jobName']['value'] = task_object.job_name
            self._job_selection_types['type']['value'] = 'PIPELINE_JOB'
        else:
            self._job_selection_types['reportId']['value'] = task_object.id
            self._job_selection_types['reportName']['value'] = task_object.name
            self._job_selection_types['type']['value'] = 'REPORT_JOB'
        _response = self._control_hub.api_client.trigger_selection_info(data={'data': self._job_selection_types},
                                                                        api_version=2)
        task = _response.response.json()['response']['data']

        for key, value in params.items():
            if json_to_python_style(key) in ScheduledTask._ATTRIBUTES_TO_REMAP:
                key = ScheduledTask._ATTRIBUTES_TO_REMAP[json_to_python_style(key)]
            task[key]['value'] = value

        return ScheduledTask(task, self._control_hub)


class ScheduledTask(ScheduledTaskBaseModel):
    """Model for Scheduled Task.

    Args:
        task (:py:obj:`dict`): JSON representation of task.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """
    _REPR_METADATA = ['id', 'name', 'status']
    _ATTRIBUTES_TO_REMAP = {'cron_expression': 'crontabMask',
                            'missed_execution_handling': 'missedTriggerHandling'}

    def __init__(self, task, control_hub=None):
        super().__init__(task,
                         repr_metadata=ScheduledTask._REPR_METADATA,
                         attributes_to_remap=ScheduledTask._ATTRIBUTES_TO_REMAP)
        self._control_hub = control_hub
        self._allowed_actions = {'PAUSE', 'RESUME', 'KILL', 'DELETE'}
        # With this we would be able to call actions like task.pause(), task.kill(), task.resume() and task.delete()
        for action in self._allowed_actions:
            setattr(self, action.lower(), partial(self._perform_action, action=action))

    @property
    def runs(self):
        """Get Scheduled Task Runs.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of inherited instances of
            :py:class:`streamsets.sdk.sch_models.ScheduledTaskRun`.
        """
        _repsonse = self._control_hub.api_client.get_scheduled_task(id=self.id,
                                                                    run_info=True,
                                                                    audit_info=False,
                                                                    api_version=2)
        runs = _repsonse.response.json()['response']['data']['runs']
        return SeekableList(ScheduledTaskRun(run) for run in runs)

    @property
    def audits(self):
        """Get Scheduled Task Audits.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of inherited instances of
            :py:class:`streamsets.sdk.sch_models.ScheduledTaskAudit`.
        """
        _response = self._control_hub.api_client.get_scheduled_task(id=self.id,
                                                                    run_info=False,
                                                                    audit_info=True,
                                                                    api_version=2)
        audits = _response.response.json()['response']['data']['audits']
        return SeekableList(ScheduledTaskAudit(audit) for audit in audits)

    def _perform_action(self, action):
        """Perform a specified action on this scheduled task.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ScheduledTask`.
        """
        assert action in self._allowed_actions
        response = self._control_hub.api_client.perform_action_on_scheduled_task(self.id,
                                                                                 action,
                                                                                 api_version=2).response.json()
        updated_task = response['response']['data']
        self._data = updated_task
        return self


class ScheduledTasks(ModelCollection):
    """Collection of :py:class:`streamsets.sdk.sch_models.ScheduledTask` instances."""

    def _get_all_results_from_api(self, **kwargs):
        """Args order_by, offset, len are not exposed directly as arguments because of their limited use by normal
        users but, could still be specified just like any other args with the help of kwargs.

        Args:
            **kwargs: Optional other arguments to be passed to filter the results.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.ScheduledTask` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        kwargs_defaults = {'offset': None, 'len': None, 'order_by': None}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        tasks = self._control_hub.api_client.get_scheduled_tasks(kwargs_unioned['order_by'],
                                                                 kwargs_unioned['offset'],
                                                                 kwargs_unioned['len'],
                                                                 api_version=2).response.json()['response']
        result = SeekableList(ScheduledTask(task['data'], self._control_hub) for task in tasks)
        kwargs_unused = kwargs_instance.subtract()
        return ModelCollectionResults(result, kwargs_unused)


class ScheduledTaskRun(ScheduledTaskBaseModel):
    """Scheduled Task Run.

    Args:
        run (:py:obj:`dict`): JSON representation if scheduled task run.
    """
    _REPR_METADATA = ['id', 'scheduledTime']

    def __init__(self, run):
        super().__init__(run,
                         repr_metadata=ScheduledTaskRun._REPR_METADATA)


class ScheduledTaskAudit(ScheduledTaskBaseModel):
    """Scheduled Task Audit.

    Args:
        run (:py:obj:`dict`): JSON representation of scheduled task audit.
    """
    _REPR_METADATA = ['id', 'action']

    def __init__(self, audit):
        super().__init__(audit,
                         repr_metadata=ScheduledTaskAudit._REPR_METADATA)


class Subscription(BaseModel):
    """Subscription.

    Args:
        subscription (:obj:`dict`): JSON representation of Subscription.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """
    _REPR_METADATA = ['id', 'name']

    def __init__(self, subscription, control_hub):
        super().__init__(subscription,
                         repr_metadata=Subscription._REPR_METADATA)
        self._control_hub = control_hub

    @property
    def events(self):
        """Events of the Subscription."""

        return SeekableList(SubscriptionEvent(event, self._control_hub) for event in self._data['events'])

    @property
    def action(self):
        """Action of the Subscription."""
        return SubscriptionAction(self._data['externalActions'][0])


class SubscriptionAction(BaseModel):
    """Action to take when the Subscription is triggered.

    Args:
        action (:obj:`dict`): JSON representation of an Action for a Subscription.
    """
    _REPR_METADATA = ['event_type']

    def __init__(self, action):
        super().__init__(action,
                         repr_metadata=SubscriptionAction._REPR_METADATA)
        self.config = json.loads(self.config) if isinstance(self.config, str) else self.config


class SubscriptionEvent(BaseModel):
    """An Event of a Subscription.

    Args:
        event (:obj:`dict`): JSON representation of Events of a Subscription.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """
    _REPR_METADATA = ['event_type', 'filter']

    def __init__(self, event, control_hub):
        event_types = control_hub._en_translations['notifications']['subscriptions']['events']
        if event['eventType'] in event_types:
            event['eventType'] = event_types[event['eventType']]
        super().__init__(event,
                         repr_metadata=SubscriptionEvent._REPR_METADATA)


class Subscriptions(ModelCollection):
    """Collection of :py:class:`streamsets.sdk.sch_models.Subscription` instances.

    Args:
        control_hub (:py:class:`streamsets.sdk.sch.ControlHub`): Control Hub object.
    """

    def _get_all_results_from_api(self, organization=None, **kwargs):
        """Args offset, len, orderBy, order are not exposed directly as arguments because of their limited use by normal
        users but, could still be specified just like any other args with the help of kwargs.

        Args:
            organization (:obj:`str`): Organization ID.
            **kwargs: Optional other arguments to be passed to filter the results offline.

        Returns:
            A :obj:`collections.namedtuple`: of
                results (:py:class:`streamsets.sdk.utils.SeekableList`): a SeekableList of
                :py:class:`streamsets.sdk.sch_models.Subscription` instances and
                kwargs (:obj:`dict`): a dict of local variables not used in this function.
        """
        kwargs_defaults = {'offset': 0, 'len': -1, 'order_by': 'NAME', 'order': 'ASC'}
        kwargs_instance = MutableKwargs(kwargs_defaults, kwargs)
        kwargs_unioned = kwargs_instance.union()
        result = SeekableList(Subscription(subscription, self._control_hub)
                              for subscription in
                              self._control_hub.
                              api_client.get_all_event_subscriptions(organization=organization,
                                                                     offset=kwargs_unioned['offset'],
                                                                     len=kwargs_unioned['len'],
                                                                     order_by=kwargs_unioned['order_by'],
                                                                     order=kwargs_unioned['order']).response.json())
        kwargs_unused = kwargs_instance.subtract()
        return ModelCollectionResults(result, kwargs_unused)


class SubscriptionBuilder:
    """Builder for Subscription.

    Instead of instantiating this class directly, most users should use
        :py:meth:`streamsets.sdk.sch.ControlHub.get_subscription_builder`.

    Args:
        subscription (:py:obj:`dict`): JSON representation of event subscription.
        control_hub (:py:class:`streamsets.sdk.ControlHub`): Control Hub instance.
    """

    def __init__(self, subscription, control_hub):
        self._subscription = subscription
        self._events = SeekableList()
        self._action = {}
        self._control_hub = control_hub

    def add_event(self, event_type, filter=None):
        """Add event to the Subscription.

        Args:
            event_type (:obj:`str`): Type of event in {'Job Status Change', 'Data SLA Triggered', 'Pipeline Committed',
                                                       'Pipeline Status Change', 'Report Generated',
                                                       'Data Collector not Responding'}.
            filter (:obj:`str`, optional): Filter to be applied on event. Default: ``None``.
        """
        event = {'eventType': event_type, 'filter': filter}
        if self._subscription is not None: self._subscription['events'].append(event)
        self._events.append(SubscriptionEvent(event, self._control_hub))

    def remove_event(self, event_type):
        """Remove event from the subscription.

        Args:
            event_type (:obj:`str`): Type of event in {'Job Status Change', 'Data SLA Triggered', 'Pipeline Committed',
                                                       'Pipeline Status Change', 'Report Generated',
                                                       'Data Collector not Responding'}.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.SubscriptionEvent`.
        """
        popped = self._events.get(event_type=event_type)
        self._events = SeekableList(i for i in self._events if getattr(i, 'event_type') != event_type)
        if self._subscription is not None:
            self._subscription['events'] = [i for i in self._subscription['events'] if i.get(event_type) != event_type]
        return popped

    def import_subscription(self, subscription):
        """Import an existing Subscription into the builder to update it.

        Args:
            subscription (:py:class:`streamsets.sdk.sch_models.Subscription`): Subscription instance.
        """
        self._subscription = subscription._data
        self._events = SeekableList(SubscriptionEvent(event,
                                                      self._control_hub) for event in subscription._data['events'])
        self._action = subscription._data['externalActions'][0]

    def set_email_action(self, recipients, subject=None, body=None):
        """Set the Email action.

        Args:
            recipients (:obj:`list`): List of email addresses.
            subject (:obj:`str`, optional): Subject of the email. Default: ``None``.
            body (:obj:`str`, optional): Body of the email. Default: ``None``.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        params['recipients'] = ','.join(params['recipients'])
        self._action.update({'eventType': 'EMAIL',
                             'config': params})

    def set_webhook_action(self, uri, method='GET', content_type=None, payload=None, auth_type=None, username=None,
                           password=None, timeout=30000, headers=None):
        """Set the Webhook action.

        Args:
            uri (:obj:`str`): URI for the Webhook.
            method (:obj:`str`, optional): HTTP method to use. Default: ``'GET'``.
            content_type (:obj:`str`, optional): Content Type of the request. Default:  ``None``.
            payload (:obj:`str`, optional): Payload of the request. Default:  ``None``.
            auth_type (:obj:`str`, optional): ``'basic'`` or ``None``. Default: ``None``.
            username (:obj:`str`, optional): username for the authentication. Default: ``None``.
            password (:obj:`str`, optional): password for the authentication. Default: ``None``.
            timeout (:obj:`int`, optional): timeout for the Webhook action. Default: ``30000``.
            headers (:obj:`dict`, optional): Headers to be sent to the Webhook call. Default: ``None``.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        if auth_type is None:
            params['authType'] = "none"
        self._action.update({'eventType': 'WEBHOOKV1',
                             'config': params})

    def build(self, name, description=None):
        """Builder for Scheduled Task.

        Args:
            name (:py:obj:`str`): Name of Subscription.
            description (:py:obj:`str`, optional): Description of subscription. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Subscription`.
        """
        self._subscription['events'] = [event._data for event in self._events]
        self._subscription['externalActions'] = [self._action]
        self._subscription['name'] = name
        self._subscription['description'] = description
        return Subscription(self._subscription, self._control_hub)


# We define module-level attributes to allow users to extend certain
# SCH classes and have them used by other classes without the need to override
# their methods (e.g. allow the Pipeline class to be extended and be built using a
# non-extended PipelineBuilder class).
_Pipeline = Pipeline
_Stage = Stage
