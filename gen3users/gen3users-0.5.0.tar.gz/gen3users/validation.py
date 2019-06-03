from cdislogging import get_logger
import collections
import logging
import yaml


logger = get_logger("gen3users")
logging.basicConfig()


def assert_and_log(assertion_success, error_message):
    """
    If an assertion fails, logs the provided error message and updates
    the global variable "failed_validation" for future use.
    
    Args:
        assertion_success (bool): result of an assertion.
        error_message (str): message to display if the assertion failed.

    Return:
        assertion_success(bool): result of the assertion.
    """
    if not assertion_success:
        logger.error(error_message)
    return assertion_success


def validate_user_yaml(user_yaml, name="user.yaml"):
    """
    Runs all the validation checks against a user.yaml file.

    Args:
        user_yaml (str): Contents of a user.yaml file.
        name (str): Displayable name of the tested file.
    """
    logger.info("Validating {}".format(name))
    try:
        user_yaml_dict = yaml.safe_load(user_yaml)
        assert user_yaml_dict, "Empty file"
    except:
        logger.error("Unable to parse YAML file")
        raise

    ok = validate_syntax(user_yaml_dict)
    ok = validate_groups(user_yaml_dict) and ok
    ok = validate_policies(user_yaml_dict) and ok
    ok = validate_users(user_yaml_dict) and ok

    if not ok:
        raise AssertionError(
            "user.yaml validation failed. See errors in previous logs."
        )
    else:
        logger.info("OK")


def get_field_from_list(li, field):
    """
    Returns the field value for each dictionary in a list of dictionaries.

    Args:
        li (list[dict]): List of dictionaries.
        field (str): Name of the property to select.

    Return:
        (list)
    """
    return [item.get(field) for item in li]


def resource_tree_to_paths(user_yaml_dict):
    """
    Builds the list of existing resource paths from the rbac.resources
    section of the user.yaml.

    Args:
        user_yaml_dict (dict): Contents of a user.yaml file.

    Return:
        paths_list(list[str]): list of existing resource paths.
    """
    paths_list = []
    for resource in user_yaml_dict["rbac"].get("resources", []):
        resource_tree_to_paths_recursive("", paths_list, resource)
    return paths_list


def resource_tree_to_paths_recursive(root, paths_list, resource):
    """
    Recursively builds resource paths by appending a slash.

    Args:
        root (str): current resource path.
        paths_list (list[str]): list of existing resource paths.
        resource (dict): current resource.
    """
    new_root = "{}/{}".format(root, resource["name"])
    if resource["name"] not in ["programs", "projects"]:
        paths_list.append(new_root)
    for sub in resource.get("subresources", []):
        resource_tree_to_paths_recursive(new_root, paths_list, sub)


def validate_resource_syntax_recursive(resource):
    """
    Recursively validates the resource tree by checking the syntax
    of subresources.

    Args:
        resource (dict): current resource.

    Return:
        ok(bool): whether the validation succeeded.
    """
    ok = True

    ok = (
        assert_and_log("name" in resource, "Resource without name: {}".format(resource))
        and ok
    )
    if resource["name"] == "programs" or resource["name"] == "projects":
        ok = (
            assert_and_log(
                "subresources" in resource,
                'Resource "{}" does not have subresources'.format(resource["name"]),
            )
            and ok
        )

    subresources = resource.get("subresources", [])
    ok = (
        assert_and_log(
            type(subresources) == list,
            'Subresources for resource "{}" should be a list'.format(resource["name"]),
        )
        and ok
    )
    for subresource in subresources:
        validate_resource_syntax_recursive(subresource)

    return ok


