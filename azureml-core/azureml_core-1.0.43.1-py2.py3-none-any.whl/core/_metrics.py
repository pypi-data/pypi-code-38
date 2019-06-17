# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import io
import imghdr
import logging
import json
import six
import sys
import time

from azureml.exceptions import AzureMLException, UserErrorException
from azureml._logging.chained_identity import ChainedIdentity
from azureml._restclient.contracts.utils import get_new_id, get_timestamp
from azureml._restclient.constants import RUN_ORIGIN
from azureml._restclient.models.metric_schema_dto import MetricSchemaDto
from azureml._restclient.models.metric_schema_property_dto import MetricSchemaPropertyDto
from azureml._restclient.models.run_metric_dto import RunMetricDto
from azureml._restclient.models.metric_dto import MetricDto

module_logger = logging.getLogger(__name__)

AZUREML_BOOL_METRIC_TYPE = "bool"
AZUREML_FLOAT_METRIC_TYPE = "float"
AZUREML_INT_METRIC_TYPE = "int"
AZUREML_NULL_METRIC_TYPE = "none"
AZUREML_STRING_METRIC_TYPE = "string"
AZUREML_DOUBLE_METRIC_TYPE = "double"

# INLINE METRICS
AZUREML_SCALAR_METRIC_TYPE = "azureml.v1.scalar"
AZUREML_LIST_METRIC_TYPE = "azureml.v1.list"
AZUREML_TABLE_METRIC_TYPE = "azureml.v1.table"

INLINE_METRICS = [
    AZUREML_SCALAR_METRIC_TYPE,
    AZUREML_LIST_METRIC_TYPE,
    AZUREML_TABLE_METRIC_TYPE
]

# OLD ARTIFACT-BACKED METRICS
AZUREML_OLD_IMAGE_METRIC_TYPE = "azureml.v1.image"
AZUREML_OLD_CONFUSION_MATRIX_METRIC_TYPE = "azureml.v1.confusion_matrix"
AZUREML_OLD_ACCURACY_TABLE_METRIC_TYPE = "azureml.v1.accuracy_table"
AZUREML_OLD_RESIDUALS_METRIC_TYPE = "azureml.v1.residuals"
AZUREML_OLD_PREDICTIONS_METRIC_TYPE = "azureml.v1.predictions"

OLD_JSON_METRICS = [
    AZUREML_OLD_ACCURACY_TABLE_METRIC_TYPE,
    AZUREML_OLD_CONFUSION_MATRIX_METRIC_TYPE,
    AZUREML_OLD_RESIDUALS_METRIC_TYPE,
    AZUREML_OLD_PREDICTIONS_METRIC_TYPE
]

# NEW ARTIFACT-BACKED METRICS
AZUREML_IMAGE_METRIC_TYPE = "azureml.v2.image"
AZUREML_CONFUSION_MATRIX_METRIC_TYPE = "azureml.v2.confusion_matrix"
AZUREML_ACCURACY_TABLE_METRIC_TYPE = "azureml.v2.accuracy_table"
AZUREML_RESIDUALS_METRIC_TYPE = "azureml.v2.residuals"
AZUREML_PREDICTIONS_METRIC_TYPE = "azureml.v2.predictions"

ARTIFACT_ID_PREFIX = "aml://artifactId/"

AZUREML_MAX_NUMBER_SIZE_IN_BITS = 64

_metric_type_initializers = {}


