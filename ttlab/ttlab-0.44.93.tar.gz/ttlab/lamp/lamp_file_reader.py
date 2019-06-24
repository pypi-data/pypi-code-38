from datetime import datetime
import pytz
import numpy as np

class Data:

    def __init__(self):
        self.abs_time = []
        self.rel_time = []
        self.power = []


class LampFileReader:

    @staticmethod
    def read_data(filename,powerFile=False):
        abs_time = []
        power = []
        with open(filename, "r") as file:
            for count, line in enumerate(file):
                if powerFile:
                    pass
                else:
                    if LampFileReader._RepresentsInt(line.split(' ')[0].split('-')[0]):
                        split_line=line.split(' ')
                        date_str = split_line[0]
                        time_str = split_line[1]
                        on_off_str = split_line[3]

                        date_str = date_str.split('-')
                        year = int(date_str[0])+2000
                        month = int(date_str[1])
                        day = int(date_str[2])

                        time_str = time_str.split(':')
                        hour = int(time_str[0])
                        mins = int(time_str[1])
                        secs = int(time_str[2])

                        d = datetime(year, month, day, hour, mins, secs, tzinfo=pytz.utc)
                        abs_time.append(d.timestamp())

                        if on_off_str=='on':
                            power.append(250)
                        else:
                            power.append(0)

        data = Data()
        data.power = np.array(power)
        data.abs_time = np.array(abs_time)
        return data



    @staticmethod
    def _RepresentsInt(s):
        try:
            int(s)
            return True
        except ValueError:
            return False