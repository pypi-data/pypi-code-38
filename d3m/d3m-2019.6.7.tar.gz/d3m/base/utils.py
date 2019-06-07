import copy
import typing

from d3m import container, exceptions
from d3m.metadata import base as metadata_base


def get_columns_to_use(
    metadata: metadata_base.DataMetadata, use_columns: typing.Sequence[int], exclude_columns: typing.Sequence[int],
    can_use_column: typing.Callable,
) -> typing.Tuple[typing.List[int], typing.List[int]]:
    """
    A helper function which computes a list of columns to use and a list of columns to ignore
    given ``use_columns``, ``exclude_columns``, and a ``can_use_column`` function which should
    return ``True`` when column can be used.
    """

    all_columns = list(use_columns)

    # If "use_columns" is provided, this is our view of which columns exist.
    if not all_columns:
        # Otherwise, we start with all columns.
        all_columns = list(range(metadata.query_field((metadata_base.ALL_ELEMENTS,), 'dimension')['length']))

        # And remove those in "exclude_columns".
        all_columns = [column_index for column_index in all_columns if column_index not in exclude_columns]

    # Now we create a list of columns for which "can_use_column" returns "True",
    # but also a list of columns for which it does not. The latter can be used
    # to determine if there is an error or warning. For example, when using "use_columns",
    # ideally, "columns_not_to_use" should be empty or a warning should be made.
    # Or, some primitives might require to operate on all columns, so "columns_not_to_use"
    # is empty, an error should be raised.
    columns_to_use = []
    columns_not_to_use = []
    for column_index in all_columns:
        if can_use_column(column_index):
            columns_to_use.append(column_index)
        else:
            columns_not_to_use.append(column_index)

    return columns_to_use, columns_not_to_use


def combine_columns(
    inputs: container.DataFrame, column_indices: typing.Sequence[int], columns_list: typing.Sequence[container.DataFrame], *,
    return_result: str, add_index_columns: bool,
) -> container.DataFrame:
    """
    Method which appends existing columns, replaces them, or creates new result from them, based on
    ``return_result`` argument, which can be ``append``, ``replace``, or ``new``.

    ``add_index_columns`` controls if when creating a new result, primary index columns should be added
    if they are not already among columns.

    ``inputs`` is a DataFrame for which we are appending on replacing columns, or if we are creating new result,
    from where a primary index column can be taken.

    ``column_indices`` controls which columns in ``inputs`` were used to create ``columns_list``,
    and which columns should be replaced when replacing them.

    ``columns_list`` is a list of DataFrames representing all together new columns. The reason it is a list is
    to make it easier to operate per-column when preparing ``columns_list`` and not have to concat them all
    together unnecessarily.

    Top-level metadata in ``columns_list`` is ignored, except when creating new result.
    In that case top-level metadata from the first element in the list is used.

    When ``column_indices`` columns are being replaced with ``columns_list``, existing metadata in ``column_indices``
    columns is not preserved but replaced with metadata in ``columns_list``. Ideally, metadata for ``columns_list``
    has been constructed by copying source metadata from ``column_indices`` columns and modifying it as
    necessary to adapt it to new columns. But ``columns_list`` also can have completely new metadata, if this
    is more reasonable, but it should be understood that in this case when replacing ``column_indices``
    columns, any custom additional metadata on those columns will be lost.

    ``column_indices`` and ``columns_list`` do not have to match in number of columns. Columns are first
    replaced in order for matching indices and columns. If then there are more ``column_indices`` than
    ``columns_list``, additional ``column_indices`` columns are removed. If there are more ``columns_list`` than
    ``column_indices`` columns, then additional ``columns_list`` are inserted after the last replaced column.

    If ``column_indices`` is empty, then the replacing behavior is equivalent to appending.
    """

    if return_result == 'append':
        outputs = inputs
        for columns in columns_list:
            outputs = outputs.append_columns(columns)

    elif return_result == 'replace':
        if not column_indices:
            return combine_columns(inputs, column_indices, columns_list, return_result='append', add_index_columns=add_index_columns)

        # We copy here and disable copying inside "replace_columns" to copy only once.
        # We have to copy because "replace_columns" is modifying data in-place.
        outputs = copy.copy(inputs)

        columns_replaced = 0
        for columns in columns_list:
            columns_length = columns.shape[1]
            if columns_replaced < len(column_indices):
                # It is OK if the slice of "column_indices" is shorter than "columns", Only those columns
                # listed in the slice will be replaced and others appended after the last replaced column.
                outputs = outputs.replace_columns(columns, column_indices[columns_replaced:columns_replaced + columns_length], copy=False)
            else:
                # We insert the rest of columns after the last columns we replaced. We know that "column_indices"
                # is non-empty and that the last item of "column_indices" points ot the last column we replaced
                # for those listed in "column_indices". We replaced more columns though, so we have to add the
                # difference, and then add 1 to insert after the last column.
                outputs = outputs.insert_columns(columns, column_indices[-1] + (columns_replaced - len(column_indices)) + 1)
            columns_replaced += columns_length

        if columns_replaced < len(column_indices):
            outputs = outputs.remove_columns(column_indices[columns_replaced:len(column_indices)])

    elif return_result == 'new':
        if not any(columns.shape[1] for columns in columns_list):
            raise ValueError("No columns produced.")

        outputs = columns_list[0]
        for columns in columns_list[1:]:
            outputs = outputs.append_columns(columns)

        if add_index_columns:
            inputs_index_columns = inputs.metadata.get_index_columns()
            outputs_index_columns = outputs.metadata.get_index_columns()

            if inputs_index_columns and not outputs_index_columns:
                # Add index columns at the beginning.
                outputs = inputs.select_columns(inputs_index_columns).append_columns(outputs, use_right_metadata=True)

    else:
        raise exceptions.InvalidArgumentValueError("\"return_result\" has an invalid value: {return_result}".format(return_result=return_result))

    return outputs


