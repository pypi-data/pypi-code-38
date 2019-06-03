"""
Copyright 2019 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import List, Union, Optional, Tuple, Type, Any
import json
import attr
import numpy as np
import pydash
import traceback
from attr import attrs, fields
from cortex_common.constants import ATTRIBUTE_VALUES, VERSION, DESCRIPTIONS
from cortex_common.utils import describableAttrib, dicts_to_classes, str_or_context, \
    converter_for_union_type, union_type_validator, dict_to_attr_class, attr_class_to_dict, numpy_type_to_python_type

from .events import EntityEvent
from .schemas import ProfileValueTypeSummary

# Bool is getting consumes by the union since it is a subclass of int ...

Void: Type[Any] = type(None)
PrimitiveJSONUnionType: Type[Any] = Union[str, int, float, bool, Void]
PrimitiveJSONTypes: Type[Any] = PrimitiveJSONUnionType.__args__
PrimitiveJSONTypeHandlers = pydash.merge(dict(zip(PrimitiveJSONTypes[:-1], PrimitiveJSONTypes[:-1])), {Void: lambda x: None})  # type: ignore

ObjectJSONUnionType: Type[Any] = Union[dict, Void]  # type: ignore
ObjectJSONTypes: Type[Any] = ObjectJSONUnionType.__args__  # type: ignore
ObjectJSONTypeHandlers = pydash.merge(dict(zip(ObjectJSONTypes[:-1], ObjectJSONTypes[:-1])), {Void: lambda x: None})  # type: ignore

ListJSONUnionType: Type[Any] = Union[list, Void]  # type: ignore
ListJSONTypes: Type[Any] = ListJSONUnionType.__args__  # type: ignore
ListJSONTypeHandlers = pydash.merge(dict(zip(ListJSONTypes[:-1], ListJSONTypes[:-1])), {Void: lambda x: None})  # type: ignore

JSONUnionTypes: Type[Any] = Union[str, int, float, bool, Void, dict, list]  # type: ignore

__all__ = [
    'BaseAttributeValue',
    'StringAttributeValue',
    'DecimalAttributeValue',
    'BooleanAttributeValue',
    'IntegerAttributeValue',
    # 'PrimitiveAttributeValue',
    'EntityAttributeValue',
    # 'ObjectAttributeValue',
    'ListAttributeValue',
    'RelationshipAttributeValue',
    'NumericAttributeValue',
    'NumericWithUnitValue',
    'PercentileAttributeValue',
    'PercentageAttributeValue',
    # 'AverageAttributeValue',
    'CounterAttributeValue',
    'TotalAttributeValue',
    # 'ConceptAttributeValue',
    "Dimension",
    'DimensionalAttributeValue',
    'WeightedAttributeValue',
    'ProfileAttributeValueTypes',
    "ProfileAttributeValue",
    "ListOfProfileAttributes",
]

@attrs(frozen=True)
class BaseAttributeValue(object):
    """
    Interface Attribute Values Need to Adhere to ...
    """
    value = describableAttrib(type=object, description="What value is captured in the attribute?")
    context = describableAttrib(type=str, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, description=DESCRIPTIONS.VERSION)

    @classmethod
    def detailed_schema_type(cls, *args, **kwargs) -> ProfileValueTypeSummary:
        return ProfileValueTypeSummary(  # type: ignore # wait until attr support ...
            outerType=fields(cls).context.default,
            innerTypes=[]
        )

    def __iter__(self):
        return iter(attr_class_to_dict(self, hide_internal_attributes=True).items())

# - [ ] Do we put versions on everything ... even it its meant to be nested? or only stuff saved in db?
@attrs(frozen=True)
class Dimension(object):
    """
    Representing a single dimension in a dimensional attribute ...
    """
    dimensionId = describableAttrib(type=str, description="What entity does this dimension represent?")
    dimensionValue = describableAttrib(type=Union[str, list, dict, int, bool, float], description="What is the value of this dimension?")


@attrs(frozen=True)
class StringAttributeValue(BaseAttributeValue):
    """
    Attributes that have an arbitrary string as their value
    """
    value = describableAttrib(
        type=str,
        default=None,
        validator=[attr.validators.instance_of(str), lambda s,a,v: v is not None],
        description="What is the value of the string itself?"
    )
    context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.STRING_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)


@attrs(frozen=True)
class DecimalAttributeValue(BaseAttributeValue):
    """
    Attributes that have an arbitrary decimal number as their value
    """
    value = describableAttrib(type=float, default=0.0, description="What is the value of the decimal number itself?")
    context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.DECIMAL_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)


@attrs(frozen=True)
class BooleanAttributeValue(BaseAttributeValue):
    """
    Attributes that have an arbitrary boolean as their value
    """
    value = describableAttrib(type=bool, default=True, description="What is the value of the boolean itself?")
    context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.BOOLEAN_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)


@attrs(frozen=True)
class IntegerAttributeValue(BaseAttributeValue):
    """
    Attributes that have an arbitrary integer number as their value
    """
    value = describableAttrib(type=int, default=0, description="What is the value of the integer number itself?")
    context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.INTEGER_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)


# @attrs(frozen=True)
# class PrimitiveAttributeValue(BaseAttributeValue):
#     """
#     Attributes that have an arbitrary JSON Object / Map / Hash as their value
#     """
#     value = describableAttrib(
#         type=PrimitiveJSONUnionType,
#         default=None,
#         validator=[
#             union_type_validator(PrimitiveJSONUnionType),
#             attr.validators.instance_of(PrimitiveJSONTypes)
#         ],
#         converter=converter_for_union_type(PrimitiveJSONUnionType, PrimitiveJSONTypeHandlers),
#         description="What is the value of the object itself?")
#     context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.PRIMITIVE_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
#     version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)


