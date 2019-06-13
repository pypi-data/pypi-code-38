"""
This module is Developed by Devesh Bajaj @deveshbajaj59@gmail.com
for the beteterment ans assistance of the developer for the usage and working with aws cloudwatch to view 
them and acess rthem on terminal and get all perform sll ther terminsl related snipping on it like 
Grep and all

"""

from sys import argv, path
from prettytable import PrettyTable
from os import system
from logging import exception
from .cloudwatch import CloudWatchlogs
from .display import DisplayData
"""
    1. use to colour text 
    @prGreen()
    @prCyan()
    @prYellow()
    @prRed()
    Parameters:
        skk (str)

    Returns:
        str(coloured string)
    Note :
        returns colored string  
"""


def prGreen(skk):
    return("\033[92m {}\033[00m" .format(skk))


def prCyan(skk):
    return("\033[96m {}\033[00m" .format(skk))


def prRed(skk):
    return("\033[91m {}\033[00m" .format(skk))


def prYellow(skk):
    return("\033[93m {}\033[00m" .format(skk))


class Services():
    def __init__(self):
        pass

    def CloudWatchlogs(self):
        """
            Calles @Configure()
        """
        CloudWatchlogs.Configure()

    def DisplayHelp(self):
        """
            shows help
        """
        t = PrettyTable(['Flags', 'supported Servies'])
        t.add_row(["logs", prCyan("To view Logs")])
        t.add_row(["[ServiceName ] -help", prCyan("To view help of Service")])
        print(t)


def main():
    """
    Main function of the Client Entry point of the Servies
    Determine Whhic service to Call
    for Now only cloudwatch and help

    parametre :
                Commandline :
                    -help
                    -logs 
    """
    try:
        argument = argv[1:]
        length = len(argument)

        object = Services()
        if length == 0:
            object.DisplayHelp()
        elif argument[0] == '-help':
            object.DisplayHelp()
        elif argument[0] == 'logs':
            if length == 1:
                CloudWatchlogs.Configure()
            elif length >= 2:
                argumentforlogs = argument[1:]
                print(argumentforlogs)
                CloudWatchlogs.ArgumentforCloudwatch(argumentforlogs)
    except Exception as identifier:
        print(identifier)
        exception(argument)
        # python3 CloudWatchlogs.py -t 5 now
        # python3 CloudWatchlogs.py -list
        # python3 CloudWatchlogs.py -t 5 2019-05-25 15:30:5
        # python3 CloudWatchlogs.py -d 5 2019-05-25 15:30:5 2019-05-25 15:30:5
        # awsassitance logs -t Ansible 2766 12:15:56 12:12:12


if __name__ == "__main__":
    main()
