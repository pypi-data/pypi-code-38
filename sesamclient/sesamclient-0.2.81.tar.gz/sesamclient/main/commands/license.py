# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import os

from ..utils import print_item, exit_with_error


def get_license_cmd(connection, args):
    license_info = connection.get_license()
    print_item(license_info, args)


def put_license_cmd(connection, args):
    license_path = args.license_file
    if not os.path.exists(license_path):
        exit_with_error("The specified path '%s' doesn't exist!" % (license_path,))
    with open(license_path) as licence_content:
        license_info = connection.set_license(licence_content)
        print_item(license_info, args)
