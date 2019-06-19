#!/usr/bin/env python3


"""
@author: xi
@since: 2016-11-11
"""

import collections
import os
import re
import sys
import threading

import numpy as np
import tensorflow as tf

from .. import conf
from .. import init
from .. import io
from .. import ops


class __GlobalContext(object):

    def __init__(self):
        self._session_config = tf.ConfigProto()
        self._session_config.gpu_options.allow_growth = True
        self._session = None

    # def __del__(self):
    #     if self._session is not None:
    #         self._session.close()

    @property
    def session_config(self):
        return self._session_config

    @property
    def session(self):
        if self._session is None:
            self._session = tf.Session(config=self._session_config)
        return self._session


__GLOBAL = __GlobalContext()

TF_LOG_ALL = '0'
TF_LOG_NO_INFO = '1'
TF_LOG_NO_WARN = '2'
TF_LOG_NONE = '3'


def get_tf_log_level():
    return os.environ['TF_CPP_MIN_LOG_LEVEL']


def set_tf_log_level(level):
    if level not in ('0', '1', '2', '3'):
        raise ValueError(
            'level should be one of {'
            'TF_LOG_ALL, '
            'TF_LOG_NO_INFO, '
            'TF_LOG_NO_WARN, '
            'TF_LOG_NONE}.'
        )
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = level


def get_session_config():
    return __GLOBAL.session_config


def get_session():
    return __GLOBAL.session


def initialize_global_variables():
    __GLOBAL.session.run(tf.global_variables_initializer())


def deprecated(message):
    def _decorator(fn):
        def _fn(*args, **kwargs):
            print(message, file=sys.stderr)
            return fn(*args, **kwargs)

        return _fn

    return _decorator


def variable(name,
             initial_value,
             dtype=conf.dtype,
             trainable=True):
    """Create a variable.
    Shortcut to "tf.Variable()".

    Args:
        name (str): Variable name.
        initial_value: A `Tensor`, or Python object convertible to a `Tensor`,
            which is the initial value for the Variable.
        dtype (tf.DType): The type of elements in the tensor to be fed.
        trainable (bool): If `True`, the default, also adds the variable to the graph collection
            `GraphKeys.TRAINABLE_VARIABLES`.

    Returns:
        tf.Variable: The variable object.

    Raises:
        ValueError: If both `variable_def` and initial_value are specified.
        ValueError: If the initial value is not specified, or does not have a shape and `validate_shape` is `True`.
        RuntimeError: If eager execution is enabled.

    """
    return tf.Variable(
        name=name,
        initial_value=initial_value,
        trainable=trainable,
        dtype=dtype
    )


def placeholder(name,
                shape,
                dtype=conf.dtype):
    """Create a placeholder.
    Shortcut to "tf.placeholder()".

    Args:
        name (str): Name of the placeholder.
        shape (tuple|list): The shape of the tensor to be fed (optional). If the shape is not specified,
            you can feed a tensor of any shape.
        dtype (tf.DType): The type of elements in the tensor to be fed.

    Returns:
        The placeholder tensor.

    """
    return tf.placeholder(name=name, shape=shape, dtype=dtype)


class _ContextManager(object):

    def __init__(self):
        self._stack = list()

    def push(self, context_dict):
        stack = self._stack
        if len(stack) > 0:
            top = dict(stack[-1])
            context_dict = top.update(context_dict)
        stack.append(context_dict)

    def pop(self):
        return self._stack.pop()

    def top(self):
        return self._stack[-1] if len(self._stack) > 0 else None


