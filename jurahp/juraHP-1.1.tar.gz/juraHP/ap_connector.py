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


def ssh_ap_rename(host_name, user_name, pass_word, commands):
    """This is function is used to connect to an AP and rename the interfaces"""

    ENTER = "\n"
    ssh = paramiko.SSHClient()

    try:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host_name, username=user_name, password=pass_word, look_for_keys=False, port=22)
        print("connected to {0}\n".format(host_name))

    except:  # Record unreachable hosts in a list
        un_reachable_hosts.append(host_name)
        print("could not connect to {}".format(host_name))
        ssh.close()
    else:
        #  Create a channel to send commands to the host
        channel = ssh.invoke_shell()

        for cmd in commands:
            channel.send(cmd)
            channel.send(ENTER)
            time.sleep(4)

            read_output = channel.recv(9999)
            time.sleep(6)
            print(read_output)

        print("=" * 100)
        print()

        channel.close()
        ssh.close()


def rename_aps(data):

    print("\n\nStarting the login process !!!\n\n")
    user_name = getpass.getuser()
    pass_word = get_sshpass_pwd()

    for line in data:
        host_name = line[0]
        commands = line[1:]
        ssh_ap_rename(host_name, user_name, pass_word, commands)

    print("\nRenaming Completed !!\n".upper())

















