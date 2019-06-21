from functools import lru_cache

from .enums import enum, blood_types, constellations, hands, home_towns

        
class Idol:
    """
    Represents an idol and her data

    Attributes
    ----------
    char_id : int
        The idol's character id

    age : int
        The idol's age

    bday : int
        The idol's birthday (not including month)

    bmonth : int
        The idol's birthmonth

    btype : str
        The idol's bloodtype

    bust : int
        The idol's bust measurement

    waist : int
        The idol's waist mearsurement

    hip : int
        The idol's hip measurement

    horoscope : str
        The idol's constellation horoscope

    conventional : str
        The idol's conventional name

    favorite : str
        The idol's favorite hobby

    hand : str
        The idol's dominant hand

    height : int
        The idol's height (in centimeters)

    home_town : str
        The idol's hometown

    kana_spaced : str
        The idol's name but in spaced kana

    kanji_spaced : str
        The idol's name but in kanji

    name : str
        The idol's name in japanese

    name_kana : str
        The idol's name in kana

    personality : int
        The idol's personality value

    type : str
        The idol's type (Cute, Cool, Passion, etc.)

    voice : str
        The idol's VA

    weight : int
        The idol's weight
    
    icon : str
        The link to the idol's icon
    """
    def __init__(self, char_data: dict):
        self.age = char_data['age']
        self.bday = char_data['birth_day']
        self.bmonth = char_data['birth_month']
        self.btype = enum(blood_types, char_data['blood_type'])
        self.bust = char_data['body_size_1']
        self.waist = char_data['body_size_2']
        self.hip = char_data['body_size_3']
        self.horoscope = enum(constellations, char_data['constellation'])
        self.conventional = char_data['conventional']
        self.favorite = char_data['favorite'] # NOTE: In Japanese due to read_tl not returning english
        self.hand = enum(hands, char_data['hand'])
        self.height = char_data['height']
        self.home_town = enum(home_towns, char_data['home_town'])
        self.kana_spaced = char_data['kana_spaced']
        self.kanji_spaced = char_data['kanji_spaced']
        self.name = char_data['name']
        self.name_kana = char_data['name_kana']
        self.personality = char_data['personality']
        self.type = char_data['type']
        self.voice = char_data['voice']
        self.weight = char_data['weight']
        self.icon = char_data['icon_image_ref']