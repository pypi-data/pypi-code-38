from datetime import datetime as dt, timedelta
from mcneelat.pyutils.confutils import AbstractLogUtils
import requests


class ThreatStream(AbstractLogUtils):
    """Class containing handy methods common to working with the Anomali ThreatStream API."""

    """Map of general IOC categories to the most interesting IOC types."""
    ICATEGORY_MAP = {
        "domain": "apt_domain,c2_domain,exfil_domain,exploit_domain,mal_domain",
        "ip": "apt_ip,c2_ip,exfil_ip,exploit_ip,mal_ip",
        "url": "apt_url,c2_url,exfil_url,exploit_url,mal_url"
    }

    def __init__(self, api_user, api_key, min_confidence=50, last_modified_days=90,
                 results_limit=0, verbose=True):
        """
        Initialize class.
        :param api_user: API username
        :param api_key: API secret key
        :param min_confidence: minimum confidence for IOCs to look for
        :param last_modified_days: number of days ago IOCs must have been modified in order to include in results
        :param results_limit: limit of results from API queries; 0 = unlimited
        """
        self.base_url = "https://api.threatstream.com"
        self.intel_url_part = "/api/v2/intelligence/"
        self.creds_url_part = "username=%s&api_key=%s" % (api_user, api_key)
        self.min_confidence = min_confidence
        self.last_modified_days = last_modified_days
        self.results_limit = results_limit
        self.next_url_base = "%s?%s&status=active&confidence__gte=%i&limit=%i" % (
            self.intel_url_part, self.creds_url_part, self.min_confidence, self.results_limit
        )
        AbstractLogUtils.__init__(self, verbose)

    def is_threat(self, test_object):
        """
        Check if an indicator is malicious (i.e. an active IOC in ThreatStream)
        :param test_object: indicator to check
        :return: True if malicious, False if not found active in ThreatStream
        """
        last_modified = (dt.today() - timedelta(days=self.last_modified_days)).strftime("%Y-%m-%dT00:00:00Z")
        next_url = "%s&modified_ts__gte=%s&value=%s" % (self.next_url_base, last_modified, test_object)
        try:
            json_data = requests.get(self.base_url + next_url).json()
        except ValueError:
            return False
        try:
            json_data.get('objects')[0]
        except:
            return False
        return True

    def get_iocs(self, icategory, severity="high"):
        """
        Get a list of IOCs and their details from a specified category.
        :param icategory: domain, ip, or url
        :param severity: low, medium, high, very-high
        :return: list of IOCs and their details
        """
        last_modified = (dt.today() - timedelta(days=self.last_modified_days)).strftime("%Y-%m-%dT00:00:00Z")
        next_url = "%s&modified_ts__gte=%s&meta.severity__contains=%s&itype=%s" % (
            self.next_url_base, last_modified, severity, ThreatStream.ICATEGORY_MAP[icategory]
        )
        self.log("Starting to gather IOCs...")
        results = []
        while next_url != None and next_url != "null":
            try:
                json_data = requests.get(self.base_url + next_url).json()
            except ValueError:
                self.log("Warning, call to URL '%s' resulted in no JSON object response." % self.base_url + next_url)
                break
            for entry in json_data.get('objects'):
                results.append(entry)
            next_url = json_data.get('meta').get('next')
        return results
