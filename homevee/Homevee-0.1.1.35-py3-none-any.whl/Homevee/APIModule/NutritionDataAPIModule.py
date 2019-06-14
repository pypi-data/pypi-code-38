from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.NutritionDataManager import NutritionDataManager

ACTION_KEY_SUBMIT_FOOD = "submitfood"
ACTION_KEY_GET_USER_NUTRITION_OVERVIEW = "getusernutritionoverview"
ACTION_KEY_GET_USER_DAY_NUTRITION_ITEMS = "getuserdaynutritionitems"
ACTION_KEY_ADD_EDIT_USER_DAY_NUTRITION_ITEMS = "addedituserdaynutritionitem"
ACTION_KEY_LOAD_NUTRITION_MANAGER_SETTINGS = "loadnutritionmanagersettings"
ACTION_KEY_DELETE_FOOD_ITEM = "deletefooditem"
ACTION_KEY_SAVE_NUTRITION_MANAGER_SETTINGS = "savenutritionmanagersettings"
ACTION_KEY_MOVE_NUTRTITION_ITEM = "movenutritionitem"

class NutritionDataAPIModule(APIModule):
    def __init__(self):
        super(NutritionDataAPIModule, self).__init__()
        self.nutrition_data_manager = NutritionDataManager()
        return

    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_SUBMIT_FOOD: self.submit_food,
            ACTION_KEY_GET_USER_NUTRITION_OVERVIEW: self.get_user_nutrition_overview,
            ACTION_KEY_GET_USER_DAY_NUTRITION_ITEMS: self.get_user_day_nutrition_items,
            ACTION_KEY_ADD_EDIT_USER_DAY_NUTRITION_ITEMS: self.add_edit_user_day_nutrition_item,
            ACTION_KEY_LOAD_NUTRITION_MANAGER_SETTINGS: self.load_user_settings,
            ACTION_KEY_DELETE_FOOD_ITEM: self.delete_food_item,
            ACTION_KEY_SAVE_NUTRITION_MANAGER_SETTINGS: self.save_user_settings,
            ACTION_KEY_MOVE_NUTRTITION_ITEM: self.move_item
        }

        return mappings

    def submit_food(self, user, request, db):
        success = self.nutrition_data_manager.submit_food(user, request['name'], request['calories'],
                                                          request['portionsize'],
                                                          request['portionunit'], request['protein'], request['fat'],
                                                          request['saturated'], request['unsaturated'],
                                                          request['carbs'],
                                                          request['sugar'], request['ean'], db)
        if success:
            return Status(type=STATUS_OK)
        else:
            return Status(type=STATUS_ERROR)

    def get_user_nutrition_overview(self, user, request, db):
        data = self.nutrition_data_manager.get_user_nutrition_overview(user, db)
        return Status(type=STATUS_OK, data=data)

    def get_user_day_nutrition_items(self, user, request, db):
        data = self.nutrition_data_manager.get_user_day_nutrition_items(user, request['date'], db)
        return Status(type=STATUS_OK, data=data)

    def add_edit_user_day_nutrition_item(self, user, request, db):
        self.nutrition_data_manager.add_edit_user_day_nutrition_item(user, request['id'], request['date'],
                                                                               request['daytime'], request['name'],
                                                                               request['eatenportionsize'],
                                                                               request['portionsize'],
                                                                               request['portionunit'],
                                                                               request['calories'], request['fat'],
                                                                               request['saturated'],
                                                                               request['unsaturated'],
                                                                               request['carbs'], request['sugar'],
                                                                               request['protein'], db)
        return Status(type=STATUS_OK)

    def load_user_settings(self, user, request, db):
        data = self.nutrition_data_manager.load_user_settings(user, db)
        return Status(type=STATUS_OK, data=data)

    def delete_food_item(self, user, request, db):
        self.nutrition_data_manager.delete_food_item(user, request['id'], db)
        return Status(type=STATUS_OK)

    def save_user_settings(self, user, request, db):
        data = self.nutrition_data_manager.save_user_settings(user, request['height'], request['weight'],
                                                                 request['birthdate'],
                                                                 request['mode'], request['activity'], db)
        return Status(type=STATUS_OK, data=data)

    def move_item(self, user, request, db):
        self.nutrition_data_manager.move_item(user, request['id'], request['date'], request['daytime'],
                                                        request['deleteold'], db)
        return Status(type=STATUS_OK)