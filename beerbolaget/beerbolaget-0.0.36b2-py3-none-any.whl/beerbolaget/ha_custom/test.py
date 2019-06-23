import asyncio
import json
import common

class beer_handler():
    def __init__(self, api_key, ratebeer, untappd):
        self.api_key = api_key
        self.ratebeer = ratebeer
        self.untappd = untappd
        self.beers = []
        self.release = None

    async def update_new_beers(self):
        beer_available = await common.get_beverage(self.api_key, 'Öl')
        if len(beer_available) > 0:
            self.release = beer_available[-1]['SellStartDate']
        for beer_item in beer_available:
            if beer_item['SellStartDate'] == self.release:
                new_beer = beer('beer', beer_item['ProducerName'], beer_item['ProductNameBold'], beer_item['ProductNameThin'],
                                beer_item['Type'], beer_item['Price'], beer_item['Country'])
                self.beers.append(new_beer)
    
    async def get_beers(self):
        beers = []
        for beer in self.beers:
            beers.append(beer.__dict__)
        return json.dumps(beers)

    async def get_release(self):
        return self.release

class beer():
    def __init__(self, beverage_type, brewery, name, detailed_name, type, price, country):
        self.beverage_type = beverage_type
        self.brewery = brewery
        self.name = name
        self.detailed_name = detailed_name
        self.type = type
        self.price = price
        self.country = country
        self.rating = None

if __name__ == '__main__':
    beer_handle = beer_handler('8d15733674534d50b8a41889fe2a11f8', None, None)
    asyncio.run(beer_handle.update_new_beers())
    print(asyncio.run(beer_handle.get_beers()))