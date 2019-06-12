import os
import json


def read_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            config_dict = json.load(f)
            return config_dict
    else:
        print "config file doesn't exist!"