@attrs(frozen=True)
class EntityAttributeValue(BaseAttributeValue):
    """
    Capturing an raw EntityEvent as a profile attribute ...
    """
    value = describableAttrib(
        type=EntityEvent,
        default=None,
        converter=lambda x: dict_to_attr_class(x, EntityEvent),
        validator=[attr.validators.instance_of(EntityEvent)],
        description="What are the properties of the entity?"
    )
    context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.ENTITY_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)


# @attrs(frozen=True)
# class ObjectAttributeValue(BaseAttributeValue):
#     """
#     Attributes that have an arbitrary JSON Object / Map / Hash as their value
#     """
#     value = describableAttrib(
#         type=ObjectJSONUnionType,
#         validator=union_type_validator(ObjectJSONUnionType),
#         factory=dict,
#         converter=converter_for_union_type(ObjectJSONUnionType, ObjectJSONTypeHandlers),
#         description="What is the value of the object itself?")
#     context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.OBJECT_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
#     version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)


@attrs(frozen=True)
class ListAttributeValue(BaseAttributeValue):
    """
    Attributes that have an arbitrary JSON List / Array as their value.
    """
    value = describableAttrib(
        type=ListJSONUnionType,
        validator=union_type_validator(ListJSONUnionType),
        factory=list,
        converter=converter_for_union_type(ListJSONUnionType, ListJSONTypeHandlers),
        description="What is the value of the object itself?")
    context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.LIST_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)
    summary = describableAttrib(type=str, description=DESCRIPTIONS.ATTRIBUTE_SUMMARY)

    @summary.default  # type: ignore # waiting until attr support ...
    def summarize(self):
        template = "{} items exist within the list."
        if self.value is None:
            return template.format(0)
        return template.format(len(self.value))

    @classmethod
    def detailed_schema_type(cls, *args, typeOfItems:Optional[Union[str,type]]=None, **kwargs) -> ProfileValueTypeSummary:
        return ProfileValueTypeSummary(  # type: ignore # waiting for attr support ...
            outerType = fields(cls).context.default,
            innerTypes = [
                ProfileValueTypeSummary(outerType=str_or_context(typeOfItems))  # type: ignore # waiting for attr support ...
            ]
        )


@attrs(frozen=True)
class RelationshipAttributeValue(BaseAttributeValue):
    """
    Representing the content of a percentage attribute ...
    """
    value = describableAttrib(type=str, description="What is the id of the related concept to the profile?")
    relatedConceptType = describableAttrib(type=str, description="What is the type of the related concept?")
    relationshipType = describableAttrib(type=str, description="How is the related concept related to the profile? What is the type of relationship?")
    relationshipTitle = describableAttrib(type=str, description="What is a short, human readable description of the relationship between the profile and the related concept?")
    relatedConceptTitle = describableAttrib(type=str, description="What is a short, human readable description of the related concept to the profile?")
    relationshipProperties = describableAttrib(type=dict, factory=dict, description="What else do we need to know about the relationship?")
    context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.RELATIONSHIP_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)
    summary = describableAttrib(type=str, description=DESCRIPTIONS.ATTRIBUTE_SUMMARY)

    @summary.default  # type: ignore # waiting until attr support ...
    def summarize(self):
        return "Profile-{}->{}".format(self.relationshipTitle, self.relatedConceptTitle)


