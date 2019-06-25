import os
import sys
import time
import random
import os.path as osp
from collections import OrderedDict


def check_file_exists(filepath):
    return os.path.exists(filepath)


def logging(message):
    print('%s %s' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), message))


def make_list(name):
    return name if isinstance(name, list) else [name]


def make_tuple(data):
    return data if isinstance(data, tuple) else (data,)


def print_version():
    import platform
    logging('Python: %s' % platform.python_version())
    logging('Trainer: %s' % os.path.split(os.path.realpath(__file__))[0])
    try:
        from git import Repo
        repo = Repo(os.curdir, search_parent_directories=True)
        signature = repo.head.commit.hexsha[:6]
        if repo.git.diff(repo.head.commit.tree) == '':
            logging('Git Signature: {} [commited]'.format(signature))
        else:
            logging('Git Signature: {} [uncommited]'.format(signature))
    except:
        tmpfile_log = '/tmp/' + str(random.random()) + '.log.txt'
        tmpfile_diff = '/tmp/' + str(random.random()) + '.diff.txt'
        log_cmd = 'git log  > %s' % tmpfile_log
        diff_cmd = 'git diff  > %s' % tmpfile_diff
        log_status = os.system(log_cmd)
        if log_status == 0:
            signature = open(tmpfile_log).readline().split()[1]
            diff_status = os.system(diff_cmd)
            diff_result = open(tmpfile_diff).read()
            if len(diff_result) == 0:
                logging('Git Signature: {} [commited]'.format(signature))
            else:
                logging('Git Signature: {} [uncommited]'.format(signature))


def tensor2blob(tensor_data):
    import ptcaffe.proto.caffe_pb2 as caffe_pb2
    blob = caffe_pb2.BlobProto()
    blob.shape.dim.extend(tensor_data.shape)
    blob.data.extend(tensor_data.numpy().flat)
    return blob


def torch_version_ge(other_version):
    import torch
    from packaging import version
    return version.parse(torch.__version__) >= version.parse(other_version)


class ThreadsSync:
    def __init__(self):
        import threading
        self.cond = threading.Condition()
        self.count = 0

    def wait_synchronize(self, num_threads):
        self.cond.acquire()
        self.count += 1
        if self.count < num_threads:
            self.cond.wait()
        else:
            self.cond.notify_all()
        self.count = 0
        self.cond.release()


class SafeNetwork:
    def __init__(self, model):
        self.model = model

    def save_model(self, savename):
        self.model.save_model(savename)


def get_visdom(server_param, cfg=None):
    viz = None
    try:
        import visdom
        if 'server' in server_param:
            server = server_param['server']
        elif cfg is not None and cfg.VISDOM_SERVER is not None:
            server = cfg.VISDOM_SERVER
        else:
            return None

        if server.find('http://') < 0:
            server = 'http://%s' % server
        port = 8097
        if 'port' in server_param:
            port = int(server_param['port'])
        elif cfg is not None:
            port = cfg.VISDOM_SERVER_PORT

        incoming = False
        if 'incoming' in server_param:
            incoming = (server_param['incoming'] == 'true')
        elif cfg is not None:
            incoming = cfg.VISDOM_SERVER_USING_INCOMING_SOCKET

        env_name = "main"
        if 'env' in server_param:
            env_name = server_param['env']
        elif cfg is not None and cfg.VISDOM_ENV_NAME is not None:
            env_name = cfg.VISDOM_ENV_NAME
        print('init visom server: %s:%d, incoming=%s, env_name=%s' % (server, port, incoming, env_name))
        viz = visdom.Visdom(server=server, port=port, use_incoming_socket=incoming, env=env_name)
        return viz

    except ImportError:
        viz = None
        return viz


def python_version():
    return "%d.%d.%d" % (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)

def get_lname(layer):
    lname = layer['name']
    if 'include' in layer and 'phase' in layer['include']:
        phase = layer['include']['phase']
        return lname + '@' + phase
    return lname

# return top or train_top in TRAIN; top or test_top in TEST
# return top or train_top or test_top in ""
def get_layer_bnames(layer, phase):
    #check
    assert phase in ["TEST", "TRAIN"], "phase should be TRAIN or TEST but {}".format(phase)

    if ("train_bottom" in layer or "test_bottom" in layer)\
            and "bottom" in layer:
        raise("bottom should not in layer if train_bottom\
                or test bottom in layer")
    else: pass


    if phase == 'TRAIN':
        if 'bottom' in layer:
            return make_list(layer['bottom'])
        elif 'train_bottom' in layer:
            return make_list(layer['train_bottom'])
        else:
            return []

    elif phase == "TEST":
        if 'bottom' in layer:
            return make_list(layer['bottom'])
        elif 'test_bottom' in layer:
            return make_list(layer['test_bottom'])
        else:
            return []

    #elif phase=="":
    #    if 'bottom' in layer:
    #        return make_list(layer['bottom'])
    #    elif  "train_bottom" in layer or "teat_bottom" in layer:
    #        buff = []
    #        buff += make_list(layer["train_bottom"]) \
    #                if "train_bottom" in layer else []
    #        buff += make_list(layer["test_bottom"]) \
    #                if "test_bottom" in layer else []
    #        return buff
    #    else:
    #        return []

    else: raise(RuntimeError("phase [{}] should be TRAIN, TEST or '' ".format(phase)))


