import traceback

from Homevee.Exception import DatabaseSaveFailedException, InvalidParametersException
from Homevee.Helper import Logger
from Homevee.Item import Item
from Homevee.Utils.Database import Database


class HeatingSchemeItem(Item):
    def __init__(self, time, value, days, is_active, devices, id=None):
        super(HeatingSchemeItem, self).__init__()
        self.time = time
        self.value = value
        self.days = days
        self.is_active = is_active
        self.devices = devices
        self.id = id

    def delete(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            db.delete("DELETE FROM HEATING_SCHEME WHERE ID == :id", {'id': self.id})
            db.delete("DELETE FROM HEATING_SCHEME_DAYS WHERE HEATING_SCHEME_ID == :id", {'id': self.id})
            db.delete("DELETE FROM HEATING_SCHEME_DEVICES WHERE ID == :id", {'id': self.id})
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
                # TODO add generated id to object
        except:
            if (Logger.IS_DEBUG):
                traceback.print_exc()
            raise DatabaseSaveFailedException("Could not save event to database")

    def build_dict(self):
        dict = {
            'id': self.id,
            'time': self.time,
            'value': self.value,
            'is_active': self.is_active,
            'days': self.days,
            'devices': self.devices
        }
        return dict

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        items = []
        for result in db.select_all(query, params):
            print(result)
            item = HeatingSchemeItem(None, None, None, None, None, result['ID'])
            items.append(item)
        return items

    @staticmethod
    def load_all(db: Database):
        if db is None:
            db = Database()
        return HeatingSchemeItem.load_all_from_db('SELECT * FROM EVENTS', {})

    @staticmethod
    def load_all_by_day(day, db: Database = None):
        if db is None:
            db = Database()
        return HeatingSchemeItem.load_all_from_db("""SELECT HEATING_SCHEME.ID, TIME, VALUE, ACTIVE, WEEKDAY_ID, 
        ROOMS.NAME as LOCATION, TYPE, DEVICE_ID FROM HEATING_SCHEME, HEATING_SCHEME_DAYS, HEATING_SCHEME_DEVICES, 
        ROOMS WHERE HEATING_SCHEME.ID = HEATING_SCHEME_DAYS.HEATING_SCHEME_ID AND HEATING_SCHEME.ID = 
        HEATING_SCHEME_DEVICES.ID AND HEATING_SCHEME_DEVICES.LOCATION = ROOMS.LOCATION AND WEEKDAY_ID = :day ORDER BY TIME""",
                                                  {'day': day})

    @staticmethod
    def load_all_ids_from_db(ids: list, db: Database = None):
        if db is None:
            db = Database()
        return HeatingSchemeItem.load_all_from_db("""SELECT HEATING_SCHEME.ID FROM HEATING_SCHEME 
        WHERE HEATING_SCHEME.ID in (%s)""" % ','.join('?'*len(ids)), ids)

    @staticmethod
    def create_from_dict(dict):
        try:
            id = dict['id']
            time = dict['timestamp']
            value = dict['text']
            is_active = dict['is_active']
            days = dict['days']
            devices = dict['devices']

            item = HeatingSchemeItem(time, value, days, is_active, devices, id)

            return item
        except:
            raise InvalidParametersException("HeatingSchemeItem.create_from_dict(): invalid dict")