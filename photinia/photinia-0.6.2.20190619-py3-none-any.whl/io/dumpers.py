#!/usr/bin/env python3

"""
@author: xi
@since: 2018-01-13
"""

import os
import pickle
import re
import shutil

import gridfs


class ModelDumper(object):
    """ModelDumper
    """

    def dump(self, widget, name):
        """Dump the model to somewhere (file, DB, ...) using the given name.

        Args:
            widget: The model to be dumped.
            name (str): The output name.
                This is not the model name. Note that the output is just one instance of the model.

        """
        param_dict = widget.get_parameters()
        self._dump(param_dict, name)

    def _dump(self, param_dict, name):
        raise NotImplementedError

    def load(self, widget, name, path=None, strict=True):
        """Load a model (or part of the model) parameters into the given widget.

        If the parameters we loaded are like below:

            param_dict = {
                'model/part_1/layer/w': w_value_1,
                'model/part_1/layer/b': b_value_1,
                'model/part_2/layer/w': w_value_2,
                'model/part_2/layer/b': b_value_2
            }.

        At the same time, we set path as:

            path = 'model/part1'

        The model that we want to fill the parameters has the following structure:

            my_model
            |---layer
            |-------w
            |-------b
            |---cell
            |-------w
            |-------u
            |-------b

        So, before we call "set_parameters" of the model, we need to filter param_dict,
        to keep the parameters whose name starts with 'model/part1'. Then 'model/part1'
        in their names are replaced by 'my_model' in order to match the parameter names
        in the target model.

        Args:
            widget: A widget (or a Trainable).
            name (str): Model name.
            path (str): The path would like to be loaded into the target widget.
            strict (bool):  Strict mode.

        """
        param_dict = self._load(name)
        if path is not None:
            new_dict = {}
            for key, value in param_dict.items():
                if not key.startswith(path):
                    continue
                key, _ = re.subn('^%s' % path, widget.full_name, key)
                new_dict[key] = value
            param_dict = new_dict
        widget.set_parameters(param_dict, strict)

    def _load(self, name):
        raise NotImplementedError


class FileDumper(ModelDumper):
    """File Dumper
    """

    _INSTANCE = None

    @staticmethod
    def get_instance():
        if FileDumper._INSTANCE is None:
            FileDumper._INSTANCE = FileDumper()
        return FileDumper._INSTANCE

    def __init__(self):
        super(FileDumper, self).__init__()

    def _dump(self, param_dict, model_file):
        with open(model_file, 'wb') as f:
            pickle.dump(param_dict, f)

    def _load(self, model_file):
        with open(model_file, 'rb') as f:
            return pickle.load(f)


class TreeDumper(ModelDumper):
    """Tree Dumper

    Dump a model into a directory as a tree form.
    For example, a model with parameters {model/h1/b:0, model/h1/w:0} will be dumped in the following form:
    model/
    ....h1/
    ........w.0
    ........b.0
    """

    _INSTANCE = None

    @staticmethod
    def get_instance():
        if TreeDumper._INSTANCE is None:
            TreeDumper._INSTANCE = TreeDumper()
        return TreeDumper._INSTANCE

    def __init__(self, output_dir=None):
        super(TreeDumper, self).__init__()
        self._output_dir = output_dir

    def _dump(self, param_dict, name):
        #
        # prepare model dir
        if self._output_dir is None:
            model_dir = name
        else:
            model_dir = os.path.join(self._output_dir, name)
        if os.path.exists(model_dir):
            shutil.rmtree(model_dir)
        os.mkdir(model_dir)

        #
        #  start to dump
        for path, value in param_dict.items():
            param_dir, _ = os.path.split(path)
            param_dir = os.path.join(model_dir, param_dir)
            param_file = os.path.join(model_dir, path)
            param_file = TreeDumper._escape(param_file)
            if not os.path.exists(param_dir):
                os.makedirs(param_dir)
            with open(param_file, 'wb') as f:
                pickle.dump(value, f)

    @staticmethod
    def _escape(path):
        path = list(path)
        for i in range(len(path) - 1, -1, -1):
            ch = path[i]
            if ch == os.sep:
                break
            if ch == ':':
                path[i] = '.'
        return ''.join(path)

    def _load(self, name):
        #
        # prepare model dir
        if self._output_dir is None:
            model_dir = name
        else:
            model_dir = os.path.join(self._output_dir, name)
        if not os.path.exists(model_dir):
            raise FileNotFoundError()

        #
        # load
        param_dict = {}
        for path in os.listdir(model_dir):
            TreeDumper._load_tree(model_dir, path, param_dict)
        return param_dict

    @staticmethod
    def _load_tree(model_dir, path, param_dict):
        real_path = os.path.join(model_dir, path)
        if os.path.isdir(real_path):
            for subpath in os.listdir(real_path):
                subpath = os.path.join(path, subpath)
                TreeDumper._load_tree(model_dir, subpath, param_dict)
        elif os.path.isfile(real_path):
            path = TreeDumper._unescape(path)
            with open(real_path, 'rb') as f:
                value = pickle.load(f)
                param_dict[path] = value

    @staticmethod
    def _unescape(path):
        path = list(path)
        for i in range(len(path) - 1, -1, -1):
            ch = path[i]
            if ch == os.sep:
                break
            if ch == '.':
                path[i] = ':'
        return ''.join(path)


class MongoDumper(ModelDumper):
    """MongoDB Model Dumper
    """

    def __init__(self, db, coll='fs'):
        self._db = db
        self._coll = coll
        super(MongoDumper, self).__init__()

    def _dump(self, param_dict, name, **kwargs):
        fs = gridfs.GridFS(self._db, collection=self._coll)
        coll = self._db[self._coll + '.files']
        doc = coll.find_one({'filename': name})
        if doc is not None:
            file_id = doc['_id']
            fs.delete(file_id)
        with fs.new_file(filename=name, **kwargs) as f:
            pickle.dump(param_dict, f)

    def _load(self, name):
        fs = gridfs.GridFS(self._db, collection=self._coll)
        f = fs.find_one({'filename': name})
        if f is None:
            return None
        with f:
            param_dict = pickle.load(f)
        return param_dict


def dump_model_as_file(widget, model_file):
    FileDumper.get_instance().dump(widget, model_file)


def load_model_from_file(widget,
                         model_file,
                         path=None,
                         strict=True):
    """Load parameters into a model (or a part of the model) using FileDumper.
    """
    FileDumper.get_instance().load(widget, model_file, path, strict)


def dump_model_as_tree(widget, name):
    TreeDumper.get_instance().dump(widget, name)


def load_model_from_tree(widget,
                         name,
                         path=None,
                         strict=True):
    """Load parameters into a model (or a part of the model) using TreeDumper.
    """
    TreeDumper.get_instance().load(widget, name, path, strict)
