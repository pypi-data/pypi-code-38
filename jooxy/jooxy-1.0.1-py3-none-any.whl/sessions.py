from requests import get, post
import json

class Sessions(object):

    headers = {
		"Origin": "https://www.joox.com",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
		}

    def search(self, q, type, limit, offset):
        params = dict(search_input=q, sin=offset, ein=limit, type=type)

        r = self._get(self.JOOX_API_DOMAIN + self.JOOX_SEARCH_PATH,
                    params=params)
        if r.status_code != 200:
            raise("Failed to get search request.")
        return json.loads(r.text)

    def _get(self, url, params={}, withAuth=False):
        if withAuth:
            auth = self.getUserInfo()
            params.update(dict(wmid=auth["wmid"],
                               s=auth["session_key"], u=auth["user_type"], c=auth["reg_country"]
                               ))
        params.update(self.DEFAULT_PARAMS)
        data = get(url, params=params, headers=self.headers)
        return data

    def _post(self, url, params={}, payload={}, files=None):
        auth = self.getUserInfo()
        params = dict(wmid=auth["wmid"],
                      s=auth["session_key"], u=auth["user_type"], c=auth["reg_country"]
                      )
        payload.update({"wmid": auth["wmid"], **self.DEFAULT_PARAMS})
        data = post(url, params=params, data=json.dumps(payload), headers=self.headers)
        return data
