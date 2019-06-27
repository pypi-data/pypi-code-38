"""
User utilities.
~~~~~~~~~~~~~~~
"""

import requests

# Roles that should not be processed.
RESERVED_ROLES = ['offline_access', 'uma_authorization']


class InvalidUserResponse(Exception):
    pass


class InvalidRoleResponse(Exception):
    pass


def get_role_by_name(realm_name, role_name, keycloak_client):
    """
    Gets a role representation.
    :param realm_name: The realm of the role
    :param role_name: the role name
    :param keycloak_client: The client to use when interacting with Keycloak
    :return: The role representation
    """

    path = '/admin/realms/{0}/roles/{1}'.format(realm_name, role_name)
    get_response = keycloak_client.get(path)

    if get_response.status_code == requests.codes.ok:
        return get_response.json()

    if get_response.status_code == requests.codes.not_found:
        return None

    raise InvalidRoleResponse('Unexpected role get response ({0})'.format(get_response.status_code))


def role_names_to_roles(realm_name, role_names, keycloak_client):
    """
    Convert a list of role names into role representations.
    :param realm_name: The realm of the roles
    :param role_names: The name of the roles
    :param keycloak_client: The client to use when interacting with Keycloak
    :return: The role representations
    """

    roles = []
    for role_name in role_names:
        role = get_role_by_name(realm_name, role_name, keycloak_client)
        if not role:
            raise InvalidRoleResponse('Unknown role: {0}'.format(role_name))
        roles.append(role)
    return roles


def get_user(realm_name, user_id, keycloak_client):
    """
    Get a user representation.
    :param realm_name: The realm of the user
    :param user_id: the user UUID
    :param keycloak_client: The client to use when interacting with Keycloak
    :return: The user configuration
    """

    path = '/admin/realms/{0}/users/{1}'.format(realm_name, user_id)
    get_response = keycloak_client.get(path)

    if get_response.status_code == requests.codes.ok:
        return get_response.json()

    if get_response.status_code == requests.codes.not_found:
        return None

    raise InvalidUserResponse('Unexpected user get response ({0})'.format(get_response.status_code))


def get_user_by_email(realm_name, email, keycloak_client):
    """
    Get a user representation by email.
    :param realm_name: The realm of the user
    :param email: the email of the user
    :param keycloak_client: The client to use when interacting with Keycloak
    :return: The user configuration
    """

    path = '/admin/realms/{0}/users'.format(realm_name, params={'email': email})
    get_response = keycloak_client.get(path)

    if get_response.status_code == requests.codes.ok:
        for user_data in get_response.json():
            if user_data.get('email', None) == email:
                return user_data
        return None

    if get_response.status_code == requests.codes.not_found:
        return None

    raise InvalidUserResponse('Unexpected user get response ({0})'.format(get_response.status_code))


def update_user(realm_name, user_id, user_config, keycloak_client):
    """
    Update a user.
    :param realm_name: The realm of the user
    :param user_id: the user UUID
    :param user_config: The user configuration
    :param keycloak_client: The client to use when interacting with Keycloak
    """

    path = '/admin/realms/{0}/users/{1}'.format(realm_name, user_id)
    update_response = keycloak_client.put(path, json=user_config)

    if update_response.status_code == requests.codes.no_content:
        return

    raise InvalidUserResponse('Unexpected user update response ({0})'.format(update_response.status_code))


def get_user_roles(realm_name, user_id, keycloak_client):
    """
    Get the roles associated with a user.
    :param realm_name: The realm of the user
    :param user_id: The UUID of the user
    :param keycloak_client: The client to use when interacting with Keycloak
    :return: The roles of the user
    """
    path = '/admin/realms/{0}/users/{1}/role-mappings/realm'.format(realm_name, user_id)
    get_response = keycloak_client.get(path)

    if get_response.status_code == requests.codes.ok:
        return get_response.json()

    if get_response.status_code == requests.codes.not_found:
        return None

    raise InvalidRoleResponse('Unexpected user role get response ({0})'.format(get_response.status_code))


def add_user_roles(realm_name, user_id, roles, keycloak_client):
    """
    Add roles to the user.
    :param realm_name: The realm of the user
    :param user_id: the user UUID
    :param roles: The roles to add to the user
    :param keycloak_client: The client to use when interacting with Keycloak
    """

    path = '/admin/realms/{0}/users/{1}/role-mappings/realm'.format(realm_name, user_id)
    update_response = keycloak_client.post(path, json=roles)

    if update_response.status_code == requests.codes.no_content:
        return

    raise InvalidUserResponse('Unexpected user role update response ({0})'.format(update_response.status_code))


def delete_user_roles(realm_name, user_id, roles, keycloak_client):
    """
    Add roles to the user.
    :param realm_name: The realm of the user
    :param user_id: the user UUID
    :param roles: The roles to delete from the user
    :param keycloak_client: The client to use when interacting with Keycloak
    """

    path = '/admin/realms/{0}/users/{1}/role-mappings/realm'.format(realm_name, user_id)
    update_response = keycloak_client.delete(path, json=roles)

    if update_response.status_code == requests.codes.no_content:
        return

    raise InvalidUserResponse('Unexpected user role deletion response ({0})'.format(update_response.status_code))


def process_user_roles(realm_name, user_id, existing_roles, new_role_names, keycloak_client):
    """
    Process the roles for a given user.
    :param realm_name: The realm of the user.
    :param user_id: The UUID of the user.
    :param existing_roles: The existing roles of the user
    :param new_role_names: The new role names for the user
    :param keycloak_client: The client to use when interacting with Keycloak
    """

    existing_role_names = []
    for existing_role in existing_roles:
        existing_role_names.append(existing_role['name'])

    update_role_names = []
    for new_role_name in new_role_names:
        if new_role_name not in existing_role_names:
            update_role_names.append(new_role_name)

    if len(update_role_names):
        update_roles = role_names_to_roles(realm_name, update_role_names, keycloak_client)
        add_user_roles(realm_name, user_id, update_roles, keycloak_client)

    delete_roles = []
    for existing_role in existing_roles:
        if existing_role['name'] not in new_role_names and existing_role['name'] not in RESERVED_ROLES:
            delete_roles.append(existing_role)

    if len(delete_roles):
        delete_user_roles(realm_name, user_id, delete_roles, keycloak_client)
