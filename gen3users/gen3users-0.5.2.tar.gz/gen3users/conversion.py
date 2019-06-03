from cdislogging import get_logger
import json
import logging
import os
import yaml

from .validation import validate_user_yaml


logger = get_logger("gen3users")
logging.basicConfig()


# turn off array references in the resulting YAML file
yaml.Dumper.ignore_aliases = lambda *args: True


# do not alphabetically sort keys
yaml.add_representer(
    dict,
    lambda self, data: yaml.representer.SafeRepresenter.represent_dict(
        self, data.items()
    ),
)


# "base_rbac.json" contains RBAC elements that are included in all
# user.yaml files
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(CURRENT_DIR, "base_rbac.json")) as f:
    BASE_RBAC = json.load(f)


PRIVILEGE_TO_ROLE_NAME = {
    "create": "creator",
    "read": "reader",
    "update": "updater",
    "delete": "deleter",
    "upload": "uploader",
    "read-storage": "storage_reader",
    "write-storage": "storage_writer",
}


BASIC_ROLES = {
    frozenset(["create"]): PRIVILEGE_TO_ROLE_NAME["create"],
    frozenset(["read"]): PRIVILEGE_TO_ROLE_NAME["read"],
    frozenset(["update"]): PRIVILEGE_TO_ROLE_NAME["update"],
    frozenset(["delete"]): PRIVILEGE_TO_ROLE_NAME["delete"],
    frozenset(["upload"]): PRIVILEGE_TO_ROLE_NAME["upload"],
    frozenset(["read-storage"]): PRIVILEGE_TO_ROLE_NAME["read-storage"],
    frozenset(["write-storage"]): PRIVILEGE_TO_ROLE_NAME["write-storage"],
    frozenset(["read", "read-storage"]): "viewer",
    frozenset(["create", "read", "update", "delete", "read-storage"]): "admin",
    frozenset(["create", "read", "update", "delete"]): "service-admin",
    frozenset(
        [
            "create",
            "read",
            "update",
            "delete",
            "upload",
            "read-storage",
            "write-storage",
        ]
    ): "storage-admin",
    frozenset(
        ["create", "read", "update", "delete", "upload", "read-storage"]
    ): "upload-storage-admin",
    frozenset(
        ["create", "read", "update", "delete", "read-storage", "write-storage"]
    ): "write-storage-admin",
}


def add_basic_roles(user_yaml_dict):
    """
    Generates basic roles from BASIC_ROLES and add them to the user.yaml
    role list.

    Args:
        user_yaml_dict (dict): Contents of a user.yaml file.
    """
    for permissions, name in BASIC_ROLES.items():
        user_yaml_dict["rbac"]["roles"].append(
            {
                "id": name,
                "permissions": [
                    {
                        "id": PRIVILEGE_TO_ROLE_NAME[p],
                        "action": {"service": "*", "method": p},
                    }
                    for p in permissions
                ],
            }
        )


def auth_id_to_resource_path(user_yaml_dict, auth_id):
    """
    Recursively searches the resource tree for a program or project
    named auth_id.

    Args:
        user_yaml_dict (dict): Contents of a user.yaml file.
        auth_id (str): Program or project name as defined in user access.

    Returns:
        str: resource path for this auth_id if it exist, None otherwise.
    """
    for resource in user_yaml_dict["rbac"].get("resources", []):
        res = auth_id_to_resource_path_recursive("", resource, auth_id)
        if res:
            return res


def auth_id_to_resource_path_recursive(root, resource, auth_id):
    """
    Recursively searches the resource tree for a program or project
    named auth_id.

    Args:
        root (str): current resource path.
        resource (dict): current resource.
        auth_id (str): Program or project name as defined in user access.

    Returns:
        str: resource path for this auth_id if it exist, None otherwise.
    """
    new_root = "{}/{}".format(root, resource["name"])
    if resource["name"] in ["programs", "projects"]:
        for sub in resource.get("subresources", []):
            if sub["name"] == auth_id:
                return "{}/{}".format(new_root, sub["name"])
    for sub in resource.get("subresources", []):
        res = auth_id_to_resource_path_recursive(new_root, sub, auth_id)
        if res:
            return res


