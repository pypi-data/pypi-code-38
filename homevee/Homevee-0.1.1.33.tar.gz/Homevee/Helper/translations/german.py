#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Homevee.Utils import Constants


def get_translations():
    translations = {
        'no_users_create_admin': "Es wurden noch keine Benutzer erstellt.\Du kannst jetzt einen Administrator erstellen.",
        'enter_password': 'Gib ein Passwort ein: ',
        'password_dont_match': 'Die Passwörter stimmen nicht überein',
        'enter_username': 'Gib einen Nuternamen ein: ',
        'your_remote_id_is': 'Deine Remote-ID lautet: ',
        'homevee_server_started': "Homevee-Server (Version: " + Constants.HOMEVEE_VERSION_NUMBER + ") wurde gestartet...",
        'update_available': "Es ist ein Update auf eine neue Version ({}) von Homevee verfügbar.",
        'no_cloud_connection': "Keine Verbindung zu Homevee-Cloud möglich..."
    }
    return translations