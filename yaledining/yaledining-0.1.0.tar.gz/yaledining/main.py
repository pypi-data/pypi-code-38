import requests


class ConnectionError(Exception):
    """Raised when an error occurs in connecting to the API."""
    pass


class YaleDining:
    API_ROOT = 'http://www.yaledining.org/fasttrack/'
    API_VERSION = 3

    def __init__(self):
        pass

    def get(self, endpoint: str, make_list: bool = True, params: dict = {}):
        """
        Make a GET request to the dining API.

        :param endpoint: path to resource desired.
        :param make_list: should data be restructured into a list of dictionaries for easier manipulation?
        :param params: dictionary of custom params to add to request.
        """
        custom_params = {
            'version': self.API_VERSION,
        }
        custom_params.update(params)
        request = requests.get(self.API_ROOT + endpoint, params=custom_params)
        if request.ok:
            data = request.json()
            if make_list:
                data = [
                    {data['COLUMNS'][index]: entry[index] for index in range(len(entry))}
                    for entry in data['DATA']
                ]
            return data
        else:
            # TODO: Can we be more helpful?
            raise ConnectionError('API request failed.')

    def get_locations(self):
        return self.get('locations.cfm')

    def get_menus(self, location_id: int):
        return self.get('menus.cfm', params={'location': location_id})

    def get_nutrition(self, item_id: int):
        return self.get('menuitem-nutrition.cfm', params={'MENUITEMID': item_id})[0]

    def get_traits(self, item_id: int):
        return self.get('menuitem-codes.cfm', params={'MENUITEMID': item_id})[0]

    def get_ingredients(self, item_id: int):
        return self.get('menuitem-ingredients.cfm', params={'MENUITEMID': item_id})