class _DictContext(dict):

    def __init__(self, context_manager):
        self._context_manager = context_manager
        super(_DictContext, self).__init__()

    def __enter__(self):
        self._context_manager.push(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._context_manager.pop()


class Trainable(object):
    """Trainable
    A trainable object contains TensorFlow Variables.
    """

    instance_lock = threading.Semaphore(1)
    instance_dict = collections.OrderedDict()

    reuse_context = _ContextManager()

    def __init__(self, name, build=True):
        """Construct a widget.

        Args:
            name (str): Widget name.
            build (bool): If the widget will be built during the construction.

        """
        if name is not None:
            if not isinstance(name, str):
                raise ValueError('Trainable name must be specified with string.')
            if len(name.strip()) != len(name) or name == '':
                raise ValueError('Trainable name cannot be empty or contain space characters.')
        self._name = name

        self._scope = ''
        self._full_name = None
        self._prefix = None
        self._built = False
        if build:
            self.build()

    @property
    def name(self):
        return self._name

    @property
    def built(self):
        return self._built

    def build(self):
        """Build the widget.
        The main purpose of this function is to create the trainable variables (parameters) for the widget.

        """
        if self._built:
            return self
        #
        # Build WITH scope.
        self._scope = tf.get_variable_scope().name
        if self._scope == '':
            self._full_name = self._name
        else:
            if self._scope.endswith('/'):
                self._full_name = self._scope + self._name
            else:
                self._full_name = '%s/%s' % (self._scope, self._name)
        self._prefix = self._full_name + '/'

        with tf.variable_scope(self._name):
            self._build()
            self._built = True

        with self.instance_lock:
            if self._full_name in self.instance_dict:
                raise ValueError('Duplicated trainable name %s.' % self._full_name)
            self.instance_dict[self._full_name] = self
        return self

    def _build(self):
        """Build the widget.
        Abstract method.
        All subclass must implement this method.

        There is one task to be done in this method:
        1) Create the parameters (trainable variables) for the widget.

        """
        raise NotImplementedError()

    def _variable(self,
                  name,
                  initializer,
                  shape,
                  dtype=conf.dtype,
                  trainable=True,
                  lookup=True):
        """Create a variable.
        Shortcut to "tf.Variable()".

        Args:
            name (str): Variable name.
            initializer (init.Initializer): An initializer used to initial the variable.
                Note that create an initializer does not create any Tensors on the graph.
                To create a Tensor, initializer.build() should be called.
            shape (tuple|list): Variable shape.
            dtype: Data type.
            trainable (bool): If `True`, the default, also adds the variable to the graph collection
                `GraphKeys.TRAINABLE_VARIABLES`.
            lookup (bool): Look up reuse_dict first?

        Returns:
            tf.Variable: The variable object.

        """
        var_ = self._variable_lookup(name) if lookup else None
        return tf.Variable(
            name=name,
            initial_value=initializer.build(shape=shape, name='init_' + name),
            dtype=dtype,
            trainable=trainable
        ) if var_ is None else var_

    def _variable_lookup(self, name):
        """Lookup existing variable from the given var_dict.

        Args:
            name (str): Relative variable name. (Not a full name or absolute path.)

        Returns:
            Tensor or Variable if the required variable exists in the var_dict.

        """
        reuse_dict = self.reuse_context.top()
        if reuse_dict:
            if name.rfind(':') == -1:
                name += ':0'
            full_name = self._prefix + name
            return reuse_dict.get(full_name)
        return None

    def get_variables(self):
        """Get variables(tensors) of the widget.

        Returns:
            list: List of variables.

        """
        if self._name is None:
            return list()
        prefix = self._prefix
        global_vars = tf.global_variables()
        return [var for var in global_vars if var.name.startswith(prefix)]

    def get_trainable_variables(self):
        """Get variables(tensors that marked as "trainable") of the widget.

        Returns:
            list: List of variables.

        """
        if self._name is None:
            return list()
        trainable_vars = tf.trainable_variables()
        return [var for var in trainable_vars if var.name.startswith(self._prefix)]

    @property
    def full_name(self):
        """Get the full name of the widget.
        E.g., model/layers/layer1
        The full name does not contain "/" character.

        Returns:
            str: Full name of the widget.

        """
        return self._full_name

    @property
    def prefix(self):
        """Get the prefix of the widget.
        E.g., model/layers/layer1/
        The prefix always ends with a "/" character.

        Returns:
            str: Prefix of the widget.

        """
        return self._prefix

    def get_parameters(self):
        """Get parameter values of the widget.

        Returns:
            dict[str, np.ndarray]: Name to value dictionary of the parameters.

        """
        var_list = self.get_trainable_variables()
        param_dict = {var.name: var for var in var_list}
        param_dict = get_session().run(param_dict)
        return param_dict

    def set_parameters(self, param_dict, strict=True):
        """Set values to the parameters.

        Args:
            param_dict (dict[str, np.ndarray]): Name to value dictionary.
            strict (bool): If strict is True, all values in the dictionary must be used to assigned to the
                associated parameter, or an error will be risen.

        Raises:
            ValueError: If strict is True and there are some values in the dictionary unused.

        """
        var_list = self.get_trainable_variables()
        var_dict = {var.name: var for var in var_list}
        session = get_session()
        for name, value in param_dict.items():
            name_replace = name.replace('\\', '/')
            if name_replace not in var_dict:
                if strict:
                    raise ValueError('%s is not in this model.' % name)
            var = var_dict[name_replace]
            var.load(value, session=session)

    def dump(self, name, dumper=None):
        """Dump the model. (Save all trainable variables)

        Args:
            name (str): Model name.
                If the "dumper" argument is None, "name" is the path of the model file.
            dumper (dumpers.ModelDumper): Model dumper.

        """
        if dumper is None:
            io.dump_model_as_file(self, name)
        else:
            dumper.dump(self, name)

    def load(self, name, path=None, strict=True, dumper=None):
        """Load the model.

        Args:
            name (str): Model name.
            path (str): The path would like to be loaded into the target widget.
            strict (bool):  Strict mode.
            dumper (dumpers.ModelDumper): Model dumper.

        """
        if dumper is None:
            io.load_model_from_file(self, name, path, strict)
        else:
            dumper.load(self, name, path, strict)

    def get_operation(self, name):
        name = self._prefix + name
        try:
            return tf.get_default_graph().get_operation_by_name(name)
        except KeyError:
            return None

    def get_tensor(self, name):
        if name.rfind(':') == -1:
            name = '%s%s:0' % (self._prefix, name)
        else:
            name = self._prefix + name
        try:
            return tf.get_default_graph().get_tensor_by_name(name)
        except KeyError:
            return None

    def get_variable(self, name):
        if name.rfind(':') == -1:
            name = '%s%s:0' % (self._prefix, name)
        else:
            name = self._prefix + name
        for var in tf.global_variables():
            if name == var.name:
                return var
        return None

    def __getitem__(self, name):
        name = self._prefix + name
        with self.instance_lock:
            if name in self.instance_dict:
                instance = self.instance_dict[name]
                if isinstance(instance, Trainable):
                    return instance

        if name.rfind(':') == -1:
            name += ':0'
        try:
            return tf.get_default_graph().get_tensor_by_name(name)
        except KeyError:
            return None


class Model(Trainable):

    def _build(self):
        raise NotImplementedError()


class ReuseContext(_DictContext):

    def __init__(self, tensors=None, alias=None):
        """Reuse dict.

        Args:
            tensors (dict): Name -> Tensor map.
            alias (dict[str, str]): Alisa dict.

        """
        super(ReuseContext, self).__init__(Trainable.reuse_context)
        if tensors:
            self.add(tensors, alias)

    def add(self, tensors, alias):
        """

        Args:
            tensors (dict): Name -> Tensor map.
            alias (dict[str, str]): Alisa dict.

        """
        alias = [
            ('^' + old, new)
            for old, new in alias.items()
        ] if alias is not None else list()
        for name, tensor in tensors.items():
            for old, new in alias:
                name = re.sub(old, new, name)
            self[name] = tensor


class Widget(Trainable):
    """Widget
    The basic component to form a model.
    This an abstract class which can only be inherited.
    """

    def _build(self):
        raise NotImplementedError()

    def setup(self, *args, **kwargs):
        """Setup the widget.
        "Setup" means to create a new series of operator in the TF graph, which can be called a "path".
        No matter how many paths be created, the number of trainable variables is (and of course cannot) be changed.
        They share the same parameters of the widget.

        """
        if not self._built:
            raise RuntimeError('This widget has not been built. Please build first.')
        if self._name is None:
            #
            # Setup only WITHOUT scope.
            return self._setup(*args, **kwargs)
        else:
            #
            # Setup only WITH scope.
            with tf.variable_scope(self._prefix):
                return self._setup(*args, **kwargs)

    def _setup(self, *args, **kwargs):
        """Setup the widget.
        Abstract method.
        All subclass must implement this method.

        There is one task to be done in this method:
        1) Construct the model's graph structure with TF.

        In this method, you CANNOT create any trainable variables.

        """
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        return self.setup(*args, **kwargs)


def setup(x, widget_list):
    """Setup a series of widgets/ops with the given input "x".

    Args:
        x: The input tensor.
        widget_list (list): List of widgets/ops.

    Returns:
        Output tensor.

    """
    if widget_list is None:
        return x
    if not isinstance(widget_list, (list, tuple)):
        widget_list = [widget_list]
    y = x
    for w in widget_list:
        if callable(w):
            #
            # Note that Widget is also callable.
            y = w(y)
        elif isinstance(w, (tuple, list)):
            if len(w) != 2:
                raise ValueError('The tuple must have two elements.')
            fn = w[0]
            if not callable(fn):
                raise ValueError('%s is not callable.' % str(fn))
            if isinstance(w[1], dict):
                kwargs = w[1]
                y = fn(y, **kwargs)
            elif isinstance(w[1], str):
                y = fn(y, name=w[1])
            elif w[1] is None:
                y = fn(y)
            else:
                raise ValueError('The second term of the tuple must be str or dict.')
        elif isinstance(w, str):
            tf.identity(y, name=w)
        elif w is None:
            continue
        else:
            raise ValueError('%s is not callable.' % str(w))
    return y


def setup_sequence(seq, widget_list):
    """Setup a series of widgets/ops with the given sequence "seq".

    Args:
        seq: Tensor represents a sequence shaped (batch_size, seq_length, ...).
        widget_list (list): List of widgets/ops.

    Returns:
        tf.Tensor: Output tensor.

    """
    seq = ops.transpose_sequence(seq)
    y = tf.map_fn(
        fn=lambda elem: setup(elem, widget_list),
        elems=seq
    )
    y = ops.transpose_sequence(y)
    return y


class Step(object):
    """Train step.
    Trainable is trained and tested step by step~
    """

    def __init__(self,
                 inputs=None,
                 outputs=None,
                 updates=None,
                 givens=None,
                 callbacks=None):
        """A slot object is a callable which accepts multiple tensor inputs
        and gives out multiple outputs.

        Args:
            inputs (list[tf.Tensor]|tuple[tf.Tensor]|tf.Tensor):
                Input tensor(s).
            outputs (dict[str, tf.Tensor]|list[tf.Tensor]|tuple[tf.Tensor]|tf.Tensor):
                Output tensor(s).
            updates (list[tf.Operation]|tuple[tf.Operation]|tf.Operation):
                Operation(s) when invoked. These are usually generated by optimizers.
            givens (dict[tf.Tensor, Any]):
                Preset values for some placeholder, e.g., the keep_prob value for dropout.
            callbacks (list[(Any) -> None]|tuple[(Any) -> None]|(Any) -> None): Callback(s)

        """
        self._session = get_session()
        #
        # Inputs.
        if inputs is None:
            inputs = ()
        if not isinstance(inputs, (tuple, list)):
            inputs = (inputs,)
        self._inputs = inputs
        #
        # Outputs.
        if outputs is None:
            outputs = ()
        if not isinstance(outputs, (tuple, list)) \
                and not isinstance(outputs, (dict, collections.OrderedDict)):
            outputs = (outputs,)
        self._outputs = outputs
        #
        # Updates.
        if updates is None:
            updates = ()
        if not isinstance(updates, (tuple, list)):
            updates = (updates,)
        self._updates = updates
        #
        # Givens.
        if givens is None:
            givens = {}
        if not isinstance(givens, dict):
            raise ValueError('Givens must be dict.')
        self._givens = givens
        #
        # Callbacks.
        if callbacks is None:
            callbacks = ()
        if not isinstance(callbacks, (tuple, list)):
            callbacks = (callbacks,)
        self._callbacks = callbacks
        #
        self._feed_dict = givens.copy()
        self._fetches = (outputs, updates)
        if len(outputs) == 0 and len(updates) == 0:
            raise ValueError('At least one output or update should be set.')

    @property
    def outputs(self):
        return self._outputs

    @property
    def inputs(self):
        return self._inputs

    @property
    def updates(self):
        return self._updates

    @property
    def givens(self):
        return self._givens

    def __call__(self, *args):
        #
        # Check input length.
        if len(args) != len(self._inputs):
            print(len(args), len(self._inputs))
            raise ValueError('The count of parameters is not match the inputs.')
        #
        # Make "feed_dict".
        for index, placeholder_ in enumerate(self._inputs):
            self._feed_dict[placeholder_] = args[index]
        #
        # Run the graph on the session.
        ret = self._session.run(fetches=self._fetches, feed_dict=self._feed_dict)[0]
        for callback in self._callbacks:
            callback(ret)
        return ret
