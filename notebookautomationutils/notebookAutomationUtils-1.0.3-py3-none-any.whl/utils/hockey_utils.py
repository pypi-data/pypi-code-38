#!/usr/bin/env python3.4
from hockeyapp.api import Hockeyapp
from typing import Dict
from pathlib import Path
import re
import os
import yaml

def get_app_version(app_link: str) -> Dict[str, str]:
    """
    Takes hockey app link in following format
    https://rink.hockeyapp.net/manage/apps/31029/app_versions/7432

    Args:
        datatype (object): Object on which aggregation is to be applied.
    
    Returns:  
        Dict[str, str]: Returns a dictonary containing version and build number as key-value pairs
    """
    if not app_link:
        return None
    
    try:
        filepath = os.path.realpath(__file__)
        index = filepath.rfind("/")
        dirpath = filepath[:index]
        
        config = yaml.load(open(dirpath + '/config.yaml', 'r'))
        k = app_link.rfind("/")

        # Fetch app version from the link
        app_version = app_link[k+1:]

        # Fetch app identifier from the link
        j = app_link.rfind("apps/")
        l = app_link.rfind("/app_versions")
        app_identifier = app_link[j+5:l]

        token = config['hockeyapp_token']
        app = Hockeyapp([token])
        app_id = Hockeyapp.convert_id_to_public_identifier(app, int(app_identifier))
        version_list = Hockeyapp.get_versions(Hockeyapp([token], app_id))
        for v in version_list:        
            # Get appversion and compare
            url = v.config_url
            i = url.rfind("/")
            url = url[i+1:]

            if url == app_version:
                short_version = (re.sub("[a-zA-Z]+", "", v.shortversion)).strip()
                return {'version': short_version, 'build': v.version}

    except Exception as e:
      print("get_app_version():: Error retriving app version: ", e)