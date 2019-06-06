import json
from itertools import groupby

import requests

def get_title(card):
    return card['title']

def fetch_cards_from_netrunnerdb():
    return requests.get(
        'https://netrunnerdb.com/api/2.0/public/cards'
    ).json()['data']

def load_cards_from_nrdb(collection):
    card_data = fetch_cards_from_netrunnerdb()
    load_cards(collection, card_data)

def load_cards_from_disk(collection):
    with open('downloads/card_data.json', 'r') as card_file:
        card_data = json.load(card_file)
    load_cards(collection, card_data)

def load_cards(collection, card_data):
    card_data = sorted(card_data, key=get_title)
    collection.insert_many([
        {
            'name': name,
            'side': [printing['side_code'] for printing in printings][0],
            'packs': [printing['pack_code'] for printing in printings]
        }
        for name, printings in groupby(card_data, get_title)
    ])
