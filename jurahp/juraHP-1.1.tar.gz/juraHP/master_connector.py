#!/usr/bin/env python

__author__ = 'david.johnnes@gmail.com'

"""
This Script will be used to establish SSH connection.
"""

import paramiko
import time
import subprocess
import os
import getpass

un_reachable_hosts = []


def ssh_connector(user_name, pass_word, host_name):
    """ """
    ENTER = "\n"
    ssh = paramiko.SSHClient()

    try:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host_name, username=user_name, password=pass_word, look_for_keys=False, port=22)
        print("connected to {0}\n".format(host_name))
        time.sleep(4)
    except:  # Record unreachable hosts in a list
        print("Could not connect to >> {}".format(host_name))
        ssh.close()
        exit()
    else:
        #  Create a channel to send commands to the host
        channel = ssh.invoke_shell()
        print("Starting the channel !!!\n")

        channel.send("terminal length 1000")
        channel.send(ENTER)
        time.sleep(2)
        channel.send("show lldp info re")
        channel.send(ENTER)
        time.sleep(4)

        output = channel.recv(9999)
        time.sleep(6)
        print(output)
        channel.close()
        ssh.close()
        return output


#  This function is used to check and use the .sshpass as default authentication password
def get_sshpass_pwd():
    """ """
    home_path = os.environ["HOME"]
    os.chdir(home_path)

    file = subprocess.Popen(["ls", "-a"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = file.communicate()[0]
    output = output.decode()

    if ".sshpass" in output:
        password = subprocess.Popen(["cat", ".sshpass"], stdout=subprocess.PIPE)
        password = password.communicate()[0]
        password = password.decode()
        return password.strip()
    else:
        print("Can not use the script. Need sshpass file.")
        exit()


def save_to_file(data):
    file = open("temp_file", "w")
    file.write(data)


def main(hostname):
    """ """

    user_name = getpass.getuser()
    pass_word = get_sshpass_pwd()
    output = ssh_connector(user_name, pass_word, hostname)
    save_to_file(output)

    print("\n\nSaving the data to file.............")
    time.sleep(4)
