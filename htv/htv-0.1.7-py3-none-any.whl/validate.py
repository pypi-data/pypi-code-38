# System imports
import os
from os import listdir
from os.path import isfile, join
import traceback
import datetime
# Yaml imports
import yaml
from yamllint.config import YamlLintConfig
from yamllint import linter
from htvalidator.os_utility.miscellanea import printout, get_yaml
from htvalidator.os_utility.os_check import check_openstack

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
home = os.environ['HOME']


def validate_template(clients):
    ##################################################################
    #                        Variables setting                       #
    ##################################################################
    # It sets the date to the current day, the log will refer to this date when the script will be executed
    today = (str(datetime.datetime.now())).split(" ")[0]
    # It gets the files of the directory "./TemplateLocalStorage"
    onlyyaml = get_yaml()
    app_dir = "{}/htv".format(home)
    # It defines the name of the directories (for valid, warning, error, log files)
    pathvalid = app_dir + "/ValidYamlFiles"
    pathwarn = app_dir + "/WarnYamlFiles"
    patherr = app_dir + "/ErrYamlFiles"
    pathlog = app_dir + "/Log"
    pathfiles = app_dir + "/TemplateLocalStorage"

    ##################################################################
    #                      Validation process                        #
    ##################################################################
    # For every YAML file in onlyyalm list it will examine the file
    for yamlfile in onlyyaml:
        printout("\n\n>>> Examination of \"{}\" <<<\n".format(yamlfile), CYAN)
        # It saves the name of the file
        filename = yamlfile.split('.')[0]
        # It uses the file into the open function
        with open("{}/{}".format(pathfiles, yamlfile)) as F:
            # It reads the data and saves it into the variable 'data'
            data = F.read()
            print(">> Trying the validity")
            try:
                # It checks if the file is a valid yaml file
                doc = yaml.safe_load(data)
                printout("     Valid YAML file for yaml module\n", GREEN)
                conf = YamlLintConfig('extends: default')
                # It saves warnings if there are any
                gen = linter.run(data, conf)
                warnings = list(gen)
                # If there are warnings they will be saved into the Log file with the file name and the timestamp
                if warnings:
                    with open("{0}/{1}-{2}-warning.log".format(pathlog, filename, today), 'a+') as output:
                        printout("     This file has one or more warnings\n", YELLOW)
                        for warning in warnings:
                            output.write("{}\n".format(str(warning)))
                        # Then the file will be moved into a directory containing all the files with warnings
                        os.rename("{}/{}".format(pathfiles, yamlfile), "{}/{}".format(pathwarn, yamlfile))
                else:
                    # Otherwise the file will be moved into a directory containing all the valid YAML files
                    os.rename("{}/{}".format(pathfiles, yamlfile), "{}/{}".format(pathvalid, yamlfile))
                    printout("     No error for yaml lint too\n", GREEN)

                """Files are valid (even if with some warnings), so it will save items (such as the image, flavor etc) 
                in a specific list and then try to check for their existence into the openstack server"""
                print(">> Analyzing the template structure and items existence:")
                #################################################
                #    Search for items into openstack server     #
                #################################################

                check_openstack(doc, yamlfile, clients)

            # if the file has errors it is saved in ./ErrorsYamlFiles and a log is created
            except:
                # If there is an exception it will be saved into the Log file
                with open("{0}/{1}-{2}-error.log".format(pathlog, filename, today), 'a+') as output:
                    output.write("{}\n".format(str(traceback.format_exc())))
                printout("     Invalid YAML file\n", RED)
                os.rename("{}/{}".format(pathfiles, yamlfile), "{}/{}".format(patherr, yamlfile))
    printout("\n>> All files have been analyzed\n", CYAN)
