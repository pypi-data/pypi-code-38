import random
import requests


def get_joke():
    jokes = get_jokes()
    return random.choice(jokes)


def get_jokes():
    url = 'https://raw.githubusercontent.com/EugeneKay/git-jokes/lulz/Jokes.txt'  # noqa: E501
    resp = requests.get(url)
    if resp.ok:
        return resp.text.splitlines()
    else:
        resp.raise_for_status()
