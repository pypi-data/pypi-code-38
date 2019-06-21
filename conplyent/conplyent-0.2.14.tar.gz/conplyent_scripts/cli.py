#!/usr/bin/env python3

'''
:File: cli.py
:Author: Jayesh Joshi
:Email: jayeshjo1@utexas.edu

Console script used to install conplyent as a startup program on both Windows
and Linux, and provides means to run both the client and the server.
'''

import os
import sys
import ast
import re
import logging

import click
import conplyent


def _install_windows(port):
    from subprocess import run, CREATE_NEW_CONSOLE
    print("Detected Windows OS")
    print("Installing conplyent server listening to port # {}".format(port))
    user = os.getlogin()
    startup = "{}\\..\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup".format(
        os.environ.get("windir"), user)  # This works for Windows 10... not sure about Windows 7-
    print("Assumming startup folder is in {}".format(startup))
    file_name = "{}\\conplyent_{}.bat".format(startup, port)
    with open(file_name, "w") as file:
        file.write("if not DEFINED IS_MINIMIZED set IS_MINIMIZED=1 && start \"\" /min \"%~dpnx0\" %* && exit\n"
                   "    conplyent start-server --port {}\n".format(port) +
                   "    set /p id=\"Press enter to exit command...\"\n" +
                   "exit")
    print("Created new file {}".format(file_name))

    print("Starting new console to start off the server")
    run("{}\\conplyent_{}.bat".format(startup, port), creationflags=CREATE_NEW_CONSOLE)


def _install_linux(port):
    import lsb_release
    release = lsb_release.get_lsb_information()["RELEASE"]
    print("Detected Linux OS {}".format(release))
    if(not(release[:2] == "16" or release[:2] == "18")):
        print("Linux OS not currently supported for installation")
        return
    print("Installing conplyent server listening to port # {}".format(port))

    if(not(os.path.isdir("/usr/bin/conplyent"))):
        os.mkdir("/usr/bin/conplyent")

    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open("/usr/bin/conplyent/conplyent_{}.sh".format(port), "w") as file:
        file.write("#!/bin/sh\npip3 install conplyent\n{} {}/cli.py start-server --port {}".format(
            sys.executable, dir_path, port))

    os.system("chmod +x /usr/bin/conplyent/conplyent_{}.sh".format(port))

    with open("/etc/systemd/system/conplyent_{}.service".format(port), "w") as file:
        file.write("[Unit]\nDescription=conplyent service\nWants=network-online.target\n"
                   "After=network-online.target network.target\n\n")
        file.write("[Service]\nExecStart=/usr/bin/conplyent/conplyent_{}.sh\n\n".format(port))
        file.write("[Install]\nWantedBy=default.target")

    os.system("chmod 664 /etc/systemd/system/conplyent_{}.service".format(port))
    os.system("systemctl enable conplyent_{}.service".format(port))
    os.system("systemctl restart conplyent_{}.service".format(port))

    print("Done")


def _parse_args(arg_list):
    args = []
    kwargs = {}

    for arguments in arg_list[1:]:
        if(arguments):
            if("=" in arguments):
                key, value = arguments.split("=")
                try:
                    kwargs[key] = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    kwargs[key] = value
            else:
                try:
                    args.append(ast.literal_eval(arguments))
                except (ValueError, SyntaxError):
                    args.append(arguments)

    return args, kwargs


@click.group()
def cli():
    if(os.name == 'posix'):
        if(os.geteuid() != 0):
            os.system("sudo python3 {}".format(" ".join(sys.argv)))
            sys.exit()


@cli.command(help="Installs the server to startup on each boot")
@click.option("-p", "--port", help="Startup server will run on specified port", default=9922, type=int)
def install(port):
    '''
    Installs conplyent server for each platform. This currently supports Windows
    10 and Ubuntu 16.04+. On windows, this simply adds it to the startup local
    location. On ubuntu, this registers the server as a systemd service.
    '''
    if(os.name == "nt"):
        _install_windows(port)
    elif(os.name == "posix"):
        _install_linux(port)
    else:
        raise NotImplementedError("Unknown OS... unsupported by conplyent at the moment")


@cli.command(help="Uninstalls the server and prevents it from starting up")
@click.option("-p", "--port", help="Define port to uninstall", default=9922, type=int)
def uninstall(port):
    raise NotImplementedError("To be implemented")


@cli.command(help="Edit system local options for conplyent")
@click.option("--revert", help="Revert conplyent options to defaults", default=False, is_flag=True)
def edit_options(revert):
    '''
    Allows users to edit local options for conplyent
    '''
    conplyent.edit_options(revert=revert)


@cli.command(name="start-server", help="Runs the server and starts listening on port")
@click.option("-p", "--port", help="Starts server on specified port", default=9922, type=int)
@click.option("--quiet", help="Sets the logging to quiet", default=False, is_flag=True)
@click.option("--debug", help="Sets the logging to debug (quiet must be false)", default=False, is_flag=True)
@click.option("--savelog/--no-savelog", help="Saves consoleoutput to log directory", default=True, is_flag=True)
def start_server(port, quiet, debug, savelog):
    '''
    Starts the server on localhost on the provided port. Users can run this on
    quiet mode, basic info mode, or on debug mode.
    '''
    if(not(quiet)):
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

    if(savelog):
        conplyent.save_logs()

    conplyent.server.start(port)


@cli.command(name="start-client", help="Run client to talk to server")
@click.option("-h", "--hostname", help="Host name of server to connect to", required=True, type=str)
@click.option("-p", "--port", help="Starts server on specified port", default=9922, type=int)
@click.option("-t", "--timeout", help="Timeout waiting for server to connect", default=None, type=int)
def start_client(hostname, port, timeout):
    '''
    Starts interactive client mode. Only keyword connected to this interactive
    mode is "commands" which will print out all available server commands.
    '''
    conn = conplyent.client.add(hostname, port)
    conn.connect(timeout=timeout)
    server_methods = conn.server_methods()

    while(True):
        response = input("Enter command: ")
        arg_list = re.split(r"\[(.*)\]|\"(.*)\"|\'(.*)\'| ", response)
        if(arg_list and (arg_list[0] == "commands")):
            print("Server commands:\n{}".format("\n".join(server_methods)))
        elif(not(arg_list) or not(arg_list[0] in server_methods)):
            print("Unknown command")
        else:
            args, kwargs = _parse_args(arg_list)
            getattr(conn, arg_list[0])(*args, **kwargs, complete=True, echo_response=True)


if(__name__ == '__main__'):
    cli()
