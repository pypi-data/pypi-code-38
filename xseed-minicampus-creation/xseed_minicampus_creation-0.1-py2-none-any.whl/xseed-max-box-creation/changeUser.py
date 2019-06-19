import subprocess as sp
import os

def changeUser(oldName, newName, password):
    os.system('echo %s|sudo pkill -u %s' %(password, oldName))
    os.system('sudo killall -u %s' %oldName)

    oldID = os.popen('id %s' %oldName).read()

    os.system('sudo usermod -l %s %s' %(newName, oldName))
    os.system('sudo groupmod -n %s %s' %(newName, oldName))
    os.system('sudo usermod -d /home/%s -m %s' %(newName, newName))
    os.system('sudo usermod -c "%s" %s' %(newName, newName))

    if (oldID == os.popen('id %s' %newName).read():
        print("User changed successfully from %s to %s" %(oldName, newName))
    else:
        raise Exception("ID of old user is not matching with new username")
