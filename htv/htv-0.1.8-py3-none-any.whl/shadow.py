# Encryption utilities imports
from cryptography.fernet import Fernet
# System imports
from os.path import isfile, join
from os import listdir
import os
import sys
import subprocess
# Crontab generator import
from htvalidator.os_utility.crongen import cron_gen, empty_cron
from htvalidator.os_utility.miscellanea import get_shfiles, write_pwd, printout, get_key, ask_pwd

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

home = os.environ['HOME']


def shadow():
    # It deletes list_cron.txt
    try:
        empty_cron()
    except:
        printout(">> File list_cron.txt not found \n", RED)

    ############################################
    #              Encryption key              #
    ############################################
    # It gets the encryption key
    e_key = get_key()
    # It saves all the .sh files corresponding to the admin-openrc.sh files
    onlysh = get_shfiles()

    ############################################
    #       Password encryption and save       #
    ############################################
    # It opens every openrc.sh file and insert the encrypted password in it
    if onlysh:
        for shfile in onlysh:
            # It gets the openstack password in the form of a string, encodes it and encrypts it.
            openstack_password = input(">> Enter the Openstack password for the file {}: ".format(shfile))
            passwd = openstack_password.encode()
            f = Fernet(e_key)
            pwd = f.encrypt(passwd)
            # It creates the variable to insert
            password_line = "export OS_PASSWORD={}".format(pwd)
            # It opens the openrc.sh file and change the PASSWORD line with the new encrypted password
            path_to_file = "{}/htv/rc_files/{}".format(home, shfile)
            write_pwd(password_line, path_to_file)
            # It generates the crontab for each openrc file and for each password
            cron_gen(pwd, shfile)
        print(">> Passwords have been correctly saved, now you can use 'htv'")
        print(">> Remember to move the Heat templates to '{}/htv/TemplateLocalStorage' "
              "everytime you want to use 'htv'".format(home))
    else:
        printout(">> There are no openrc files in '{}/htv/rc_files' dir. The application will now exit\n".format(home),
                 RED)
        sys.exit()
