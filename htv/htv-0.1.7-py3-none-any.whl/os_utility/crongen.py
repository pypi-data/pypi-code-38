# System imports
import os
from os.path import isfile, join
from os import listdir
import sys
import subprocess
from htvalidator.os_utility.miscellanea import get_saved_pwd, get_shfiles, empty_cron, printout, get_htv_path

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
home = os.environ['HOME']


#################################################
#               Crontab generator               #
#################################################
def cron_gen(pwd, shfile):
    venv_path = get_htv_path()
    crontabs = []
    crontab = '*/10 * * * * source {0}activate && python {0}/validate.py "{1}" "{2}"'.format(venv_path,
                                                                                             pwd, shfile)
    # It adds the crontab to the list 'crontabs'
    crontabs.append(crontab)
    # For every item in the list crontabs it saves the item into the file
    for cron in crontabs:
        with open('{}/htv/list_cron.txt'.format(home), 'a+') as F:
            F.write("{}\n".format(cron))


#################################################
#              Password collection              #
#################################################
# It saves the password from the openrc files and creates the crontabs
def cron_gen_nopwd():
    # It deletes list_cron.txt
    empty_cron()
    # It saves all the .sh files corresponding to the admin-openrc.sh files
    onlysh = get_shfiles()
    for shfile in onlysh:
        # It opens the openrc file and reads it line by line
        passwd = get_saved_pwd(shfile)
        # It then tries to split it by '
        try:
            passwd = passwd.split("'")[1]
        # If it does not succeed it means there is no encoded password but just the old input variable from the openrc f
        except:
            printout(""">> Run 'htv -s' or 'htv --shadow' first to insert the Openstack password\n""", CYAN)
            sys.exit()
        # It encodes the password
        pwd = passwd.encode()
        cron_gen(pwd, shfile)
    printout(">> Crontabs have been correctly updated\n", CYAN)
