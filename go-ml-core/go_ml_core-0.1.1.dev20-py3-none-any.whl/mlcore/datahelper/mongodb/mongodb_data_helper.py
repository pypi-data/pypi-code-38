import pymongo
from pymongo import MongoClient
import json
from uuid import UUID
from bson import ObjectId

import sys
import logging

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)-s %(levelname)-7s %(name)-s.%(funcName)s(): %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            #return obj.hex
            return str(obj)
        elif isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

class MongoDBDataHelper():

    def __init__(self, config):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        self.connect()

    def connect(self):
        if 'authmech' in self.config:
            self.client = MongoClient(
                host=self.config['server'], 
                username=self.config['username'],
                password=self.config['password'],
                port=int(self.config['port']),
                authSource=self.config['database'],
                authMechanism=self.config['authmech'])
        else:
            self.client = MongoClient(
                host=self.config['server'], 
                port=int(self.config['port']))
                
        self.logger.info('client = %s' % self.client)

        if 'database' in self.config:
            self.db = self.client[self.config['database']]
        else:
            self.db = None

        return self.client, self.db

    def get_collection(self, collection):
        return self.db[collection]

    def find(self, collection, condition):
        self.logger.info('start finding result for ... ')
        self.logger.info('\tdb = %s' % self.db)
        self.logger.info('\tcollection = %s' % collection)
        self.logger.info('\tcondition = %s' % condition)

        cursor = self.db[collection].find(condition)

        result = []
        for c in cursor:
            # make UUID and ObjectID JSON serializable
            result.append(json.loads(json.dumps(c, cls=JSONEncoder)))

        self.logger.info('result.count = %s' % len(result))
        if len(result) > 0:
            self.logger.info('result[0] = %s' % result[0])

        return result

