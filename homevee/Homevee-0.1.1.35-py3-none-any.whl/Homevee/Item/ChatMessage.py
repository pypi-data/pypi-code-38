import json
import time
import traceback

from Homevee.Exception import InvalidParametersException, DatabaseSaveFailedException
from Homevee.Helper import Logger
from Homevee.Item import Item
from Homevee.Utils.Database import Database
from Homevee.Utils.NotificationManager import NotificationManager


class ChatMessage(Item):
    def __init__(self, username, data, timestamp=None, id=None):
        super(ChatMessage, self).__init__()
        self.username = username
        self.data = data
        self.timestamp = timestamp
        self.id = id
        #self.format_time()

    def send(self, db: Database = None):
        self.timestamp = int(time.time())*1000
        self.save()

        results = db.select_all("SELECT USERNAME FROM USERDATA WHERE USERNAME != :user", {'user': self.username})
        users = []

        for user in results:
            users.append(user['USERNAME'])

        NotificationManager().send_notification_to_users(users, "Neue Nachricht von " + self.username,
                                                       json.loads(self.data)['msg'], db,
                                                       click_action="ChatActivity")

        return {'username': self.username, 'data': self.data, 'time': self.timestamp}


    def save(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            print("dict:")
            print(self.get_dict())

            if (self.id is None or self.id == ""):
                timestamp = self.timestamp

                if timestamp is None:
                    timestamp = int(time.time())*1000

                print("params:")
                print({'username': self.username, 'data': self.data, 'timestamp': timestamp})

                db.insert("""INSERT INTO CHAT_DATA (USERNAME, DATA, TIMESTAMP) VALUES (:username, :data, :timestamp)""",
                            {'username': self.username, 'data': self.data, 'timestamp': timestamp})
        except:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
            raise DatabaseSaveFailedException("Could not save event to database")

    def build_dict(self):
        dict = {
            'id': self.id,
            'timestamp': self.timestamp,
            #'formatted_timestamp': self.formatted_timestamp,
            'data': self.data,
            'username': self.username
        }
        return dict

    '''
    def format_time(self):
        try:
            if self.timestamp is not None:
                local_time = datetime.datetime.fromtimestamp(int(self.timestamp))
                formatted_timestamp = local_time.strftime("%d.%m.%Y %H:%M")
                self.formatted_timestamp = formatted_timestamp
        except:
            self.formatted_timestamp = self.timestamp
    '''

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        items = []
        for result in db.select_all(query, params):
            item = ChatMessage(result['USERNAME'], result['DATA'], result['TIMESTAMP'], result['ID'])
            items.append(item)
        return items

    @staticmethod
    def load_all(db: Database):
        return ChatMessage.load_all_from_db('SELECT * FROM CHAT_DATA', {}, db)

    @staticmethod
    def load_all_by_time(time: int, limit: int, db: Database = None) -> list:
        """
        Loads all (or limited) chat messages before a timestamp
        :param time: the time in unixtime format
        :param limit: the number of results to show
        :param db: the database connection
        :return: the list of ChatMessages
        """
        where_clause = ""
        params = {'limit': limit}

        if time is not None and int(time) is not -1:
            where_clause = "WHERE TIMESTAMP < :time"
            params['time'] = time

        return ChatMessage.load_all_from_db("SELECT * FROM CHAT_DATA "+where_clause+" ORDER BY TIMESTAMP DESC LIMIT :limit",
        params, db)

    @staticmethod
    def create_from_dict(dict):
        try:
            id = dict['id']
            timestamp = dict['timestamp']
            data = dict['data']
            username = dict['username']

            item = ChatMessage(username, data, timestamp, id)

            return item
        except:
            raise InvalidParametersException("ChatMessage.create_from_dict(): invalid dict")