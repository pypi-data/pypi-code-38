#!/usr/bin/env python
__author__ = 'david.johnnes@gmail.com'

from juraHP import master_connector
from juraHP import ap_generator
from juraHP import ap_connector
from juraHP import hp_generator
from juraHP import hp_connector

""" """


def generate_ap_data(parent_switch):
    """ """
    client = ap_generator.APGenRobot("temp_file", parent_switch)
    output = client.generator()
    client.show_interfaces()
    print("\n")
    return output


def generate_hp_data():
    """ """
    client = hp_generator.HPGenRobot("temp_file")
    output = client.generator()
    client.show_interfaces()
    print("\n")
    return output

print("#" * 110)


def run_rename():
    """ """
    parent_switch = raw_input("Enter parent switch: ")
    master_connector.main(parent_switch)

    ap_data = generate_ap_data(parent_switch)
    ap_connector.rename_aps(ap_data)

    commands = generate_hp_data()
    hp_connector.ssh_hp_rename(parent_switch, commands)

if __name__ == "__main__":
    run_rename()



