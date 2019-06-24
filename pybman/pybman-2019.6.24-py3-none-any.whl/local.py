import os

from datetime import date

from pybman import data
from pybman import utils


class LocalData:

    def __init__(self, base_dir='./data/', ous_dir='ous', ctx_dir='ctx', pers_dir='pers', create=False):

        self.data_dir = os.path.realpath(base_dir)
        # self.data_file = os.path.join(self.data_dir, 'paths.txt')
        self.data_exists = True

        self.ou_dir = os.path.join(self.data_dir, ous_dir)
        self.ctx_dir = os.path.join(self.data_dir, ctx_dir)
        self.pers_dir = os.path.join(self.data_dir, pers_dir)

        self.ou_exists = True
        self.ctx_exists = True
        self.pers_exists = True

        self.data_paths = []

        if not os.path.exists(self.data_dir):
            self.data_exists = False
            self.ou_exists = False
            self.ctx_exists = False
            self.pers_exists = False
            if create:
                os.mkdir(self.data_dir)
                os.mkdir(self.ou_dir)
                os.mkdir(self.ctx_dir)
                os.mkdir(self.pers_dir)

        if not os.path.exists(self.ou_dir) and self.ou_exists:
            self.ou_exists = False
            if create:
                os.mkdir(self.ou_dir)

        if not os.path.exists(self.ctx_dir) and self.ctx_exists:
            self.ctx_exists = False
            if create:
                os.mkdir(self.ctx_dir)

        if not os.path.exists(self.pers_dir) and self.pers_exists:
            self.pers_exists = False
            if create:
                os.mkdir(self.pers_dir)

        if self.data_exists:
            for root, dirs, files in os.walk(self.data_dir):
                for name in files:
                    if name.endswith(".txt"):
                        self.data_paths.append(os.path.join(root, name))
                    elif name.endswith(".json"):
                        self.data_paths.append(os.path.join(root, name))
                    elif name.endswith(".csv"):
                        self.data_paths.append(os.path.join(root, name))
                    else:
                        continue
            if self.data_paths:
                self.data_paths.sort()
                print('local pulication data:')
                for p in self.data_paths[:25]:
                    print(p)
                if len(self.data_paths) > 25:
                    print(". . .")

    # find path by given pattern
    def find_data_path(self, pattern):
        found_paths = []
        if self.data_paths:
            for p in self.data_paths:
                if pattern in p:
                    found_paths.append(p)
            if not found_paths:
                print("could not find path containing", pattern)
            return found_paths
        else:
            print('no local data!')
            return found_paths

    # get local data
    def get_data(self, pattern):
        data_sets = []
        paths = self.find_data_path(pattern)
        if paths:
            for path in paths:
                json_data = utils.read_json(path)
                data_idx = path.split("/")[-1].split(".")[0]
                data_sets.append(data.DataSet(data_idx, data=json_data))
        else:
            print("could not find local data!")
        return data_sets

    # write local data file
    def store_data(self, idx, dict_data):
        print("store local data of", idx)
        # self.change_data_path(idx)
        path = self.generate_data_path(idx)
        utils.write_json(path, dict_data)

    # get data path for given id
    def generate_data_path(self, data_id):
        return self.data_dir + data_id + "--" + date.today().isoformat() + ".json"

    # def change_data_path(self, idx):
    #    """
    #    update list of paths
    #    """
    #    pos = -1
    #    for i, path in enumerate(self.data_paths):
    #        if idx in path:
    #            pos = i
    #            break
    #    new = self.generate_data_path(idx)
    #    if pos < 0:
    #        self.data_paths.append(new)
    #        utils.write_list(self.data_file, self.data_paths)
    #        print("local data file added", new)
    #    else:
    #        old = self.data_paths[pos]
    #        # self.clean_local_data(old)
    #        self.data_paths[pos] = new
    #        utils.write_list(self.data_file, self.data_paths)
    #        print("local data file updated", new)

    # remove old local data
    # def clean_local_data(self, idx):
    #    """
    #    clean up local data
    #    """
    #    path = self.find_data_path(idx)
    #    if path:
    #        print("removing file", path)
    #        os.remove(path)
    #    else:
    #        print("failed to remove file from entity", idx)

#    def store_titles_local(self, idx, data):
#        pass
