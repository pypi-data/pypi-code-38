# System imports
from os.path import isfile, join
from os import listdir
import sys
import os
import subprocess
# Encryption utilities imports
from cryptography.fernet import Fernet

# It saves the current working directory and the home of the user
dir_base = os.getcwd()
home = os.environ['HOME']


#################################################
#              Interactive or not?              #
#################################################
def interactive():
    # It calls the function ask_openrc to ask the operator which openrc.sh file he wants to use for the authentication
    pwd, path_to_file = ask_openrc()
    return pwd, path_to_file


def no_interactive(arg):
    # It calls the function parse_args in order to save the various args
    pwd, path_to_file = parse_args(arg)
    return pwd, path_to_file


#################################################
#              Get PARAMETERS values            #
#################################################
# It cycles the document in order to find the given parameter
def get_param(param, doc):
    result = ""
    # It checks if there is the key 'parameters' inside the document
    try:
        parameters = doc['parameters']
    # If not the function returns a "No parameter" message
    except:
        result = {"message": "     There are no parameters in this template"}
        return result
    if type(param) is list:
        print("is list, TODO")
    elif type(param) is dict:
        # For every k, v in the items of the parameter it checks if the key is "get_param"
        for k, v in param.items():
            if k == "get_param":
                parameter = v
                # If so it saves the value into the varaible "parameter"
                for key, value in parameters[parameter].items():
                    # For k, v in the parameter dict inside the parameters of the template it saves v, if k is "default"
                    if key == "default":
                        result = value
                    else:
                        pass
            # If k is "get_resource" it returns a message
            elif k == "get_resource":
                result = {"message": "     The parameter will be allocated automatically through another resource"}
            else:
                pass
    if not result:
        result = {"message": "     The parameter is not present"}
    return result


#################################################
#            Ask for the openrc file            #
#################################################
# Function that asks the user to choose an openrc file form the given list
def ask_openrc():
    # It saves all the .sh files corresponding to the admin-openrc.sh files
    onlysh = get_shfiles()
    pwd = ""
    number = 1
    # If the length of the list is 1 it means there is only one openrc file and it will be the one taken by the app
    if len(onlysh) == 1:
        shfile = onlysh[0]
        path_to_file = "{}/htv/rc_files/{}".format(home, shfile)
        return pwd, path_to_file
    else:
        # For every file it prints the name with the corresponding number in the list
        print(">> Choose the openrc.sh you prefer: ")
        for F in onlysh:
            print("{} - {}".format(number, F))
            number += 1
        # It saves the user's input choice of the admin-openrc.sh file
        choice = input(">> Type the corresponding number and press enter: ")
        try:
            # It converts from string to int
            value = int(choice)
            # It saves the file from the list depending on the chosen option
            shfile = onlysh[value - 1]
            path_to_file = "{}/htv/rc_files/{}".format(home, shfile)
            return pwd, path_to_file
        except:
            printout(">> Wrong input, the program will now exit\n", RED)
            sys.exit()


#################################################
#               Arguments parsing               #
#################################################
# TODO check if it works with openstack auth
# It parses and saves the arguments passed with 'htv' command
def parse_args(arg):
    path_to_file = arg
    shfile = path_to_file.split("/")[-1:][0]
    # If the arg is an openrc file:
    with open('{}'.format(path_to_file), 'rt') as F:
        lines = [line for line in F.readlines() if "export OS_PASSWORD=" in line]
        if lines:
            # If the list has been created it splits the line
            line = lines[0].split("export OS_PASSWORD=")[1]
            first_character = line[0:1]
            # It checks if the first character of the pwd is '$', if so the cycle ends
            if first_character == "$":
                pwd = ask_pwd(path_to_file)
            # If not, the pwd is splitted and encoded
            else:
                pwd = line.split("'")[1]
                pwd = pwd.encode()
        else:
            printout(">> This openrc file '{}' is not valid. The program will now exit".format(shfile), RED)
            sys.exit()

    # TODO accept multiple args (openrc and passwd)
    # If openrc is in the args it saves the file name
    """if ".sh" in arg:
        shfile = arg
        # If the passwd is in the args it saves it, splits it accordingly and encodes it.
        if "b'" in arg:
            pwd = arg.split("'")[1]
            pwd = pwd.encode()
        # If the password is not in the args
        else:
            if shfile in onlysh:
                # It opens the file and uses a list comprehension in order to saves all the lines with OS_PASSWORD
                with open('{}/htv/rc_files/{}'.format(home, shfile), 'rt') as F:
                    lines = [line for line in F.readlines() if "export OS_PASSWORD=" in line]
                    if lines:
                        # If the list has been created it splits the line
                        line = lines[0].split("export OS_PASSWORD=")[1]
                        first_character = line[0:1]
                        # It checks if the first character of the pwd is '$', if so the cycle ends
                        if first_character == "$":
                            pass
                        # If not, the pwd is splitted and encoded
                        else:
                            pwd = line.split("'")[1]
                            pwd = pwd.encode()
            else:
                printout(
                    ">> The selected openrc file is not present in '{}/htv/rc_files' dir. The application will now exit\n".format(
                        home), RED)
                sys.exit()
    elif "b'" in arg:
        pwd = arg.split("'")[1]
        pwd = pwd.encode()
    # If openrc is not in the args the app'll go in the interactive mode and ask the user to chose an openrc file
    else:
        pwd, shfile = ask_openrc()"""
    return pwd, path_to_file


