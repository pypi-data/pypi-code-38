#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import urllib.error
import urllib.parse
import urllib.request

from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant import Helper


#todo change route module to class(es)

def get_distance_data(username, text, context, db: Database = None):
    if db is None:
        db = Database()

    distance_to_person = get_person_distance_data(username, text, context, db)
    if(distance_to_person is not None):
        return distance_to_person

    distance_to_place = get_person_distance_data(username, text, context, db)
    if(distance_to_place is not None):
        return distance_to_place

    text = text.replace(" an der ", "/")
    text = text.replace("bis nach", "nach")
    words = text.split()

    loc_from = None
    loc_to = None

    is_from = False
    is_to = False
    for i in range(0, len(words)):
        word = words[i]
        if not is_from:
            if word == "von":
                is_from = True
                continue
        else:
            if not is_to:
                if word == "nach":
                    is_to = True
                    continue
                if loc_from is None:
                    loc_from = word
                else:
                    loc_from += ' '+word
            else:
                if loc_to is None:
                    loc_to = word
                else:
                    loc_to += ' '+word

    #print((loc_from, loc_to))

    distance, duration = load_distance(loc_from, loc_to)

    minutes = duration/60

    duration_string = str(minutes) + ' Minuten'

    if minutes > 60:
        hours = minutes/60
        minutes = minutes%60

        if hours == 1:
            hour_string = "eine Stunde und"
        else:
            hour_string = str(hours) + " Stunden und"

        if minutes == 1:
            minute_string = "eine Minute"
        else:
            minute_string = str(minutes) + " Minuten"

        duration_string = hour_string + " " + minute_string

    answer_data = [
        ['Von ', loc_from.capitalize(), ' nach ', loc_to.capitalize(), ' sind es ', ['ca', 'etwa', 'in etwa', 'ungefähr'], ' ', distance/1000,
         ' Kilometer und die Fahrt dauert ', ['ca', 'etwa', 'in etwa', 'ungefähr'], ' ', duration_string, '.']
    ]
    output = Helper.generate_string(answer_data)

    return {'msg_speech': output, 'msg_text': output}

def get_person_distance_data(username, text, context, db: Database = None):
    if db is None:
        db = Database()
    results = db.select_all("SELECT * FROM PEOPLE_DATA", {})

    person = None

    for item in results:
        if(item['NAME'].lower() in text):
            person = item
        elif item['NICKNAME'].lower in text:
            person = item

    if(person is None):
        return None

    return None

def get_place_distance_data(username, text, context, db: Database = None):
    if db is None:
        db = Database()
    results = db.select_all("SELECT * FROM PLACES", {})

    place = None

    for item in results:
        if (item['NAME'].lower() in text):
            place = item

    if (place is None):
        return None

    return None

def load_distance(loc_from, loc_to):
    url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins="+loc_from+"&destinations="+loc_to+"&mode=driving&language=de-DE&sensor=false"

    result = urllib.request.urlopen(url).read()

    data = json.loads(result)

    distance = data['rows'][0]['elements'][0]['distance']['value']
    duration = data['rows'][0]['elements'][0]['duration']['value']

    return distance, duration