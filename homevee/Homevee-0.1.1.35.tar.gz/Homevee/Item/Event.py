import traceback

from Homevee.Exception import DatabaseSaveFailedException, InvalidParametersException
from Homevee.Helper import Logger
from Homevee.Item import Item, User
from Homevee.Utils.Database import Database


class Event(Item):
    def __init__(self, text, type, timestamp=None, id=None):
        super(Event, self).__init__()

        self.timestamp = timestamp
        self.text = text
        self.type = type
        self.id = id

    def delete(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            db.delete("DELETE FROM EVENTS WHERE ID == :id", {'id': self.id})
            return True
        except:
            return False

    def save(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            if (self.id is None or self.id == ""):
                db.insert("""INSERT INTO EVENTS (TEXT, TYPE) VALUES (:text, :type)""",
                            {'text': self.text, 'type': self.type})
            # update
            else:
                db.update("""UPDATE EVENTS SET TEXT = :text, TYPE = :type WHERE ID = :id""",
                            {'text': self.text, 'type': self.type, 'id': self.id})
                #TODO add generated id to object
        except:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
            raise DatabaseSaveFailedException("Could not save event to database")

    def build_dict(self):
        dict = {
            'id': self.id,
            'timestamp': self.timestamp,
            'text': self.text,
            'type': self.type
        }
        return dict

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        items = []
        for result in db.select_all(query, params):
            item = Event(result['TEXT'], result['TYPE'], result['TIMESTAMP'], result['ID'])
            items.append(item)
        return items

    @staticmethod
    def load_all_from_db_desc_date_by_type(offset: int, limit: int, type: str = None, db: Database = None) -> list:
        """
        Loads all events by the given type ordered by descending timestamp
        :param offset: skip the first x results
        :param limit: only show x results
        :param type: the type of the events to show
        :param db: the database connection
        :return: list of events
        """
        params = {'limit': limit, 'offset': offset}
        where_clause = ""
        if type is not None and type != "":
            params['type'] = type
            where_clause = "WHERE TYPE == :type "
        query = "SELECT * FROM 'EVENTS' " + where_clause + "ORDER BY TIMESTAMP DESC LIMIT :limit OFFSET :offset"
        return Event.load_all_from_db(query, params)

    @staticmethod
    def get_unseen_events(user: User, db: Database = None) -> int:
        """
        Returns the number of unseen events for the given user
        :param user: the user
        :param db: the database connection
        :return: number of unseen events
        """
        last_checked = user.events_last_checked
        events = Event.load_all_from_db("SELECT * FROM 'EVENTS' WHERE TIMESTAMP > :time",
                        {'time': last_checked})

        return len(events)

    @staticmethod
    def load_all_types_from_db(types, db: Database = None):
        if db is None:
            db = Database()
        query = 'SELECT * FROM EVENTS WHERE TYPE IN (%s)' % ','.join('?'*len(types)), types
        return Event.load_all_from_db(query, {})

    @staticmethod
    def load_all(db: Database):
        return Event.load_all_from_db('SELECT * FROM EVENTS', {})

    @staticmethod
    def create_from_dict(dict):
        try:
            id = dict['id']
            timestamp = dict['timestamp']
            text = dict['text']
            type = dict['type']

            item = Event(text, type, timestamp, id)

            return item
        except:
            raise InvalidParametersException("Event.create_from_dict(): invalid dict")