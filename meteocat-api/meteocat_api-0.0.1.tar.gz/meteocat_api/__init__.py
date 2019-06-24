"""Meteocat API to retrieve Meteocat data"""

__author__ = "Alvaro Rodriguez"
__author_email__ = "alvaro.rdrgz.ramos@gmail.com"

import os.path

from meteocat_api.Manager import Manager
import meteocat_api.profile


def connection(profile_name='default', api_key=None):
    """Connect to Meteocat API with the given API key profile name."""
    if api_key is None:
        profile_fname = meteocat_api.profile.API_profile_fname(profile_name)
        if not os.path.exists(profile_fname):
            raise ValueError('Profile not found in {}. Please install your API \n'
                             'key with meteocat_api.profile.install_API_key('
                             '"<YOUR-KEY>")'.format(profile_fname))
        with open(profile_fname) as fh:
            api_key = fh.readlines()
    return Manager(api_key=api_key)

name = "meteocat_api"