def get_layer_tnames(layer, phase):
    #check
    assert phase in ["TEST", "TRAIN"], "phase should be TRAIN or TEST but {}".format(phase)

    if ("train_top" in layer or "test_top" in layer)\
            and "top" in layer:
        raise("top should not in layer if train_top\
                or test top in layer")
    else: pass

    if phase == 'TRAIN':
        if 'top' in layer:
            return make_list(layer['top'])
        elif 'train_top' in layer:
            return make_list(layer['train_top'])
        else:
            return []

    elif phase == "TEST":
        if 'top' in layer:
            return make_list(layer['top'])
        elif 'test_top' in layer:
            return make_list(layer['test_top'])
        else:
            return []

    #elif phase=="":
    #    if 'top' in layer:
    #        return make_list(layer['top'])
    #    elif  "train_top" in layer or "teat_top" in layer:
    #        buff = []
    #        buff += make_list(layer["train_top"]) \
    #                if "train_top" in layer else []
    #        buff += make_list(layer["test_top"]) \
    #                if "test_top" in layer else []
    #        return buff
    #    else:
    #        return []

    else: raise(RuntimeError("phase [{}] should be TRAIN, TEST or '' ".format(phase)))



def register_plugin(plugin):
    if plugin is not None:
        import sys
        import importlib
        try:
            from ptcaffe_plugins import PLUGIN_LIST
        except BaseException:
            PLUGIN_LIST = []
        from ptcaffe.utils.config import cfg
        from ptcaffe.utils.logger import logger
        sys.path.insert(0, '.')
        plugins = plugin.split(',')
        for plugin in plugins:
            if plugin.find('.py'):
                plugin = plugin.replace('.py', '')

            if plugin in PLUGIN_LIST:
                plugin = 'ptcaffe_plugins.%s' % plugin
                print('enable system plugin %s' % plugin)
                importlib.import_module(plugin)
            else:
                print('load user plugin %s' % plugin)
                importlib.import_module(plugin)


def add_path(path):
    if path not in sys.path:
        sys.path.insert(0, path)


def add_local_path(path_name):
    this_dir = osp.dirname(__file__)
    lib_path = osp.join(this_dir, path_name)
    add_path(lib_path)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def auto_value(value):
    if isinstance(value, OrderedDict):
        return parse_types(value)
    elif isinstance(value, dict):
        return parse_types(value)
    elif isinstance(value, list):
        return [auto_value(v) for v in value]
    elif is_number(value):
        if value.find('.') >= 0:
            return float(value)
        else:
            return int(value)
    elif value in ['true', 'false']:
        return value == 'true'
    else:
        return value

def parse_types(params):
    new_params = type(params)()
    for key, value in params.items():
        if isinstance(value, str):
            new_params[key] = auto_value(value)
        elif isinstance(value, list):
            new_params[key] = [auto_value(v) for v in value]
        elif isinstance(value, OrderedDict):
            new_params[key] = parse_types(value)
        elif isinstance(value, dict):
            new_params[key] = parse_types(value)
        else:
            assert False, "Unknown value type"

    return new_params


def get_kw(fun, bigdict):
    from inspect import isfunction, isclass
    if isfunction(fun):
        keys = fun.__code__.co_varnames
    elif isclass(fun):
        keys = fun.__init__.__code__.co_varnames
        keys = tuple(keys[1:]) # pop self
    else: raise("wrong in getkw not class or function")

    try:
        return {k:bigdict[k] for k in keys if k in bigdict}
    except:
        raise("wrong in getkw")

def parse_kw(bigdict):

    def _fn(fun, *other_args , **other_kwargs):
        kwargs = get_kw(fun=fun, bigdict=bigdict)
        kwargs.update(other_kwargs)
        try:
            return fun(*other_args, **kwargs)
        except Exception as e:
            print("-------DEBUG INFO-------")
            print("fun", fun)
            print("other_args", other_args)
            print("other_kwargs", other_kwargs)
            print("kwargs", kwargs)
            raise(e)

    return _fn


def make_edict(params, parse_type=True):
    from easydict import EasyDict as edict
    if parse_type:
        params = parse_types(params)
    return edict(params)
