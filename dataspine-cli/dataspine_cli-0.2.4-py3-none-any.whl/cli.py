#-*- coding: utf-8 -*-

import os
import json
import click
import requests
import os.path
from basicauth import encode
#import keyring
import configparser
from utils import API_URL_BASE, PUBLIC_KEY_PATH, USERDATA_PATH, API_SERVER
#from cluster import cluster
from model import model
from predict import predict
#from get import get


@click.group()
def main():
    pass


#main.add_command(cluster)
main.add_command(model)
main.add_command(predict)
#main.add_command(get)
################################

# data = {}
# decoded_data = {}

# secret = 'bw$u55&le#a=mm_zths96b!i@0=z7)#c9#k)4!j(q1f9+8^8y0'
# current_time = calendar.timegm(time.gmtime())
#
#
# def valid_token():
#     if 'exp' in decoded_data:
#         return current_time < decoded_data['exp']
#     else:
#         return False
#
#


@main.command()
@click.option('--username', prompt='Username', help='User Name.')
@click.option('--password', prompt='Password', help='User Password.', hide_input=True)
@click.option('--account-uuid', prompt='Account UUID', help='User Account UUID.', hide_input=False)
def login(username, password, account_uuid):
    """Authentication for Dataspine"""
    url = API_URL_BASE+"/login"
    encoded_str = encode(username, password)
    headers = {
        "authorization": encoded_str,
        "x-account-uuid": account_uuid
    }
    try:
        from json.decoder import JSONDecodeError
    except ImportError:
        JSONDecodeError = ValueError


    response = requests.get(url, headers=headers)
    try:
        keys = json.loads(response.text)
        # print(keys)
    except JSONDecodeError:
        print ("Something went wrong")

    user_data = keys["user"]
    config = configparser.ConfigParser()
    config['default'] = {'First Name': user_data["user_name"], 'Second Name': user_data["user_lastname"], 'Email': user_data["user_email"], 'Role': user_data["user_role"],
          'username': username, 'account-uuid': account_uuid, 'token': keys["token"], 'password':password}

    if response.status_code == 200:
        os.makedirs(os.path.dirname(PUBLIC_KEY_PATH), exist_ok=True)
        with open(PUBLIC_KEY_PATH, 'w') as f:
            f.write(keys["public_key"])

        os.makedirs(os.path.dirname(USERDATA_PATH), exist_ok=True)
        with open(USERDATA_PATH, "w") as configfile:
            config.write(configfile)

        #keyring.set_password(service_name=account_uuid, username=username, password=password)
        print('Login Succeeded!')
    else:
        print('Invalid credentials!')


@main.command()
def help():
    """Help command on main group"""
    url = API_URL_BASE + '/help'
    response = requests.get(url).json()
    for f in response['functions']:
        print(f)
    # if (valid_token() == True):
    #     url = URL + '/help'
    #     response = requests.gore_filter


@main.command()
@click.option('--account-uuid', prompt='Account UUID', help='User Account UUID.', hide_input=False)
def init(account_uuid):
   """Init command on main group"""
   url = API_URL_BASE + '/init'
   headers = {
       "x-account-uuid": account_uuid
   }
   response = requests.get(url, headers=headers).json()
   print (response)


@main.command()
def version():
    """Version command on main group"""
    url = API_URL_BASE + '/version'
    response = requests.get(url).json()
    for i in response:
        print(i, response[i], "\n")


cli_commands = click.CommandCollection(sources=[main])

if __name__ == '__main__':
    cli_commands()
