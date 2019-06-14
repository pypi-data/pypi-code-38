#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import json
import random
import time
import urllib.error
import urllib.error
import urllib.error
import urllib.parse
import urllib.parse
import urllib.parse
import urllib.request
import urllib.request
import urllib.request

from Homevee.Helper import Logger
from Homevee.Item.User import User
from Homevee.Utils.Database import Database

CONTEXT_VALIDITY = 60

SMART_API_PATH = "https://api.homevee.de/api.php"

def contains_pattern(patterns, text):
    for pattern in patterns:
        #print pattern
        if is_in_order(pattern, text):
            return True
    return False

def is_in_order(words, text):
    indices = []

    word_parts = text.split(" ")

    for word in words:
        found = False
        if isinstance(word, list):
            for word_item in word:
                if found:
                    break
                #print word_item

                if(word_item in word_parts):
                    if(len(indices) > 0):
                        max_index = indices[len(indices)-1]
                        indices.append(word_parts.index(word_item, max_index+1))
                    else:
                        indices.append(word_parts.index(word_item))
                    #print word_item+" found"
                    found = True

            if not found:
                return False
        else:
            #print word

            if (word in word_parts):
                if(len(indices) > 0):
                    max_index = indices[len(indices)-1]
                    indices.append(word_parts.index(word, max_index+1))
                else:
                    indices.append(word_parts.index(word))
                #print word+" found"
            else:
                return False

    last_value = -1
    for index in indices:
        if index is -1 or index <= last_value:
            return False
        last_value = index
    return True

def is_in_order_backup(words, text):
    indices = []

    for word in words:
        found = False
        if isinstance(word, list):
            for word_item in word:
                if found:
                    break
                #print word_item
                position = text.find(word_item)
                if position is not -1:
                    indices.append(position)
                    found = True
            if not found:
                return False
        else:
            #print word
            position = text.find(word)
            if position is not -1:
                indices.append(position)
            else:
                return False

    last_value = -1
    for index in indices:
        if index is -1 or index <= last_value:
            return False
        last_value = index
    return True

def get_no_permission_text():
    return random.choice(["Du hast nicht die nötigen Berechtigungen für diese Aktion.",
		"Dazu fehlen dir die Berechtigungen.",
		"Das darfst du nicht."])

def classify_voice_command(request):
    url = "https://assistant.Homevee.de:444/"
    data = urllib.request.urlopen(url + urllib.parse.quote(codecs.encode(request, 'utf-8'))).read()
    return json.loads(data)

def generate_string(answer_data):
    if not isinstance(answer_data, list):
        return str(answer_data)

    chosen_answer = random.choice(answer_data)

    output = ""

    if isinstance(chosen_answer, list):
        for part in chosen_answer:
            output = output + generate_string(part)
    else:
        return str(chosen_answer)
    return str(output)

def set_context(user: User,context_key, context_data, db: Database = None):
    if db is None:
        db = Database()

    Logger.log(context_data)

    context_data = json.dumps(context_data)

    db.delete("DELETE FROM 'VOICE_COMMAND_USER' WHERE USERNAME == :user",
                {'user': user.username})

    db.insert("INSERT INTO VOICE_COMMAND_USER (USERNAME, CONTEXT_TIME, CONTEXT_KEY, CONTEXT_DATA) VALUES (:username, :time, :key, :data)",
                {'username': user.username, 'time': int(time.time()), 'key': context_key, 'data': context_data})

def get_context(user: User,db: Database = None):
    if db is None:
        db = Database()
    data = db.select_one("SELECT * FROM 'VOICE_COMMAND_USER' WHERE USERNAME == :user",
                {'user': user.username})

    if data:
        context_data = data

        if(int(time.time()) - int(context_data['CONTEXT_TIME'])) <= CONTEXT_VALIDITY:
            db.delete("DELETE FROM 'VOICE_COMMAND_USER' WHERE USERNAME == :user",
                        {'user': user.username})

            return context_data
        return None
    else:
        return None

def get_okay():
    try:
        url = SMART_API_PATH + "/?action=okay"
        Logger.log(url)

        response = urllib.request.urlopen(url)
        data = response.read()

        data = data.decode('utf-8')

        if data is not None:
            return data
    except urllib.error.HTTPError as e:
        Logger.log(e)
        return ['Sehr gern', 'Ok', 'Alles klar']

def replace_voice_commands(text, user, db: Database = None):
    if db is None:
        db = Database()

    results = db.select_all("SELECT * FROM VOICE_COMMAND_REPLACE WHERE USERNAME = :user",
                {'user': user.username})

    for item in results:
        text = text.replace(item['TEXT'], item['REPLACE_WITH'])

    return text