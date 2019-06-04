from Homevee.Utils.Database import Database
from Homevee.VoiceAssistant.Modules import VoiceModule


class VoiceShoppingListModule(VoiceModule):
    def find_items(self, text, db: Database = None):
        if db is None:
            db = Database()
        items = []

        results = db.select_all("SELECT * FROM SHOPPING_LIST", {})

        for item in results:
            position = text.find(item['ITEM'].lower())
            if position is not -1:
                items.append({'item': item['ITEM'], 'amount': item['AMOUNT'], 'id': item['ID']})

        return items