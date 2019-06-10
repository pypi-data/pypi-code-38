# System imports
from os.path import isfile, join
from os import listdir
import sys
import os

# It saves the current working directory and the home of the user
dir_base = os.getcwd()
home = os.environ['HOME']

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
                result = {"message":
                "     The parameter will be allocated automatically through another resource"}
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
    onlyfiles = [f for f in listdir("{}/htv/rc_files".format(home)) if isfile(join("{}/htv/rc_files".format(home), f))]
    onlysh = [f for f in onlyfiles if f.endswith(".sh")]
    shfile = ""
    pwd = None
    shfile = None
    number = 1
    # For every file it prints the name with the corresponding number in the list
    if onlysh:
        printout(">> Choose the openrc.sh you prefer: \n", CYAN)
        for F in onlysh:
            print("{} - {}".format(number, F))
            number += 1
        # It saves the user's input choice of the admin-openrc.sh file
        printout("\n>> Type the corresponding number and press enter: \n", CYAN)
        choice = input()
        # It converts from string to int
        value = int(choice)
        try:
            # It saves the file from the list depending ont he chosen option
            shfile = onlysh[value - 1]
        except Exception as e:
            print(e)
    else:
        printout(">> There are no openrc files in '{}/htv/rc_files' dir. The application will now exit\n".format(home), RED)
        sys.exit()
    return pwd, shfile

#################################################
#               Arguments parsing               #
#################################################
# It parses and saves the arguments passed with the function validator.py
def parse_args(arguments):
    # It saves all the .sh files corresponding to the admin-openrc.sh files
    onlyfiles = [f for f in listdir("{}/htv/rc_files".format(home)) if isfile(join("{}/htv/rc_files".format(home), f))]
    onlysh = [f for f in onlyfiles if f.endswith(".sh")]
    shfile = ""
    pwd = None
    shfile = None
    for arg in arguments:
        # If openrc is in the args it saves the file name
        if ".sh" in arg:
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
                        ">> The selected openrc file is not present in '{}/htv/rc_files' dir. The application will now exit\n".format(home), RED)
                    sys.exit()
        elif "b'" in arg:
            pwd = arg.split("'")[1]
            pwd = pwd.encode()
        # If openrc is not in the args the app'll go in the interactive mode and ask the user to chose an openrc file
        else:
            pwd, shfile = ask_openrc()
    return pwd, shfile

#################################################
#                RAINBOW TERMINAL               #
#################################################
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

#following from Python cookbook, #475186
def has_colours(stream):
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():
        return False # auto color only on TTYs
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
        seq = "\x1b[1;%dm" % (30+colour) + text + "\x1b[0m"
        sys.stdout.write(seq)
    else:
        sys.stdout.write(text)
