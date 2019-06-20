################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from __future__ import print_function
from watson_machine_learning_client.libs.repo.mlrepository import MetaNames
from tabulate import tabulate
import copy
from watson_machine_learning_client.wml_resource import WMLResource
from watson_machine_learning_client.utils import STR_TYPE, STR_TYPE_NAME
from watson_machine_learning_client.log_util import get_logger
from watson_machine_learning_client.wml_client_error import WMLClientError
from watson_machine_learning_client.href_definitions import API_VERSION, SPACES,PIPELINES, LIBRARIES, EXPERIMENTS, RUNTIMES, DEPLOYMENTS
import json
logger = get_logger('watson_machine_learning_client.metanames')


class MetaProp:
    def __init__(self, name, key, prop_type, required, example_value, ignored=False, hidden=False, default_value='', schema= '',path=None, transform=lambda x, client: x):
        self.key = key
        self.name = name
        self.prop_type = prop_type
        self.required = required
        self.example_value = example_value
        self.ignored = ignored
        self.hidden = hidden
        self.schema = schema
        self.default_value = default_value
        self.path = path if path is not None else '/' + key
        self.transform = transform


class MetaNamesBase:
    def __init__(self, meta_props_definitions):
        self._meta_props_definitions = meta_props_definitions

    def _validate(self, meta_props):
        for meta_prop in self._meta_props_definitions:
            if meta_prop.ignored is False:
                WMLResource._validate_meta_prop(meta_props, meta_prop.key, meta_prop.prop_type, meta_prop.required)
            else:
              if(meta_prop.key in meta_props):
                logger.warning('\'{}\' meta prop is deprecated. It will be ignored.'.format(meta_prop.name))

    def _check_types_only(self, meta_props):
        for meta_prop in self._meta_props_definitions:
            if meta_prop.ignored is False:
                WMLResource._validate_meta_prop(meta_props, meta_prop.key, meta_prop.prop_type, False)
            else:
              if (meta_prop.key in meta_props):
                logger.warning('\'{}\' meta prop is deprecated. It will be ignored.'.format(meta_prop.name))

    def get(self):
        return sorted(list(map(lambda x: x.name, filter(lambda x: not x.ignored and not x.hidden, self._meta_props_definitions))))

    def show(self):
        print(self._generate_table())

    def _generate_doc_table(self):
        return self._generate_table('MetaName', 'Type', 'Required', 'Default value', 'Schema', 'Example value',
                                    show_examples=True, format='grid', values_format='``{}``')

    def _generate_doc(self, resource_name):
        return """
Set of MetaNames for {}.

Available MetaNames:

{}

""".format(resource_name, MetaNamesBase(self._meta_props_definitions)._generate_doc_table())


    def _generate_table(self, name_label='META_PROP NAME', type_label='TYPE',
                       required_label='REQUIRED', default_value_label='DEFAULT_VALUE',
                       example_value_label='EXAMPLE_VALUE', schema_label='SCHEMA',show_examples=False, format='simple', values_format='{}'):

        show_defaults = any(meta_prop.default_value is not '' for meta_prop in filter(lambda x: not x.ignored and not x.hidden, self._meta_props_definitions))
        show_schema = any(meta_prop.schema is not '' for meta_prop in filter(lambda x: not x.ignored and not x.hidden, self._meta_props_definitions))

        header = [name_label, type_label, required_label]
        if show_schema:
            header.append(schema_label)

        if show_defaults:
            header.append(default_value_label)

        if show_examples:
            header.append(example_value_label)

        table_content = []

        for meta_prop in filter(lambda x: not x.ignored and not x.hidden, self._meta_props_definitions):
            row = [meta_prop.name, meta_prop.prop_type.__name__, u'Y' if meta_prop.required else u'N']

            if show_defaults:
                row.append(values_format.format(meta_prop.default_value) if meta_prop.default_value is not '' else '')

            if show_examples:
                row.append(values_format.format(meta_prop.example_value) if meta_prop.example_value is not '' else '')

            if show_schema:
                row.append(values_format.format(meta_prop.schema) if meta_prop.schema is not '' else '')

            table_content.append(row)

        table = tabulate(
            [header] + table_content,
            tablefmt=format
        )
        return table

    def get_example_values(self):
        return dict((x.key, x.example_value) for x in filter(lambda x: not x.ignored and not x.hidden, self._meta_props_definitions))

    def _generate_resource_metadata(self, meta_props, client=None, with_validation=False, initial_metadata={}):
        if with_validation:
            self._validate(meta_props)

        metadata = copy.deepcopy(initial_metadata)

        def update_map(m, path, el):
            if type(m) is dict:
                if len(path) == 1:
                    m[path[0]] = el
                else:
                    if path[0] not in m:
                        if type(path[1]) is not int:
                            m[path[0]] = {}
                        else:
                            m[path[0]] = []
                    update_map(m[path[0]], path[1:], el)
            elif type(m) is list:
                if len(path) == 1:
                    if len(m) > len(path):
                        m[path[0]] = el
                    else:
                        m.append(el)
                else:
                    if len(m) <= path[0]:
                        m.append({})
                    update_map(m[path[0]], path[1:], el)
            else:
                raise WMLClientError('Unexpected metadata path type: {}'.format(type(m)))


        for meta_prop_def in filter(lambda x: not x.ignored, self._meta_props_definitions):
            if meta_prop_def.key in meta_props:

                path = [int(p) if p.isdigit() else p for p in meta_prop_def.path.split('/')[1:]]

                update_map(
                    metadata,
                    path,
                    meta_prop_def.transform(meta_props[meta_prop_def.key], client)
                )

        return metadata


    def _generate_patch_payload(self, current_metadata, meta_props, client=None, with_validation=False):
        if with_validation:
            self._check_types_only(meta_props)

        updated_metadata = self._generate_resource_metadata(meta_props, client, False, current_metadata)

        patch_payload = []

        def contained_path(metadata, path):
            if path[0] in metadata:
                if len(path) == 1:
                    return [path[0]]
                else:
                    rest_of_path = contained_path(metadata[path[0]], path[1:])
                    if rest_of_path is None:
                        return [path[0]]
                    else:
                        return [path[0]] + rest_of_path
            else:
                return []

        def get_value(metadata, path):
            if len(path) == 1:
                return metadata[path[0]]
            else:
                return get_value(metadata[path[0]], path[1:])

        def already_in_payload(path):
            return any([el['path'] == path for el in patch_payload])

        def update_payload(path):
            existing_path = contained_path(current_metadata, path)

            if len(existing_path) == len(path):
                patch_payload.append({
                    'op': 'replace',
                    'path': '/' + '/'.join(existing_path),
                    'value': get_value(updated_metadata, existing_path)
                })
            else:
                if not already_in_payload(existing_path):
                    patch_payload.append({
                        'op': 'add',
                        'path': '/' + '/'.join(existing_path + [path[len(existing_path)]]),
                        'value': get_value(updated_metadata, existing_path + [path[len(existing_path)]])
                    })

        for meta_prop_def in filter(lambda x: not x.ignored, self._meta_props_definitions):
            if meta_prop_def.key in meta_props:

                path = [int(p) if p.isdigit() else p for p in meta_prop_def.path.split('/')[1:]]

                update_payload(path)

        return patch_payload


