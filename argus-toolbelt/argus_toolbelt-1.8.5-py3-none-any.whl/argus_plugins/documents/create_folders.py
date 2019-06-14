from argus_cli.helpers.log import log
from argus_cli.plugin import register_command
from argus_plugins import argus_cli_module
from argus_plugins.cases.utils import get_customer_id

from argus_api.api.documents.v1.customer.customer import get_customer_root_folder
from argus_api.api.documents.v1.folder.folder_root import add_folder, browse_folder


DEFAULT_FOLDER_STRUCTURE = {
    "Reports": {
        "Service Reports": {},
        "Other Reports": {},
    },
    "Technical Documentation": {
        "Solution Design": {},
        "Network Documentation": {}
    },
    "Projects": {},
    "Service Handbook": {},
}


def create_folders(parent: int, name: str, children: dict, existing_folders: dict):
    """Recurses trough the folder structure to create new folders

    :param parent: The ID of the folders parrent
    :param name: The name of the new folder
    :param children: The children of the folder
    :return: The ID of the new folder
    """
    if not name and not existing_folders:
        # Use name as the base case. The rootfolder will end up here
        folder = parent
    elif name.lower() not in existing_folders.keys():
        print("Creating folder: %s" % name)
        folder = add_folder(parent, name)["data"]["id"]
    else:
        print("Folder already exists: %s" % name)
        folder = existing_folders[name.lower()]

    if not children:
        # If there are no children then return.
        # This is to avoid doing an extra API call
        return

    existing_folders = {folder["name"].lower(): folder["id"] for folder in browse_folder(folder)["data"]}
    for folder_name, children in children.items():
        create_folders(folder, folder_name, children, existing_folders)


@register_command(extending="documents", module=argus_cli_module)
def initialize_customer(customer: get_customer_id, folder_structure: dict = DEFAULT_FOLDER_STRUCTURE):
    """Creates a folder-structure for the specified customer

    :param customer: The costumer to create the folder structure for
    :param folder_structure: The desired folder tree structure in the form of a JSON object
    """
    log.debug("Getting customer root folder")
    root_folder = get_customer_root_folder(customer)["data"]["id"]

    log.debug("Creating folder structure")
    create_folders(root_folder, None, folder_structure, None)
