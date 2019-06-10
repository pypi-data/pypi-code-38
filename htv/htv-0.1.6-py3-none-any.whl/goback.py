# System imports
import os
from os import listdir
from os.path import isfile, join
from htvalidator.os_utility.miscellanea import printout
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

try:
    # It gets the current working directory
    dir_base = os.getcwd()
    home = os.environ['HOME']
    app_dir = "{}/htv".format(home)
    # It defines the name of the directories (for valid files and for warning files)
    pathvalid = app_dir + "/ValidYamlFiles"
    pathwarn = app_dir + "/WarnYamlFiles"
    patherr = app_dir + "/ErrYamlFiles"
    pathfiles = app_dir + "/TemplateLocalStorage"
    pathlog = app_dir + "/Log"

    # It creates the list of valid files inside the valid directory
    validfiles = [f for f in listdir("{}".format(pathvalid)) if isfile(join("{}".format(pathvalid), f))]
    # It creates the list of warning files inside the warning directory
    warnfiles = [f for f in listdir("{}".format(pathwarn)) if isfile(join("{}".format(pathwarn), f))]
    # It creates the list of error files inside the error directory
    errfiles = [f for f in listdir("{}".format(patherr)) if isfile(join("{}".format(patherr), f))]
    # It then saves a list of only log files out of the previous list
    onlylog = [f for f in listdir("{}".format(pathlog)) if isfile(join("{}".format(pathlog), f)) and f.endswith(".log")]



    # It removes the Log files
    for logfile in onlylog:
        os.remove("{0}/{1}".format(pathlog, logfile))

    # It moves the valid file from the ValidYamlFile directory
    for validfile in validfiles:
        os.rename("{}/{}".format(pathvalid, validfile), "{}/{}".format(pathfiles, validfile))

    # It moves the warning file from the WarnYamlFile directory
    for warnfile in warnfiles:
        os.rename("{}/{}".format(pathwarn, warnfile), "{}/{}".format(pathfiles, warnfile))

    # It moves the warning file from the WarnYamlFile directory
    for errfile in errfiles:
        os.rename("{}/{}".format(patherr, errfile), "{}/{}".format(pathfiles, errfile))

    printout(">> Back to a clear testing environment, now you can execute:\n", CYAN)
    print("     - python validator.py")

except Exception as e:
    printout(">> An error occurred:\n{}\n".format(e), RED)
