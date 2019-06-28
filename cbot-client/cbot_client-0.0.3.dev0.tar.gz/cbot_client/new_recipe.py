import hashlib
import os
from builtins import input
import requests

from cbot_client.index_storage import IndexStorage


def yes_or_no(question):
    while "the answer is invalid":
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            return False


def command_new_version(storage, name, version, folder, url):
    version = version or input("Enter the version: ")
    cur_versions = storage.versions(name)
    if version in cur_versions:
        print("The version already exists!")
        exit(-1)

    folders = storage.folders(name)
    if folders:
        print("Current recipe folders: {}".format(", ".join(folders)))

    folder = folder or input("Enter the folder name containing the recipe "
                             "(Default {}) ".format(version))
    if not folder:
        folder = version
    storage.add_new_version(name, version, folder)

    if not os.path.exists(storage.conanfile_path(name, folder)):
        create_recipe = yes_or_no("Do you want to create an empty recipe?")
        if create_recipe:
            header_only = yes_or_no("Is it a header only recipe?")
            storage.generate_recipe_for_version(name, version, folder, header_only)

    while True:
        url = url or input("Enter the sources URL for the {} version: ".format(version)).strip()
        print("Calculating SHA256...")
        try:
            r = requests.get(url, allow_redirects=True)
        except Exception as e:
            url = None
            print("Error downloading the file: {}".format(e))
            if yes_or_no("Exit?"):
                return
        else:
            the_hash = hashlib.sha256(r.content).hexdigest()
            storage.add_entry_to_conandata_yml(name, version, folder, url, the_hash, "sha256")
            print("\nCreated version files!\n")
            break


def new_recipe(base_path, name, version, folder, url):

    storage = IndexStorage(os.path.abspath(base_path))
    name = name or input("Introduce the package name (lowercase). e.g: openssl: ")
    if name.lower() != name:
        print("The package name should be lowercase!")
        exit(-1)
    if name in storage.package_names:
        versions = storage.versions(name)
        print("The package already exists with the "
              "following versions: {}".format(", ".join(versions)))

    command_new_version(storage, name, version, folder, url)

    print("All done!\n")
