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
       "aisleriot": "sudo apt-get remove aisleriot -y",
       "Browser": "sudo apt purge webbrowser-app",
       "Libreoffice": "sudo apt-get remove -y libreoffice-\*",
       "Sudoku": "sudo apt-get remove sudoku -y",
       "Thunderbird": "sudo apt-get purge thunderbird* -y",
       "Transmission": "sudo apt-get purge transmission* -y && sudo apt autoremove --purge -y"
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
    try:
        packageCleanUp()
        bashAndBrowserCleanUp()
    except OSError:
        print (e.message)
        print ("Exiting the process because of above error")
        exit();
