
from datetime import datetime


def parse_time(time_string: str) -> datetime:  # place holder in case we want to add in timezones.
    return datetime.strptime(time_string, "%m/%d/%Y %H:%M:%S")  # Using a world inward in timestamp
#
# def parse_time_back(time_string: str) -> datetime:  # place holder in case we want to add in timezones.
#     return datetime.strptime(time_string, "%Y %H:%M:%S")  # Using a world inward in timestamp