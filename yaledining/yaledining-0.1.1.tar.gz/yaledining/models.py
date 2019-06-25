import datetime


class _base_model():
    def __init__(self, raw: dict, api):
        self.raw = raw
        self.api = api

    def parse_datetime(self, raw: str) -> datetime.datetime:
        return datetime.datetime.strptime(raw, '%B, %d %Y %H:%M:%S')

    def parse_time(self, raw: str):
        return datetime.datetime.strptime(raw, '%H:%M %p').time()


def _make_model(class_name):
    return type(class_name, (_base_model,), {})


class Manager:
    """
    A manager for a dining location.

    Built at request time to make processing/iteration easier.
    """
    def __init__(self, name, email):
        self.name = name
        self.email = email


class Location(_base_model):
    def __init__(self, raw: dict, api):
        super().__init__(raw, api)
        self.id = int(raw['ID_LOCATION'])
        self.location_code = int(raw['LOCATIONCODE'])
        self.name = raw['DININGLOCATIONNAME']
        # TODO: enum?
        self.type = raw['TYPE']
        self.capacity = raw['CAPACITY']
        self.percent_capacity = 10 * self.capacity if self.capacity is not None else None
        self.geolocation = raw['GEOLOCATION']
        self.latitude, self.longitude = tuple([float(coordinate) for coordinate in self.geolocation.split(',')])
        self.closed = bool(raw['ISCLOSED'])
        self.open = not self.closed
        self.address = raw['ADDRESS']
        self.phone = raw['PHONE']
        managers = []
        num_managers = 0
        while num_managers < 4:
            num_managers += 1
            name = raw[f'MANAGER{num_managers}NAME']
            email = raw[f'MANAGER{num_managers}EMAIL']
            if name is not None and email is not None:
                managers.append(Manager(name, email))
        self.managers = tuple(managers)

    @property
    def meals(self):
        return self.api.meals(self.id)


class Meal(_base_model):
    def __init__(self, raw: dict, api):
        super().__init__(raw, api)
        self.items = []

        self.location_id = int(raw['ID_LOCATION'])
        self.location_code = int(raw['LOCATIONCODE'])
        self.location_name = raw['LOCATION']

        self.name = raw['MEALNAME']
        self.code = int(raw['MEALCODE'])
        # Dates are formatted like:
        # June, 18 2019 00:00:00
        # TODO: should we provide the string format as well?
        self.raw_date = raw['MENUDATE']
        self.date = self.parse_datetime(self.raw_date)
        self.id = int(raw['ID'])
        # TODO: What is this?
        #self.is_par = bool(raw['ISPAR'])
        # Times formatted like:
        # 08:00 AM
        self.raw_open_time = raw['MEALOPENS']
        self.open_time = self.parse_time(self.raw_open_time)
        self.raw_close_time = raw['MEALCLOSES']
        self.close_time = self.parse_time(self.raw_close_time)
        self.is_default_meal = bool(raw['ISDEFAULTMEAL'])
        self.is_menu = bool(raw['ISMENU'])


class Item(_base_model):
    def __init__(self, raw: dict, api):
        super().__init__(raw, api)
        self.name = raw['MENUITEM']
        self.id = int(float(raw['MENUITEMID']))
        self.course = raw['COURSE']
        self.course_code = int(float(raw['COURSECODE']))

    @property
    def nutrition(self):
        """
        Get nutrition information for the current item.
        """
        return self.api.nutrition(self.id)

    @property
    def traits(self):
        """
        Get traits of the current item.
        """
        return self.api.traits(self.id)

    @property
    def ingredients(self):
        """
        Get ingredients of the current item.
        """
        return self.api.ingredients(self.id)


class Nutrition(_base_model):
    def __init__(self, raw: dict, api):
        super().__init__(raw, api)
        # RECP_NAME for this one is the same thing as a menu item ID so just correct the naming
        self.item = raw['RECP_NAME']
        self.item_id = int(raw['MENUITEMID'])

        # TODO: This is returned in the format '1 srv spn (12 bns)'. I feel like we could make this more useful.
        # Also, yes, that is a space.
        self.serving_size = raw['SERVING SIZE']
        self.calories = raw['CALORIES']
        self.protein = raw['PROTEIN']
        self.fat = raw['FAT']
        self.saturated_fat = raw['SATURATED FAT']
        self.cholesterol = raw['CHOLESTEROL']
        self.carbohydrates = raw['CARBOHYDRATES']
        self.sugar = raw['SUGAR']
        self.dietary_fiber = raw['DIETARY FIBER']
        self.vitamin_c = raw['VITAMIN C']
        self.vitamin_a = raw['VITAMIN A']
        self.iron = raw['IRON']


class Traits(_base_model):
    def __init__(self, raw: dict, api):
        super().__init__(raw, api)
        self.item = raw['MENUITEM']
        self.item_id = int(raw['MENUITEMID'])

        self.alcohol = bool(raw['ALCOHOL'])
        self.nuts = bool(raw['NUTS'])
        self.shellfish = bool(raw['SHELLFISH'])
        self.peanut = bool(raw['PEANUT'])
        self.dairy = bool(raw['DAIRY'])
        self.eggs = bool(raw['EGGS'])
        self.vegan = bool(raw['VEGAN'])
        self.pork = bool(raw['PORK'])
        # TODO: reevaluate naming?
        self.seafood = bool(raw['FISHSEAFOOD'])
        self.soy = bool(raw['SOY'])
        self.wheat = bool(raw['WHEAT'])
        self.gluten = bool(raw['GLUTEN'])
        self.vegetarian = bool(raw['VEGETARIAN'])
        self.gluten_free = bool(raw['GLUTENFREE'])
        self.facility_warning = raw['FACILITYWARNING']


class Ingredient(_base_model):
    def __init__(self, raw: dict, api):
        super().__init__(raw, api)
        self.item_id = int(raw['RECIPE NUMBER'])

        self.name = raw['INGREDIENT']
