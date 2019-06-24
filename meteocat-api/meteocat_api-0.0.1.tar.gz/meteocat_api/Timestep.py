class Timestep(object):
    def __init__(self, api_key=""):
        self.api_key = api_key

        self.name = None
        self.date = None
        self.weather = None
        
        self.temperature = None #32
        self.feels_like_temperature  = None #
        self.wind_speed = None #26
        self.wind_direction = None #27
        self.wind_gust = None #56
        self.visibility = None #
        self.uv = None #39
        self.precipitation = None #35
        self.humidity = None #33
        self.pressure = None #34
        self.pressure_tendency = None #
        self.dew_point = None #

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield attr, value

    def elements(self):
        """Return a list of the elements which are not None"""

        elements = []

        for el in ct:
            if isinstance(el[1], meteocat_api.Element.Element):
                elements.append(el[1])

        return elements

