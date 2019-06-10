# System imports
import os
from os.path import isfile, join
from os import listdir
import sys
import subprocess
from htvalidator.os_utility.miscellanea import printout
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
home = os.environ['HOME']

############################################
#        Crontab generator function        #
############################################
# It saves the crontabs into the main file list_cron.txt
def cron_generator(crontabs):
    # For every item in the list crontabs it saves the item into the file
    for cron in crontabs:
        file = open('{}/htv/list_cron.txt'.format(home), 'a+')
        file.write("{}\n".format(cron))
        file.close()

#################################################
#             Password collection               #
#################################################
# It saves the password from the openrc files and creates the crontabs
def direct_cron_gen():
    # Data and info collection
    crontabs = []
    # It gets the venv path
    venv_path = subprocess.run(["which", "htv"], stdout=subprocess.PIPE).stdout.decode('utf-8')
    venv_path = venv_path[:-3]
    # It deletes list_cron.txt
    file = open('{}/htv/list_cron.txt'.format(home), 'w')
    file.write("")
    file.close()
    # It saves all the .sh files corresponding to the admin-openrc.sh files
    onlyfiles = [f for f in listdir("{}/htv/rc_files".format(home)) if isfile(join("{}/htv/rc_files".format(home), f))]
    onlysh = [f for f in onlyfiles if f.endswith(".sh")]
    arguments = []
    for shfile in onlysh:
        # It opens the openrc file and reads it line by line
        with open("{0}/htv/rc_files/{1}".format(home, shfile), 'rt') as F:
            data = F.readlines()
            passwd = ""
            for line in data:
                # For every line it checks if OS_PASSWORD is in it and if so it saves the pwd
                if "export OS_PASSWORD=" in line:
                    passwd = line.split("export OS_PASSWORD=")[1]
        # It then tries to split it by '
        try:
            passwd = passwd.split("'")[1]
        # If it does not succeed it means there is no encoded password but just the old input variable from the openrc f
        except:
            printout(""">> Run 'htv -s' or 'htv --shadow' first to insert the Openstack password\n""", CYAN)
            sys.exit()
        # It encodes the password
        encrypted = passwd.encode()
        # It creates the crontab with the variables: password, openrc file
        crontab = '*/10 * * * * source {0}activate && python {0}/validator.py "{1}" "{2}"'.format(
            venv_path, encrypted, shfile)
        # It appends the crontabs to the list
        crontabs.append(crontab)
    # It calls the primary function to save them into the main file list_cron.txt
    cron_generator(crontabs)
