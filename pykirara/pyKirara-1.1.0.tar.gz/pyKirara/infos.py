class Info:
    """
    Represents the API's info

    Attributes
    ----------
    truth : str
        The game's (Deresute) truth version

    api_major : int
        The API's version major

    api_revision : int
        The API's revision number        

    """

    def __init__(self, info_data: dict):
        self.truth = info_data['truth_version']
        self._api_major = info_data['api_major']
        self._api_revision = info_data['api_revision']
        
class Gacha:
    """
    Represents gacha information

    Attributes
    ----------
    gacha : int
        A value that represents the gacha's position

    id : int
        The gacha's id

    name : str
        The gacha's name in japanese

    start_date : UNIX-datetime
        The gacha's start date

    end_date : UNIX-datetime    
        The gacha's end date

    type : int
        The gacha type

    subtype : int
        The gacha sub-type

    rates : dict
        The weighted rates for the gacha

    """
    def __init__(self, gacha_data: dict):
        self.id = gacha_data['id']
        self.name = gacha_data['name']
        self.start_date = gacha_data['start_date']
        self.end_date = gacha_data['end_date']
        self.type = gacha_data['type']
        self.subtype = gacha_data['subtype']
        self.rates = gacha_data['rates']

class Event:
    """
    Represents event info

    Attributes
    -------
    event : int
        Event index number in 'happening/now' endpoint

    id : int
        The event's id

    name : str
        Event name

    start_date : datetime obj
        Event start date

    end_date : datetime obj
        Event end date

    result_end_date : datetime obj
        The time left for the Event until it ends
    """

    def __init__(self, gacha_data):
        self.id = gacha_data['id']
        self.name = gacha_data['name']
        self.start_date = gacha_data['start_date']
        self.end_date = gacha_data['end_date']
        self.result_end_date = gacha_data['result_end_date']