@attrs(frozen=True)
class NumericAttributeValue(BaseAttributeValue):
    """
    Representing the content of a numeric attribute ...
    """
    value = describableAttrib(type=Union[int, float], description="What is the number that we are interested in?")
    context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.NUMERICAL_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)
    summary = describableAttrib(type=str, description=DESCRIPTIONS.ATTRIBUTE_SUMMARY)

    @summary.default  # type: ignore # waiting until attr support ...
    def summarize(self):
        return "{:.3f}".format(self.value)


@attrs(frozen=True)
class NumericWithUnitValue(NumericAttributeValue):
    """
    Representing the content of a numeric attribute as a measuring unit ...
    """
    value = describableAttrib(type=Union[int, float], default=0, description="What numeric value is captured by this attribute value?")
    unitId = describableAttrib(type=str, default=None, description="What is the unique id of the unit? i.e USD, GBP, %, ...")
    unitContext = describableAttrib(type=str, default=None, description="What type of unit is this? i.e currency, population of country, ...")
    unitTitle = describableAttrib(type=str, default=None, description="What is the symbol desired to represent the unit?")
    unitIsPrefix = describableAttrib(type=bool, default=None, description="Should the symbol be before or after the unit?")
    summary = describableAttrib(type=str, description=DESCRIPTIONS.ATTRIBUTE_SUMMARY)

    @summary.default  # type: ignore # waiting until attr support ...
    def summarize(self):
        return "{}{}{}".format(
            ("{}".format(self.unitTitle) if (self.unitIsPrefix and self.unitTitle) else ""),
            ("{}".format(self.value)),
            ("{}".format(self.unitTitle) if (self.unitTitle and not self.unitIsPrefix) else "")
        )

@attrs(frozen=True)
class PercentileAttributeValue(NumericAttributeValue):
    """
    Representing the content of a percentile attribute ...
    """
    value = describableAttrib(type=float, description="What is the numeric value of the percentile?")
    context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.PERCENTILE_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)
    summary = describableAttrib(type=str, description=DESCRIPTIONS.ATTRIBUTE_SUMMARY)

    @summary.default  # type: ignore # waiting until attr support ...
    def summarize(self):
        return "{:.3f}%%".format(self.value)


@attrs(frozen=True)
class PercentageAttributeValue(NumericAttributeValue):
    """
    Representing the content of a percentage attribute ...
    """
    value = describableAttrib(type=float, description="What numeric value of the percentage?")
    context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.PERCENTAGE_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)
    summary = describableAttrib(type=str, description=DESCRIPTIONS.ATTRIBUTE_SUMMARY)

    @summary.default  # type: ignore # waiting until attr support ...
    def summarize(self):
        return "{:.2f}%".format(self.value)


# @attrs(frozen=True)
# class AverageAttributeValue(NumericAttributeValue):
#     """
#     Representing the content of a percentage attribute ...
#     """
#     value = describableAttrib(type=float, description="What numeric value of the average?")
#     context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.AVERAGE_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
#     version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)
#     summary = describableAttrib(type=str, description=DESCRIPTIONS.ATTRIBUTE_SUMMARY)
#
#     @summary.default  # type: ignore # waiting until attr support ...
#     def summarize(self):
#         return "Avg: {:.3f}".format(self.value)


@attrs(frozen=True)
class CounterAttributeValue(NumericWithUnitValue):
    """
    Representing the content of a counter attribute ...
    """
    value = describableAttrib(type=int, default=0, description="What is the numeric value of the current total?")
    context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.COUNTER_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)
    summary = describableAttrib(type=str, description=DESCRIPTIONS.ATTRIBUTE_SUMMARY)

    @summary.default  # type: ignore # waiting until attr support ...
    def summarize(self):
        return "{}{}{}".format(
            ("{}".format(self.unitTitle) if (self.unitIsPrefix and self.unitTitle) else ""),
            ("{}".format(self.value)),
            ("{}".format(self.unitTitle) if (self.unitTitle and not self.unitIsPrefix) else "")
        )