class TrainingConfigurationMetaNames(MetaNamesBase):
    TAGS = "tags"
    EXPERIMENT_UID = "experiment_uid"
    PIPELINE_UID = "pipeline_uid"
    TRAINING_LIB = "training_lib"
    PIPELINE_DATA_BINDINGS = "data_bindings"
    PIPELINE_NODE_PARAMETERS = "node_parameters"
    PIPELINE_MODEL_TYPE = "model_type"

    TRAINING_DATA_REFERENCES = "training_data_references"
    TRAINING_RESULTS_REFERENCE = "results_reference"
    _COMPUTE_CONFIGURATION_DEFAULT = u'k80'
    _meta_props_definitions = [
        MetaProp('TRAINING_DATA_REFERENCES',     TRAINING_DATA_REFERENCES,             list,       True,   [{u'connection': {u'endpoint_url': u'https://s3-api.us-geo.objectstorage.softlayer.net',u'access_key_id': u'***',u'secret_access_key': u'***'},u'location': {u'bucket': u'train-data',u'path':u'training_path'},u'type': u's3',u'schema':{u'id':u'1', u'fields': [{u'name': u'x', u'type': u'double', u'nullable': u'False'}]}}] ,schema=[{u'name(optional)': u'string',u'type(required)': u'string',u'connection(required)':{u'endpoint_url(required)': u'string',u'access_key_id(required)':u'string',u'secret_access_key(required)':u'string'},u'location(required)':{u'bucket':u'string',u'path':u'string'},u'schema(optional)':{u'id(required)':u'string',u'fields(required)':[{u'name(required)':u'string',u'type(required)':u'string',u'nullable(optional)':u'string'}]}}]),
        MetaProp('TRAINING_RESULTS_REFERENCE',  TRAINING_RESULTS_REFERENCE,            dict,       True,   {u'connection': {u'endpoint_url': u'https://s3-api.us-geo.objectstorage.softlayer.net',u'access_key_id': u'***',u'secret_access_key': u'***'},u'location': {u'bucket': u'test-results',u'path':u'training_path'},u'type': u's3'},schema={u'name(optional)': u'string',u'type(required)': u'string',u'connection(required)':{u'endpoint_url(required)': u'string',u'access_key_id(required)':u'string',u'secret_access_key(required)':u'string'},u'location(required)':{u'bucket':u'string',u'path':u'string'}}),
        MetaProp('TAGS',                        TAGS                                 , list,       False,  [{u'value': u"string",u"description": u"string"}],schema=[{u'value(required)': u'string',u'description(optional)': u'string'}]),
        MetaProp('PIPELINE_UID',                PIPELINE_UID,                          STR_TYPE,   False, example_value="3c1ce536-20dc-426e-aac7-7284cf3befc6", path="/pipeline/href",transform=lambda x, client: API_VERSION+PIPELINES+"/"+x),
        MetaProp('EXPERIMENT_UID',              EXPERIMENT_UID,                        STR_TYPE,       False, example_value="3c1ce536-20dc-426e-aac7-7284cf3befc6", path="/experiment/href",transform=lambda x, client: API_VERSION + EXPERIMENTS + "/" + x),
        MetaProp('PIPELINE_DATA_BINDINGS',      PIPELINE_DATA_BINDINGS,                STR_TYPE,  False,  path="/pipeline/data_bindings",example_value=[{ "data_reference_name": "string","node_id": "string"}],schema=[{"data_reference_name(required)":"string","node_id(required)":"string"}]),
        MetaProp('PIPELINE_NODE_PARAMETERS',    PIPELINE_NODE_PARAMETERS,              dict,       False,  path="/pipeline/node_parameters",example_value=[{"node_id": "string","parameters": {}}],schema=[{"node_id(required)":"string","parameters(required)":"dict"}] ),
        MetaProp('TRAINING_LIB',                TRAINING_LIB,                          dict,       False, example_value={"href": "/v4/libraries/3c1ce536-20dc-426e-aac7-7284cf3befc6","compute": {"name": "k80","nodes": 0},"runtime": { "href": "/v4/runtimes/3c1ce536-20dc-426e-aac7-7284cf3befc6"},"command": "python3 convolutional_network.py","parameters": {}}, path="/training_lib",schema={"href(required)":"string","type(required)":"string","runtime(optional)":{"href":"string"},"command(optional)":"string","parameters(optional)":"dict"}),
        MetaProp('PIPELINE_MODEL_TYPE',         PIPELINE_MODEL_TYPE,                   str,        False, example_value="tensorflow_1.1.3-py3",path="/pipeline/model_type")
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('trainings')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)


