"""
support modules: get jokes

"""
import requests


def get_joke(search_term=None):
    """ returns joke """

    headers = {"Accept": "application/json"}

    random_jokes_url = "https://icanhazdadjoke.com/"
    keyword_jokes_url = "https://icanhazdadjoke.com/search"

    # Initialize returned joke(s)
    returned_joke = None

    if search_term:
        params = {"term": search_term}
        r = requests.get(keyword_jokes_url, params=params, headers=headers)
        returned_jokes = r.json()  # joke_response_objectn()
        if returned_jokes["status"] == 200:
            joke_list = []
            for joke in range(returned_jokes["total_jokes"]):
                joke_list.append(returned_jokes["results"][joke]["joke"])
            returned_joke = joke_list
    else:
        r = requests.get(random_jokes_url, headers=headers)
        returned_joke = r.json()
        if returned_joke["status"] == 200:
            returned_joke = {"success": True, "joke": returned_joke["joke"]}
        else:
            returned_joke = {"success": False, "joke": "I've no jokes, folks!"}

    return returned_joke
