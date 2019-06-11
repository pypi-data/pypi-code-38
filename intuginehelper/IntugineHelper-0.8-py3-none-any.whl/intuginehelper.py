from pymongo import MongoClient
import os
import math


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
    server, port = os.environ['DATABASE_SERVER'].rsplit(':', 1)
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


def get_days(diff):
    return diff.total_seconds() / (24 * 60 * 60)


def get_eta_days(trip):
    if 'eta_days' in trip.keys():
        eta_days = trip['eta_days']
        eta_days = str(eta_days) or eta_days  # to remove that None shit in the eta_days
        try:
            return float(eta_days)
        except Exception as e:
            # print("ERR {0} {1} in {2}".format(e, 'eta_days', trip['_id']))
            return None
    else:
        # print("ERR No {0} in {1}".format('eta_days', trip['_id']))
        return None


def get_eta_hrs(trip):
    eta_days = get_eta_days(trip)
    if eta_days is None:
        if 'eta_hrs' in trip.keys():
            eta_hrs = str(trip['eta_hrs']) or trip['eta_hrs']  # to remove that None shit in the eta_hrs
            try:
                return float(eta_hrs)
            except Exception as e:
                print("ERR {} For Trip {}".format(e, trip['_id']))
    if eta_days is not None:
        return eta_days * 24
    else:
        try:
            return trip['base_google_time'] / 3600
        except Exception as e:
            print(e)
            return -1