class ExperimentMetaNames(MetaNamesBase):
    NAME = "name"
    DESCRIPTION = "description"
    TAGS = "tags"
    EVALUATION_METHOD = "evaluation_method"
    EVALUATION_METRICS = "evaluation_metrics"
    TRAINING_REFERENCES = "training_references"
    SPACE_UID = "space_uid"
    LABEL_COLUMN = "label_column"
    CUSTOM = "custom"



    _meta_props_definitions = [
        MetaProp('NAME',                            NAME,                           STR_TYPE,   True,     u'Hand-written Digit Recognition'),
        MetaProp('DESCRIPTION',                     DESCRIPTION,                    STR_TYPE,   False,    u'Hand-written Digit Recognition training'),
        MetaProp('TAGS',                            TAGS,                           list,       False,    [{u'value': 'dsx-project.<project-guid>',u'description': 'DSX project guid'}],schema=[{u'value(required)': u'string',u'description(optional)': u'string'}]),
        MetaProp('EVALUATION_METHOD',               EVALUATION_METHOD,              STR_TYPE,   False,    u'multiclass', path="/evaluation_definition/method"),
        MetaProp('EVALUATION_METRICS',              EVALUATION_METRICS,             list,       False,    [{u'name':u'accuracy', u'maximize': False}], path="/evaluation_definition/metrics", schema=[{u'name(required)': u'string', u'maximize(optional)': u'boolean'}]),
        MetaProp('TRAINING_REFERENCES',             TRAINING_REFERENCES,            list,       True,     [{u'pipeline': {u'href': u'/v4/pipelines/6d758251-bb01-4aa5-a7a3-72339e2ff4d8'}}],schema=[{u'pipeline(optional)': {u'href(required)': u'string', u'data_bindings(optional)':[{u'data_reference(required)':u'string', u'node_id(required)':u'string'}], u'nodes_parameters(optional)':[{u'node_id(required)':u'string', u'parameters(required)':u'dict'}]}, u'training_lib(optional)': {u'href(required)': u'string', u'compute(optional)': {u'name(required)': u'string', u'nodes(optional)': u'number'}, u'runtime(optional)': {u'href(required)': u'string'}, u'command(optional)': u'string', u'parameters(optional)':u'dict'}}]),
        MetaProp('SPACE_UID',                       SPACE_UID,                      STR_TYPE,   False,    u'3c1ce536-20dc-426e-aac7-7284cf3befc6', path='/space/href', transform=lambda x, client: API_VERSION + SPACES + "/" + x),
        MetaProp('LABEL_COLUMN',                    LABEL_COLUMN,                   STR_TYPE ,  False,    u'label'),
        MetaProp('CUSTOM',                          CUSTOM,                         dict,       False,     {"field1": "value1"})

    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('experiments')


    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)

