# System imports
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
from htvalidator.config.keygen import keygen
from htvalidator.os_utility.miscellanea import write_pwd, get_key, printout

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
home = os.environ['HOME']


def config(pwd, path_to_file):
    #################################################
    #        Authentication info collection         #
    #################################################
    # It opens the chosen file as F
    with open("{}".format(path_to_file), 'rt') as F:
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
                        print(
                            ">> Run 'htv -s' or 'htv --shadow' first because the application requires the openstack"
                            " password in order to run")
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
    e_key = get_key()
    fernet = Fernet(e_key)
    # It takes the password variable from the auth_dict or from 'pwd' variable if it exists
    password = pwd if pwd else (auth_dict['OS_PASSWORD']).encode()
    # It decrypts it using the key
    try:
        decrypted_pwd = fernet.decrypt(password)
        password = decrypted_pwd.decode()
    except:
        keygen()
        password = input(">> Insert the password for the openrc file '{}': ".format(path_to_file))
        pwd = password.encode()
        e_key = get_key()
        fernet = Fernet(e_key)
        pwd = fernet.encrypt(pwd)
        password_line = "export OS_PASSWORD={}".format(pwd)
        write_pwd(password_line, path_to_file)
    # It saves the decrypted openstack password
    auth_dict['OS_PASSWORD'] = password

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
            glance = gclient(str(int(auth_dict['OS_IDENTITY_API_VERSION']) - 1), session=sess)
        # NOVA client
        try:
            nova = novclient.Client(auth_dict['OS_IDENTITY_API_VERSION'], session=sess)
        except:
            nova = novclient.Client(str(int(auth_dict['OS_IDENTITY_API_VERSION']) - 1), session=sess)
        # KEYSTONE client
        keystone = kclient.Client(session=sess, include_metadata=True)
        # NEUTRON client
        neutron = neuclient.Client(session=sess)
        # CINDER client
        cinder = cinclient.Client(auth_dict['OS_IDENTITY_API_VERSION'], session=sess)
        clients = [glance, nova, neutron, cinder, keystone]
        return clients
    except:
        printout(">> The Openstack server is down, the program will now exit", RED)
        sys.exit()
