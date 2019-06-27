import os
import json
import pymongo
from pymongo import MongoClient
import tios
"""
Module with functions to initialise and edit the Tios environment

Currently only a Mongo-based environment is available.
"""
def load_mongo_env(source=None, authenticate=True, administrator=False):
    '''
    Get the tios environment from the configuration file, if it exists.
    '''
    if source is None:
        if os.path.exists(tios.TIOS_CONFIGFILE):
            with open(tios.TIOS_CONFIGFILE, 'r') as f:
                env = json.load(f)
        else:
            env = {
                    'DB_URL': 'tirith.pharm.nottingham.ac.uk',
                    'DB_NAME': 'tios',
                    'DB_COLLECTION': 'guest',
                    'DB_PORT': 27017,
                    'DB_USER': 'guest',
                    'DB_PWD': 'guest123',
                    'IMD_PORT': '40237',
                  }
        save_mongo_env(env)
    else:
        env = source

    if not authenticate:
        return env

    db = MongoClient(env['DB_URL'], int(env['DB_PORT']))[env['DB_NAME']]
    if administrator:
        if 'DB_ADMINISTRATOR' in env and 'DB_ADMIN_PWD' in env:
            db.authenticate(name=env['DB_ADMINISTRATOR'], 
                            password=env['DB_ADMIN_PWD'], source='admin')
        else:
            raise RuntimeError('You do not have administrator rights')
    else:
        db.authenticate(name=env['DB_USER'], password=env['DB_PWD'])
    env['COLLECTION'] = db[env['DB_COLLECTION']]
    return env

def save_mongo_env(env):
    '''
    Save the tios environment to the configuration file.
    '''
    coll = None
    if 'COLLECTION' in env:
        coll = env.pop('COLLECTION')
    if not os.path.exists(tios.TIOS_CONFIGDIR):
        os.mkdir(tios.TIOS_CONFIGDIR)
    with open(tios.TIOS_CONFIGFILE, 'w') as f:
        json.dump(env, f, indent=4)
    os.chmod(tios.TIOS_CONFIGFILE, 0o600)
    if coll is not None:
        env['COLLECTION'] = coll