def validate_syntax(user_yaml_dict):
    """
    Validates the syntax of the user.yaml by checking expected sections and
    fields are present. Also checks that there are no duplicates in key fields.

    Args:
        user_yaml_dict (dict): Contents of a user.yaml file.

    Return:
        ok(bool): whether the validation succeeded.
    """
    logger.info("- Validating user.yaml syntax")
    ok = True

    # check expected sections are defined
    # assert_and_log("rbac" in user_yaml_dict, 'Missing "rbac" section')
    # TODO: after all user.yamls are migrated to new format, uncomment the assertion and remove these 2 lines (waiting on dcfstaging)
    if "rbac" not in user_yaml_dict:
        user_yaml_dict["rbac"] = {}
    ok = assert_and_log("users" in user_yaml_dict, 'Missing "users" section') and ok

    # check expected fields are defined
    # - in rbac.groups
    for group in user_yaml_dict["rbac"].get("groups", []):
        ok = (
            assert_and_log("name" in group, "Group without name: {}".format(group))
            and ok
        )
        ok = (
            assert_and_log(
                "policies" in group,
                'Group "{}" does not have policies'.format(group["name"]),
            )
            and ok
        )
        ok = (
            assert_and_log(
                "users" in group, 'Group "{}" does not have users'.format(group["name"])
            )
            and ok
        )
    # - in rbac.policies
    for policy in user_yaml_dict["rbac"].get("policies", []):
        ok = (
            assert_and_log("id" in policy, "Policy without id: {}".format(policy))
            and ok
        )
        ok = (
            assert_and_log(
                "role_ids" in policy,
                'Policy "{}" does not have role_ids'.format(policy["id"]),
            )
            and ok
        )
        ok = (
            assert_and_log(
                "resource_paths" in policy,
                'Policy "{}" does not have resource_paths'.format(policy["id"]),
            )
            and ok
        )
    # - in rbac.resources
    for resource in user_yaml_dict["rbac"].get("resources", []):
        ok = validate_resource_syntax_recursive(resource) and ok
    # - in users
    for user_email, user_access in user_yaml_dict["users"].items():
        for project in user_access.get("projects", {}):
            ok = (
                assert_and_log(
                    "auth_id" in project,
                    'Project without auth_id for user "{}": {}'.format(
                        user_email, project
                    ),
                )
                and ok
            )
            ok = (
                assert_and_log(
                    "privilege" in project,
                    'Project "{}" without privilege section for user "{}"'.format(
                        project["auth_id"], user_email
                    ),
                )
                and ok
            )

    # make sure there are no duplicates
    # - in rbac.groups.name
    existing_groups = get_field_from_list(
        user_yaml_dict["rbac"].get("groups", []), "name"
    )
    duplicate_group_names = [
        group_name
        for group_name, count in collections.Counter(existing_groups).items()
        if count > 1
    ]
    ok = (
        assert_and_log(
            len(duplicate_group_names) == 0,
            "Duplicate group names: {}".format(duplicate_group_names),
        )
        and ok
    )
    # - in rbac.policies.id
    existing_policies = get_field_from_list(
        user_yaml_dict["rbac"].get("policies", []), "id"
    )
    duplicate_policy_ids = [
        policy_id
        for policy_id, count in collections.Counter(existing_policies).items()
        if count > 1
    ]
    ok = (
        assert_and_log(
            len(duplicate_policy_ids) == 0,
            "Duplicate policy ids: {}".format(duplicate_policy_ids),
        )
        and ok
    )
    # - in rbac.roles.id
    existing_roles = get_field_from_list(user_yaml_dict["rbac"].get("roles", []), "id")
    duplicate_role_ids = [
        role_id
        for role_id, count in collections.Counter(existing_roles).items()
        if count > 1
    ]
    ok = (
        assert_and_log(
            len(duplicate_role_ids) == 0,
            "Duplicate role ids: {}".format(duplicate_role_ids),
        )
        and ok
    )

    return ok


def validate_groups(user_yaml_dict):
    """
    Validates the "groups" section of the user.yaml by checking that the users
    and policies used in the groups are defined in the lists of users and in
    the list of policies respectively.

    Args:
        user_yaml_dict (dict): Contents of a user.yaml file.

    Return:
        ok(bool): whether the validation succeeded.
    """
    logger.info("- Validating groups")
    ok = True

    existing_policies = get_field_from_list(
        user_yaml_dict["rbac"].get("policies", []), "id"
    )
    for group in user_yaml_dict["rbac"].get("groups", []):
        # check users are defined
        for user_email in group["users"]:
            ok = (
                assert_and_log(
                    user_email in user_yaml_dict["users"],
                    'User "{}" in group "{}" is not defined in main user list'.format(
                        user_email, group["name"]
                    ),
                )
                and ok
            )
        # check policies are defined
        for policy_id in group["policies"]:
            ok = (
                assert_and_log(
                    policy_id in existing_policies,
                    'Policy "{}" in group "{}" is not defined in list of policies'.format(
                        policy_id, group["name"]
                    ),
                )
                and ok
            )

    for predefined_group in ["anonymous_policies", "all_users_policies"]:
        # check policies are defined
        for policy_id in user_yaml_dict["rbac"].get(predefined_group, []):
            ok = (
                assert_and_log(
                    policy_id in existing_policies,
                    'Policy "{}" in group "{}" is not defined in list of policies'.format(
                        policy_id, predefined_group
                    ),
                )
                and ok
            )

    return ok


