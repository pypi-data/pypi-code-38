import os
import traceback
from htvalidator.config.keygen import keygen
from htvalidator.os_utility.miscellanea import printout

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)



def install():
    home = os.environ['HOME']
    app_dir = "{}/htv".format(home)
    paths = ["/.key", "/TemplateLocalStorage", "/WarnYamlFiles", "/ErrYamlFiles", "/ValidYamlFiles", "/Log",
             "/rc_files"]
    # Main and sub directories creation in $HOME
    try:
        os.system("mkdir $HOME/htv")
    except:
        return "An error occurred"
    for path in paths:
        try:
            new_path = "{}{}".format(app_dir, path)
            os.system("mkdir -p {}".format(new_path))
        except:
            pass
    printout(">> Now move the Heat template files in {0}/TemplateLocalStorage "
             "and the openrc files (for Openstack authentication) to {0}/rc_files\n".format(app_dir), CYAN)
    keygen()
    printout(">> Then execute 'htv -s' or 'htv --shadow' to authenticate to your Openstack server\n", CYAN)
