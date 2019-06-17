import datetime
import hashlib
import os
import typing

import dateutil.parser
import numpy  # type: ignore

from d3m import container, utils as d3m_utils
from d3m.base import utils as base_utils
from d3m.metadata import base as metadata_base, hyperparams
from d3m.primitive_interfaces import base, transformer

from sri.common import config

# __all__ = ('SimpleColumnParserPrimitive',)

DEFAULT_DATETIME = datetime.datetime.fromtimestamp(0, datetime.timezone.utc)

Inputs = container.DataFrame
Outputs = container.DataFrame


class Hyperparams(hyperparams.Hyperparams):
    parse_semantic_types = hyperparams.Set(
        elements=hyperparams.Enumeration(
            values=[
                'http://schema.org/Boolean', 'https://metadata.datadrivendiscovery.org/types/CategoricalData',
                'http://schema.org/Integer', 'http://schema.org/Float',
                'https://metadata.datadrivendiscovery.org/types/FloatVector', 'http://schema.org/DateTime',
            ],
            # Default is ignored.
            # TODO: Remove default. See: https://gitlab.com/datadrivendiscovery/d3m/issues/141
            default='http://schema.org/Boolean',
        ),
        default=(
            'http://schema.org/Boolean', 'https://metadata.datadrivendiscovery.org/types/CategoricalData',
            'http://schema.org/Integer', 'http://schema.org/Float',
            'https://metadata.datadrivendiscovery.org/types/FloatVector', 'http://schema.org/DateTime',
        ),
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="A set of semantic types to parse. One can provide a subset of supported semantic types to limit what the primitive parses.",
    )
    use_columns = hyperparams.Set(
        elements=hyperparams.Hyperparameter[int](-1),
        default=(),
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="A set of column indices to force primitive to operate on. If any specified column cannot be parsed, it is skipped.",
    )
    exclude_columns = hyperparams.Set(
        elements=hyperparams.Hyperparameter[int](-1),
        default=(),
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="A set of column indices to not operate on. Applicable only if \"use_columns\" is not provided.",
    )
    return_result = hyperparams.Enumeration(
        values=['append', 'replace', 'new'],
        default='replace',
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="Should parsed columns be appended, should they replace original columns, or should only parsed columns be returned?",
    )
    add_index_columns = hyperparams.UniformBool(
        default=True,
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="Also include primary index columns if input data has them. Applicable only if \"return_result\" is set to \"new\".",
    )
    parse_categorical_target_columns = hyperparams.UniformBool(
        default=False,
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="Should it parse also categorical target columns?",
    )
    replace_index_columns = hyperparams.UniformBool(
        default=True,
        semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
        description="Replace primary index columns even if otherwise appending columns. Applicable only if \"return_result\" is set to \"append\".",
    )