def validate_policies(user_yaml_dict):
    """
    Validates the "policies" section of the user.yaml by checking that the
    roles and resources used in the policies are defined in the list of roles
    and in the resource tree respectively.

    Args:
        user_yaml_dict (dict): Contents of a user.yaml file.

    Return:
        ok(bool): whether the validation succeeded.
    """
    logger.info("- Validating policies")
    ok = True

    existing_resources = resource_tree_to_paths(user_yaml_dict)
    existing_roles = get_field_from_list(user_yaml_dict["rbac"].get("roles", []), "id")
    for policy in user_yaml_dict["rbac"].get("policies", []):

        # check resource paths in "rbac.policies" are valid
        # given "rbac.resources" resource tree
        for resource_path in policy["resource_paths"]:
            ok = (
                assert_and_log(
                    resource_path.startswith("/"),
                    'Resource path "{}" in policy "{}" should start with a "/"'.format(
                        resource_path, policy["id"]
                    ),
                )
                and ok
            )
            ok = (
                assert_and_log(
                    resource_path in existing_resources,
                    'Resource "{}" in policy "{}" is not defined in resource tree'.format(
                        resource_path, policy["id"]
                    ),
                )
                and ok
            )

        # checks roles are defined
        for role_id in policy["role_ids"]:
            ok = (
                assert_and_log(
                    role_id in existing_roles,
                    'Role "{}" in policy "{}" is not defined in list of roles'.format(
                        role_id, policy["id"]
                    ),
                )
                and ok
            )

    return ok


def validate_users(user_yaml_dict):
    """
    Validates the "users" section of the user.yaml by checking that the
    policies assigned to the users are defined in the list of policies.

    Args:
        user_yaml_dict (dict): Contents of a user.yaml file.

    Return:
        ok(bool): whether the validation succeeded.
    """
    logger.info("- Validating users")
    ok = True

    existing_policies = get_field_from_list(
        user_yaml_dict["rbac"].get("policies", []), "id"
    )
    existing_resources = resource_tree_to_paths(user_yaml_dict)
    for user_email, user_access in user_yaml_dict["users"].items():

        # check policies are defined
        user_policies = user_access.get("policies", [])
        invalid_policies = set(user_policies).difference(existing_policies)
        ok = (
            assert_and_log(
                len(invalid_policies) == 0,
                'Policies {} for user "{}" are not defined in list of policies'.format(
                    invalid_policies, user_email
                ),
            )
            and ok
        )

        # check resource paths in "users.projects.resource" are valid
        # given "rbac.resources" resource tree
        for project in user_access.get("projects", {}):
            if "resource" in project:
                ok = (
                    assert_and_log(
                        project["resource"].startswith("/"),
                        'Resource path "{}" in project "{}" for user "{}" should start with a "/"'.format(
                            project["resource"], project["auth_id"], user_email
                        ),
                    )
                    and ok
                )

                ok = (
                    assert_and_log(
                        project["resource"] in existing_resources,
                        'Resource "{}" in project "{}" for user "{}" is not defined in resource tree'.format(
                            project["resource"], project["auth_id"], user_email
                        ),
                    )
                    and ok
                )

            # if no resource path is provided, make sure "auth_id" exists
            # XXX: disabled for now because some commons do not have
            # the "rbac" section yet
            # else:
            #     resource_path = auth_id_to_resource_path(
            #         user_yaml_dict, project["auth_id"]
            #     )
            #     ok = (
            #         assert_and_log(
            #             resource_path,
            #             'auth_id "{}" for user "{}" is not found in list of resources and no resource path has been provided'.format(
            #                 project["auth_id"], user_email
            #             ),
            #         )
            #         and ok
            #     )

    return ok