class PipelineMetanames(MetaNamesBase):
    NAME = "name"
    DESCRIPTION = "description"
    TAGS = "tags"
    SPACE_UID = "space_url"
    IMPORT = "import"
    DOCUMENT = "document"
    CUSTOM = "custom"
    RUNTIMES = "runtimes"
    COMMAND = "command"
    LIBRARY_UID = "training_lib_href"
    COMPUTE = "compute"

    _meta_props_definitions = [
        MetaProp('NAME',                        NAME,                         STR_TYPE,   True,     u'Hand-written Digit Recognitionu'),
        MetaProp('DESCRIPTION',                 DESCRIPTION,                  STR_TYPE,   False,    u'Hand-written Digit Recognition training'),
        MetaProp('SPACE_UID',                   SPACE_UID,                    STR_TYPE,   False,    u'3c1ce536-20dc-426e-aac7-7284cf3befc6',path="/space/href",transform=lambda x, client: API_VERSION+SPACES+"/"+x),
        MetaProp('TAGS',                        TAGS,                         list,       False,    [{u'value': 'dsx-project.<project-guid>',u'description': 'DSX project guid'}],schema=[{u'value(required)': u'string',u'description(optional)': u'string'}]),
        MetaProp('DOCUMENT',                    DOCUMENT,                     dict,       False,    example_value={"doc_type":"pipeline","version": "2.0","primary_pipeline": "dlaas_only","pipelines": [{"id": "dlaas_only","runtime_ref": "hybrid","nodes": [{"id": "training","type": "model_node","op": "dl_train","runtime_ref": "DL","inputs": [],"outputs": [],"parameters": {"name": "tf-mnist","description": "Simple MNIST model implemented in TF","command": "python3 convolutional_network.py --trainImagesFile ${DATA_DIR}/train-images-idx3-ubyte.gz --trainLabelsFile ${DATA_DIR}/train-labels-idx1-ubyte.gz --testImagesFile ${DATA_DIR}/t10k-images-idx3-ubyte.gz --testLabelsFile ${DATA_DIR}/t10k-labels-idx1-ubyte.gz --learningRate 0.001 --trainingIters 6000","compute": {"name": "k80","nodes": 1},"training_lib_href":"/v4/libraries/64758251-bt01-4aa5-a7ay-72639e2ff4d2/content"},"target_bucket": "wml-dev-results"}]}]},schema={"doc_type(required)":"string","version(required)": "string","primary_pipeline(required)": "string","pipelines(required)": [{"id(required)": "string","runtime_ref(required)": "string","nodes(required)": [{"id": "string","type": "string","inputs": "list","outputs": "list","parameters": {"training_lib_href":"string"}}]}]}),
        MetaProp('CUSTOM',                      CUSTOM,                       dict,       False,    example_value={"field1":"value1"}),
        MetaProp('IMPORT',                      IMPORT,                       dict,       False,    example_value={u'connection': {u'endpoint_url': u'https://s3-api.us-geo.objectstorage.softlayer.net',u'access_key_id': u'***',u'secret_access_key': u'***'},u'location': {u'bucket': u'train-data',u'path':u'training_path'},u'type': u's3'},schema={u'name(optional)': u'string',u'type(required)': u'string',u'connection(required)':{u'endpoint_url(required)': u'string',u'access_key_id(required)':u'string',u'secret_access_key(required)':u'string'},u'location(required)':{u'bucket':u'string',u'path':u'string'}}),
        MetaProp('RUNTIMES',                    RUNTIMES,                     list,       False,    example_value=[{"id":"id","name":"tensorflow","version":"1.13-py3"}]),
        MetaProp('COMMAND',                     COMMAND,                      STR_TYPE,   False,    example_value="convolutional_network.py --trainImagesFile train-images-idx3-ubyte.gz --trainLabelsFile train-labels-idx1-ubyte.gz --testImagesFile t10k-images-idx3-ubyte.gz --testLabelsFile t10k-labels-idx1-ubyte.gz --learningRate 0.001 --trainingIters 6000"),
        MetaProp("LIBRARY_UID",                 LIBRARY_UID,                  STR_TYPE,   False,    example_value="fb9752c9-301a-415d-814f-cf658d7b856a"),
        MetaProp("COMPUTE",                     COMPUTE,                      dict,       False,    example_value={"name":"k80","nodes":1})
        ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('pipelines')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)

