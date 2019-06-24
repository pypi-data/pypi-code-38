from io import StringIO

import pandas as pd


def read_list_to_df(data):
    missing = data[1].split()[1:]
    cols = data[2].split()
    buffer = StringIO(''.join(data[3:]))
    df = pd.read_csv(buffer, sep='\s+', names=cols, na_values=missing)
    return df

class L2Reader:
    def __init__(self, fname):
        with open(fname, 'r') as f:
            self.data = f.readlines()
        self.parse_data()

    def parse_data(self):
        comments_found = 0
        self.header_dic = {}
        self.rms_data = []
        self.limb_data = []
        self.nadir_data = []
        self.profiles_data = []

        for line in self.data:
            if line.startswith(' ### '):
                comments_found += 1
                continue
            if comments_found < 1:
                continue
            if comments_found == 1:
                key, value = line.split('=')
                self.header_dic[key.strip()] = value.strip()
            if comments_found == 2:
                self.rms_data.append(line)
            if comments_found == 3:
                self.limb_data.append(line)
            if comments_found == 4:
                self.nadir_data.append(line)
            if comments_found == 5:
                self.profiles_data.append(line)

    @property
    def header(self):
        return pd.Series(self.header_dic)

    @property
    def rms(self):
        return read_list_to_df(self.rms_data)

    @property
    def limb(self):
        return read_list_to_df(self.limb_data)

    @property
    def nadir(self):
        return read_list_to_df(self.nadir_data)

    @property
    def profiles(self):
        return read_list_to_df(self.profiles)