class SimpleColumnParser(transformer.TransformerPrimitiveBase[Inputs, Outputs, Hyperparams]):
    """
    A primitive which parses strings into their parsed values. This primitive was adapted
    from Mitars ColumnParserPrimitive in the Common Primitives repo.

    It goes over all columns (by default, controlled by ``use_columns``, ``exclude_columns``)
    and checks those with structural type ``str`` if they have a semantic type suggesting
    that they are a boolean value, categorical, integer, float, or time (by default,
    controlled by ``parse_semantic_types``). Categorical values are converted to integer
    encodings.

    What is returned is controlled by ``return_result`` and ``add_index_columns``.
    """

    metadata = metadata_base.PrimitiveMetadata(
        {
            'id': 'd519cb7a-1782-4f51-b44c-58f0236e47c7',
            'version': config.VERSION,
            'name': "Parses strings into their types",
            'description': 'Adapted from Mitars Column Parser - this implementation turns categorical values into integers instead of hashes',
            'python_path': 'd3m.primitives.data_transformation.simple_column_parser.DataFrameCommon',
            'source': config.SOURCE,
            'installation':  [ config.INSTALLATION ],
            'algorithm_types': [
                metadata_base.PrimitiveAlgorithmType.DATA_CONVERSION,
            ],
            'primitive_family': metadata_base.PrimitiveFamily.DATA_TRANSFORMATION,
        },
    )

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:
        columns_to_use, output_columns = self._produce_columns(inputs, self.hyperparams)

        if self.hyperparams['replace_index_columns'] and self.hyperparams['return_result'] == 'append':
            assert len(columns_to_use) == len(output_columns)

            index_columns = inputs.metadata.get_index_columns()

            index_columns_to_use = []
            other_columns_to_use = []
            index_output_columns = []
            other_output_columns = []
            for column_to_use, output_column in zip(columns_to_use, output_columns):
                if column_to_use in index_columns:
                    index_columns_to_use.append(column_to_use)
                    index_output_columns.append(output_column)
                else:
                    other_columns_to_use.append(column_to_use)
                    other_output_columns.append(output_column)

            outputs = base_utils.combine_columns(inputs, index_columns_to_use, index_output_columns, return_result='replace', add_index_columns=self.hyperparams['add_index_columns'])
            outputs = base_utils.combine_columns(outputs, other_columns_to_use, other_output_columns, return_result='append', add_index_columns=self.hyperparams['add_index_columns'])
        else:
            outputs = base_utils.combine_columns(inputs, columns_to_use, output_columns, return_result=self.hyperparams['return_result'], add_index_columns=self.hyperparams['add_index_columns'])

        return base.CallResult(outputs)

    @classmethod
    def _can_use_column(cls, inputs_metadata: metadata_base.DataMetadata, column_index: int, hyperparams: Hyperparams) -> bool:
        column_metadata = inputs_metadata.query((metadata_base.ALL_ELEMENTS, column_index))

        # We produce only on columns which have not yet been parsed (are strings).
        if column_metadata['structural_type'] != str:
            return False

        semantic_types = column_metadata.get('semantic_types', [])

        for semantic_type in hyperparams['parse_semantic_types']:
            if semantic_type not in semantic_types:
                continue

            if semantic_type == 'https://metadata.datadrivendiscovery.org/types/CategoricalData':
                # Skip parsing if a column is categorical, but also a target column.
                if not hyperparams['parse_categorical_target_columns'] and 'https://metadata.datadrivendiscovery.org/types/Target' in semantic_types:
                    continue

            return True

        return False

    @classmethod
    def _produce_columns(cls, inputs: Inputs, hyperparams: Hyperparams) -> typing.Tuple[typing.List[int], typing.List[Outputs]]:
        # The logic of parsing values tries to mirror also the logic of detecting
        # values in "SimpleProfilerPrimitive". One should keep them in sync.

        columns_to_use = cls._get_columns(inputs.metadata, hyperparams)

        # We check against this list again, because there might be multiple matching semantic types
        # (which is not really valid).
        parse_semantic_types = hyperparams['parse_semantic_types']

        output_columns = []

        for column_index in columns_to_use:
            column_metadata = inputs.metadata.query((metadata_base.ALL_ELEMENTS, column_index))
            semantic_types = column_metadata.get('semantic_types', [])
            if column_metadata['structural_type'] == str:
                if 'http://schema.org/Boolean' in parse_semantic_types and 'http://schema.org/Boolean' in semantic_types:
                    output_columns.append(cls._parse_boolean_data(inputs, column_index))

                elif 'https://metadata.datadrivendiscovery.org/types/CategoricalData' in parse_semantic_types and \
                        'https://metadata.datadrivendiscovery.org/types/CategoricalData' in semantic_types and \
                        (hyperparams['parse_categorical_target_columns'] or 'https://metadata.datadrivendiscovery.org/types/Target' not in semantic_types):
                    output_columns.append(cls._parse_categorical_data(inputs, column_index))

                elif 'http://schema.org/Integer' in parse_semantic_types and 'http://schema.org/Integer' in semantic_types:
                    # For primary key we know all values have to exist so we can assume they can always be represented as integers.
                    if 'https://metadata.datadrivendiscovery.org/types/PrimaryKey' in semantic_types:
                        integer_required = True
                    else:
                        integer_required = False

                    output_columns.append(cls._parse_integer(inputs, column_index, integer_required))

                elif 'http://schema.org/Float' in parse_semantic_types and 'http://schema.org/Float' in semantic_types:
                    output_columns.append(cls._parse_float_data(inputs, column_index))

                elif 'https://metadata.datadrivendiscovery.org/types/FloatVector' in parse_semantic_types and 'https://metadata.datadrivendiscovery.org/types/FloatVector' in semantic_types:
                    output_columns.append(cls._parse_float_vector_data(inputs, column_index))

                elif 'http://schema.org/DateTime' in parse_semantic_types and 'http://schema.org/DateTime' in semantic_types:
                    output_columns.append(cls._parse_time_data(inputs, column_index))

                else:
                    assert False, column_index

        assert len(output_columns) == len(columns_to_use)

        return columns_to_use, output_columns

    @classmethod
    def _produce_columns_metadata(cls, inputs_metadata: metadata_base.DataMetadata, hyperparams: Hyperparams) -> typing.Tuple[typing.List[int], typing.List[metadata_base.DataMetadata]]:
        columns_to_use = cls._get_columns(inputs_metadata, hyperparams)

        # We check against this list again, because there might be multiple matching semantic types
        # (which is not really valid).
        parse_semantic_types = hyperparams['parse_semantic_types']

        output_columns = []

        for column_index in columns_to_use:
            column_metadata = inputs_metadata.query((metadata_base.ALL_ELEMENTS, column_index))
            semantic_types = column_metadata.get('semantic_types', [])
            if column_metadata['structural_type'] == str:
                if 'http://schema.org/Boolean' in parse_semantic_types and 'http://schema.org/Boolean' in semantic_types:
                    output_columns.append(cls._parse_boolean_metadata(inputs_metadata, column_index))

                elif 'https://metadata.datadrivendiscovery.org/types/CategoricalData' in parse_semantic_types and \
                        'https://metadata.datadrivendiscovery.org/types/CategoricalData' in semantic_types and \
                        (hyperparams['parse_categorical_target_columns'] or 'https://metadata.datadrivendiscovery.org/types/Target' not in semantic_types):
                    output_columns.append(cls._parse_categorical_metadata(inputs_metadata, column_index))

                elif 'http://schema.org/Integer' in parse_semantic_types and 'http://schema.org/Integer' in semantic_types:
                    output_columns.append(cls._parse_integer_metadata(inputs_metadata, column_index))

                elif 'http://schema.org/Float' in parse_semantic_types and 'http://schema.org/Float' in semantic_types:
                    output_columns.append(cls._parse_float_metadata(inputs_metadata, column_index))

                elif 'https://metadata.datadrivendiscovery.org/types/FloatVector' in parse_semantic_types and 'https://metadata.datadrivendiscovery.org/types/FloatVector' in semantic_types:
                    output_columns.append(cls._parse_float_vector_metadata(inputs_metadata, column_index))

                elif 'http://schema.org/DateTime' in parse_semantic_types and 'http://schema.org/DateTime' in semantic_types:
                    output_columns.append(cls._parse_time_metadata(inputs_metadata, column_index))

                else:
                    assert False, column_index

        assert len(output_columns) == len(columns_to_use)

        return columns_to_use, output_columns

    @classmethod
    def _get_columns(cls, inputs_metadata: metadata_base.DataMetadata, hyperparams: Hyperparams) -> typing.List[int]:
        def can_use_column(column_index: int) -> bool:
            return cls._can_use_column(inputs_metadata, column_index, hyperparams)

        columns_to_use, columns_not_to_use = base_utils.get_columns_to_use(inputs_metadata,  hyperparams['use_columns'], hyperparams['exclude_columns'], can_use_column)

        # We are OK if no columns ended up being parsed.
        # "base_utils.combine_columns" will throw an error if it cannot work with this.

        if hyperparams['use_columns'] and columns_not_to_use:
            cls.logger.warning("Not all specified columns can parsed. Skipping columns: %(columns)s", {
                'columns': columns_not_to_use,
            })

        return columns_to_use

    @classmethod
    def _parse_boolean_data(cls, inputs: Inputs, column_index: metadata_base.SimpleSelectorSegment) -> Outputs:
        return cls._parse_categorical_data(inputs, column_index)

    @classmethod
    def _parse_boolean_metadata(cls, inputs_metadata: metadata_base.DataMetadata, column_index: metadata_base.SimpleSelectorSegment) -> metadata_base.DataMetadata:
        return cls._parse_categorical_metadata(inputs_metadata, column_index)

    @classmethod
    def _parse_categorical_data(cls, inputs: Inputs, column_index: metadata_base.SimpleSelectorSegment) -> Outputs:
        values_map: typing.Dict[str, int] = {}
        for value in inputs.iloc[:, column_index]:
            value = value.strip()
            if value not in values_map:
                value_int = len(values_map)
                values_map[value] = value_int

        outputs = container.DataFrame({inputs.columns[column_index]: [values_map[value.strip()] for value in inputs.iloc[:, column_index]]}, generate_metadata=False)
        outputs.metadata = cls._parse_categorical_metadata(inputs.metadata, column_index)

        return outputs

    @classmethod
    def _parse_categorical_metadata(cls, inputs_metadata: metadata_base.DataMetadata, column_index: metadata_base.SimpleSelectorSegment) -> metadata_base.DataMetadata:
        outputs_metadata = inputs_metadata.select_columns([column_index])
        return outputs_metadata.update_column(0, {'structural_type': int})

    @classmethod
    def _str_to_int(cls, value: str) -> typing.Union[float, int]:
        try:
            return int(value.strip())
        except ValueError:
            try:
                # Maybe it is an int represented as a float. Let's try this. This can get rid of non-integer
                # part of the value, but the integer was requested through a semantic type, so this is probably OK.
                return int(float(value.strip()))
            except ValueError:
                # No luck, use NaN to represent a missing value.
                return float('nan')

    @classmethod
    def _parse_integer(cls, inputs: Inputs, column_index: metadata_base.SimpleSelectorSegment,
                       integer_required: bool) -> container.DataFrame:
        outputs = container.DataFrame({inputs.columns[column_index]: [cls._str_to_int(value) for value in inputs.iloc[:, column_index]]}, generate_metadata=False)

        if outputs.dtypes.iloc[0].kind == 'f':
            structural_type: type = float
        elif outputs.dtypes.iloc[0].kind in ['i', 'u']:
            structural_type = int
        else:
            assert False, outputs.dtypes.iloc[0]

        if structural_type is float and integer_required:
            raise ValueError("Not all values in a column can be parsed into integers, but only integers were expected.")

        outputs.metadata = inputs.metadata.select_columns([column_index])
        outputs.metadata = outputs.metadata.update_column(0, {'structural_type': structural_type})

        return outputs

    @classmethod
    def _parse_integer_metadata(cls, inputs_metadata: metadata_base.DataMetadata, column_index: metadata_base.SimpleSelectorSegment) -> metadata_base.DataMetadata:
        outputs_metadata = inputs_metadata.select_columns([column_index])
        # Without data we assume we can parse everything into integers. This might not be true and
        # we might end up parsing into floats if we have to represent missing (or invalid) values.
        return outputs_metadata.update_column(0, {'structural_type': int})

    @classmethod
    def _str_to_float(cls, value: str) -> float:
        try:
            return float(value.strip())
        except ValueError:
            return float('nan')

    @classmethod
    def _parse_float_data(cls, inputs: Inputs, column_index: metadata_base.SimpleSelectorSegment) -> Outputs:
        outputs = container.DataFrame({inputs.columns[column_index]: [cls._str_to_float(value) for value in inputs.iloc[:, column_index]]}, generate_metadata=False)
        outputs.metadata = cls._parse_float_metadata(inputs.metadata, column_index)

        return outputs

    @classmethod
    def _parse_float_metadata(cls, inputs_metadata: metadata_base.DataMetadata, column_index: metadata_base.SimpleSelectorSegment) -> metadata_base.DataMetadata:
        outputs_metadata = inputs_metadata.select_columns([column_index])
        return outputs_metadata.update_column(0, {'structural_type': float})

    @classmethod
    def _parse_float_vector_data(cls, inputs: Inputs, column_index: metadata_base.SimpleSelectorSegment) -> Outputs:
        # We are pretty strict here because we are assuming this was generated programmatically.
        outputs = container.DataFrame(
            {
                inputs.columns[column_index]: [
                    container.ndarray([cls._str_to_float(value) for value in values.split(',')])
                    for values in inputs.iloc[:, column_index]
                ],
            },
            generate_metadata=False,
        )
        outputs.metadata = cls._parse_float_metadata(inputs.metadata, column_index)
        # We have to automatically generate metadata to set ndarray dimension(s).
        outputs.metadata = outputs.metadata.generate(outputs)

        return outputs

    @classmethod
    def _parse_float_vector_metadata(cls, inputs_metadata: metadata_base.DataMetadata, column_index: metadata_base.SimpleSelectorSegment) -> metadata_base.DataMetadata:
        outputs_metadata = inputs_metadata.select_columns([column_index])
        # We cannot know the dimension of the ndarray without data.
        outputs_metadata = outputs_metadata.update_column(0, {'structural_type': container.ndarray})
        outputs_metadata = outputs_metadata.update((metadata_base.ALL_ELEMENTS, 0, metadata_base.ALL_ELEMENTS), {'structural_type': numpy.float64})
        return outputs_metadata

    @classmethod
    def _time_to_foat(cls, value: str) -> float:
        try:
            return dateutil.parser.parse(value, default=DEFAULT_DATETIME, fuzzy=True).timestamp()
        except (ValueError, OverflowError):
            return float('nan')

    @classmethod
    def _parse_time_data(cls, inputs: Inputs, column_index: metadata_base.SimpleSelectorSegment) -> Outputs:
        outputs = container.DataFrame({inputs.columns[column_index]: [cls._time_to_foat(value) for value in inputs.iloc[:, column_index]]}, generate_metadata=False)
        outputs.metadata = cls._parse_time_metadata(inputs.metadata, column_index)

        return outputs

    @classmethod
    def _parse_time_metadata(cls, inputs_metadata: metadata_base.DataMetadata, column_index: metadata_base.SimpleSelectorSegment) -> metadata_base.DataMetadata:
        outputs_metadata = inputs_metadata.select_columns([column_index])
        return outputs_metadata.update_column(0, {'structural_type': float})

    @classmethod
    def can_accept(cls, *, method_name: str, arguments: typing.Dict[str, typing.Union[metadata_base.Metadata, type]], hyperparams: Hyperparams) -> typing.Optional[metadata_base.DataMetadata]:
        output_metadata = super().can_accept(method_name=method_name, arguments=arguments, hyperparams=hyperparams)

        # If structural types didn't match, don't bother.
        if output_metadata is None:
            return None

        if method_name != 'produce':
            return output_metadata

        if 'inputs' not in arguments:
            return output_metadata

        inputs_metadata = typing.cast(metadata_base.DataMetadata, arguments['inputs'])

        columns_to_use, output_columns = cls._produce_columns_metadata(inputs_metadata, hyperparams)

        # We are stricter here than "produce" because we are not really useful.
        if not columns_to_use:
            return None

        if hyperparams['replace_index_columns'] and hyperparams['return_result'] == 'append':
            assert len(columns_to_use) == len(output_columns)

            index_columns = inputs_metadata.get_index_columns()

            index_columns_to_use = []
            other_columns_to_use = []
            index_output_columns = []
            other_output_columns = []
            for column_to_use, output_column in zip(columns_to_use, output_columns):
                if column_to_use in index_columns:
                    index_columns_to_use.append(column_to_use)
                    index_output_columns.append(output_column)
                else:
                    other_columns_to_use.append(column_to_use)
                    other_output_columns.append(output_column)

            outputs_metadata = base_utils.combine_columns_metadata(
                inputs_metadata, index_columns_to_use, index_output_columns,
                return_result='replace', add_index_columns=hyperparams['add_index_columns'],
            )
            return base_utils.combine_columns_metadata(
                outputs_metadata, other_columns_to_use, other_output_columns,
                return_result='append', add_index_columns=hyperparams['add_index_columns'],
            )
        else:
            return base_utils.combine_columns_metadata(
                inputs_metadata, columns_to_use, output_columns,
                return_result=hyperparams['return_result'], add_index_columns=hyperparams['add_index_columns'],
            )
