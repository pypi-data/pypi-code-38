import os
from htvalidator.config.keygen import keygen
from htvalidator.os_utility.miscellanea import printout

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


def install():
    home = os.environ['HOME']
    app_dir = "{}/htv".format(home)
    paths = ["/.key", "/TemplateLocalStorage", "/WarnYamlFiles", "/ErrYamlFiles", "/ValidYamlFiles", "/Log",
             "/rc_files"]
    # Main and sub directories creation in $HOME
    for path in paths:
        try:
            os.system("mkdir $HOME/htv >/dev/null 2>&1")
            new_path = "{}{}".format(app_dir, path)
            os.system("mkdir -p {} >/dev/null 2>&1".format(new_path))
        except:
            pass
    printout(">> The directory, and relative subdirs, has been created: {0}/\n\n".format(app_dir), CYAN)
    printout(">> Now move the Heat template files in {0}/TemplateLocalStorage "
             "and the openrc files (for Openstack authentication) to {0}/rc_files\n\n".format(app_dir), CYAN)
    keygen()
    printout(">> Then execute 'htv -s' or 'htv --shadow' to authenticate to your Openstack server\n", CYAN)