class LearningSystemMetaNames(MetaNamesBase):
    _COMPUTE_CONFIGURATION_DEFAULT = 'k80'
    FEEDBACK_DATA_REFERENCE = "feedback_data_reference"
    SPARK_REFERENCE = "spark_instance"
    MIN_FEEDBACK_DATA_SIZE = "min_feedback_data_size"
    AUTO_RETRAIN = "auto_retrain"
    AUTO_REDEPLOY = "auto_redeploy"
    COMPUTE_CONFIGURATION = "compute_configuration"
    TRAINING_RESULTS_REFERENCE = "training_results_reference"

    _meta_props_definitions = [
        MetaProp('FEEDBACK_DATA_REFERENCE', FEEDBACK_DATA_REFERENCE,     dict,       True, example_value={}),
        MetaProp('SPARK_REFERENCE',         SPARK_REFERENCE,             dict,       False, example_value={}),
        MetaProp('MIN_FEEDBACK_DATA_SIZE',  MIN_FEEDBACK_DATA_SIZE,      int,        True, example_value=100),
        MetaProp('AUTO_RETRAIN',            AUTO_RETRAIN,                STR_TYPE,   True, example_value="conditionally"),
        MetaProp('AUTO_REDEPLOY',           AUTO_REDEPLOY,               STR_TYPE,   True, example_value="always"),
        MetaProp('COMPUTE_CONFIGURATION',   COMPUTE_CONFIGURATION,       dict,       False, example_value={u'name': _COMPUTE_CONFIGURATION_DEFAULT}),
        MetaProp('TRAINING_RESULTS_REFERENCE', TRAINING_RESULTS_REFERENCE, dict,        False, example_value={u'connection': {u'endpoint_url': u'https://s3-api.us-geo.objectstorage.softlayer.net', u'access_key_id': u'***', u'secret_access_key': u'***'},u'target': {u'bucket': u'train-data'}, u'type': u's3'}),
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('learning system')


class ModelMetaNames(MetaNamesBase):
    NAME = "name"
    DESCRIPTION = MetaNames.DESCRIPTION
    TRAINING_DATA_REFERENCES = "training_data_references"
    OUTPUT_DATA_SCHEMA = MetaNames.OUTPUT_DATA_SCHEMA
    LABEL_FIELD = MetaNames.LABEL_FIELD
    TRANSFORMED_LABEL_FIELD = MetaNames.TRANSFORMED_LABEL_FIELD
    RUNTIME_UID = "runtime"
    INPUT_DATA_SCHEMA = MetaNames.INPUT_DATA_SCHEMA
    CUSTOM="custom"
    DOMAIN="domain"
    HYPER_PARAMETERS="hyper_parameters"
    TAGS = "tags"
    SPACE_UID = "space"
    PIPELINE_UID = "pipeline"
    RUNTIME_UID = "runtime"
    TYPE="type"
    SIZE="size"
    IMPORT = "import"
    TRAINING_LIB_UID = "training_lib"
    METRICS="metrics"

    _meta_props_definitions = [
        MetaProp('NAME',                    NAME,                        STR_TYPE,   True,   "my_model"),
        MetaProp('DESCRIPTION',             DESCRIPTION,                 STR_TYPE,   False,  "my_description", path="/description"),
        MetaProp('INPUT_DATA_SCHEMA',       INPUT_DATA_SCHEMA,           dict,       False,  example_value={"id":"1","type": "struct", "fields": [{"name": "x", "type": "double", "nullable": False, "metadata": {}}, {"name": "y", "type": "double", "nullable": False, "metadata": {}}]}, path="/input_data_schema",schema={u'id(required)':u'string',u'fields(required)':[{u'name(required)':u'string',u'type(required)':u'string',u'nullable(optional)':u'string'}]}),
        MetaProp('TRAINING_DATA_REFERENCES',TRAINING_DATA_REFERENCES,     list,       False,  [], path="/training_data_references",schema=[{"name(optional)":"string","type(required)":"string",u'connection(required)':{u'endpoint_url(required)': u'string',u'access_key_id(required)':u'string',u'secret_access_key(required)':u'string'},u'location(required)':{u'bucket':u'string',u'path':u'string'},u'schema(optional)':{u'id(required)':u'string',u'fields(required)':[{u'name(required)':u'string',u'type(required)':u'string',u'nullable(optional)':u'string'}]}}]),
        MetaProp('OUTPUT_DATA_SCHEMA',      OUTPUT_DATA_SCHEMA,          dict,       False,  example_value={"id":"1","type": "struct", "fields": [{"name": "x", "type": "double", "nullable": False, "metadata": {}}, {"name": "y", "type": "double", "nullable": False, "metadata": {}}]}, path="/output_data_schema",schema={u'id(required)':u'string',u'fields(required)':[{u'name(required)':u'string',u'type(required)':u'string',u'nullable(optional)':u'string'}]}),
        MetaProp('LABEL_FIELD',             LABEL_FIELD,                 STR_TYPE,   False,  example_value='PRODUCT_LINE', path="/label_column"),
        MetaProp('TRANSFORMED_LABEL_FIELD', TRANSFORMED_LABEL_FIELD,     STR_TYPE,   False,  example_value='PRODUCT_LINE_IX', path="/transformed_label"),
        MetaProp('RUNTIME_UID',             RUNTIME_UID,                 STR_TYPE,   False,  example_value='53628d69-ced9-4f43-a8cd-9954344039a8', path="/runtime/href", transform=lambda x, client: API_VERSION+RUNTIMES+"/"+x),
        MetaProp('TAGS',                    TAGS,                        list,       False,  example_value=[{"value": "string","description": "string"}],schema=[{u'value(required)': u'string',u'description(optional)': u'string'}]),
        MetaProp('SIZE',                    SIZE,                        dict,       False, example_value={"in_memory": 0,"content": 0},schema={u'in_memory(optional)': u'string', u'content(optional)': u'string'}),
        MetaProp('SPACE_UID',                   SPACE_UID,                       STR_TYPE,   False,  example_value="53628d69-ced9-4f43-a8cd-9954344039a8", path="/space/href"),
        MetaProp('PIPELINE_UID',                PIPELINE_UID,                    STR_TYPE,   False,  example_value="53628d69-ced9-4f43-a8cd-9954344039a8", path="/pipeline/href"),
        MetaProp('RUNTIME_UID',                 RUNTIME_UID,                     STR_TYPE,   True,  example_value="53628d69-ced9-4f43-a8cd-9954344039a8", path="/runtime/href"),
        MetaProp('TYPE',                    TYPE,                        STR_TYPE,   True,  example_value="mllib_2.1", path="/type"),
        MetaProp('CUSTOM',                  CUSTOM ,                      dict,     False, example_value={}),
        MetaProp('DOMAIN',                  DOMAIN,                       STR_TYPE, False, example_value="Watson Machine Learning"),
        MetaProp('HYPER_PARAMETERS', HYPER_PARAMETERS,                    dict, False, example_value=""),
        MetaProp('METRICS',                 METRICS,                      list, False, example_value=""),
        MetaProp('IMPORT',                  IMPORT,                       dict,       False,  example_value={u'connection': {u'endpoint_url': u'https://s3-api.us-geo.objectstorage.softlayer.net',u'access_key_id': u'***',u'secret_access_key': u'***'},u'location': {u'bucket': u'train-data',u'path':u'training_path'},u'type': u's3'},schema={u'name(optional)': u'string',u'type(required)': u'string',u'connection(required)':{u'endpoint_url(required)': u'string',u'access_key_id(required)':u'string',u'secret_access_key(required)':u'string'},u'location(required)':{u'bucket':u'string',u'path':u'string'}}),
        MetaProp('TRAINING_LIB_UID',            TRAINING_LIB_UID,                STR_TYPE,       False,  example_value="53628d69-ced9-4f43-a8cd-9954344039a8", path="/training_lib")
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('models')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)


class PayloadLoggingMetaNames(MetaNamesBase):
    PAYLOAD_DATA_REFERENCE = "payload_store"
    LABELS = "labels"
    OUTPUT_DATA_SCHEMA = "output_data_schema"

    _meta_props_definitions = [
        MetaProp('PAYLOAD_DATA_REFERENCE',  PAYLOAD_DATA_REFERENCE,       dict, True,     {}),
        MetaProp('LABELS',                  LABELS,              list, False,    ['a', 'b', 'c']),
        MetaProp('OUTPUT_DATA_SCHEMA',      OUTPUT_DATA_SCHEMA,  dict, False,    {})
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('payload logging system')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)


class FunctionMetaNames(MetaNamesBase):
    NAME = "name"
    DESCRIPTION = "description"
    RUNTIME_UID = "runtime_uid"
    INPUT_DATA_SCHEMAS = "input_data_schemas"
    OUTPUT_DATA_SCHEMAS = "output_data_schemas"
    TAGS = "tags"
    SPACE_UID = "space_uid"
    TYPE = "type"
    CUSTOM="custom"
    SAMPLE_SCORING_INPUT="sample_scoring_input"

    _meta_props_definitions = [
        MetaProp('NAME',                NAME,                STR_TYPE,   True,   "ai_function"),
        MetaProp('DESCRIPTION',         DESCRIPTION,         STR_TYPE,   False,  "This is ai function"),
        MetaProp('RUNTIME_UID',         RUNTIME_UID,         STR_TYPE,   False,  '53628d69-ced9-4f43-a8cd-9954344039a8', path="/runtime/href", transform=lambda x, client: API_VERSION+RUNTIMES+"/"+x),
        MetaProp('INPUT_DATA_SCHEMAS',  INPUT_DATA_SCHEMAS,  list,       False,  [{"id":"1","type": "struct", "fields": [{"name": "x", "type": "double", "nullable": False, "metadata": {}}, {"name": "y", "type": "double", "nullable": False, "metadata": {}}]}],schema=[{u'id(required)':u'string',u'fields(required)':[{u'name(required)':u'string',u'type(required)':u'string',u'nullable(optional)':u'string'}]}]),
        MetaProp('OUTPUT_DATA_SCHEMAS', OUTPUT_DATA_SCHEMAS, list,       False,  [{"id":"1","type": "struct", "fields": [{"name": "multiplication", "type": "double", "nullable": False, "metadata": {}}]}],schema=[{u'id(required)':u'string',u'fields(required)':[{u'name(required)':u'string',u'type(required)':u'string',u'nullable(optional)':u'string'}]}]),
        MetaProp('TAGS',                TAGS,                list,       False,  [{"value": "ProjectA", "description": "Functions created for ProjectA"}],schema=[{u'value(required)': u'string',u'description(optional)': u'string'}]),
        MetaProp('TYPE',                TYPE,                STR_TYPE,   False,  u'python'),
        MetaProp('CUSTOM',              CUSTOM,              dict,       False,  example_value=u'{}'),
        MetaProp('SAMPLE_SCORING_INPUT', SAMPLE_SCORING_INPUT, list,     False,  example_value={ "input_data": [ { "fields": [ "name",  "age", "occupation" ], "values": [ [ "john",23, "student"], [ "paul", 33, "engineer" ]] }]},schema={"id(optional)":"string","fields(optional)":"array","values(optional)":"array"}),
        MetaProp('SPACE_UID',           SPACE_UID,           STR_TYPE,   False,  u'3628d69-ced9-4f43-a8cd-9954344039a8',path="/space/href",transform=lambda x, client: API_VERSION+SPACES+"/"+x)
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('AI functions')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)


class ScoringMetaNames(MetaNamesBase):
    INPUT_DATA = "scoring_input_data"
    INPUT_DATA_REFERENCES = "scoring_input_data_references"
    OUTPUT_DATA_REFERENCE = "scoring_output_data_references"
    COMPUTE_METRICS = "scoring_compute_metrics"

    _meta_props_definitions = [
        MetaProp('INPUT_DATA',INPUT_DATA,list,False,  path="/scoring/input_data",example_value=[{"fields": ["name","age","occupation"],"values": [["john",23,"student"]]}], schema=[{"name(optional)":"string","id(optional)":"string","fields(optional)":"array[string]","values":"array[array[string]]"}]),
        MetaProp('INPUT_DATA_REFERENCES',         INPUT_DATA_REFERENCES,         list,   False,example_value = "",path="/scoring/input_data_references",schema=[{"id(optional)":"string","name(optional)":"string","type(required)":"string",u'connection(required)':{u'endpoint_url(required)': u'string',u'access_key_id(required)':u'string',u'secret_access_key(required)':u'string'},u'location(required)':{u'bucket':u'string',u'path':u'string'},u'schema(optional)':{u'id(required)':u'string',u'fields(required)':[{u'name(required)':u'string',u'type(required)':u'string',u'nullable(optional)':u'string'}]}}]),
        MetaProp('OUTPUT_DATA_REFERENCE',         OUTPUT_DATA_REFERENCE,         dict,   False, example_value = "",path="/scoring/output_data_reference", schema={"name(optional)":"string","type(required)":"string",u'connection(required)':{u'endpoint_url(required)': u'string',u'access_key_id(required)':u'string',u'secret_access_key(required)':u'string'},u'location(required)':{u'bucket':u'string',u'path':u'string'},u'schema(optional)':{u'id(required)':u'string',u'fields(required)':[{u'name(required)':u'string',u'type(required)':u'string',u'nullable(optional)':u'string'}]}}),
        MetaProp('COMPUTE_METRICS',  COMPUTE_METRICS,  list,       False,  path="/scoring/compute_metrics",example_value=["auroc","accuracy"]),
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('Scoring')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)


class DecisionOptimizationMetaNames(MetaNamesBase):
    INPUT_DATA = "do_input_data"
    INPUT_DATA_REFERENCES = "do_input_data_references"
    OUTPUT_DATA = "do_output_data"
    OUTPUT_DATA_REFERENCES = "do_output_data_references"
    SOLVE_PARAMETERS = "do_solve_parameters"

    _meta_props_definitions = [
        MetaProp('INPUT_DATA', INPUT_DATA,     list,       False,path="/decision_optimization/input_data",  example_value=[{"fields": ["name","age","occupation"],"values": [["john",23,"student"]]}], schema=[{"name(optional)":"string","id(optional)":"string","fields(optional)":"array[string]","values":"array[array[string]]"}]),
        MetaProp('INPUT_DATA_REFERENCES', INPUT_DATA_REFERENCES,                list,       False,path="/decision_optimization/input_data_references",  example_value=[{"fields": ["name","age","occupation"],"values": [["john",23,"student"]]}], schema=[{"name(optional)":"string","id(optional)":"string","fields(optional)":"array[string]","values":"array[array[string]]"}]),
        MetaProp('OUTPUT_DATA', OUTPUT_DATA,                list,   False,example_value="",path="/decision_optimization/output_data",  schema=[{"name(optional)": "string"}]),
        MetaProp('OUTPUT_DATA_REFERENCES', OUTPUT_DATA_REFERENCES, list, False,example_value="",path="/decision_optimization/output_data_references",  schema={"name(optional)":"string","type(required)":"string",u'connection(required)':{u'endpoint_url(required)': u'string',u'access_key_id(required)':u'string',u'secret_access_key(required)':u'string'},u'location(required)':{u'bucket':u'string',u'path':u'string'},u'schema(optional)':{u'id(required)':u'string',u'fields(required)':[{u'name(required)':u'string',u'type(required)':u'string',u'nullable(optional)':u'string'}]}}),
        MetaProp('SOLVE_PARAMETERS', SOLVE_PARAMETERS, dict,     False, example_value="",path="/decision_optimization/solve_parameters")
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('Decision Optimization')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)


class RuntimeMetaNames(MetaNamesBase):
    NAME = "name"
    DESCRIPTION = "description"
    CUSTOM = "custom"
    PLATFORM = "platform"
    LIBRARIES_UIDS = "libraries_uids"
    CONFIGURATION_FILEPATH = "configuration_filepath"
    TAGS = "tags"
    SPACE_UID = "space"
    COMPUTE = "compute"

    _meta_props_definitions = [
        MetaProp('NAME',                            NAME,                            STR_TYPE,   True,   "runtime_spec_python_3.5"),
        MetaProp('DESCRIPTION',                     DESCRIPTION,                     STR_TYPE,   False,  "sample runtime"),
        MetaProp('PLATFORM',                        PLATFORM,                        dict,   True,   u'{"name":python","version":"3.5")',schema={"name(required)":"string","version(required)":"version"}),
        MetaProp('LIBRARIES_UIDS',                  LIBRARIES_UIDS,                  list, False,   ["46dc9cf1-252f-424b-b52d-5cdd9814987f"]),
        MetaProp('CONFIGURATION_FILEPATH',          CONFIGURATION_FILEPATH,          STR_TYPE,   False,   "/home/env_config.yaml"),
        MetaProp('TAGS',                            TAGS,                            list,       False,   [{u'value': 'dsx-project.<project-guid>',u'description': 'DSX project guid'}],schema=[{u'value(required)': u'string',u'description(optional)': u'string'}]),
        MetaProp('CUSTOM',                          CUSTOM,                          dict,       False,   u'{"field1": "value1"}'),
        MetaProp('SPACE_UID',                       SPACE_UID,                       STR_TYPE,   False,   path="/space/href",example_value="46dc9cf1-252f-424b-b52d-5cdd9814987f",transform=lambda x, client:API_VERSION+SPACES+"/"+x),
        MetaProp('COMPUTE',                         COMPUTE,                         dict,       False,   example_value={"name":"name1", "nodes": 1},schema={"name(required)":"string","nodes(optional)":"string"})

    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('Runtime Specs')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)


class LibraryMetaNames(MetaNamesBase):
    NAME = "name"
    DESCRIPTION = "description"
    FILEPATH = "filepath"
    VERSION = "version"
    PLATFORM = "platform"
    TAGS = "tags"
    SPACE_UID = "space_uid"
    MODEL_DEFINITION = "model_definition"
    CUSTOM = "custom"
    COMMAND = "command"


    _meta_props_definitions = [
        MetaProp('NAME',                NAME,             STR_TYPE,   True,     "my_lib"),
        MetaProp('DESCRIPTION',         DESCRIPTION,      STR_TYPE,   False,    "my lib"),
        MetaProp('PLATFORM',            PLATFORM,         dict,       True,     {"name": "python", "versions": ["3.5"]},schema={"name(required)":"string","version(required)":"version"}),
        MetaProp('VERSION',             VERSION,          STR_TYPE,   True,     "1.0"),
        MetaProp('FILEPATH',            FILEPATH,         STR_TYPE,   True,     "/home/user/my_lib_1_0.zip"),
        MetaProp('TAGS',                TAGS,             dict,       False,    [{u'value': 'dsx-project.<project-guid>',u'description': 'DSX project guid'}],schema=[{u'value(required)': u'string',u'description(optional)': u'string'}]),
        MetaProp('SPACE_UID',           SPACE_UID,        STR_TYPE,   False,    u'3c1ce536-20dc-426e-aac7-7284cf3befc6', path='/space/href', transform=lambda x, client: API_VERSION+SPACES+"/"+x),
        MetaProp('MODEL_DEFINITION',    MODEL_DEFINITION, bool,       False,     False),
        MetaProp('COMMAND',             COMMAND,          STR_TYPE,   False,     u'command'),
        MetaProp('CUSTOM',              CUSTOM,           dict,       False,     {"field1": "value1"})


    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('Custom Libraries')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)

class SpacesMetaNames(MetaNamesBase):
    TAGS = "tags"
    CUSTOM = "custom"
    NAME = "name"
    DESCRIPTION = "description"
    ONLINE_DEPLOYMENTS = "online_deployments"
    SCHEDULES = "schedules"

    _meta_props_definitions = [
        MetaProp('NAME',                        NAME,               STR_TYPE, True,   "my_space"),
        MetaProp('TAGS', TAGS, list, False, [{u'value': 'dsx-project.<project-guid>',u'description': 'DSX project guid'}],schema=[{u'value(required)': u'string',u'description(optional)': u'string'}]),
        MetaProp('CUSTOM', CUSTOM, dict, False, '{"field1":"value1"}'),
        MetaProp('DESCRIPTION',                DESCRIPTION,         STR_TYPE, False,  "my_description"),
        MetaProp('ONLINE_DEPLOYMENTS',         ONLINE_DEPLOYMENTS,  list,     False,  [{}], path="/deployment_descriptor/online_deployments", schema=[{u'name(optional)': u'string',u'description(optional)': u'string', u'guid(optional)': u'string', u'compute(optional)': {u'name(required)': u'string', u'nodes(optional)': u'number'}}]),
        MetaProp('SCHEDULES',                  SCHEDULES,           list,     False,  [{}],path="/deployment_descriptor/schedules", schema=[{u'cron(optional)': u'string', u'assets(optional)': [{u'name(optional)': u'string', u'description(optional)': u'string', u'guid(optional)': u'string', u'compute(optional)': {u'name(required)': u'string', u'nodes(optional)': u'number'}}]}]),
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('Spaces Specs')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)
class DeploymentMetaNames(MetaNamesBase):
    NAME = "name"
    TAGS = "tags"
    DESCRIPTION = "description"
    #ENVIRONMENTS = "environments"
    CUSTOM = "custom"
    AUTO_REDEPLOY = "auto_redeploy"
    COMPUTE = "compute"
    ONLINE = "online"
    BATCH = "batch"
    VIRTUAL = "virtual"
    # VIRTUAL = "virtual"

    _meta_props_definitions = [
        MetaProp('NAME',             NAME,          STR_TYPE,   False, 'my_deployment'),
        MetaProp('TAGS',             TAGS,          list,       False, [{u'value': 'dsx-project.<project-guid>',u'description': 'DSX project guid'}],schema=[{u'value(required)': u'string',u'description(optional)': u'string'}]),
        MetaProp('DESCRIPTION',      DESCRIPTION,   STR_TYPE,   False, 'my_deployment'),
        #MetaProp('ENVIRONMENTS',     ENVIRONMENTS,  list,       False,  ['dev', 'staging']),
        MetaProp('CUSTOM',           CUSTOM,        dict,       False,  {}),
        MetaProp('AUTO_REDEPLOY',    AUTO_REDEPLOY, bool,       False,  False),
        MetaProp('COMPUTE', COMPUTE, dict, example_value=None,required=False),
        MetaProp('ONLINE', ONLINE, dict, example_value={}, required=False),
        MetaProp('BATCH', BATCH, dict, example_value={}, required=False),
        MetaProp('VIRTUAL', VIRTUAL, dict, example_value={}, required=False),
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('Deployments Specs')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)

# class EnvironmentMetaNames(MetaNamesBase):
#     NAME = "name"
#     DESCRIPTION = "description"
#     BASE_URL = "base_url"
#     # VIRTUAL = "virtual"
#
#     _meta_props_definitions = [
#         MetaProp('NAME',             NAME,          STR_TYPE,   False, 'my_deployment'),
#         MetaProp('DESCRIPTION',      DESCRIPTION,   STR_TYPE,   False, 'my_deployment'),
#         MetaProp('BASE_URL', BASE_URL, STR_TYPE, False)
#     ]
#
#     __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('Environment Specs')
#
#     def __init__(self):
#         MetaNamesBase.__init__(self, self._meta_props_definitions)