#################################################
#                Ask for password               #
#################################################
# It asks for the password for the openrc file
def ask_pwd(path_to_file):
    # It gets the encryption/decryption key
    e_key = get_key()
    # It saves the openrc file name without the full path
    shfile = path_to_file.split("/")[-1:][0]
    # It gets the openstack password in the form of a string, encodes it and encrypts it with the key
    openstack_password = input(">> Enter the Openstack password for the file {}: ".format(shfile))
    pwd = openstack_password.encode()
    f = Fernet(e_key)
    encrypted = f.encrypt(pwd)
    # It creates the variable to insert
    password_line = "export OS_PASSWORD={}".format(encrypted)
    # It opens the openrc.sh file and change the PASSWORD line with the new encrypted password
    with open("{}".format(path_to_file), 'r+') as F:
        lines = F.readlines()
        F.seek(0)
        for line in lines:
            # If 'OS_PASSWORD' is not in the line, it re-writes the for-loop-line to the file
            if "export OS_PASSWORD=" not in line:
                F.write(line)
        # At the end it appends the new line with the saved password
        F.write("\n{}".format(password_line))
    # And it returns the password encoded and encrypted
    return encrypted


#################################################
#               Get various values              #
#################################################
# It gets the encryption/decryption key from the file key.key
def get_key():
    with open('{}/htv/key.key'.format(home), 'r') as F:
        e_key = F.read()
    return e_key


# It gets the htv application root path and then the base url of the venv where htv has been installed
def get_htv_path():
    venv_path = subprocess.run(["which", "htv"], stdout=subprocess.PIPE).stdout.decode('utf-8')
    # It deletes 'htv' from the path
    venv_path = venv_path[:-3]
    return venv_path


# It deletes everything from the file list_cron.txt
def empty_cron():
    with open('{}/htv/list_cron.txt'.format(home), 'w') as F:
        F.write("")


# It gets all the openrc.sh inside the directory where the user should puts em and saves them in a list 'onlysh'
def get_shfiles():
    try:
        onlyfiles = [f for f in listdir("{}/htv/rc_files".format(home)) if
                     isfile(join("{}/htv/rc_files".format(home), f))]
        onlysh = [f for f in onlyfiles if f.endswith(".sh")]
        if onlysh:
            return onlysh
    except:
        printout(">> There are no openrc files in {}/htv/rc_files! The program will now exit\n".format(home), RED)
        sys.exit()
    printout(">> There are no openrc files in {}/htv/rc_files! The program will now exit\n".format(home), RED)
    sys.exit()


# It gets all the yaml file inside the directory where the user should puts em and saves them in a list 'onlyyaml'
def get_yaml():
    try:
        # It first saves a list of files of the directory "./TemplateLocalStorage"
        onlyfiles = [f for f in listdir("{}/htv/TemplateLocalStorage".format(home)) if
                     isfile(join("{}/htv/TemplateLocalStorage".format(home), f))]
        # It then saves a list of only YAML files
        onlyyaml = [f for f in onlyfiles if f.endswith(".yaml")]
        if onlyyaml:
            return onlyyaml
    except:
        printout(">> There are no YAML files in {}/htv/TemplateLocalStorage! The program will now exit\n".format(home),
                 RED)
        sys.exit()
    printout(">> There are no YAML files in {}/htv/TemplateLocalStorage! The program will now exit\n".format(home), RED)
    sys.exit()


# It gets the already saved password from the openrc.sh file
def get_saved_pwd(shfile):
    with open("{0}/htv/rc_files/{1}".format(home, shfile), 'rt') as F:
        data = F.readlines()
        for line in data:
            # For every line it checks if OS_PASSWORD is in it and if so it saves the pwd and splits it accordingly
            if "export OS_PASSWORD=" in line:
                passwd = line.split("export OS_PASSWORD=")[1]
                pwd = passwd.split("'")[1]
                pwd = pwd.encode()
    return pwd


# It overwrite the new password to the openrc.sh file
def write_pwd(password_line, path_to_file):
    with open("{}".format(path_to_file), 'r+') as F:
        lines = F.readlines()
        F.seek(0)
        for line in lines:
            # If 'OS_PASSWORD' is not in the line, it re-writes the line to the file
            if "export OS_PASSWORD=" not in line:
                F.write(line)
        # At the end it appends the new line with the saved password
        F.write("\n{}".format(password_line))


#################################################
#                RAINBOW TERMINAL               #
#################################################
# It just let the application to print colored lines accordingly to errors, warnings, or valid results
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


# following from Python cookbook, #475186
def has_colours(stream):
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():
        return False  # auto color only on TTYs
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except:
        # guess false in case of error
        return False


has_colours = has_colours(sys.stdout)


def printout(text, colour=WHITE):
    if has_colours:
        seq = "\x1b[1;%dm" % (30 + colour) + text + "\x1b[0m"
        sys.stdout.write(seq)
    else:
        sys.stdout.write(text)
