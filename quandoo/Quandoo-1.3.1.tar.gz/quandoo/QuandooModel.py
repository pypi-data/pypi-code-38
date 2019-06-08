import json
import sys
import time
from datetime import datetime as dt, timezone, timedelta


class PrettyClass:
    useless_attrs = ["api_response", "agent"]

    def __str__(self):
        useful_attrs = ["{}: {}".format(key, val) for key, val in self.__dict__.items() if
                        key not in self.useless_attrs]

        return "{}(\n\t{}\n)".format(
            self.__class__.__name__,
            ",\n\t".join(useful_attrs)
        )

    def __repr__(self):
        return "\n" + indent(str(self))

    def to_tuple(self):
        return tuple([val for key, val in self.__dict__.items() if key not in self.useless_attrs])


class QuandooModel(PrettyClass):

    def __init__(self, data):
        self.api_response = data

    def get_api_response(self):
        return json.dumps(self.api_response, indent=2)


class QuandooDatetime(PrettyClass):
    TIME_RESOLUTION = 15  # minutes

    def __init__(self, year, month=None, day=None, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        second = microsecond = 0
        if not tzinfo:
            tzinfo = timezone(timedelta(seconds=-time.timezone))

        self.datetime = dt(year, month, day, hour, minute, second, microsecond, tzinfo)
        self.__resolve_time()

    def __str__(self):
        useful_attrs = ["{}: {}".format(key, val) for key, val in self.__dict__.items() if
                        key not in self.useless_attrs] + ["{}: {}".format("q_datetime", self.get_qdt()),
                                                          "{}: {}".format("pretty_date", self.pretty_date())]

        return "{}(\n\t{}\n)".format(
            self.__class__.__name__,
            ",\n\t".join(useful_attrs)
        )

    def __eq__(self, other):
        return self.datetime == other.datetime

    def __lt__(self, other):
        return self.datetime > other.datetime

    @staticmethod
    def now():
        y, m, d, h, i, *_ = dt.now().timetuple()
        return QuandooDatetime(y, m, d, h, i)

    @staticmethod
    def parse_str_qdt(string):
        d = string.split("+")
        d[1] = d[1].replace(":", "")
        y, m, d, h, i, *_ = dt.strptime("+".join(d), "%Y-%m-%dT%H:%M:%S%z").timetuple()
        return QuandooDatetime(y, m, d, h, i)

    @staticmethod
    def parse_pretty_qdt(string):
        y, m, d, h, i, *_ = dt.strptime(string, "%I:%M %p, %a %d %B %Y").timetuple()
        return QuandooDatetime(y, m, d, h, i)

    def __resolve_time(self):
        y, m, d, h, i, *_ = self.datetime.timetuple()
        i = ((i // QuandooDatetime.TIME_RESOLUTION) * QuandooDatetime.TIME_RESOLUTION)

        self.datetime = dt(y, m, d, h, i, tzinfo=self.datetime.tzinfo)

    def get_qdt(self):
        return dt.strftime(self.datetime, "%Y-%m-%dT%H:%M:%S{}".format(str(self.datetime.tzinfo)[-6:]))

    def get_urldt(self):
        return self.datetime.strftime("%Y-%m-%d %H:%M:%S")

    def pretty_date(self):
        if sys.platform.startswith("win"):
            token = "#"
        elif sys.platform.startswith("linux"):
            token = "-"
        else:
            token = ""
        return self.datetime.strftime("%{token}I:%M %p, %a %{token}d %B %Y".format(**{"token": token}))


def urljoin(*argv):
    return "/".join([str(arg) for arg in argv])


def indent(string, indent_amount=1):
    return "\n".join(["\t" * indent_amount + line for line in string.split("\n")])