class Artifact(object):
    def __init__(self, data_location, filename=None, data=None,
                 metric_type=None, _is_image_metric=False, data_container=None):
        data_location = Artifact._correct_data_location(data_location, metric_type, data_container)
        origin, container, path = Artifact.parse_data_location(data_location)
        self.filename = filename if filename is not None else path
        self.data = data
        self.data_location = data_location
        self.metric_type = metric_type
        self._is_image_metric = _is_image_metric
        self.origin = origin
        self.container = container
        self.path = path

    def convert_to_object(self):
        if self._is_image_metric:
            raise UserErrorException("Cannot convert byte string of image to another object." +
                                     "Write the bytes to a file.")
        try:
            decoded_data = self.data.decode("utf-8")
            return json.loads(decoded_data)
        except json.decoder.JSONDecodeError as e:
            module_logger.debug("Unable to decode metric artifact: {}".format(e))

    def retrieve_artifact(self, artifact_client):
        if self.data is None:
            self.data = artifact_client.download_artifact_contents_to_bytes(self.origin, self.container, self.path)

    def __repr__(self):
        # Shouldn't dump the entire byte string of the artifact if it already has been retrieved
        # but somehow notify users the data is there TODO
        artifact_repr = "Artifact(data_location={0}, filename={1}, metric_type={2})".format(self.data_location,
                                                                                            self.filename,
                                                                                            self.metric_type)
        return artifact_repr

    @staticmethod
    def parse_data_location(data_location):
        # data location strings are of the format aml://artifactId/{origin}/{container}/{path}
        artifact_id = data_location[len(ARTIFACT_ID_PREFIX):]
        parsed_artifact_id = artifact_id.split("/")

        origin = parsed_artifact_id[0]
        container = parsed_artifact_id[1]
        path = "/".join(parsed_artifact_id[2:])

        return origin, container, path

    @staticmethod
    def _correct_data_location(data_location, metric_type, data_container=""):
        if metric_type not in (OLD_JSON_METRICS + [AZUREML_OLD_IMAGE_METRIC_TYPE]):
            return data_location

        artifact_id = data_location[len(ARTIFACT_ID_PREFIX):]
        # v1 image artifacts have the following incorrect form: aml://artifactId/{path}
        if metric_type == AZUREML_OLD_IMAGE_METRIC_TYPE:
            origin = RUN_ORIGIN
            container = data_container
            path = artifact_id
        # v1 JSON Metrics have an unncessary outputs in front of the path
        # format: aml://artifactId/{origin}/{container}/outputs/{path}
        elif metric_type in OLD_JSON_METRICS:
            parsed_artifact_id = artifact_id.split("/")
            origin = parsed_artifact_id[0]
            container = parsed_artifact_id[1]
            path = "/".join(parsed_artifact_id[3:])
        return ARTIFACT_ID_PREFIX + "{}/{}/{}".format(origin, container, path)

    @staticmethod
    def create_unpopulated_artifact_from_data_location(data_location, metric_type,
                                                       _is_image_metric=False, data_container=None):
        return Artifact(data_location=data_location, metric_type=metric_type,
                        _is_image_metric=_is_image_metric, data_container=data_container)


