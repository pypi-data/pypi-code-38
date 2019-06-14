import traceback

from Homevee.Exception import DatabaseSaveFailedException, InvalidParametersException
from Homevee.Helper import Logger
from Homevee.Item import Item
from Homevee.Utils.Database import Database


class CalendarEntry(Item):
    def __init__(self, name, date, start, end, note, address, id=None):
        super(CalendarEntry, self).__init__()
        self.name = name
        self.date = date
        self.start = start
        self.end = end
        self.note = note
        self.address = address
        self.id = id

    def delete(self, db: Database = None):
        if db is None:
            db = Database()
        return db.delete("DELETE FROM CALENDAR WHERE ID == :id", {'id': self.id})

    def save(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            if (self.id is None or self.id == ""):
                new_id = db.insert("""INSERT INTO CALENDAR (NAME, START, END, NOTE, DATE, ADDRESS) VALUES 
                (:name, :start, :end, :note, :date, :address)""",
                                {'name': self.name, 'date': self.date, 'start': self.start, 'end': self.end,
                                 'note': self.note, 'address': self.address})
                self.id = new_id
            #update
            else:
                db.update("""UPDATE CALENDAR SET NAME = :name, START = :start, END = :end, NOTE = :note, 
                DATE = :date, ADDRESS = :address WHERE ID = :id""",
                                {'name': self.name, 'date': self.date, 'start': self.start, 'end': self.end,
                                 'note': self.note, 'address': self.address, 'id': self.id})
                # TODO add generated id to object
        except:
            if (Logger.IS_DEBUG):
                traceback.print_exc()
            raise DatabaseSaveFailedException("Could not save calendar-entry to database")

    def build_dict(self):
        dict = {
            'id': self.id,
            'name': self.name,
            'date': self.date,
            'start': self.start,
            'end': self.end,
            'address': self.address,
            'note': self.note,
        }

        return dict

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        items = []
        for result in db.select_all(query, params):
            item = CalendarEntry(result['NAME'], result['DATE'], result['START'], result['END'],
                                 result['NOTE'], result['ADDRESS'], result['ID'])
            items.append(item)
        return items

    @staticmethod
    def load_all_by_date(date, db: Database = None):
        if db is None:
            db = Database()
        return CalendarEntry.load_all_from_db('SELECT * FROM CALENDAR WHERE DATE = :date ORDER BY START ASC',
                                              {'date': date})

    @staticmethod
    def load_all(db: Database):
        if db is None:
            db = Database()
        return CalendarEntry.load_all_from_db('SELECT * FROM CALENDAR ORDER BY START ASC', {}, db)

    @staticmethod
    def load_all_ids_from_db(ids, db: Database = None):
        if db is None:
            db = Database()
        return CalendarEntry.load_all_from_db('SELECT * FROM CALENDAR WHERE ID IN (%s)'
                                       % ','.join('?' * len(ids)), ids, db)

    @staticmethod
    def create_from_dict(dict):
        try:
            id = dict['id']
            name = dict['name']
            date = dict['date']
            start = dict['start']
            end = dict['end']
            address = dict['address']
            note = dict['note']

            item = CalendarEntry(name, date, start, end, note, address, id)

            return item
        except:
            raise InvalidParametersException("CalendarEntry.create_from_dict(): invalid dict")

    @staticmethod
    def get_calendar_item_dates(year, db: Database = None):
        if db is None:
            db = Database()
        calendar_item_dates = []

        results = db.select_all("SELECT DISTINCT DATE FROM CALENDAR WHERE strftime('%Y', DATE) = :year",
                                      {'year': year})

        for calendar_entry in results:
            calendar_item_dates.append(calendar_entry['DATE'])

        return calendar_item_dates