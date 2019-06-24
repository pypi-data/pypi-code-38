import requests
from datetime import datetime
from tmdbv3api import TMDb, TV
from pprint import pprint

def eztv(q, limit, page=1, quality=None, debug=False):
    tmdb = TMDb(debug=True)
    tmdb.api_key = 'e1076b74406e0a7d0efb5318f1b662d0'
    tv = TV()
    sr = tv.search(q)
    if not sr:
        return
    url = 'https://eztv.ag/api/get-torrents'
    details = tv.external_ids(sr[0].id)
    overview = sr[0].overview
    req = requests.get('%s?imdb_id=%s&page=%s&limit=%s' % (url, details['imdb_id'][2:], page, limit))
    if debug:
        print(req.status_code)
    if not req.ok:
        return
    results, count = [], 1
    search_results = req.json()
    if debug:
        pprint(search_results)
    if 'torrents' not in search_results:
        return
    for result in search_results['torrents']:
        obj = {
            'id': count,
            'title': result['title'],
            'magnet': result['magnet_url'],
            'seeds': result['seeds'],
            'peers': result['peers'],
            'overview': overview,
            'rating' : '-',
            'release_date': datetime.fromtimestamp(int(result['date_released_unix'])).strftime('%Y-%m-%d %H:%M:%S')
        }
        if quality is not None:
            if quality.lower() in result['title']:
                results.append(obj)
                count += 1
        else:
            results.append(obj)
            count += 1
    if debug:
        pprint(results)
    return results
