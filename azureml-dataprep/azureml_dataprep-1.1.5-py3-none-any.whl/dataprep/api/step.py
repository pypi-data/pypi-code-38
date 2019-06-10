# Copyright (c) Microsoft Corporation. All rights reserved.
from .engineapi.typedefinitions import (AnonymousBlockData, PropertyValues, ColumnsSelector, ColumnsSelectorType,
                                        DynamicColumnsSelectorDetails, StaticColumnsSelectorDetails,
                                        ColumnsSelectorDetails, SingleColumnSelectorDetails)
from typing import List, Dict, Any, TypeVar, cast
from textwrap import dedent, indent
from pprint import pformat
import uuid


class ColumnSelector:
    """
    Matches a set of columns by name according to a search term.

    :param term: Search term to match available columns with.
    :vartype term: str
    :param use_regex: (Optional) Determines if the search term should be treated as a regular expression. Default `False`. 
    :vartype use_regex: bool
    :param ignore_case: (Optional) Determines if string match should be case insensitive. Default `False`. Only applies in non-regex case.
    :vartype ignore_case: bool
    :param match_whole_word: (Optional) Determines if string match should be for the whole word. Default `False`. Only applies in non-regex case. 
    :vartype match_whole_word: bool
    :param invert: (Optional) Determines if the only columns not matching the term should be selected. Default `False`.  
    :vartype invert: bool
    """
    def __init__(self,
                 term: str,
                 use_regex: bool = False,
                 ignore_case: bool = False,
                 match_whole_word: bool = False,
                 invert: bool = False):
        self._term = term
        self._use_regex = use_regex
        self._ignore_case = ignore_case
        self._match_whole_word = match_whole_word
        self._invert = invert

    @property
    def term(self) -> str:
        return self._term

    @property
    def use_regex(self) -> bool:
        return self._use_regex

    @property
    def ignore_case(self) -> bool:
        return self._ignore_case

    @property
    def match_whole_word(self) -> bool:
        return self._match_whole_word

    @property
    def invert(self) -> bool:
        return self._invert


MultiColumnSelection = TypeVar('MultiColumnSelection', str, List[str], ColumnSelector)


def column_selection_to_selector_value(selection: MultiColumnSelection) -> ColumnsSelector:
    is_dynamic = False
    if isinstance(selection, str):
        details = StaticColumnsSelectorDetails([selection])
    elif isinstance(selection, list):
        details = StaticColumnsSelectorDetails(selection)
    elif isinstance(selection, ColumnSelector):
        is_dynamic = True
        details = DynamicColumnsSelectorDetails(term=selection.term,
                                                use_regex=selection.use_regex,
                                                ignore_case=selection.ignore_case,
                                                match_whole_word=selection.match_whole_word,
                                                invert=selection.invert)
    else:
        raise ValueError('Unsupported value for column selection.')

    return ColumnsSelector(type=ColumnsSelectorType.DYNAMIC if is_dynamic else ColumnsSelectorType.STATICLIST,
                           details=cast(ColumnsSelectorDetails, details))


def single_column_to_selector_value(column: str) -> ColumnsSelector:
    details = cast(ColumnsSelectorDetails, SingleColumnSelectorDetails(column))
    return ColumnsSelector(type=ColumnsSelectorType.SINGLECOLUMN, details=details)


class Step:
    """
    Single operation to be applied to data as part of the Dataflow.

    .. remarks::

        This should not be created directly. To create a new Step, use one of the methods of Dataflow or one of the builder classes.
    """
    def __init__(self, step_type: str, arguments: Dict[str, Any], local_data: Dict[str, Any] = None):
        self.id = uuid.uuid4()
        self.step_type = step_type
        self.arguments = arguments
        self.local_data = local_data
        self._block_data = None

    def __repr__(self, list_args=True):
        result = dedent("""\
        Step {{
          type: {step_type},\n""".format(**vars(self)))
        if list_args:
            result += "  arguments:" + indent(pformat(self.arguments, indent=2, compact=True), '  ') + "\n"
        result += "}"
        return result

    def __str__(self):
        return self.__repr__(False)

    def __deepcopy__(self, memodict=None):
        import copy
        new_step = Step(self.step_type, copy.deepcopy(self.arguments), copy.deepcopy(self.local_data))
        new_step.id = self.id
        new_step._block_data = self._block_data
        return new_step


def step_to_block_data(step: Step) -> AnonymousBlockData:
    return AnonymousBlockData(id=step.id,
                              type=step.step_type,
                              arguments=PropertyValues.from_pod(step.arguments),
                              local_data=PropertyValues.from_pod(step.local_data))


def steps_to_block_datas(steps: List[Step]) -> List[AnonymousBlockData]:
    return [step_to_block_data(s) for s in steps]
