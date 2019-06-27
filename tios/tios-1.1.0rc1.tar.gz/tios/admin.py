import sys
import datetime
from tios import environments

env = environments.load_mongo_env(administrator=True)
db = env['COLLECTION'].database
db_name = env['DB_NAME']

def add_guest(password):
    '''
    Create the Tios guest account.
    '''
    now = datetime.datetime.utcnow()

    guest_privileges = {'resource':{'db':db_name, 'collection':''}, 
                        'actions':["find", 
                                   "listCollections", 
                                   "createIndex"]}
    db.command('createRole', 'guest', 
               privileges=[guest_privileges], roles=[])

    custom_data = {'registration_date': now}
    db.add_user('guest', password, customData=custom_data, 
                roles=['guest'], mechanisms=['SCRAM-SHA-1'])

def add_user(name, password):
    '''
    Add a new user with the given name and password
    '''

    now = datetime.datetime.utcnow()

    general_privileges = {'resource':{'db':db_name, 'collection':''}, 
                          'actions':["find", 
                                     "changeOwnPassword", 
                                     "listCollections", 
                                     "createIndex"]}
    user_privileges = {'resource':{'db':db_name, 'collection':name}, 
                       'actions':["find", 
                                  "update", 
                                  "insert", 
                                  "remove"]}
    db.command('createRole', name, 
               privileges=[general_privileges, user_privileges], roles=[])
    custom_data = {'registration_date': now}

    db.add_user(name, password, customData=custom_data, 
                roles=[name], mechanisms=['SCRAM-SHA-1'])

def remove_user(name):
    '''
    Delete a user from the tios database
    '''

    db.command('dropRole', name)
    db.drop_collection(name)
    db.remove_user(name)

def list_users():
    '''
    List the users in the tios database
    '''

    result = db.command('usersInfo', 1)
    return result['users']
