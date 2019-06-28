import json
import pytz
from datetime import datetime
from xml.etree import ElementTree


class Utils(object):

    @staticmethod
    def read_config(config):
        obj = dict()
        with open(config) as f:
            obj = json.load(f)
        return obj

    @staticmethod
    def print_title(config):
        cfn = Utils.read_config(config)
        title = "Starting process " + cfn["name"] + " v" + cfn["version"]
        return title

    @staticmethod
    def utc_to_date(timestamp, format="%Y-%m-%d %H:%M:%S"):
        ts = int(timestamp)
        return datetime.utcfromtimestamp(ts).strftime(format)

    @staticmethod
    def utc_to_datetime(intdate):
        return datetime.utcfromtimestamp(int(intdate))

    @staticmethod
    def datetime_zone(date, timezone):
        da = pytz.utc.localize(date)
        return da.astimezone(pytz.timezone(timezone))

    @staticmethod
    def string_to_date(date, format="%Y-%m-%d %H:%M:%S"):
        return datetime.strptime(date, format)

    @staticmethod
    def datetime_to_timestamp(date):
        return int(date.strftime("%s"))

    @staticmethod
    def format_date(date, format="%Y-%m-%d %H:%M:%S"):
        return datetime.strftime(date, format)

    @staticmethod
    def get_secret(secret):
        f = open('/run/secrets/' + secret).read().rstrip('\n')
        return f

    def _parse_child(self, ele):
        obj = dict()
        for child in ele:
            if child.text is None:
                obj[child.tag] = self._parse_child(child)
            else:
                obj[child.tag] = child.text
        return obj

    @staticmethod
    def parse_xml(self, input):
        obj = dict()
        try:
            root = ElementTree.fromstring(input)
            for child in root:
                if child.text is None:
                    obj[child.tag] = self._parse_child(child)
                else:
                    obj[child.tag] = child.text
        except Parse:
            return None
        return obj
