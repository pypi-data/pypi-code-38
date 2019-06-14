from pymongo import MongoClient
import datetime
import os

gmt_to_ist = datetime.timedelta(hours=5, minutes=30)


def get_database():
    server, port = os.environ['DATABASE_SERVER'].rsplit(':', 1)
    client = MongoClient(server, port=int(port))
    database = client[os.environ['DATABASE_CLIENT']]
    return database


def get_all_users():
    """
    :return: list of all users in database
    """
    database = get_database()
    collection = database['users']
    data = collection.find({})
    return list(x for x in data)


def get_running_trips():
    """
    :return: list of all trips that are running
    """
    database = get_database()
    collection = database['trips']
    data = collection.find({'running': True, 'user': {
        '$nin': os.environ['BLACKLIST_CLIENTS'].split(',')
    }, 'client_client': {
        '$nin': os.environ['BLACKLIST_CLIENT_CLIENT'].split(',')
    }})
    return list(x for x in data)


def get_trips(user, client, start, end):
    """
    :param user: username
    :param client: client name
    :param start: start time ex: [2019, 01, 01]
    :param end:  End Time ex: [2019, 02, 02]
    :return: list of all the trips with given client name else return all the trips with user
    """
    database = get_database()
    collection = database['trips']
    start = datetime.datetime(start[2], start[1], start[0]) - gmt_to_ist
    end = datetime.datetime(end[2], end[1], end[0]) - gmt_to_ist

    query = {
        'user': user,
        '$and': [{
            '$or': [{
                'startTime': {'$lte': end}
            }, {
                'startTime': {'$lte': end.isoformat()}
            }]
        }, {
            '$or': [{
                'endTime': {'$gte': start}
            }, {
                'endTime': {'$gte': start.isoformat()}
            }, {
                'running': True
            }]
        }
        ]
    }
    if client == '' or client is None:
        data = collection.find(query)
    else:
        query['client_client'] = client
        data = collection.find(query)
    if isinstance(data, list):
        return data
    else:
        res = list()
        for x in data:
            res.append(x)
        return res


def get_all_pings(trips_list):
    """
    get all pings for all the trips
    :param trips_list: list of all the trips Id's
    :return: Object containing list of ['_id':'tripId', 'pings': list( all pings )]
    """
    trips_ids = [x['_id'] for x in trips_list]
    database = get_database()
    collection = database['status']
    try:
        data = collection.aggregate([{
            '$match': {'tripId': {'$in': trips_ids}}
        }, {
            '$group': {'_id': '$tripId', 'pings': {'$push': '$$ROOT'}}
        }], allowDisUse=True)
        return list(x for x in data)
    except Exception as e:
        print(str(e))
        return []


def get_pings(trips_list, start, end):
    """
    get all pings for all the trips that have created at between start and end
    :param trips_list: list of all the trips Id's
    :param start: start time for the trips
    :param end: end time for the trips
    :return: Object containing list of ['_id':'tripId', 'pings': list( all pings )]
    """
    start = datetime.datetime(start[2], start[1], start[0]) - gmt_to_ist
    end = datetime.datetime(end[2], end[1], end[0]) - gmt_to_ist + datetime.timedelta(1)
    database = get_database()
    collection = database['status']
    data = collection.aggregate([{
        '$match': {'tripId': {'$in': trips_list}, 'createdAt': {'$gte': start, '$lte': end}}
    }, {
        '$group': {'_id': '$tripId', 'pings': {'$push': '$$ROOT'}}
    }], allowDiskUse=True)
    return list(x for x in data)