class Metric(ChainedIdentity):

    _type_to_metric_type = {float: AZUREML_FLOAT_METRIC_TYPE,
                            str: AZUREML_STRING_METRIC_TYPE,
                            bool: AZUREML_BOOL_METRIC_TYPE,
                            type(None): AZUREML_NULL_METRIC_TYPE}

    for integer_type in six.integer_types:
        _type_to_metric_type[integer_type] = AZUREML_INT_METRIC_TYPE

    _type_to_converter = {}
    try:
        import numpy as np

        try:
            # Add boolean type support
            _type_to_converter[np.bool_] = bool
        except AttributeError:
            module_logger.debug("numpy.bool_ is unsupported")

        # Add str type support
        _type_to_converter[np.unicode_] = str

        # Add int type support
        numpy_ints = [np.int0, np.int8, np.int16, np.int16, np.int32]
        numpy_unsigned_ints = [np.uint0, np.uint8, np.uint8, np.uint16, np.uint32]

        for numpy_int_type in numpy_ints + numpy_unsigned_ints:
            _type_to_converter[numpy_int_type] = int

        # Add float type support
        numpy_floats = [np.float16, np.float32, np.float64]

        for numpy_float_type in numpy_floats:
            _type_to_converter[numpy_float_type] = float

        try:
            # Support large float as string
            _type_to_converter[np.float128] = repr
        except AttributeError:
            module_logger.debug("numpy.float128 is unsupported, expected for windows")
    except ImportError:
        module_logger.debug("Unable to import numpy, numpy typed metrics unsupported")

    def __init__(self, name, value, data_location=None, description="", **kwargs):
        super(Metric, self).__init__(**kwargs)
        self.name = name
        self.value = value
        self.data_location = data_location
        self.description = description
        self.metric_type = "vienna.custom"

    def to_cells(self):
        raise NotImplementedError()

    @staticmethod
    def create_metric(name, value, metric_type, data_location=None, description=""):
        if metric_type not in _metric_type_initializers:
            raise UserErrorException("Unsupported metric type")

        return _metric_type_initializers[metric_type](name, value, data_location=data_location,
                                                      description=description)

    @classmethod
    def get_converted_value(cls, value):
        """return supported metrics value, otherwise, convert to string"""
        value_type = type(value)
        if value_type in cls._type_to_metric_type:
            return value
        else:
            converter = cls._type_to_converter.get(value_type, repr)
            return converter(value)

    def create_run_metric_dto(self, run_id):
        """create a new run_metric Dto"""
        # Load cells and handle list vs non list cells
        value = self.to_cells()
        num_cells, cells = (len(value), value) if isinstance(value, list) else (1, [value])
        seen = set()
        properties = []
        for cell in cells:
            for key in cell:
                if key not in seen:
                    val = cell[key]
                    properties.append(Metric.get_value_property(self.name, val, key))
                    seen.add(key)

        metrics_schema_dto = MetricSchemaDto(num_properties=len(properties),
                                             properties=properties)
        run_metric_dto = RunMetricDto(run_id=run_id,
                                      metric_id=get_new_id(),
                                      metric_type=self.metric_type,
                                      created_utc=get_timestamp(),
                                      name=self.name,
                                      description=self.description,
                                      num_cells=num_cells,
                                      cells=cells,
                                      schema=metrics_schema_dto,
                                      data_location=self.data_location)
        return run_metric_dto

    def create_metric_dto(self):
        """create a new metric dto"""
        # Load cells and handle list vs non list cells
        value = self.to_cells()
        num_cells, cells = (len(value), value) if isinstance(value, list) else (1, [value])
        seen = set()
        properties = []
        for cell in cells:
            for key in cell:
                if key not in seen:
                    val = cell[key]
                    properties.append(Metric.get_value_property(self.name, val, key))
                    seen.add(key)

        metrics_schema_dto = MetricSchemaDto(num_properties=len(properties),
                                             properties=properties)
        metric_dto = MetricDto(metric_id=get_new_id(),
                               metric_type=self.metric_type,
                               created_utc=get_timestamp(),
                               name=self.name,
                               description=self.description,
                               num_cells=num_cells,
                               cells=cells,
                               schema=metrics_schema_dto,
                               data_location=self.data_location)
        return metric_dto

    @staticmethod
    def get_value_property(name, value, property_id=None):
        """get metrics value property"""
        property_id = property_id if property_id else name
        prop = MetricSchemaPropertyDto(property_id=property_id,
                                       name=name,
                                       type=Metric.get_azureml_type(value))
        return prop

    @staticmethod
    def get_azureml_type(value):
        """get metrics type"""
        return Metric._type_to_metric_type.get(type(value), "string")


