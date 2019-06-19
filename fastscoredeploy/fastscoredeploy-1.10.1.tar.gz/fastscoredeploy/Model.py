from fastscore import Model as ModelBase
from fastscore.attachment import Attachment
from fastscore.snapshot import Snapshot
from fastscore.errors import FastScoreError
from fastscore import Stream

from fastscore.io import Slot

from .codec import datatype
from .codec import recordset_from_json, recordset_to_json, from_json, to_json

from inspect import getargspec

import re
import six
import json
import hashlib

class Model(ModelBase):
    """
    Represents an analytic model. A model can be created directly:

    >>> model = fastscoredeploy.Model('model-1')
    >>> model.mtype = 'python'
    >>> model.source = '...'

    Or, retrieved from a Model Manage instance:

    >>> mm = connect.lookup('model-manage')
    >>> model = mm.models['model-1']

    A directly-created model must be saved to make attachment and snapshot
    manipulation functions available:

    >>> mm = connect.lookup('model-manage')
    >>> model.update(mm)
    >>> model.attachments.names()
    []

    """

    class Annotation(object):
        """
        A class to manage model annotations.
        """
        def __init__(self, *args, **kwargs):
            self.schema = {}
            self.recordsets = {}
            self.action = {}
            self.slot = {}
            self.modules_attached = []
            self.snapshots = None
            for arg in args:
                if isinstance(arg, dict):
                    for k,v in six.iteritems(arg):
                        if k in self.__dict__:
                            self.__dict__[k] = v
                        else:
                            raise FastScoreError("Unknown option: {}".format(k))
            if kwargs:
                for k, v in six.iteritems(kwargs):
                    if k in self.__dict__:
                        self.__dict__[k] = v
                    else:
                        raise FastScoreError("Unknown option: {}".format(k))

        def __str__(self):
            result = ''
            for x,v  in six.iteritems(self.schema):
                result += '# fastscore.schema.' + str(x) + ': ' + str(v) + '\n'
            for x,v in six.iteritems(self.recordsets):
                result += '# fastscore.recordsets.' + str(x) + ': ' + str(v) + '\n'
            for x,v in six.iteritems(self.action):
                result += '# fastscore.action.' + str(x) + ': ' + str(v) + '\n'
            for x,v in six.iteritems(self.slot):
                result += '# fastscore.slot.' + str(x) + ': ' + str(v) + '\n'
            for module in self.modules_attached:
                result += '# fastscore.module-attached: ' + str(module) + '\n'
            if self.snapshots is not None:
                result += '# fastscore.snapshots: ' + str(self.snapshots) + '\n'

            return result

        @classmethod
        def from_string(self, source):
            options = {
                'schema':{},
                'recordsets':{},
                'action':{},
                'slot':{},
                'modules_attached':[],
                'snapshots':None
            }
            lines = source.split('\n')
            for line in lines:
                option = re.search(r'# *fastscore\.(.*):(.*)', line.strip())
                if option:
                    option_path = option.group(1).strip().split('.')
                    option_value = option.group(2).strip()
                    opt = option_path[0]
                    if opt == 'module-attached':
                        options['modules_attached'].append(option_value)
                    elif opt == 'snapshots':
                        options['snapshots'] = option_value
                    elif opt == 'action':
                        options['action'] = option_value
                    else:
                        slot = option_path[1]
                        if slot.isdigit():
                            slot = int(slot)
                        options[opt][slot] = option_value
            return Model.Annotation(options)

    class FunctionBag(dict):
        def __init__(self, *args, **kwargs):
            super(Model.FunctionBag, self).__init__(*args, **kwargs)
            for arg in args:
                if isinstance(arg, dict):
                    for k, v in six.iteritems(arg):
                        self[k] = v
            if kwargs:
                for k, v in six.iteritems(kwargs):
                    self[k] = v

        def __getattr__(self, attr):
            return self.get(attr)

        def __setattr__(self, key, value):
            raise FastScoreError("Model functions cannot be changed in this way. Try updating the model's source attribute.")

        def __setitem__(self, key, value):
            super(Model.FunctionBag, self).__setitem__(key, value)
            self.__dict__.update({key: value})

        def __delattr__(self, item):
            raise FastScoreError("Model functions cannot be changed in this way. Try updating the model's source attribute.")

        def __delitem__(self, key):
            super(Model.FunctionBag, self).__delitem__(key)
            del self.__dict__[key]

    def __init__(self, name, mtype='python', source=None, model_manage=None, schemas={}):
        super(Model, self).__init__(name, mtype=mtype, source=source,
                                    model_manage=model_manage)
        if mtype == 'python' or mtype == 'python3' or mtype == 'R':
            self._parse_options(source)
        if mtype == 'python' or mtype == 'python3':
            self._compile(source)

        self.schemas = schemas # the schema objects associated to this model

    def _compile(self, source):
        self._namespace = {}
        self._code = compile(source, '<string>', 'exec')
        if self.options.action != 'unused':
            exec(self._code, self._namespace)
        self.functions = Model.FunctionBag(self._namespace)

    def _parse_options(self, source):
        self.options = Model.Annotation.from_string(source)

    def _update_source_annotations(self):
        stripped_src = self._source
        lines = self._source.split('\n')
        for line in lines:
            option = re.search(r'# *fastscore\.(.*):(.*)', line.strip())
            if option:
                stripped_src = stripped_src.replace(option.group(0) + '\n', '')
        return (str(self.options) + stripped_src).strip()

    @property
    def source(self):
        """
        The source code of the model.
        """
        self._source = self._update_source_annotations()
        return self._source

    @source.setter
    def source(self, source):
        self._source = source
        if self.mtype == 'python' or self.mtype == 'python3' or self.mtype == 'R':
            self._parse_options(source)
        if self.mtype == 'python' or self.mtype == 'python3':
            self._compile(source)

    def update(self, model_manage=None):
        result = super(Model, self).update(model_manage)
        mm = model_manage
        if mm is None and self._mm is not None:
            mm = self._mm
        for schname in self.schemas:
            self.schemas[schname].update(mm)
        return result

    def _action(self, data, slot, index):
        funcname = 'action'
        if slot in self.options.action:
            funcname = self.options.actions[slot]

        func = self.functions[funcname]
        arity = len(getargspec(func).args)
        if arity == 3:
            return [x for x in func(data, slot, index)]
        elif arity == 2:
            return [x for x in func(data, slot)]
        else:
            assert(arity==1)
            return [x for x in func(data)]

    def scoreExplicit(self, inputs):
        slot0 = Slot(0)
        slot0.load(inputs)
        slot1 = Slot(1)
        slot1.reset()
        exec(self._code)

    def score(self, inputs, complete=True, encoding=None, multi_stream=False):
        """
        Scores data using this model.

        :param inputs: The input data. This should be a list of tuples of
            the form [(slot, record_to_score)]. If the element in the list is
            not a tuple or the option multi_stream is set to False, then the
            default slot (0) will be used.

            If recordsets are used, and encoding is set to None, then the
            `record_to_score` should be replaced with an entire dataframe.

        :param complete: A boolean. If True, execute the begin() method at start
            (if defined), and the end() method at finish (if defined).

        :param encoding: How the data is encoded. Valid options are:
            - None: Data is already unpacked into a Python object.
            - 'json': Data encoded as JSON string.

        :param multi_stream: A boolean. If True, model inputs should be a list of
            tuples: [(slot, datum)], and output will be of the same form. If
            False, inputs should just be a list of data: [datum].

        :returns: A dictionary of the output of the various slots of the model.
            If all output comes from slot 1 (the default output slot), will
            return a list instead.
        """

        if self.mtype != 'python' and self.mtype != 'python3':
            raise NotImplementedError("Unable to execute model type {} locally.".format(mtype))

        if complete:
            self._compile(self.source)
            if 'begin' in self._namespace:
                self.functions.begin()

        recordset_buffer = {} # { slot: [inputs] }
        resolved_schemata = {}
        recordset_settings = {}
        record_index = {}

        outputs = []

        for row in inputs:
            if multi_stream and len(row) > 2:
                raise FastScoreError("Unable to process input---Too many fields:" \
                            " {}. Format should be (slot, datum)".format(row))
            slot, datum = None, None
            if multi_stream and len(row) == 2:
                slot, datum = row
            else:
                slot, datum = 0, row

            if slot in record_index:
                record_index[slot] = record_index[slot] + 1
            else:
                record_index[slot] = 1

            schema = None
            if slot in resolved_schemata:
                schema = resolved_schemata[slot]
            else:
                sch_name = None
                if '$all' in self.options.schema:
                    sch_name = self.options.schema['$all']
                else:
                    if '$in' in self.options.schema:
                        sch_name = self.options.schema['$in']
                    else:
                        try:
                            sch_name = self.options.schema[slot]
                        except KeyError:
                            raise FastScoreError("No schema specified for " \
                                "input slot {}".format(slot))
                try:
                    schema = datatype.jsonNodeToAvroType(self.schemas[sch_name].source)
                except KeyError:
                    raise FastScoreError("Model is missing schema: {}," \
                        " try adding it to the model object's schema dictionary.")

            use_recordsets = None
            if slot in recordset_settings:
                use_recordsets = recordset_settings[slot]
            else:
                use_recordsets = False
                if '$all' in self.options.recordsets:
                    if self.options.recordsets['$all'] == 'yes':
                        use_recordsets = True
                else:
                    if '$in' in self.options.recordsets:
                        if self.options.recordsets['$in'] == 'yes':
                            use_recordsets = True
                    if slot in self.options.recordsets:
                        if self.options.recordsets[slot] == 'yes':
                            use_recordsets = True
                recordset_settings[slot] = use_recordsets

            if encoding == 'json':
                if use_recordsets:
                    if json.loads(datum) == {'$fastscore':'set'}:
                        recordset = recordset_from_json(recordset_buffer[slot], schema)
                        recordset_buffer[slot] = []
                        outputs += self._action(recordset, slot, record_index[slot])
                    else:
                        if slot in recordset_buffer:
                            recordset_buffer[slot].append(datum)
                        else:
                            recordset_buffer[slot] = [datum]
                else:
                    data = datatype.jsonDecoder(schema, json.loads(datum))
                    outputs += self._action(data, slot, record_index[slot])
            else:
                if use_recordsets:
                    record_index[slot] += len(datum) - 1
                outputs += self._action(datum, slot, record_index[slot])

        returned_outputs = []
        for row in outputs:
            if type(row) == tuple and len(row) > 2:
                raise FastScoreError("Unable to process output---Too many fields:" \
                            " {}. Format should be (slot, datum)".format(row))
            slot, datum = None, None
            if type(row) == tuple and len(row) == 2:
                slot, datum = row
            else:
                slot, datum = 1, row # default output stream

            schema = None
            if slot in resolved_schemata:
                schema = resolved_schemata[slot]
            else:
                sch_name = None
                if '$all' in self.options.schema:
                    sch_name = self.options.schema['$all']
                else:
                    if '$out' in self.options.schema:
                        sch_name = self.options.schema['$out']
                    else:
                        try:
                            sch_name = self.options.schema[slot]
                        except KeyError:
                            raise FastScoreError("No schema specified for " \
                                "output slot {}".format(slot))
                try:
                    schema = datatype.jsonNodeToAvroType(self.schemas[sch_name].source)
                except KeyError:
                    raise FastScoreError("Model is missing schema: {}," \
                        " try adding it to the model object's schema dictionary.")

            use_recordsets = None
            if slot in recordset_settings:
                use_recordsets = recordset_settings[slot]
            else:
                use_recordsets = False
                if '$all' in self.options.recordsets:
                    if self.options.recordsets['$all'] == 'yes':
                        use_recordsets = True
                else:
                    if '$out' in self.options.recordsets:
                        if self.options.recordsets['$out'] == 'yes':
                            use_recordsets = True
                    if slot in self.options.recordsets:
                        if self.options.recordsets[slot] == 'yes':
                            use_recordsets = True
                recordset_settings[slot] = use_recordsets

            if encoding == 'json':
                if use_recordsets:
                    if multi_stream:
                        returned_outputs += [(slot, x) for x in recordset_to_json(datum, schema)]
                        returned_outputs += [(slot, '{"$fastscore":"set"}')]
                    else:
                        returned_outputs += [x for x in recordset_to_json(datum, schema)]
                        returned_outputs += ['{"$fastscore":"set"}']
                else:
                    if multi_stream:
                        returned_outputs.append((slot, json.dumps(datatype.jsonEncoder(schema, datum))))
                    else:
                        returned_outputs.append(json.dumps(datatype.jsonEncoder(schema, datum)))
            else:
                if multi_stream:
                    returned_outputs += [(slot, datum)]
                else:
                    returned_outputs += [datum]
        if complete:
            if 'end' in self._namespace:
                self.functions.end()

        return returned_outputs

    class Ghost(object): # just used for mocking
        pass

    def deploy(self, engine, streams=None):
        """
        Deploy this model to an engine using the specified streams.
        If `streams` is None, then streams using the REST transport
        will be automatically created.

        :param engine: The Engine instance to use.
        :param streams: A dictionary of fastscore.Stream objects,
                        keyed by the slot to use, e.g.,
                        { 0: input_schema, 1: output_schema}
        """
        progress = Model.Ghost()
        progress.value = 0
        max_progress = 0
        if streams is None:
            max_progress += 3*len(self.options.schema) # create stream, verify, attach
        else:
            max_progress += 2*len(streams) # verify, attach
        max_progress += 2 # verify and load_model

        try:
            get_ipython().__class__.__name__
            from ipywidgets import IntProgress
            from IPython.display import display
            progress = IntProgress(min=0, max=max_progress)
            display(progress)
        except Exception: # we're not in IPython
            pass

        engine.reset() # reset the engine

        self.update()

        try:
            engine.load_model(self, dry_run = True)
            progress.value += 1
        except FastScoreError as e:
            raise FastScoreError("Model load failed.\n{}".format(e))

        streams_dict = {}
        if streams is None: # Then we build the stream_dict ourselves.
            for slot in self.options.schema:
                sch_name = self.options.schema[slot]

                schema = None
                if sch_name in self.schemas:
                    schema = self.schemas[sch_name]
                    schema.update(model_manage=self._mm)
                elif sch_name in self._mm.schemas.names():
                    schema = self._mm.schemas[sch_name]
                else:
                    raise FastScoreError("Unable to find schema: {}".format(sch_name))

                try:
                    index = engine.verify_schema(schema)
                    engine.unverify_schema(index)
                except FastScoreError as e:
                    raise FastScoreError("Error in schema {}: {}".format(schema.name, e))

                stream_desc = {
                    "Transport": {
                        "Type":"REST",
                        "Mode": "chunked" # TODO: change to simple
                    },
                    "Encoding": "json",
                    "Envelope": "delimited", # TODO: change to None
                    "Schema": {"$ref":sch_name}
                }
                if slot in self.options.recordsets:
                    if self.options.recordsets[slot] == 'yes':
                        stream_desc["Batching"] = "explicit"
                if '$all' in self.options.recordsets:
                    if self.options.recordsets['$all'] == 'yes':
                        stream_desc["Batching"] = "explicit"
                if '$in' in self.options.recordsets and slot % 2 == 0:
                    if self.options.recordsets['$in'] == 'yes':
                        stream_desc["Batching"] = "explicit"
                if '$out' in self.options.recordsets and slot % 2 != 0:
                    if self.options.recordsets['$out'] == 'yes':
                        stream_desc["Batching"] = "explicit"
                stream_name = None
                if six.PY2:
                    stream_name = hashlib.md5(json.dumps(stream_desc)).hexdigest()
                else:
                    stream_name = hashlib.md5(json.dumps(stream_desc).encode('utf-8')).hexdigest()
                stream = Stream(stream_name, stream_desc, model_manage = self._mm)
                streams_dict[slot] = stream
                progress.value += 1
        else: # streams was not None.
            streams_dict = streams

        for slot in streams_dict: # Verify and attach each stream.
            stream = streams_dict[slot]
            stream.update(model_manage = self._mm)
            progress.value += 1
            if slot in engine.active_streams:
                engine.active_streams[slot].detach()
            try:
                stream.attach(engine, slot, dry_run = True)
            except FastScoreError as e:
                raise FastScoreError("Unable to attach stream to slot {}.\nReason: {}".format(slot, e.caused_by.body))
            stream.attach(engine, slot)
            progress.value += 1

        engine.load_model(self)
        progress.value += 1
        return
