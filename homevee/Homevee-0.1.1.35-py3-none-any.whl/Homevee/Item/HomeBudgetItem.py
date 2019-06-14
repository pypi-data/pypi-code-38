import traceback

from Homevee.Exception import DatabaseSaveFailedException, InvalidParametersException
from Homevee.Helper import Logger
from Homevee.Item import Item
from Homevee.Utils.Database import Database


class HomeBudgetItem(Item):
    def __init__(self, date, info, amount, id=None):
        super(HomeBudgetItem, self).__init__()
        self.date = date
        self.info = info
        self.amount = amount
        self.id = id

    def delete(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            db.delete("DELETE FROM HOME_BUDGET_DATA WHERE ID == :id", {'id': self.id})
            return True
        except:
            return False

    def save(self, db: Database = None):
        if db is None:
            db = Database()
        try:
            if (self.id is None or self.id == ""):
                new_id = db.insert("""INSERT INTO HOME_BUDGET_DATA (DATE, INFO, AMOUNT) VALUES 
                (:date, :info, :amount)""", {'date': self.date, 'info': self.info, 'amount': self.amount})
                self.id = new_id
            # update
            else:
                db.update("""UPDATE HOME_BUDGET_DATA SET DATE = :date, INFO = :info, AMOUNT = :amount 
                WHERE ID = :id""", {'date': self.date, 'info': self.info, 'amount': self.amount, 'id': self.id})
        except:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
            raise DatabaseSaveFailedException("Could not save homebudgetitem to database")

    def build_dict(self):
        dict = {
            'id': self.id,
            'info': self.info,
            'date': self.date,
            'amount': self.amount
        }
        return dict

    @staticmethod
    def load_all_from_db(query, params, db: Database = None):
        if db is None:
            db = Database()
        items = []
        for result in db.select_all(query, params):
            item = HomeBudgetItem(result['DATE'], result['INFO'], result['AMOUNT'], result['ID'])
            items.append(item)
        return items

    @staticmethod
    def load_all_ids_from_db(ids, db: Database = None):
        if db is None:
            db = Database()
        return HomeBudgetItem.load_all_from_db('SELECT * FROM HOME_BUDGET_DATA WHERE ID IN (%s)'
                                               % ','.join('?' * len(ids)), ids)

    @staticmethod
    def load_all(db: Database):
        if db is None:
            db = Database()
        return HomeBudgetItem.load_all_from_db("""SELECT * FROM HOME_BUDGET_ITEM""", {}, db)

    @staticmethod
    def load_home_budget_items_by_date(date, db: Database = None):
        if db is None:
            db = Database()
        return HomeBudgetItem.load_all_from_db("""SELECT * FROM HOME_BUDGET_DATA WHERE DATE = :date
         GROUP BY DATE ORDER BY DATE ASC""", {'date': date}, db)

    @staticmethod
    def create_from_dict(dict):
        try:
            id = dict['id']
            date = dict['date']
            info = dict['info']
            amount = dict['amount']

            item = HomeBudgetItem(date, info, amount, id)

            return item
        except:
            raise InvalidParametersException("HomeBudgetItem.create_from_dict(): invalid dict")