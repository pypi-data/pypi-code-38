from Homevee.Item import Item
from Homevee.Utils.Database import Database


class ShoppingListItem(Item):
    def __init__(self, item, amount, id=None):
        super(ShoppingListItem, self).__init__()
        self.id = id
        self.item = item
        self.amount = amount

    def delete(self, db: Database = None):
        if db is None:
            db = Database()

        db.delete("DELETE FROM SHOPPING_LIST WHERE ID == :id", {'id': self.id})

    def save(self, db: Database = None):
        if (db is None):
            db = Database()

        if(self.id is None or self.id == ""):
            #TODO Check if entry with same name exists and notify user(???)

            new_id = db.insert("INSERT OR IGNORE INTO SHOPPING_LIST (AMOUNT, ITEM) VALUES (:amount, :name);",
                        {'amount': self.amount, 'name': self.item})
            self.id = new_id
        else:
            db.update("UPDATE OR IGNORE SHOPPING_LIST SET AMOUNT = :amount, ITEM = :name WHERE ID = :id",
                        {'amount': self.amount, 'name': self.item, 'id': self.id})

    def build_dict(self):
        dict = {
            'id': self.id,
            'item': self.item,
            'amount': self.amount
        }
        return dict

    @staticmethod
    def load_all_ids_from_db(ids, db: Database = None):
        if db is None:
            db = Database()
        return ShoppingListItem.load_all_from_db('SELECT * FROM SHOPPING_LIST WHERE ID IN (%s)' % ','.join('?' * len(ids)),
                                     ids)

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        items = []

        results = db.select_all(query, params)

        for item in results:
            if item['AMOUNT'] is None:
                amount = -1
            else:
                amount = int(item['AMOUNT'])

            items.append(ShoppingListItem(item['ITEM'], amount, item['ID']))

        return items

    @staticmethod
    def load_all(db: Database):
        return ShoppingListItem.load_all_from_db('SELECT * FROM SHOPPING_LIST', {})

    @staticmethod
    def create_from_dict(dict):
        id = dict['id']
        item = dict['item']
        amount = dict['amount']

        return ShoppingListItem(item, amount, id)