import os
from htvalidator.config.keygen import keygen
from htvalidator.os_utility.miscellanea import printout

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


def install():
    home = os.environ['HOME']
    app_dir = "{}/htv".format(home)
    paths = ["/TemplateLocalStorage", "/WarnYamlFiles", "/ErrYamlFiles", "/ValidYamlFiles", "/Log",
             "/rc_files"]
    # Main and sub directories creation in $HOME
    for path in paths:
        try:
            os.system("mkdir $HOME/htv >/dev/null 2>&1")
            new_path = "{}{}".format(app_dir, path)
            os.system("mkdir -p {} >/dev/null 2>&1".format(new_path))
        except:
            pass
    print(">> The directory and relative subdirs have been created: {0}/".format(app_dir))
    print(">> Now move the Heat template files in {0}/TemplateLocalStorage "
          "and the openrc files (for Openstack authentication) to {0}/rc_files".format(app_dir))
    keygen()
    print(">> Then execute 'htv -s' or 'htv --shadow' to authenticate to your Openstack server OR execute 'htv' "
          "and the path to your oepnrc file")