def combine_columns_metadata(
    inputs: metadata_base.DataMetadata, column_indices: typing.Sequence[int], columns_list: typing.Sequence[metadata_base.DataMetadata], *,
    return_result: str, add_index_columns: bool,
) -> metadata_base.DataMetadata:
    """
    Analogous to ``combine_columns`` but operates only on metadata.
    """

    if return_result == 'append':
        outputs = inputs
        for columns in columns_list:
            outputs = outputs.append_columns(columns)

    elif return_result == 'replace':
        if not column_indices:
            return combine_columns_metadata(inputs, column_indices, columns_list, return_result='append', add_index_columns=add_index_columns)

        outputs = inputs

        columns_replaced = 0
        for columns in columns_list:
            columns_length = columns.query_field((metadata_base.ALL_ELEMENTS,), 'dimension')['length']
            if columns_replaced < len(column_indices):
                # It is OK if the slice of "column_indices" is shorter than "columns", Only those columns
                # listed in the slice will be replaced and others appended after the last replaced column.
                outputs = outputs.replace_columns(columns, column_indices[columns_replaced:columns_replaced + columns_length])
            else:
                # We insert the rest of columns after the last columns we replaced. We know that "column_indices"
                # is non-empty and that the last item of "column_indices" points ot the last column we replaced
                # for those listed in "column_indices". We replaced more columns though, so we have to add the
                # difference, and then add 1 to insert after the last column.
                outputs = outputs.insert_columns(columns, column_indices[-1] + (columns_replaced - len(column_indices)) + 1)
            columns_replaced += columns_length

        if columns_replaced < len(column_indices):
            outputs = outputs.remove_columns(column_indices[columns_replaced:len(column_indices)])

    elif return_result == 'new':
        if not any(columns_metadata.query_field((metadata_base.ALL_ELEMENTS,), 'dimension')['length'] for columns_metadata in columns_list):
            raise ValueError("No columns produced.")

        outputs = columns_list[0]
        for columns in columns_list[1:]:
            outputs = outputs.append_columns(columns)

        if add_index_columns:
            inputs_index_columns = inputs.get_index_columns()
            outputs_index_columns = outputs.get_index_columns()

            if inputs_index_columns and not outputs_index_columns:
                # Add index columns at the beginning.
                outputs = inputs.select_columns(inputs_index_columns).append_columns(outputs, use_right_metadata=True)

    else:
        raise exceptions.InvalidArgumentValueError("\"return_result\" has an invalid value: {return_result}".format(return_result=return_result))

    return outputs


