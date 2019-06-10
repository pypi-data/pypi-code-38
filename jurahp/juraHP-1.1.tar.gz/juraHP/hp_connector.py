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


def get_sshpass_pwd():
    get_my_home_path = os.environ["HOME"]
    os.chdir(get_my_home_path)

    find_sshpass_file = subprocess.Popen(["ls", "-a"], stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out_put = find_sshpass_file.communicate()[0]
    out_put = out_put.decode()

    if ".sshpass" in out_put:
        my_pass_word = subprocess.Popen(["cat", ".sshpass"], stdout=subprocess.PIPE)
        my_pass_word = my_pass_word.communicate()[0]
        clean_pass_word = my_pass_word.decode()
        return clean_pass_word.strip()
    else:
        print("Can not use the script. Need sshpass file.")
        exit()


def ssh_hp_rename(host_name, commands):
    """This is function is used to connect to an AP and rename the interfaces"""
    ENTER = "\n"
    user_name = getpass.getuser()
    pass_word = get_sshpass_pwd()
    ssh = paramiko.SSHClient()

    try:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host_name, username=user_name, password=pass_word, look_for_keys=False, port=22)
        print("connected to {0}\n".format(host_name))

    except:  # Record unreachable hosts in a list
        print("could not connect to {}".format(host_name))
        ssh.close()
    else:
        #  Create a channel to send commands to the host
        channel = ssh.invoke_shell()

        for cmd in commands:
            channel.send(cmd)
            channel.send(ENTER)
            time.sleep(2)

            read_output = channel.recv(9999)
            time.sleep(4)
            print(read_output)

        print("=" * 100)
        print()
        print("HP-SW ::::  Renaming Completed !!\n".upper())

        channel.close()
        ssh.close()

