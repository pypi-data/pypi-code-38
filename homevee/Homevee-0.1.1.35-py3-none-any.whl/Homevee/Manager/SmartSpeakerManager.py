from Homevee.Item.Room import Room
from Homevee.Utils.Database import Database

class SmartSpeakerManager():
    def __init__(self):
        return

    def get_smart_speakers(self, user, db: Database = None):
        if db is None:
            db = Database()
        speakers =[]

        results = db.select_all("SELECT * FROM SMART_SPEAKER ORDER BY LOCATION ASC", {})

        for speaker in results:
            if user.has_permission(speaker['LOCATION']):
                item = {'name': speaker['NAME'], 'id': speaker['ID'], 'key': speaker['KEY'],
                        'location': speaker['LOCATION'], 'location_name': Room.get_name_by_id(speaker['LOCATION'],
                                                                                              db)}

                speakers.append(item)

        return {'speakers': speakers}

    def add_edit_smart_speaker(self, user, db: Database = None):
        if db is None:
            db = Database()
        return