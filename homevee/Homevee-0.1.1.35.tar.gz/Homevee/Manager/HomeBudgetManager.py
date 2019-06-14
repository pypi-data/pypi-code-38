#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from Homevee.Item import Item
from Homevee.Item.HomeBudgetItem import HomeBudgetItem
from Homevee.Utils.Database import Database


class HomeBudgetManager:
    def __init__(self):
        return

    def get_home_budget_data(self, user, startdate, db: Database = None):
        if db is None:
            db = Database()
        data = {}

        #Find expenditures grouped by date
        results = db.select_all("SELECT SUM(AMOUNT) as AMOUNT, strftime(\"%d.%m.%Y\", DATE) as DATE FROM HOME_BUDGET_DATA WHERE AMOUNT <= 0 AND DATE >= :date GROUP BY DATE ORDER BY DATE ASC",
                    {'date': startdate})
        costs = []

        last_date = None

        for item in results:
            this_date = datetime.datetime.strptime(item['DATE'], "%d.%m.%Y")
            if(last_date is not None):
                difference = (this_date - last_date).days

                for i in range(1, difference):
                    date = last_date + datetime.timedelta(days=i)
                    costs.append({'date': date.strftime("%d.%m.%Y"), 'amount': round(0, 2)})

            last_date = this_date

            costs.append({'date': item['DATE'], 'amount': round(item['AMOUNT']*-1, 2)})
        data['costs'] = costs

        #Find amount money left
        item = db.select_one("SELECT SUM(AMOUNT) as AMOUNT FROM HOME_BUDGET_DATA", {})
        overall_amount = round(item['AMOUNT'], 2)
        data['overall_amount'] = overall_amount

        #Compute date where money reaches 0
        item = db.select_one("SELECT AVG(AMOUNT) as AMOUNT FROM (SELECT SUM(AMOUNT) as AMOUNT FROM HOME_BUDGET_DATA WHERE AMOUNT < 0 GROUP BY DATE);", {})
        average_spending_per_day = item['AMOUNT']*-1

        #compute timeperiod
        min_max_date = db.select_one("SELECT MIN(DATE) as mindate, MAX(DATE) as maxdate, COUNT(*) as numdays FROM (SELECT DISTINCT DATE FROM HOME_BUDGET_DATA);", {})
        real_numdays = (datetime.datetime.today()-datetime.datetime.strptime(min_max_date['mindate'], "%Y-%m-%d")).days
        average_spending_per_day = average_spending_per_day * min_max_date['numdays'] / real_numdays
        days_left = overall_amount/average_spending_per_day
        date = datetime.datetime.today() + datetime.timedelta(days=days_left)
        date = datetime.datetime.strftime(date, "%d.%m.%Y")
        data['sufficient_until'] = date

        return data

    def get_home_budget_data_graph(self, user, startdate, enddate, db: Database = None):
        if db is None:
            db = Database()
        item = db.select_one("SELECT SUM(AMOUNT) as AMOUNT FROM HOME_BUDGET_DATA WHERE DATE < :startdate;",
            {'startdate': startdate})

        startvalue = item['AMOUNT']

        if startvalue is None:
            startvalue = 0

        #Get values
        results = db.select_all("SELECT SUM(AMOUNT) as AMOUNT, strftime(\"%d.%m.%Y\", DATE) as FORMATTED_DATE FROM HOME_BUDGET_DATA WHERE DATE >= :startdate AND DATE <= :enddate GROUP BY DATE ORDER BY DATE ASC",
            {'startdate': startdate, 'enddate': enddate})

        values = []

        last_date = None

        for item in results:
            this_date = datetime.datetime.strptime(item['FORMATTED_DATE'], "%d.%m.%Y")
            if (last_date is not None):
                difference = (this_date - last_date).days

                for i in range(1, difference):
                    date = last_date + datetime.timedelta(days=i)
                    values.append({'date': date.strftime("%d.%m.%Y"), 'amount': round(0, 2)})

            last_date = this_date

            values.append({'date': item['FORMATTED_DATE'], 'amount': round(item['AMOUNT'], 2)})

        return {'startvalue': startvalue, 'values': values}

    def get_home_budget_data_day_items(self, user, date, db: Database = None):
        if db is None:
            db = Database()
        data = []

        results = db.select_all("SELECT *, strftime(\"%d.%m.%Y\", DATE) as FORMATTED_DATE FROM HOME_BUDGET_DATA WHERE DATE = :date ORDER BY DATE ASC",
                    {'date': date})

        for item in results:
            data.append({'id': item['ID'], 'date': item['FORMATTED_DATE'], 'amount': round(item['AMOUNT'], 2), 'info': item['INFO']})

        return data

    def add_edit_home_budget_data(self, user, id, date, info, amount, db: Database = None):
        if db is None:
            db = Database()
        home_budget_item = None
        if id is not None:
            home_budget_item = Item.load_from_db(HomeBudgetItem, id, db)
        if home_budget_item is None:
            home_budget_item = HomeBudgetItem(date, info, amount, id)
        else:
            home_budget_item.date = date
            home_budget_item.info = info
            home_budget_item.amount = amount

        return home_budget_item.save(db)

    def delete_home_budget_data(self, user, id, db: Database = None):
        if db is None:
            db = Database()
        item = Item.load_from_db(HomeBudgetItem, id)
        return item.delete(db)