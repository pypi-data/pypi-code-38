import os
from htvalidator.config.keygen import keygen

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


# It creates the main directory htv and the subdirectories, then it creates the encryption/decryption key
def install():
    # It gets the home path of the user executing the command 'htv -i'
    home = os.environ['HOME']
    app_dir = "{}/htv".format(home)
    # List of the sub directories to be created
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
    print(">> Now move the Heat template file/s in {0}/TemplateLocalStorage "
          "and the openrc.sh file/s (for Openstack authentication) to {0}/rc_files".format(app_dir))
    # Creation of encryption/decryption key
    keygen()
    print(">> Then execute 'htv -s' or 'htv --shadow' to authenticate to your Openstack server OR execute 'htv' "
          "and the absolute path to your openrc.sh file")
