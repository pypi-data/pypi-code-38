# Encryption utilities imports
from cryptography.fernet import Fernet
# System imports
from os.path import isfile, join
from os import listdir
import os
import sys
import subprocess
# Crontab generator import
from htvalidator.os_utility.crongen import cron_generator
from htvalidator.os_utility.miscellanea import printout
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

home = os.environ['HOME']

def shadow():

    # It creates an empty list
    crontabs = []
    # It gets the venv path
    venv_path = subprocess.run(["which", "htv"], stdout=subprocess.PIPE).stdout.decode('utf-8')
    venv_path = venv_path[:-3]
    # It deletes list_cron.txt
    try:
        file = open('{}/htv/list_cron.txt'.format(home), 'w')
        file.write("")
        file.close()
    except:
        printout(">> File list_cron.txt not found \n", RED)

    ############################################
    #              Encryption key              #
    ############################################
    # It gets the encryption key
    with open('{}/htv/key.key'.format(home), 'r') as F:
        e_key = F.read()

    # It saves all the .sh files corresponding to the admin-openrc.sh files
    onlyfiles = [f for f in listdir("{}/htv/rc_files".format(home)) if isfile(join("{}/htv/rc_files".format(home), f))]
    onlysh = [f for f in onlyfiles if f.endswith(".sh")]

    ############################################
    #       Password encryption and save       #
    ############################################
    # It opens every openrc.sh file and insert the encrypted password in it
    if onlysh:
        for shfile in onlysh:
            # It gets the openstack password in the form of a string, encodes it and encrypts it.
            printout(">> Enter the Openstack password for the file {}: \n".format(shfile), CYAN)
            openstack_password = input()
            passwd = openstack_password.encode()
            f = Fernet(e_key)
            encrypted = f.encrypt(passwd)
            # It creates the variable to insert
            password_line = "export OS_PASSWORD={}".format(encrypted)
            # It opens the openrc.sh file and change the PASSWORD line with the new encrypted password
            with open("{}/htv/rc_files/{}".format(home, shfile), 'r+') as F:
                lines = F.readlines()
                F.seek(0)
                for line in lines:
                    # If 'OS_PASSWORD' is not in the line, it re-writes the line to the file
                    if "export OS_PASSWORD=" not in line:
                        F.write(line)
                # At the end it appends the new line with the saved password
                F.write("\n{}".format(password_line))
            # It generates the crontab for each openrc file and for each password
            crontab = '*/10 * * * * source {0}activate && python {0}/validator.py "{1}" "{2}"'.format(venv_path, encrypted, shfile)
            # It adds the crontab to the list 'crontabs'
            crontabs.append(crontab)
    else:
        printout(">> There are no openrc files in '{}/htv/rc_files' dir. The application will now exit\n".format(home), RED)
        sys.exit()

    ############################################
    #            Crontabs generator            #
    ############################################
    # It calls the cron_generator function to save the crontabs from the "crontabs" list into the list_cron.txt file
    try:
        cron_generator(crontabs)
        printout(">> Passwords have been correctly saved\n", CYAN)
    except Exception as e:
        printout(">> Crontabs have not been saved for an error:\n\n Error: {}\n".format(e), RED)


