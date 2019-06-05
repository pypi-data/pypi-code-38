import requests
import singer

LOGGER = singer.get_logger()


def app_rating(product_id, API_key):
    
    market = "ios" if product_id == "577251728" else "google-play"
    
    if market is None:
        raise

    url = "https://api.appannie.com/v1.3/apps/{}/app/{}/ratings".format(market, product_id)

    querystring = {"page_index":"0"}

    headers = {
        'authorization': "Bearer {}".format(API_key),
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.json()

def product_sales(account_id, product_id, API_key, start_date, end_date, delta_import):
    check = "2011-11-27" if delta_import is False else start_date
    market = "ios" if product_id == "577251728" else "google-play"
    
    if market is None:
        raise
    
    url = "https://api.appannie.com/v1.3/accounts/{}/products/{}/sales".format(account_id, product_id)

    querystring = {"break_down":"date country","start_date":check,"end_date":end_date,"page_index":"0"}

    headers = {
        'authorization': "Bearer {}".format(API_key),
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.json()

def product_store_metrics(account_id, product_id, API_key, start_date, end_date, delta_import):
    check = "2015-04-01" if delta_import is False else start_date
    market = "ios" if product_id == "577251728" else "google-play"
    
    if market is None:
        raise

    LOGGER.info("{}-{}-{}".format(market, product_id, API_key))

    url = "https://api.appannie.com/v1.3/accounts/{}/products/{}/store_metrics".format(account_id, product_id)

    querystring = {"break_down":"date country","start_date":check,"end_date":end_date,"page_index":"0"}

    headers = {
        'authorization': "Bearer {}".format(API_key),
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.json()
