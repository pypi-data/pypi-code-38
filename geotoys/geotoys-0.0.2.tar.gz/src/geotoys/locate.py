"""
Methods for querying OpenStreetMaps for geolocation information from place
names.
"""
import shapely

# TODO finish
def find_places(query):
    """
    Look for a postal code, place-name combination in a string and return its location
    """
    parts = str(query).split(' ')
    for i, p in enumerate(parts):
        p = p.replace('-', ' ').strip()
        try:
            postal_code = int(p)
            if len(postal_code) == 4:
                print(postal_code, parts[i+1])
                # Check 
                #response = get_osm_location("{postal_code} {name}")
                #lon = response['lon']
                #lat = response['lat']
                #poly = 
        except Exception as e:
            continue

def get_osm_location(query):
    """
    Query OpenStreetMaps for the location information of a postal code and place name
    """
    import requests

    url = f"https://nominatim.openstreetmap.org/search/{query}?format=json"

    try:
        response = requests.get(url, params={'polygon':'1'})
    except Exception as e:
        raise e

    return response.json()
