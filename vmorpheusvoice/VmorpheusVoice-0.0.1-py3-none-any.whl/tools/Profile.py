import os
from pathlib import Path
class Profile(object):
    def __init__(self,name):
        self.filepath = str(Path.home())+"/.VMorpheus/"+str(name)
        self.dirs = {'in_audio':"/in_audio",'data_probes':"/data_probes",'out_audio':"/out_audio"}
        self.set_dirs()
    
    def make_dir_profile(self, path):
        if os.path.exists(path):
            os.path.dirname(path)
        else:
            os.makedirs(path)

    def set_dirs(self):
        for path in self.dirs.values():
            self.make_dir_profile(self.filepath+path)

    def get_filepath(self, name_dir):
        return self.filepath + self.dirs[name_dir]