class InlineMetric(Metric):
    def __init__(self, name, value, data_location=None, description=""):
        super(InlineMetric, self).__init__(name, value, data_location=data_location, description=description)

    def to_cells(self):
        """return metrics cell as list of dictionary"""
        keys, values = self.generate_keys_and_values()
        cells = []
        seen_keys = set()
        message = ""
        warning_message = ""
        for key, value in zip(keys, values):
            converted_value = Metric.get_converted_value(value)
            if key not in seen_keys and type(value) != type(converted_value):
                message_line = "Converted key {0} of value {1} to {2}.\n".format(
                    key, value, converted_value)
                if not isinstance(value, str) and isinstance(converted_value, str):
                    warning_message += message_line
                else:
                    message += message_line
                seen_keys.add(key)
            cells.append({key: converted_value})

        if message:
            module_logger.debug(message)
        if warning_message:
            module_logger.warning(warning_message)
        return cells

    def generate_keys_and_values(self):
        raise NotImplementedError()

    @staticmethod
    def add_cells(name, out, table_cell_types, cells, cell_types):
        """add new cells"""
        for cell in cells:
            for key in cell:
                var = cell[key]
                cell_type = cell_types[key].lower()
                if key not in table_cell_types:
                    table_cell_types = cell_types[key]

                if key in out:
                    out[key] = out[key] if isinstance(out[key], list) else [out[key]]

                if cell_type != table_cell_types[key]:
                    module_logger.debug("Invalid type for metric name {}, type: "
                                        "{}, expected: {} appending None instead.".format(name,
                                                                                          cell_type,
                                                                                          table_cell_types[key]))
                    out[key].append(None)
                elif key not in out:
                    if cell_type == AZUREML_FLOAT_METRIC_TYPE or cell_type == AZUREML_DOUBLE_METRIC_TYPE:
                        var = float(var)
                    out[key] = var
                else:
                    out[key].append(var)

    @staticmethod
    def add_table(name, out, table_column_types, cells, cell_types):
        """add a new table"""
        if name in out:
            table_out = out[name]
        else:
            out[name] = {}
            table_out = out[name]

        existing_columns = table_out.keys()

        # TODO find simpler way to do this
        table_length = 0
        for key in existing_columns:
            value = table_out[key]
            table_length = len(value) if isinstance(value, list) else 1
            break

        #  Fill new columns with None
        if table_length != 0:
            for col in cell_types:
                if col not in table_out:
                    table_out[col] = table_length * [None]

        #  Add column type for new columns to known
        for col in cell_types:
            if col not in table_column_types:
                table_column_types[col] = cell_types[col]

        table_to_add = {}
        InlineMetric.add_cells(name, table_to_add, table_column_types, cells, cell_types)

        #  Check for table size invariant, columns must be of the same length
        length = None
        for key in table_to_add:
            values = table_to_add[key]
            current_length = len(values) if isinstance(values, list) else 1
            if length is None:
                length = current_length
            else:
                if length != current_length:
                    module_logger.warning("Invalid table, mixmatched column sizes, column of length {} "
                                          ", expected length {}".format(current_length, length))

        #  Fill missing columns with None
        for col in existing_columns:
            if col not in table_to_add:
                table_to_add[col] = length * [None]

        #  Extend table out
        for key in table_to_add:
            to_add = table_to_add[key]
            if key not in table_out:
                table_out[key] = to_add
            elif isinstance(to_add, list):
                table_out[key].extend(to_add)
            else:
                if not isinstance(table_out[key], list):
                    table_out[key] = [table_out[key]]
                table_out[key].append(to_add)


class ScalarMetric(InlineMetric):
    def __init__(self, name, value, data_location=None, description=""):
        super(ScalarMetric, self).__init__(name, value, data_location=data_location, description=description)
        self.metric_type = AZUREML_SCALAR_METRIC_TYPE

    def generate_keys_and_values(self):
        return [self.name], [self.value]

    def get_metric(self):
        pass

    @staticmethod
    def _is_valid_scalar(value):
        value_type = type(value)
        for number_type in six.integer_types + (float,):
            if isinstance(value, number_type) and sys.getsizeof(value) > AZUREML_MAX_NUMBER_SIZE_IN_BITS:
                raise AzureMLException("Number size of {} is larger than "
                                       "the max size of {} bits".format(value_type,
                                                                        AZUREML_MAX_NUMBER_SIZE_IN_BITS))

        return any(value_type in dictionary
                   for dictionary in (Metric._type_to_metric_type, Metric._type_to_converter))

    @staticmethod
    def _check_is_valid_scalar(value):
        if not ScalarMetric._is_valid_scalar(value):
            valid_types = list(Metric._type_to_metric_type.keys())
            raise AzureMLException("Value of type {0} is not supported, "
                                   "supported types include {1}".format(type(value),
                                                                        valid_types))


_metric_type_initializers[AZUREML_SCALAR_METRIC_TYPE] = ScalarMetric


class ListMetric(InlineMetric):
    def __init__(self, name, values, data_location=None, description=""):
        super(ListMetric, self).__init__(name, values, data_location=data_location, description=description)
        self.metric_type = AZUREML_LIST_METRIC_TYPE

    def generate_keys_and_values(self):
        value_list = [val for val in self.value]
        ListMetric._check_is_valid_list(value_list)
        return (self.name for i in range(len(value_list))), value_list

    @staticmethod
    def _check_is_valid_list(list_value):
        if isinstance(list_value, list):
            index_of_reference = 0
            reference_type = type(list_value[index_of_reference]) if len(list_value) > 0 else None
            for i in range(len(list_value)):
                val = list_value[i]
                if not ScalarMetric._is_valid_scalar(val):
                    valid_types = list(Metric._type_to_metric_type.keys())
                    raise AzureMLException("Value of type {0} is not supported, "
                                           "supported types include {1}".format(type(list_value),
                                                                                valid_types))
                elif type(val) != reference_type:
                    raise AzureMLException("Scalars at index {0} and {1} differ "
                                           "in type. type: {2} != {3}.".format(i,
                                                                               index_of_reference,
                                                                               type(val),
                                                                               reference_type))


