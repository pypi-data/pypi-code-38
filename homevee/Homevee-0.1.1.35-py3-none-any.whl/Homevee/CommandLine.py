#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse

from Homevee import Homevee
from Homevee.Helper import Logger
from Homevee.Helper.translations import translate_print, translate
from Homevee.Manager.UserManager import UserManager
from Homevee.Utils.Database import Database


def main():
    homevee = Homevee()

    #parse args
    parser = argparse.ArgumentParser(description='Homevee ist dein neues Smarthome-System!')
    parser.add_argument('--mode', default="start", type=str, help='Modus; default: Homevee starten (start)')
    parser.add_argument('--use_cloud', default=True, type=bool, help='Gibt an, ob die Cloud-Verbindung genutzt werden soll')
    parser.add_argument('--websocket_server', default=False, type=bool, help='Gibt an, ob der Websocket-Server genutzt werden soll')
    parser.add_argument('--http_server', default=False, type=bool, help='Gibt an, ob HTTP-Server genutzt werden soll')
    parser.add_argument('--is_admin', default=False, type=bool, help='Gibt an, ob der neu hinzugefügte Nutzer ein Administrator sein soll')
    parser.add_argument('--is_debug', default=False, type=bool, help='Gibt an, ob Debug-Meldungen ausgegeben werden sollen')

    args = parser.parse_args()

    Logger.IS_DEBUG = args.is_debug

    #print(args)

    #check if Homevee has atleast 1 user
    if not UserManager().has_users(Database()):
        translate_print("no_users_create_admin")
        add_user(homevee, is_admin=True)

    if args.mode == "start":
        start_server(homevee)
    elif args.mode == "add_user":
        add_user(homevee, args.is_admin)

def start_server(homevee):
    homevee.start()

def get_password():
    return input(translate('enter_password'))

    password = getpass()  # prompt="Gib ein Passwort ein:")
    #print(password)

    password_again = getpass()  # prompt="Wiederhole das Passwort:")
    #print(password_again)

    while (password != password_again):
        translate_print('passwords_dont_match')
        password = getpass()  # prompt="Gib ein Passwort ein:")
        password_again = getpass()  # prompt="Wiederhole das Passwort:")

    return password

def add_user(homevee, is_admin=False):
    username = input(translate('enter_username'))
    #print(username)

    password = get_password()

    homevee.add_user(username=username, password=password, is_admin=is_admin)


if __name__ == "__main__":
    main()