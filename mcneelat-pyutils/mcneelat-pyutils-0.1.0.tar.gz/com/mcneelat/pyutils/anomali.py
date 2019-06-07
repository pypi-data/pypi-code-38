from datetime import datetime as dt, timedelta
import requests


class Anomali:
    ICATEGORY_MAP = {
        "domain": "apt_domain,c2_domain,exfil_domain,exploit_domain,mal_domain",
        "ip": "apt_ip,c2_ip,exfil_ip,exploit_ip,mal_ip",
        "url": "apt_url,c2_url,exfil_url,exploit_url,mal_url"
    }

    def __init__(self, api_user, api_key, min_confidence=50, last_modified_days=90,
                 results_limit=0):
        self.base_url = "https://api.threatstream.com"
        self.intel_url_part = "/api/v2/intelligence/"
        self.creds_url_part = "username=%s&api_key=%s" % (api_user, api_key)
        self.min_confidence = min_confidence
        self.last_modified_days = last_modified_days
        self.results_limit = results_limit
        self.next_url_base = "%s?%s&status=active&confidence__gte=%i&limit=%i" % (
            self.intel_url_part, self.creds_url_part, self.min_confidence, self.results_limit
        )

    def is_threat(self, test_object):
        last_modified = (dt.today() - timedelta(days=self.last_modified_days)).strftime("%Y-%m-%dT00:00:00Z")
        next_url = "%s&modified_ts__gte=%s&value=%s" % (self.next_url_base, last_modified, test_object)
        try:
            json_data = requests.get(self.base_url + next_url).json()
        except ValueError:
            # print("Warning, call to URL '%s' resulted in no JSON object response." % (self.base_url + next_url))
            return False
        try:
            json_data.get('objects')[0]
        except:
            return False
        return True

    def get_iocs(self, icategory, severity="high"):
        last_modified = (dt.today() - timedelta(days=self.last_modified_days)).strftime("%Y-%m-%dT00:00:00Z")
        next_url = "%s&modified_ts__gte=%s&meta.severity__contains=%s&itype=%s" % (
            self.next_url_base, last_modified, severity, Anomali.ICATEGORY_MAP[icategory]
        )
        print("Starting to gather IOCs...")
        results = []
        while next_url != None and next_url != "null":
            try:
                json_data = requests.get(self.base_url + next_url).json()
            except ValueError:
                print("Warning, call to URL '%s' resulted in no JSON object response." % self.base_url + next_url)
                break
            for entry in json_data.get('objects'):
                results.append(entry)
            next_url = json_data.get('meta').get('next')
        return results