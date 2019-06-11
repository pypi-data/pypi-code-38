import os


from cellphonedb.src.core.methods.method_launcher import MethodLauncher

cellphone_core_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = '{}/data'.format(cellphone_core_dir)

data_test_dir = '{}/tests/fixtures'.format(cellphone_core_dir)


class Cellphonedb(object):
    def __init__(self, config):
        self.config = {'default_threads': config['threads']}
        self.method = MethodLauncher(self.config['default_threads'])
        self.debug_mode = config['debug']