_metric_type_initializers[AZUREML_LIST_METRIC_TYPE] = ListMetric


class TableMetric(InlineMetric):
    def __init__(self, name, values, data_location=None, description=""):
        super(TableMetric, self).__init__(name, values, data_location=data_location, description=description)
        self.metric_type = AZUREML_TABLE_METRIC_TYPE

    def generate_keys_and_values(self):
        TableMetric._check_is_valid_table(self.value)
        keys = (key for key in self.value for i in range(len(self.value[key])))
        values = (self.value[key][i] for key in self.value for i in range(len(self.value[key])))
        return keys, values

    @staticmethod
    def _check_is_valid_table(table, is_row=False):
        if not isinstance(table, dict):
            raise AzureMLException("Table to log is not a dictionary, currently"
                                   "supported inputs are dict[string]: column\n"
                                   " where columns are scalars or a list of scalars")
        if is_row:
            for key in table:
                val = table[key]
                if isinstance(val, list):
                    raise AzureMLException("Row metrics cannot contain list values, "
                                           "column {0} contains a list value".format(key))
                else:
                    ScalarMetric._check_is_valid_scalar(val)

        keys = list(table.keys())
        if len(keys) > 0:
            reference_column = keys[0]
            table_column_length = TableMetric._get_length(table[reference_column])
            for key in table:
                column_length = TableMetric._get_length(table[key])
                if column_length != table_column_length:
                    raise AzureMLException("Columns must have the same length, "
                                           "column {0} had length {1}, "
                                           "however, column {2} had length {3}.".format(reference_column,
                                                                                        table_column_length,
                                                                                        key,
                                                                                        column_length))
        return table

    @staticmethod
    def _get_length(value):
        return len(value) if isinstance(value, list) else 1


_metric_type_initializers[AZUREML_TABLE_METRIC_TYPE] = TableMetric


class RowMetric(TableMetric):
    def __init__(self, name, values, data_location=None, description=""):
        super(RowMetric, self).__init__(name, values, data_location=data_location, description=description)

    def generate_keys_and_values(self):
        TableMetric._check_is_valid_table(self.value, is_row=True)
        return self.value.keys(), self.value.values()


class ArtifactBackedMetric(Metric):
    def __init__(self, name, value, data_location, description=""):
        super(ArtifactBackedMetric, self).__init__(name, value, data_location=data_location, description=description)

    def to_cells(self):
        return [{self.name: None}]

    @staticmethod
    def add_cells(name, out, table_cell_types, cells, cell_types):
        # ArtifactBackedMetrics don't have anything in cells
        for cell in cells:
            for key in cell:
                var = cell[key]
                cell_type = cell_types[key]
                if key not in table_cell_types:
                    table_cell_types = cell_types[key]

                if key in out:
                    out[key] = out[key] if isinstance(out[key], list) else [out[key]]

                if cell_type != table_cell_types[key]:
                    module_logger.debug("Invalid type for metric name {}, type: "
                                        "{}, expected: {} appending None instead.".format(name,
                                                                                          cell_type,
                                                                                          table_cell_types[key]))
                    out[key].append(None)
                elif key not in out:
                    out[key] = var
                else:
                    out[key].append(var)

    def log_to_artifact(self, artifact_client, origin, container):
        metric_json = json.dumps(self.value)
        stream = io.BytesIO(metric_json.encode('utf-8'))
        try:
            artifact_client.upload_artifact(stream, origin, container, self.name)
        finally:
            stream.close()
        self._build_artifact_uri(origin, container, self.name)

    def retrieve_artifact(self, artifact_client):
        artifact = Artifact.create_unpopulated_artifact_from_data_location(self.data_location,
                                                                           isinstance(self, ImageMetric))
        artifact.retrieve_artifact()
        return artifact

    def _build_artifact_uri(self, origin, container, path):
        self.data_location = 'aml://artifactId/{}/{}/{}'.format(origin, container, path)


