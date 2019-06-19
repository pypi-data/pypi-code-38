  # Package Removal

import os
import subprocess as sp

def removePackages(x,y):
    try:
        null = open("log.txt", "a")
        print('Removing package %s ' % x)
        os.system('%s' % y)
        print("Package %s removed" % x)
        null.close()

    except OSError:
        print (e.message)
        print ("Exiting the process because of above error")
        exit();

def packageCleanUp ():
    packages = {
       "aisleriot": "sudo apt-get remove aisleriot",
       "Browser": "sudo apt purge webbrowser-app && sudo apt autoremove --purge",
       "Libreoffice": "sudo apt-get autoremove -y libreoffice-\*",
       "Sudoku": "sudo apt-get remove sudoku",
       "Thunderbird": "sudo apt-get purge thunderbird*",
       "Transmission": "sudo apt-get purge transmission* && sudo apt-get autoremove"
    }
    for x, y in packages.items():
        removePackages(x,y)

def bashAndBrowserCleanUp():
    # Clear bash history
    os.system('sudo sh -c \'echo "" > .bash_history \'')

    # Clear browser history
    os.system('sudo rm ~/.config/google-chrome/Default/')
    os.system('sudo rm ~/.cache/google-chrome')

def cleanUp():
    packageCleanUp()
    bashAndBrowserCleanUp()
