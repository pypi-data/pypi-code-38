# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import configparser
import os.path

import appdirs


def get_configfilename():
    data_dir = appdirs.user_data_dir(appname="sesamclient", appauthor="Sesam")
    configfilename = os.path.join(data_dir, "settings.ini")
    return configfilename


def get_configparser():
    myconfigparser = configparser.ConfigParser()
    myconfigparser.read(get_configfilename(), encoding="utf-8")
    return myconfigparser


def save_configparser_to_file(myconfigparser):
    configfilename = get_configfilename()
    data_dir = os.path.dirname(configfilename)
    os.makedirs(data_dir, exist_ok=True)
    with open(configfilename, "w", encoding="utf-8") as configfile:
        myconfigparser.write(configfile)


def config_cmd(args):
    """This function handles the 'config' command.

    Note that we don't have to check if the args.optionname is valid here, since that check has already been
    performed by the argparser.

    :param args: The arguments to the config-command.
    """
    if "." not in args.optionname:
        raise AssertionError("config key does not contain a section: %s" % (args.optionname,))

    section, optionname = args.optionname.split(".", maxsplit=1)

    myconfigparser = get_configparser()
    if args.optionvalue:
        # set the config value
        optionvalue = " ".join(args.optionvalue)
        if not myconfigparser.has_section(section):
            myconfigparser.add_section(section)
        myconfigparser.set(section, optionname, optionvalue)

        save_configparser_to_file(myconfigparser)
    else:
        # get the configvalue
        value = myconfigparser.get(section, optionname, fallback="")
        if value:
            print(value)