@attrs(frozen=True)
class TotalAttributeValue(NumericWithUnitValue):
    """
    Representing the content of a total attribute ...
    """
    value = describableAttrib(type=float, default=0.0, description="What is the current total?")
    context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.TOTAL_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)
    summary = describableAttrib(type=str, description=DESCRIPTIONS.ATTRIBUTE_SUMMARY)

    @summary.default  # type: ignore # waiting until attr support ...
    def summarize(self):
        return "{}{}{}".format(
            ("{}".format(self.unitTitle) if (self.unitIsPrefix and self.unitTitle) else ""),
            ("{}".format(self.value)),
            ("{}".format(self.unitTitle) if (self.unitTitle and not self.unitIsPrefix) else "")
        )

# @attrs(frozen=True)
# class ConceptAttributeValue(BaseAttributeValue):
#     """
#     Representing a concept ...
#     """
#     value = describableAttrib(
#         type=str,
#         default=None,
#         validator=[attr.validators.instance_of(str)],
#         description="What is the name of the concept?"
#     )
#     context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.CONCEPT_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
#     version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)


@attrs(frozen=True)
class DimensionalAttributeValue(BaseAttributeValue):
    """
    Representing the content of a 2-dimensional attribute.
    """

    value = describableAttrib(
        type=List[Dimension],
        converter=lambda x: dicts_to_classes(x, Dimension),
        description="What are the different dimensions captured in the attribute value?"
    )
    contextOfDimension = describableAttrib(type=str, description="What type are the dimensions?")
    contextOfDimensionValue = describableAttrib(type=str, description="What type are the values associated with the dimension?")
    context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.DIMENSIONAL_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)
    summary = describableAttrib(type=str, description=DESCRIPTIONS.ATTRIBUTE_SUMMARY)

    @summary.default  # type: ignore # waiting until attr support ...
    def summarize(self):
        average = None
        max = None
        min = None
        # TODO ... right now the value ... is just a value ... not an NumericAttributeValue ...
        if all(map(lambda x: isinstance(x.dimensionValue, (int, float)), self.value)):
            average = np.mean(list(map(lambda x: x.dimensionValue, self.value)))
            max = np.max(list(map(lambda x: x.dimensionValue, self.value)))
            min = np.min(list(map(lambda x: x.dimensionValue, self.value)))
        return "{}{}{}{}".format(
            ("Dimensions: {}".format(len(self.value))),
            (", Avg: {:.3f}".format(average) if average else ""),
            (", Min: {:.3f}".format(min) if min else ""),
            (", Max: {:.3f}".format(max) if max else "")
        )

    @classmethod
    def detailed_schema_type(
            cls, *args,
            firstDimensionType:Optional[Union[str,type]]=None,
            secondDimensionType:Optional[Union[str,type]]=None,
            **kwargs) -> ProfileValueTypeSummary:
        return ProfileValueTypeSummary(  # type: ignore # waiting for attr support ...
            outerType = fields(cls).context.default,
            innerTypes = [
                ProfileValueTypeSummary(outerType=str_or_context(firstDimensionType)),  # type: ignore # waiting for attr support ...
                ProfileValueTypeSummary(outerType=str_or_context(secondDimensionType))  # type: ignore # waiting for attr support ...
            ]
        )


@attrs(frozen=True)
class WeightedAttributeValue(BaseAttributeValue):
    """
    Attributes that captures a weighted value.
    """
    value = describableAttrib(type=dict, factory=dict, description="What is the value of the weighted object?")
    weight = describableAttrib(type=float, default=1.00, description="How likely is it beleived that this value encapsulates reality?")
    context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.WEIGHTED_PROFILE_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)

    @classmethod
    def detailed_schema_type(cls, *args,
                             type_of_weighted_value:Optional[Union[str,type]]=None,
                             **kwargs) -> ProfileValueTypeSummary:
        return ProfileValueTypeSummary(  # type: ignore # waiting for attr support ...
            outerType = fields(cls).context.default,
            innerTypes = [
                ProfileValueTypeSummary(outerType=str_or_context(type_of_weighted_value)),  # type: ignore # waiting for attr support ...
            ]
        )

