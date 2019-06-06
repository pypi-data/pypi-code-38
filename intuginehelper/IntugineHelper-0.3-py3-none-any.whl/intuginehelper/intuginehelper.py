#!/usr/bin/env python3
from pymongo import MongoClient
import os


def square(x):
    return x * x


def get_distane(src, dest):
    Radius = 6371000  # Radius of the earth in m
    dLat = math.radians(dest[0] - src[0])
    dLon = math.radians(dest[1] - src[1])
    a = square(math.sin(dLat / 2)) + math.cos(math.radians(src[0])) * math.cos(math.radians(dest[0])) * square(math.sin(dLon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return math.floor(Radius * c)  # Distance in m


def get_database():
    server, port = open('private', 'r').read().rsplit(':', 1)
    client = MongoClient(server, port=int(port))
    database = client[os.environ['DATABASE_CLIENT']]
    return database


def get_running_trips():
    database = get_database()
    collection = database['trips']
    data = collection.find({'running': True, 'user': {
        '$nin': os.environ['BLACKLIST_CLIENTS'].split(',')
    }, 'client_client': {
        '$nin': os.environ['BLACKLIST_CLIENT_CLIENT'].split(',')
    }})
    return list(x for x in data)


def get_all_pings(trips_list):
    trips_ids = [x['_id'] for x in trips_list]
    database = get_database()
    collection = database['status']
    try:
        data = collection.aggregate([{
            '$match': {
                'tripId': {
                    '$in': trips_ids
                }
            }
        }, {
            '$group': {
                '_id': '$tripId', 'pings': {'$push': '$$ROOT'}
            }
        }])
        return list(x for x in data)
    except Exception as e:
        print(trips_ids)
        print(str(e))
        return []

