# coding: utf-8

import requests
import json
from functools import lru_cache

from .idol import Idol
from .card import Card
from .infos import Event, Gacha, Info
from .enums import enum, blood_types, constellations, hands, home_towns, rarities
from .errors import CategoryNotFound, NotFound, NotValid

class KiraraException(Exception):
    def __init__(self, http_status, code, msg):
        self.http_status = http_status
        self.code = code
        self.msg = msg

    def __str__(self):
        return f"http status: {self.http_status} {self.code} - {self.msg}"

class Kirara(object):
    """A class that connects to the kirara api

    """
    max_retries = 10

    def __init__(self, requests_session=True, request_timeout=10):
        self.prefix = 'https://starlight.kirara.ca/api/v1/'
        self.request_timeout = request_timeout

        if isinstance(requests_session, requests.Session):
            self._session = requests_session
        else:
            if requests_session:
                self._session = requests.Session()
            else:
                from requests import api
                self._session = api

    def internal_call(self, method, url, payload, params):
        """Makes HTTP requests
        
        Parameters
        ----------
        method : str
            method of making HTTP requests ('GET', 'POST', etc.)

        url : str
            The url to make HTTP requests to

        payload : str
            Any additional parameters to pass

        params : dict
            Parameters to pass to a dict

        Returns
        ----------
        dict
            The result of the request in dict format
        """
        args = dict(params=params)
        args["timeout"] = self.request_timeout
        if not url.startswith('http'):
            url = self.prefix + url

        if payload:
            args["data"] = json.dumps(payload)

        r = self._session.request(method, url, **args)
        try:
            r.raise_for_status()
        finally:
            r.connection.close()
        if r.text and len(r.text) > 0 and r.text != 'null':
            results = r.json()
            return results
        else:
            return None

    @lru_cache(maxsize=None)
    def get(self, url, args=None, payload=None, **kwargs):
        """Make GET requests
        
        Parameters
        ----------
        url : str
            The url to the api (excluding the prefix url)

        args : dict
            Pass additional args

        payload : str
            Pass any additional parameters to request

        Returns
        ----------
        dict
            The result of the GET request
        """
        if args:
            kwargs.update(args)
        reconnect = self.max_retries
        while reconnect > 0:
            try:
                return self.internal_call('GET', url, payload, kwargs)
            except Exception as e:
                raise
                print('exception', str(e))

    def get_idol(self, idol_id: int):
        """Retrieve an idol's info

        Parameters
        ----------
        idol_id : int
            An Idol's ID to use from

        Returns
        ----------
        Idol
            An Idol object, which contains the idol's info
        """
        data = self.get(f"char_t/{idol_id}")
        if data['result'][0] is not None:

            return Idol(data['result'][0])
        else:
            raise NotFound("Idol ID can not be found in the Database. Is the ID correct?")

    def get_card(self, card_id: int):
        """Retrieve a card's data
        
        Parameters
        ----------
        card_id : int
            A Card's ID to use from
            
        Returns
        ----------
        Card
            A Card object, which contains the card's info
        """
        data = self.get(f"card_t/{card_id}")
        if data['result'][0] is not None:

            return Card(data['result'][0])
        else:
            raise NotFound("Card ID can not be found in the Database. Is the ID correct?")
    def get_version(self):
        """Retrieve the client's version
        
        Returns
        ----------
        Info
            An Info object, which contains version info
        """
        data = self.get('info')

        return Info(data)

    def get_image(self, card: 'Card', category='card'):
        """Retrieve a Card's image data
        
        Parameters
        ----------
        card : Card
            A card object to use
        catergory : str
            What type of image to use (Default value is 'card')
            
        Returns
        ----------
        bytes
            The image bytes
        """
        if type(card) is Card:
            categories = {
                'card': card.image,
                'icon': card.icon,
                'spread': card.spread,
                'sprite': card.sprite
            }
            if category in categories:
                image = categories.get(category)

                response = self._session.get(image)

                return response
            else:
                raise CategoryNotFound("Defined Category not valid, use 'card', 'icon', 'spread', or 'sprite'")
        else:
            raise NotValid("The passed object for card is not a Card object")
        

    def get_now(self, category):
        """Retrieve a list of occasions happenning in the game
        
        Parameters
        ----------
        category : str
            What type of event to iterate from
            
        Returns
        --------
        list
            A list of gachas or events
        """
        categories = {
        'events': self.get(f"happening/now")['events'],
        'gachas': self.get(f"happening/now")['gachas']
        }
        happening_list = []

        if category in categories:
            stuff = categories.get(category)

            for index, event in enumerate(stuff):
                if category == 'event':
                    happening_list.append(Event(event))

                else:
                    for gacha, event in enumerate(stuff): # I don't know why you have to iterate again, maybe Im dumb

                        happening_list.append(Gacha(event))

            return happening_list
                    
    def get_id(self, category, name, card_rarity=None, position=None):
        """Find a specific id based on parameters given
        
        Parameters
        ----------
        category : str
            Which category to search from ('card_t, or 'char_t')
        name : str
            An idol's name, full or just one part of a name
        card_rarity : str
            A rarity of card to look from (ranges from n to ssr, or n+ to ssr+)
        position : int
            Which card to get, based on release order
            
        Returns
        ----------
        list
            A list of cards matching the parameters
        int
            An ID of a specfic idol, or card"""

        cat_list = self.get(f'list/{category}')['result']
        rarity = enum(rarities, card_rarity)
        card_list= []

        for index, code in enumerate(cat_list):
            if category == 'char_t':
                if name in cat_list[index]['conventional'].lower():

                    return int(cat_list[index]['chara_id'])

            elif category == 'card_t':
                if name in cat_list[index]['conventional'].lower():
                    card_list.append(int(cat_list[index]['id']))
                    if card_rarity:
                        if int(rarity) == cat_list[index]['rarity_dep']['rarity']:
                            card_list.append(int(cat_list[index]['id']))
            else:
                raise CategoryNotFound("Category not found: Use 'card_t',or 'char_t'")
        if position:
            return card_list[position-1]
        else:
            return card_list
        
    # DEFUNCT FOR NOW
    # @lru_cache(maxsize=None)
    # def post(self, url ,load=None):
    #    payload = f"[\{load"\]".encode('utf-8')
    #    result = requests.request("POST", self.prefix + url, data=payload)
    #    return result.text
