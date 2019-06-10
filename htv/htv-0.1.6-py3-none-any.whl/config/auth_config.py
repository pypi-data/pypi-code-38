# System imports
from os.path import isfile, join
from os import listdir
import os
import sys
# Openstack clients imports
from keystoneclient.v3 import client as kclient
from keystoneauth1 import loading
from keystoneauth1 import session
from glanceclient import Client as gclient
from novaclient import client as novclient
from neutronclient.v2_0 import client as neuclient
from cinderclient import client as cinclient
# Encryption utilities imports
from cryptography.fernet import Fernet
# Utilities imports
from htvalidator.os_utility.miscellanea import ask_openrc, parse_args, printout
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
home = os.environ['HOME']


def config():
    # It saves all the .sh files corresponding to the admin-openrc.sh files
    onlyfiles = [f for f in listdir("{}/htv/rc_files".format(home)) if isfile(join("{}/htv/rc_files".format(home), f))]
    onlysh = [f for f in onlyfiles if f.endswith(".sh")]
    # It first saves a list of files of the directory "./TemplateLocalStorage"
    onlyfiles = [f for f in listdir("{}/htv/TemplateLocalStorage".format(home)) if isfile(join("{}/htv/TemplateLocalStorage".format(home), f))]
    # It then saves a list of only YAML files
    onlyyaml = [f for f in onlyfiles if f.endswith(".yaml")]
    # It saves the current working directory
    dir_base = os.getcwd()
    # It declares empty variables
    arguments = []
    openrc = ""
    shfile = ""
    pwd = ""
    #################################################
    #           Interactive mode or not?            #
    #################################################
    if onlyyaml:
        # No Interactive
        if len(sys.argv) > 1:
            # It saves the arguments in a list
            arguments = sys.argv[1:]
            # It calls the fun parse_args in order to save the various args
            pwd, shfile = parse_args(arguments)
        # Interactive
        else:
            # It calls the funct ask_openrc to ask the operator which openrc file he wants to use for the authentication
            pwd, shfile = ask_openrc()
    else:
        printout(">> There are no YAML files in here! Move at least one Heat template in {}/htv/TemplateLocalStorage. "
                 "The program will now exit\n".format(home), RED)
        sys.exit()
    #################################################
    #        Authentication info collection         #
    #################################################
    # If the chosen shfile is present in the onlysh list it saves the various variables
    if shfile in onlysh:
        # It opens the chosen file as F
        with open("{}/htv/rc_files/{}".format(home, shfile), 'rt') as F:
            # It read the file line by line
            lines = F.readlines()
            # It declares an empty dict for the authentication info
            auth_dict = {}
            for line in lines:
                # For every line if "export" is in it it saves the line differentiating between key and value
                if "export" in line:
                    splitted_line = line.split("export ")[1]
                    # If the password is present it saves it and split it accordingly
                    if "export OS_PASSWORD=" in line:
                        key = "OS_PASSWORD"
                        try:
                            value = line.split("'")[1]
                            auth_dict[key] = value
                        except:
                            printout(">> Run 'htv -s' or 'htv --shadow' first because the application requires the openstack "
                                     "password in order to run\n", CYAN)
                            sys.exit()
                    # For all the other values it just splits it by "=" and add the keys, values to the auth dict
                    else:
                        key = splitted_line.split("=")[0]
                        value = splitted_line.split("=")[1]
                        auth_dict[key] = value
                    # It deletes the '\n' and the ' " '
                    for key, value in auth_dict.items():
                        value = value.strip('\n').replace('"', '')
                        auth_dict[key] = value
    # If the shfile is not present in the list the program exits
    else:
        printout(">> The selected openrc file is not present in '{}/htv/rc_files' dir. "
                 "The application will now exit\n".format(home), RED)
        sys.exit()
    # It changes and saves these variables that can be different depending on the openrc version (V3 or V2)
    if 'USER_DOMAIN_NAME' not in auth_dict:
        auth_dict['USER_DOMAIN_NAME'] = "Default"
    if 'OS_PROJECT_ID' not in auth_dict:
        auth_dict['OS_PROJECT_ID'] = auth_dict['OS_TENANT_ID']
    if 'PROJECT_DOMAIN_NAME' not in auth_dict:
        auth_dict['PROJECT_DOMAIN_NAME'] = "Default"
    auth_dict['OS_IDENTITY_API_VERSION'] = int(auth_dict['OS_IDENTITY_API_VERSION'])

    #################################################
    #              Password decryption              #
    #################################################
    # It gets the key for the decryption
    file = open('{}/htv/key.key'.format(home), 'rb')
    # It reads it from the file
    e_key = file.read()
    file.close()
    fernet = Fernet(e_key)
    # It takes the password variable from the auth_dict or from 'pwd' variable if it exists
    password = pwd if pwd else (auth_dict['OS_PASSWORD']).encode()
    # It decrypts it using the key
    decrypted_pwd = fernet.decrypt(password)
    decrypted = decrypted_pwd.decode()
    # It saves the decrypted openstack password
    auth_dict['OS_PASSWORD'] = decrypted

    #################################################
    #                Authentication                 #
    #################################################
    # Necessary authentication info
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(
        auth_url=auth_dict['OS_AUTH_URL'],
        username=auth_dict['OS_USERNAME'],
        password=auth_dict['OS_PASSWORD'],
        project_id=auth_dict['OS_PROJECT_ID'],
        user_domain_name=auth_dict['USER_DOMAIN_NAME'],
        project_domain_name=auth_dict['PROJECT_DOMAIN_NAME'])
    # Session authentication
    sess = session.Session(auth=auth)

    #################################################
    #               Openstack Clients               #
    #################################################
    try:
        # GLANCE client
        try:
            glance = gclient(auth_dict['OS_IDENTITY_API_VERSION'], session=sess)
        except:
            glance = gclient(str(int(auth_dict['OS_IDENTITY_API_VERSION'])-1), session=sess)
        # NOVA client
        try:
            nova = novclient.Client(auth_dict['OS_IDENTITY_API_VERSION'], session=sess)
        except:
            nova = novclient.Client(str(int(auth_dict['OS_IDENTITY_API_VERSION'])-1), session=sess)
        # KEYSTONE client
        keystone = kclient.Client(session=sess, include_metadata=True)
        # NEUTRON client
        neutron = neuclient.Client(session=sess)
        # CINDER client
        cinder = cinclient.Client(auth_dict['OS_IDENTITY_API_VERSION'], session=sess)
        clients = []
        clients.append(glance)
        clients.append(nova)
        clients.append(neutron)
        clients.append(cinder)
        clients.append(keystone)
        return clients
    except:
        printout(">> The Openstack server is down, the program will now exit", RED)
        sys.exit()
