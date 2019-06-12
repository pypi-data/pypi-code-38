import os
import sys
from subprocess import check_call, CalledProcessError


def checkinstallation():
    import checkInstallationIP


def recuparchives():
    import recupArchives


def import_data():
    import import_data


def export_data():
    import export_data


def rename():
    import change_name


def remove_ldap():
    import remove_ldap


def pushdoc():
    import pushdoc


def ipclean():
    import ipclean


def ldapsearch():
    import ldapsearch


def count_files():
    import count_files


def reset_admin_password():
    import reset_admin_password


def properties_merger():
    args = sys.argv[1:]
    args.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/shell/properties-merger/properties-merger.sh")
    try:
        check_call(args)
    except CalledProcessError:
        pass
