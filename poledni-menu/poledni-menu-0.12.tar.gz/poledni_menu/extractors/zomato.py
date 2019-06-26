import datetime
import html

try:
    import requests
except ImportError:
    raise ValueError("This extractor requires requests package to work")


def _get_res_id(place_id=None, res_id=None, api_key=None):
    return res_id or place_id or "18311812"


def _parsed_api_call(
    endpoint="dailymenu", place_id=None,
    res_id=None, api_key=None,
):
    if not hasattr(_parsed_api_call, "cache"):
        _parsed_api_call.cache = dict()
    if api_key is None:
        raise ValueError(
            "This extractor requires an API key. Obtain one and "
            "add it as option called 'api_key'.",
        )
    res_id = _get_res_id(place_id, res_id)
    if (endpoint, res_id) not in _parsed_api_call.cache:
        url = "https://developers.zomato.com/api/v2.1/" + endpoint
        params = {'res_id': res_id}
        headers = {
            'user_key': api_key,
            'Accept': 'application/json',
        }
        _parsed_api_call.cache[(endpoint, res_id)] = requests.get(
            url, headers=headers, params=params,
        ).json()
    return _parsed_api_call.cache[(endpoint, res_id)]


_PLACES = {
    "16505958": ("Pod Loubím", "http://www.podloubim.com/menu/"),
    "18311812": ("Nad Alejí", "https://nadaleji.wixsite.com/nadaleji"),
    "16506914": ("DAP", "http://www.daphotel.cz/"),
}


def get_name(**kwargs):
    doc = _parsed_api_call(endpoint="restaurant", **kwargs)
    return doc.get("name", "Neznámá restaurace")


def get_url(**kwargs):
    res_id = _get_res_id(**kwargs)
    try:
        return _PLACES[res_id][1]
    except KeyError:
        doc = _parsed_api_call(endpoint="restaurant", **kwargs)
        return doc.get("menu_url", "")


def get_menu(**kwargs):
    doc = _parsed_api_call(**kwargs)
    dishes = []
    for menu in doc['daily_menus']:
        sd = menu['daily_menu'].get('start_date')
        ed = menu['daily_menu'].get('end_date')
        if sd:
            sd = datetime.datetime.strptime(sd, "%Y-%m-%d %H:%M:%S")
        if ed:
            ed = datetime.datetime.strptime(ed, "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        if sd and sd <= now and (not ed or ed > now):
            dishes.extend(menu['daily_menu'].get('dishes'))

    for meal in dishes:
        name, price = (killthatwhitespace(s)
                       for s in [meal['dish']['name'], meal['dish']['price']])
        yield (name, price)


def killthatwhitespace(string):
    return " ".join(html.unescape(s).strip()
                    for s in string.split()).capitalize()