@attrs(frozen=True)
class StatisticalSummaryValue(object):
    datapoints = describableAttrib(type=int, default=0, description="How many datapoints were considered?")
    min = describableAttrib(type=Optional[float], default=None, description="What is the minimum value considered in the data points?")
    max = describableAttrib(type=Optional[float], default=None, description="What is the maximum value considered in the data points?")
    average = describableAttrib(type=Optional[float], default=None, description="What is the average of the data points?")
    stddev = describableAttrib(type=Optional[float], default=None, description="What is the std deviation of the data points?")


@attrs(frozen=True)
class StatisticalSummaryAttributeValue(BaseAttributeValue):
    """
    Representing the content of a percentage attribute ...
    """
    value = describableAttrib(
        type=StatisticalSummaryValue,
        converter=lambda x: dict_to_attr_class(x, StatisticalSummaryValue),
        description="What is the statistical summary for a given range of data?"
    )
    context = describableAttrib(type=str, default=ATTRIBUTE_VALUES.STATISTICAL_SUMMARY_ATTRIBUTE_VALUE, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION)
    summary = describableAttrib(type=str, description=DESCRIPTIONS.ATTRIBUTE_SUMMARY)

    @summary.default  # type: ignore # waiting for attr support ...
    def summarize(self):
        return "{:.3f} points: {:.3f}..{:.3f}..{:.3f}".format(
            self.value.datapoints, self.value.min, self.value.average, self.value.max
        )

    @staticmethod
    def fromListOfValues(values:List[Union[int, float]]) -> 'StatisticalSummaryAttributeValue':
        return StatisticalSummaryAttributeValue(  # type: ignore # waiting for attr support ...
            value=StatisticalSummaryValue(  # type: ignore # waiting for attr support ...
                datapoints=numpy_type_to_python_type(np.size(values)),
                min=numpy_type_to_python_type(np.min(values)),
                max=numpy_type_to_python_type(np.max(values)),
                average=numpy_type_to_python_type(np.average(values)),
                stddev=numpy_type_to_python_type(np.std(values)),
            )
        )


ProfileAttributeValue = Union[
    StringAttributeValue,
    DecimalAttributeValue,
    BooleanAttributeValue,
    IntegerAttributeValue,
    # PrimitiveAttributeValue,
    EntityAttributeValue,
    # ObjectAttributeValue,
    ListAttributeValue,
    RelationshipAttributeValue,
    PercentileAttributeValue,
    PercentageAttributeValue,
    # AverageAttributeValue,
    CounterAttributeValue,
    TotalAttributeValue,
    # ConceptAttributeValue,
    DimensionalAttributeValue,
    WeightedAttributeValue,
    StatisticalSummaryAttributeValue,
]

# MyPy Bug ... Cant use variable inside union ... it throws things off!
ListOfProfileAttributes = List[Union[
    StringAttributeValue,
    DecimalAttributeValue,
    BooleanAttributeValue,
    IntegerAttributeValue,
    # PrimitiveAttributeValue,
    EntityAttributeValue,
    # ObjectAttributeValue,
    ListAttributeValue,
    RelationshipAttributeValue,
    PercentileAttributeValue,
    PercentageAttributeValue,
    # AverageAttributeValue,
    CounterAttributeValue,
    TotalAttributeValue,
    # ConceptAttributeValue,
    DimensionalAttributeValue,
    WeightedAttributeValue,
    StatisticalSummaryAttributeValue,
]]

ProfileAttributeValueTypes: Tuple[Any, ...] = ProfileAttributeValue.__args__ # type: ignore


def load_profile_attribute_value_from_dict(d:dict) -> Optional[BaseAttributeValue]:
    """
    Uses the context to load the appropriate profile attribute value type from a dict.
    :param d:
    :return:
    """
    context_to_value_type = {
        attr.fields(x).context.default: x
        for x in ProfileAttributeValueTypes
    }
    value_type_to_use = context_to_value_type.get(d.get("context"), None)
    if value_type_to_use is None:
        print("Unrecognized Attribute Value Type: {}".format(d.get("context")))
        return None
    try:
        return value_type_to_use(**d)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print(traceback.format_tb(e.__traceback__))
        print(json.dumps(d, indent=4))
        return None


# TODO
# class PlacementAttributeContent 1st, 2nd, 3rd ...
# class {Rank/Score}AttributeContent


if __name__ == '__main__':
    print(ProfileAttributeValueTypes)