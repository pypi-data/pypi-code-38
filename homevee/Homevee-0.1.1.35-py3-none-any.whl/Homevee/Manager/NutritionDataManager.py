#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json

import requests
from dateutil.relativedelta import relativedelta

from Homevee.Helper import Logger
from Homevee.Manager.RemoteControlManager import RemoteControlManager
from Homevee.Utils.Database import Database


class NutritionDataManager:
    def __init__(self):
        return

    def get_nutrition_data(self, user, keyword, db: Database = None):
        if db is None:
            db = Database()
        data = {'action': 'findsingleitem', 'term': keyword}

        Logger.log("Nutrition item search: "+keyword)

        r = requests.post("https://food.Homevee.de/api.php", data=data)
        # Logger.log(r.status_code, r.reason)

        if (r.status_code != 200):
            return None

        response = r.text

        #print response

        data = json.loads(response)

        if(data is None):
            return None

        if('food' not in data):
            return None

        nutrition_data = data['food']

        if(nutrition_data is None):
            return None

        if(len(nutrition_data) is 0):
            return False

        return nutrition_data[0]

    def submit_food(self, user, name, calories, portionsize, portionunit, protein, fat, saturated, unsaturated, carbs, sugar, ean, db: Database = None):
        if db is None:
            db = Database()
        remote_data = RemoteControlManager().load_remote_data(user)
        remote_id = remote_data['remote_id']

        if(remote_id is None or remote_id == ""):
            return {'result': 'noremoteid'}

        data = {'action': 'submitfood', 'name': name, 'calories': calories, 'portionsize': portionsize, 'portionunit': portionunit,
                'protein': protein, 'fat': fat, 'saturated': saturated, 'unsaturated': unsaturated, 'carbs': carbs,
                'sugar': sugar, 'ean': ean, 'user_remote_id': remote_id}

        r = requests.post("https://food.Homevee.de/api.php", data=data)
        #Logger.log(r.status_code, r.reason)

        if(r.status_code != 200):
            return {"result": "error"}

        result = json.loads(r.text)

        if("result" in result):
            if(result['result'] == "ok"):
                return True
        return False

    def get_user_day_nutrition_data(self, user, db: Database = None):
        if db is None:
            db = Database()
        return

    def get_user_nutrition_overview(self, user, db: Database = None):
        if db is None:
            db = Database()
        user_profile = self.get_user_fitness_profile(user)

        Logger.log(user_profile)

        output = {}

        if (user_profile is False):
            has_profile = False
        else:
            has_profile = True

            results = db.select_all("SELECT * FROM NUTRITION_DATA WHERE USER = :user AND DATE = :date",
                        {'user': user.username, 'date': datetime.datetime.today().strftime("%d.%m.%Y")})

            eaten_calories_today = 0
            eaten_fat_today = 0
            eaten_carbs_today = 0
            eaten_protein_today = 0

            for item in results:
                amount = (float(item['EATEN_PORTION_SIZE'])/float(item['PORTIONSIZE']))

                eaten_calories_today += item['CALORIES']*amount
                eaten_fat_today += item['FAT']*amount
                eaten_carbs_today += item['CARBS']*amount
                eaten_protein_today += item['PROTEIN']*amount

            #print datetime.datetime.today().strftime("%Y-%m-%d")

            nutrition_distribution = {'fat': eaten_fat_today, 'carbs': eaten_carbs_today,
                                      'protein': eaten_protein_today}
            nutrition_day_data = {'calories_goal': int(user_profile['caloriesgoal']),
                                  'calories_left': int(user_profile['caloriesgoal']-eaten_calories_today),
                                  'nutrition_distribution': nutrition_distribution}

            output['nutrition_day_data'] = nutrition_day_data

        weight_progress = {}

        output['has_profile'] = has_profile
        output['weight_progress'] = weight_progress

        return output

    def save_user_settings(self, user, height, weight, birthdate, mode, activity, db: Database = None):
        if db is None:
            db = Database()
        calories_goal = self.get_calorie_need(birthdate, weight, height, activity, mode)

        protein_goal, carbs_goal, fat_goal = self.get_macro_distribution(calories_goal)

        water_goal = 2.0

        self.add_user_weight(user, weight)
        result = db.select_one("SELECT COUNT(*) FROM USER_FITNESS_DATA WHERE USERNAME = :user", {'user': user.username})

        result = result['COUNT(*)']

        param_array = {'cals': calories_goal, 'user': user.username, 'fat': fat_goal, 'saturated': 0, 'carbs': carbs_goal,
                       'sugar': 0, 'protein': protein_goal, 'water': water_goal, 'birthdate': birthdate, 'height': height,
                       'weight': weight, 'activity':activity, 'diet': mode}

        if(result == 0):
            db.insert("INSERT INTO USER_FITNESS_DATA (user, CALORIE_GOAL, FAT_GOAL, SATURATED_GOAL, CARBS_GOAL, SUGAR_GOAL, PROTEIN_GOAL, WATER_GOAL, BIRTHDATE, HEIGHT, ACTIVITY_MODE, DIET_MODE) VALUES (:user, :cals, :fat, :saturated, :carbs, :sugar, :protein, :water, :birthdate, :height, :activity, :diet)", param_array)
        else:
            db.update("UPDATE USER_FITNESS_DATA SET CALORIE_GOAL = :cals, FAT_GOAL = :fat, SATURATED_GOAL = :saturated, CARBS_GOAL = :carbs, SUGAR_GOAL = :sugar, PROTEIN_GOAL = :protein, WATER_GOAL = :water, BIRTHDATE = :birthdate, HEIGHT = :height, ACTIVITY_MODE = :activity, DIET_MODE = :diet WHERE USERNAME = :user", param_array)

        return {'result': 'ok', 'calories_goal': calories_goal, 'protein_goal': protein_goal, 'carbs_goal': carbs_goal, 'fat_goal': fat_goal}

    def get_macro_distribution(self, calories):

        protein_factor = 0.25
        carbs_factor = 0.5
        fat_factor = 0.25

        protein_goal = (calories/4)*protein_factor
        carbs_goal = (calories/4)*carbs_factor
        fat_goal = (calories/8)*fat_factor

        return int(protein_goal), int(carbs_goal), int(fat_goal)

    def load_user_settings(self, user, db: Database = None):
        if db is None:
            db = Database()
        data = {}

        #{'sitting': 1.2, 'lightactivity': 1.35, 'moderateactivity': 1.55, 'highactivity': 1.75, 'extremeactivity': 1.95}

        data['activities'] = [
            {'title': 'Sitzend', 'description': 'wenig/kein Training + Bürotätigkeit', 'key': 'sitting'},
            {'title': 'leichte Aktivität', 'description': 'geringe tägliche Aktivität + leichtes Training 1-3 Mal/ Woche', 'key': 'lightactivity'},
            {'title': 'moderate Aktivität', 'description': 'moderate tägliche Aktivität + moderates Training 3-5 Mal/ Woche', 'key': 'moderateactivity'},
            {'title': 'hohe Aktivität', 'description': 'körperlich anspruchsvoller Lifestyle + schweres Training/Sport 6-7 Mal/ Woche', 'key': 'highactivity'},
            {'title': 'extrem hohe Aktivität', 'description': 'hartes tägliches Training/Sport und/oder körperlich beanspruchender Job', 'key': 'extremeactivity'}
        ]

        data['modes'] = [
            {'title': 'stark Abnehmen', 'key': 'harddiet'},
            {'title': 'Abnehmen', 'key': 'diet'},
            {'title': 'Gewicht halten', 'key': 'hold'},
            {'title': 'Muskeln aufbauen', 'key': 'gainmuscles'}
        ]

        result = db.select_one("SELECT * FROM USER_WEIGHT_DATA WHERE USERNAME = :user ORDER BY DATE DESC", {'user': user.username})
        weight_data = result['WEIGHT']

        result = db.select_one("SELECT * FROM USER_FITNESS_DATA WHERE USERNAME = :user", {'user': user.username})

        activity_title = None
        for item in data['activities']:
            if(item['key'] == result['ACTIVITY_MODE']):
                activity_title = item['title']
                break

        mode_title = None
        for item in data['modes']:
            if(item['key'] == result['DIET_MODE']):
                mode_title = item['title']
                break

        settings = {'weight': weight_data, 'height': result['HEIGHT'], 'birthdate': result['BIRTHDATE'],'activity': result['ACTIVITY_MODE'],
                    'activity_title': activity_title, 'mode': result['DIET_MODE'], 'mode_title': mode_title}

        data['settings'] = settings

        return data

    def add_user_weight(self, user, weight, db: Database = None):
        if db is None:
            db = Database()
        date = datetime.datetime.today().__format__("%Y-%m-%d")

        db.insert("INSERT INTO USER_WEIGHT_DATA (USERNAME, DATE, WEIGHT) VALUES (:user, :date, :weight)",
                   {'user': user.username, 'date': date, 'weight': weight})

    def delete_food_item(self, user, id, db: Database = None):
        if db is None:
            db = Database()
        db.delete("DELETE FROM NUTRITION_DATA WHERE ID = :id AND USER = :user",
                    {'id': id, 'user': user.username})

    def get_calorie_need(self, birthdate, weight, height, movement_mode, diet_mode):
        # (9.99 x Körpergewicht (in kg)) + (6.25 x Körpergröße (in cm)) – (4.92 x Alter (in Jahren)) – 161

        birthdate = datetime.datetime.strptime(birthdate, "%Y-%m-%d")
        today = datetime.datetime.today()
        age = relativedelta(today, birthdate).years

        base_calories = (9.99 * int(weight)) + (6.25 * int(height)) - (4.92 * age) - 161

        movement_factor = 1.2
        movement_map = {'sitting': 1.2, 'lightactivity': 1.35, 'moderateactivity': 1.55, 'highactivity': 1.75, 'extremeactivity': 1.95}
        if(movement_mode in movement_map):
            movement_factor = movement_map[movement_mode]
        calories_with_movement = base_calories * movement_factor

        diet_factor = 1
        diet_map = {'harddiet': 0.8, 'diet': 0.9, 'hold': 1.0, 'musclegain': 1.1}
        if(diet_mode in diet_map):
            diet_factor = diet_map[diet_mode]
        Logger.log(diet_mode)
        diet_calories = calories_with_movement * diet_factor

        calories_needed = diet_calories

        return int(calories_needed)

    def get_user_fitness_profile(self, user, db: Database = None):
        if db is None:
            db = Database()

        result = db.select_one("SELECT * FROM USER_FITNESS_DATA WHERE USERNAME = :user", {'user': user.username})

        if(result is None):
            return False

        data = {'caloriesgoal': result['CALORIE_GOAL'], 'fatgoal': result['FAT_GOAL'], 'saturatedgoal': result['SATURATED_GOAL'],
                'carbsgoal': result['CARBS_GOAL'], 'sugargoal': result['SUGAR_GOAL'], 'proteingoal': result['PROTEIN_GOAL'],
                'watergoal': result['WATER_GOAL']}

        return data

    def get_user_weight_progress(self, user, start, end, db: Database = None):
        if db is None:
            db = Database()
        start = datetime.datetime.strptime(start, "%d.%m.%Y").strftime("%Y-%m-%d")
        end = datetime.datetime.strptime(end, "%d.%m.%Y").strftime("%Y-%m-%d")

        weight_items = []

        results = db.select_all("SELECT WEIGHT, strftime(\"%d.%m.%Y\", DATE) as DATETIME FROM USER_WEIGHT_DATA WHERE USERNAME = :user AND DATE >= :start AND DATE <= :ende ORDER BY DATE ASC",
                    {'user': user.username, 'start': start, 'end': end})

        for item in results:
            weight_items.append({'date': item['DATETIME'], 'weight': item['WEIGHT']})

        return weight_items

    def get_user_day_nutrition_items(self, user, date, db: Database = None):
        if db is None:
            db = Database()
        daytime_items = {'morning': [], "noon": [], "evening": [], "snacks": []}

        results = db.select_all("SELECT * FROM NUTRITION_DATA WHERE USER = :user AND DATE = :date",
                    {'user': user.username, 'date': date})

        for item in results:
            food_item = {'id': item['ID'], 'daytime': item['DAYTIME'], 'name': item['FOOD_NAME'], 'eatenportionsize': item['EATEN_PORTION_SIZE'],
                         'portionsize': item['PORTIONSIZE'], 'portionunit': item['PORTIONUNIT'], 'calories': item['CALORIES'],
                         'fat': item['FAT'], 'saturated': item['SATURATED'], 'unsaturated': item['UNSATURATED'],
                         'carbs': item['CARBS'], 'sugar': item['SUGAR'], 'protein': item['PROTEIN'], 'date': item['DATE']}

            if(item['DAYTIME'] in daytime_items):
                daytime_items[item['DAYTIME']].append(food_item)
            else:
                daytime_items['snacks'].append(food_item)

        calories_goal = self.get_user_fitness_profile(user)['caloriesgoal']

        return {'items': daytime_items, 'caloriesgoal': calories_goal}

    def move_item(self, user, id, date, daytime, deleteold, db: Database = None):
        if db is None:
            db = Database()
        item = db.select_all("SELECT * FROM NUTRITION_DATA WHERE ID = :id", {'id': id})

        if(item is None):
            return {'result': 'itemnotexisting'}

        name = item['FOOD_NAME']
        eatenportionsize = item['EATEN_PORTION_SIZE']
        portionsize = item['PORTIONSIZE']
        portionunit = item['PORTIONUNIT']
        calories = item['CALORIES']
        fat = item['FAT']
        saturated = item['SATURATED']
        unsaturated = item['UNSATURATED']
        carbs = item['CARBS']
        sugar = item['SUGAR']
        protein = item['PROTEIN']

        self.add_edit_user_day_nutrition_item(user, None, date, daytime, name, eatenportionsize, portionsize, portionunit,
                                         calories, fat, saturated, unsaturated, carbs, sugar, protein)

        if deleteold == "true" or deleteold == True or deleteold == 1 or deleteold == "1":
            db.delete("DELETE FROM NUTRITION_DATA WHERE ID = :id", {'id': id})

    def add_edit_user_day_nutrition_item(self, user, id, date, daytime, name, eatenportionsize, portionsize, portionunit, calories, fat, saturated, unsaturated, carbs, sugar, protein, db: Database = None):
        if db is None:
            db = Database()
        add_new = (id == None or id == "" or id == "-1")

        param_array = {'user': user.username, 'date': date, 'daytime': daytime, 'name': name, 'eatenportionsize': eatenportionsize,
                       'portionsize': portionsize, 'portionunit': portionunit, 'calories': calories, 'fat': fat,
                       'saturated': saturated, 'unsaturated': unsaturated, 'carbs': carbs, 'sugar': sugar, 'protein': protein}

        if add_new:
            db.insert("INSERT INTO NUTRITION_DATA (USER, DATE, DAYTIME, FOOD_NAME, EATEN_PORTION_SIZE, PORTIONSIZE, PORTIONUNIT, CALORIES, FAT, SATURATED, UNSATURATED, CARBS, SUGAR, PROTEIN) VALUES (:user, :date, :daytime, :name, :eatenportionsize, :portionsize, :portionunit, :calories, :fat, :saturated, :unsaturated, :carbs, :sugar, :protein)",
                        param_array)
        else:
            param_array['id'] = id

            db.update("UPDATE NUTRITION_DATA SET USER = :user, DATE = :date, DAYTIME = :daytime, FOOD_NAME = :name, EATEN_PORTION_SIZE = :eatenportionsize, PORTIONSIZE = :portionsize, PORTIONUNIT = :portionunit, CALORIES = :calories, FAT = :fat, SATURATED = :saturated, UNSATURATED = :unsaturated, CARBS = :carbs, SUGAR = :sugar, PROTEIN = :protein WHERE ID = :id",
                        param_array)