def get_tabular_resource(
    dataset: container.Dataset, resource_id: typing.Optional[str], *,
    pick_entry_point: bool = True, pick_one: bool = True, has_hyperparameter: bool = True,
) -> typing.Tuple[str, container.DataFrame]:
    if resource_id is None and pick_entry_point:
        for dataset_resource_id in dataset.keys():
            if dataset.metadata.has_semantic_type((dataset_resource_id,), 'https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint'):
                resource_id = dataset_resource_id
                break

    if resource_id is None and pick_one:
        tabular_resource_ids = [dataset_resource_id for dataset_resource_id, dataset_resource in dataset.items() if isinstance(dataset_resource, container.DataFrame)]
        if len(tabular_resource_ids) == 1:
            resource_id = tabular_resource_ids[0]

    if resource_id is None:
        if has_hyperparameter:
            if pick_entry_point and pick_one:
                raise ValueError("A Dataset with multiple tabular resources without an entry point and no resource specified as a hyper-parameter.")
            elif pick_entry_point:
                raise ValueError("A Dataset without an entry point and no resource specified as a hyper-parameter.")
            elif pick_one:
                raise ValueError("A Dataset with multiple tabular resources and no resource specified as a hyper-parameter.")
            else:
                raise ValueError("No resource specified as a hyper-parameter.")
        else:
            if pick_entry_point and pick_one:
                raise ValueError("A Dataset with multiple tabular resources without an entry point.")
            elif pick_entry_point:
                raise ValueError("A Dataset without an entry point.")
            elif pick_one:
                raise ValueError("A Dataset with multiple tabular resources.")
            else:
                raise ValueError("No resource specified.")

    else:
        resource = dataset[resource_id]

    if not isinstance(resource, container.DataFrame):
        raise TypeError("The Dataset resource \"{resource_id}\" is not a DataFrame, but \"{type}\".".format(
            resource_id=resource_id,
            type=type(resource),
        ))

    return resource_id, resource


def get_tabular_resource_metadata(
    dataset: metadata_base.DataMetadata, resource_id: typing.Optional[metadata_base.SelectorSegment], *,
    pick_entry_point: bool = True, pick_one: bool = True,
) -> metadata_base.SelectorSegment:
    if resource_id is None and pick_entry_point:
        # This can be also "ALL_ELEMENTS" and it will work out, but we prefer a direct resource ID,
        # if available. So we reverse the list, because the first is "ALL_ELEMENTS" if it exists.
        for dataset_resource_id in reversed(dataset.get_elements(())):
            if dataset.has_semantic_type((dataset_resource_id,), 'https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint'):
                resource_id = dataset_resource_id
                break

    if resource_id is None and pick_one:
        # This can be also "ALL_ELEMENTS" and it will work out, but we prefer a direct resource ID,
        # if available. So we reverse the list, because the first is "ALL_ELEMENTS" if it exists.
        tabular_resource_ids = []
        for dataset_resource_id in reversed(dataset.get_elements(())):
            dataset_resource_type = dataset.query((dataset_resource_id,)).get('structural_type', None)

            if dataset_resource_type is None:
                continue

            if issubclass(dataset_resource_type, container.DataFrame):
                tabular_resource_ids.append(dataset_resource_id)

        if len(tabular_resource_ids) == 1:
            resource_id = tabular_resource_ids[0]

    if resource_id is None:
        if pick_entry_point and pick_one:
            raise ValueError("A Dataset with multiple tabular resources without an entry point and no DataFrame resource specified as a hyper-parameter.")
        elif pick_entry_point:
            raise ValueError("A Dataset without an entry point and no DataFrame resource specified as a hyper-parameter.")
        elif pick_one:
            raise ValueError("A Dataset with multiple tabular resources and no DataFrame resource specified as a hyper-parameter.")
        else:
            raise ValueError("No DataFrame resource specified as a hyper-parameter.")

    else:
        resource_type = dataset.query((resource_id,))['structural_type']

    if not issubclass(resource_type, container.DataFrame):
        raise TypeError("The Dataset resource \"{resource_id}\" is not a DataFrame, but \"{type}\".".format(
            resource_id=resource_id,
            type=resource_type,
        ))

    return resource_id