class ConfusionMatrixMetric(ArtifactBackedMetric):
    def __init__(self, name, value, data_location, description=""):
        super(ConfusionMatrixMetric, self).__init__(name, value, data_location, description=description)
        self.metric_type = AZUREML_CONFUSION_MATRIX_METRIC_TYPE


_metric_type_initializers[AZUREML_CONFUSION_MATRIX_METRIC_TYPE] = ConfusionMatrixMetric
_metric_type_initializers[AZUREML_OLD_CONFUSION_MATRIX_METRIC_TYPE] = ConfusionMatrixMetric


class AccuracyTableMetric(ArtifactBackedMetric):
    def __init__(self, name, value, data_location, description=""):
        super(AccuracyTableMetric, self).__init__(name, value, data_location, description=description)
        self.metric_type = AZUREML_ACCURACY_TABLE_METRIC_TYPE


_metric_type_initializers[AZUREML_ACCURACY_TABLE_METRIC_TYPE] = AccuracyTableMetric
_metric_type_initializers[AZUREML_OLD_ACCURACY_TABLE_METRIC_TYPE] = AccuracyTableMetric


class ResidualsMetric(ArtifactBackedMetric):
    def __init__(self, name, value, data_location, description=""):
        super(ResidualsMetric, self).__init__(name, value, data_location, description=description)
        self.metric_type = AZUREML_RESIDUALS_METRIC_TYPE


_metric_type_initializers[AZUREML_RESIDUALS_METRIC_TYPE] = ResidualsMetric
_metric_type_initializers[AZUREML_OLD_RESIDUALS_METRIC_TYPE] = ResidualsMetric


class PredictionsMetric(ArtifactBackedMetric):
    def __init__(self, name, value, data_location, description=""):
        super(PredictionsMetric, self).__init__(name, value, data_location, description=description)
        self.metric_type = AZUREML_PREDICTIONS_METRIC_TYPE


_metric_type_initializers[AZUREML_PREDICTIONS_METRIC_TYPE] = PredictionsMetric
_metric_type_initializers[AZUREML_OLD_PREDICTIONS_METRIC_TYPE] = PredictionsMetric


class ImageMetric(ArtifactBackedMetric):
    def __init__(self, name, value, data_location, description="", is_old_image=False):
        super(ImageMetric, self).__init__(name, value, data_location, description)
        if is_old_image:
            self.metric_type = AZUREML_OLD_IMAGE_METRIC_TYPE
            self.data_location = self.value
        else:
            self.metric_type = AZUREML_IMAGE_METRIC_TYPE

    def log_to_artifact(self, artifact_client, origin, container, is_plot=False):
        if is_plot:
            artifact_path = self._log_plot(artifact_client, self.value, origin, container)
        else:
            artifact_path = self._log_image(artifact_client, self.value, origin, container)
        self._build_artifact_uri(origin, container, artifact_path)

    def _log_plot(self, artifact_client, plot, origin, container):
        plot_name = self.name + "_" + str(int(time.time()))
        ext = "png"
        artifact_path = "{}.{}".format(plot_name, ext)
        stream = io.BytesIO()
        try:
            plot.savefig(stream, format=ext)
            stream.seek(0)
            artifact_client.upload_artifact(stream, origin, container, artifact_path,
                                            content_type="image/{}".format(ext))
        except AttributeError as attribute_error:
            raise AzureMLException("Invalid plot, must be matplotlib.pyplot", inner_exception=attribute_error)
        finally:
            stream.close()
        return artifact_path

    def _log_image(self, artifact_client, path, origin, container):
        image_type = imghdr.what(path)
        if image_type is not None:
            artifact_client.upload_artifact(path, origin, container, path,
                                            content_type="image/{}".format(image_type))
        else:
            raise AzureMLException("The path provided points to a malformed image file")
        return path


_metric_type_initializers[AZUREML_IMAGE_METRIC_TYPE] = ImageMetric
_metric_type_initializers[AZUREML_OLD_IMAGE_METRIC_TYPE] = ImageMetric