def convert_old_user_yaml_to_new_user_yaml(user_yaml, dest_path=None):
    """
    Converts a user.yaml file to the new format required by the
    latest fence and arborist.

    Args:
        user_yaml (str): Contents of a user.yaml file.
        dest_path (str, optional): Destination file. Defaults to None.

    Returns:
        str: Contents of the new user.yaml file.
    """
    # make sure the syntax is valid and expected fields exist
    logger.info("Pre-conversion validation:")
    validate_user_yaml(user_yaml)

    logger.info("Converting...")
    old_user_yaml = yaml.safe_load(user_yaml)
    new_user_yaml = {
        "cloud_providers": old_user_yaml.get("cloud_providers", {}),
        "groups": old_user_yaml.get("groups", {}),
        "users": {},
        "rbac": BASE_RBAC,
    }

    # add basic roles to RBAC list of roles
    add_basic_roles(new_user_yaml)

    # convert resources
    existing_resources = [
        item.get("name") for item in new_user_yaml["rbac"]["resources"]
    ]
    old_resources = old_user_yaml.get("rbac", {}).get("resources", [])
    for resource in old_resources:
        if resource["name"] == "programs":
            # duplicate programs for backwards compatibility
            new_user_yaml["rbac"]["resources"].append(resource)
            new_user_yaml["rbac"]["resources"].append(
                {"name": "gen3", "subresources": [resource]}
            )
        elif resource["name"] not in existing_resources:
            logger.warning("Ignoring resource {}".format(resource["name"]))

    # convert user privileges into roles and policies
    existing_policies = [item.get("id") for item in new_user_yaml["rbac"]["policies"]]
    for user_email, user_access in old_user_yaml.get("users", {}).items():

        # generate user policies
        for project in user_access.get("projects", []):

            # get the resource path.
            # if no resource path is specified, use the auth_id
            if "resource" not in project:
                resource_path = auth_id_to_resource_path(
                    new_user_yaml, project["auth_id"]
                )
                if not resource_path:
                    logger.warning(
                        'WARNING: auth_id "{}" for user "{}" is not found in list of resources and no resource path has been provided: skipping'.format(
                            project["auth_id"], user_email
                        )
                    )
                    break
            else:
                resource_path = project["resource"]
            resource_path_parts = resource_path.split("/")

            # convert list of privileges into roles and policies
            privilege = frozenset(project.get("privilege", []))
            try:
                role_names = [BASIC_ROLES[privilege]]
            except KeyError:
                # no existing basic role: create one role for each privilege
                role_names = [PRIVILEGE_TO_ROLE_NAME[p] for p in privilege]

            for role_name in role_names:
                policy_id = "{}_{}".format(".".join(resource_path_parts[1:]), role_name)

                if policy_id not in existing_policies:
                    # add the new policy to RBAC list of policies
                    new_user_yaml["rbac"]["policies"].append(
                        {
                            "id": policy_id,
                            "role_ids": [role_name],
                            "resource_paths": [resource_path],
                        }
                    )
                    existing_policies.append(policy_id)

                # assign the policy to the user
                user_access.get("policies", []).append(policy_id)

        # keep this commented out for now for backwards compatibility
        # if "projects" in user_access:
        #     del user_access["projects"]

        new_user_yaml["users"][user_email] = user_access

    result = yaml.dump(new_user_yaml)

    # make sure the syntax is valid and expected fields exist
    logger.info("Post-conversion validation:")
    validate_user_yaml(result)

    # output result
    if dest_path:
        with open(dest_path, "w") as f:
            logger.info("Saving at {}".format(dest_path))
            yaml.dump(new_user_yaml, f, default_flow_style=False)
    else:
        print(result)

    return result
