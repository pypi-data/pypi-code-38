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

from typing import List, Union, Optional, Tuple, Any

import attr
import pydash
from attr import attrs, validators, Factory
from cortex_common import validators as custom_validators
from cortex_common.constants import CONTEXTS, ATTRIBUTES, VERSION, DESCRIPTIONS
from cortex_common.utils import unique_id, utc_timestamp, AttrsAsDict, describableAttrib, dict_to_attr_class, \
    dicts_to_classes, attr_class_to_dict

from .attribute_values import ListOfProfileAttributes, ProfileAttributeValue, BaseAttributeValue, \
    load_profile_attribute_value_from_dict

__all__ = [
    'ProfileAttributeClassifications',
    'BaseProfileAttribute',
    'ProfileAttribute',
    'HistoricProfileAttribute',
    'InferredProfileAttribute',
    'ObservedProfileAttribute',
    'DeclaredProfileAttribute',
    'AssignedProfileAttribute',
    'ProfileAttributeTypes',
    "ProfileAttributeType"
]

class ProfileAttributeClassifications(AttrsAsDict):
    """
    An "Enum" like class capturing the different classifications of attributes.
    """
    inferred = "inferred"
    declared = "declared"
    observed = "observed"
    assigned = "assigned"


@attrs(frozen=True)
class BaseProfileAttribute(object):
    """
    General representation of an attribute in a profile.
    """
    profileId = describableAttrib(type=str, validator=[validators.instance_of(str)], description="Which profile is the attribute applicable to?")
    profileSchema = describableAttrib(type=str, description="Which schema is this profile built off of?")
    classification = describableAttrib(type=str, description="Which is the classification of this attribute?")
    attributeKey = describableAttrib(type=str, description=DESCRIPTIONS.ATTRIBUTE_KEY)
    context = describableAttrib(type=str, description=DESCRIPTIONS.CONTEXT)

    def __iter__(self):
        return iter(attr_class_to_dict(self, hide_internal_attributes=True).items())


@attrs(frozen=True)
class HistoricProfileAttribute(BaseProfileAttribute):
    """
    Representation of all the Historic Values Associated with a Profile Attribute
    """
    attributeValues = describableAttrib(
        type=ListOfProfileAttributes,
        validator=[custom_validators.list_items_are_instances_of(BaseAttributeValue)],
        converter=lambda x: dicts_to_classes(x, BaseAttributeValue, dict_constructor=load_profile_attribute_value_from_dict),
        description="What are all the historic version of this attribute?"
    )
    attributeContext = describableAttrib(type=str, default=None, description="What is the context of the attribute?")
    timeline = describableAttrib(type=List[str], factory=list, description="When were all the different values created?")
    seqs = describableAttrib(type=List[int], factory=list, description="At what version of the profile was this attribute inserted?")
    ids = describableAttrib(type=List[str], default=Factory(unique_id), description=DESCRIPTIONS.ID)
    context = describableAttrib(type=str, default=CONTEXTS.PROFILE_ATTRIBUTE_HISTORIC, description=DESCRIPTIONS.CONTEXT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION, internal=True)


@attrs(frozen=True)
class ProfileAttribute(BaseProfileAttribute):
    """
    Representation of a Profile Attribute
    """
    attributeValue = describableAttrib(
        type=ProfileAttributeValue,  # type: ignore
        validator=[validators.instance_of(BaseAttributeValue)],
        converter=lambda x: dict_to_attr_class(x, BaseAttributeValue,
                                               dict_constructor=load_profile_attribute_value_from_dict),
        description="What value is captured by the attribute?"
    )
    # With Defaults
    id = describableAttrib(type=str, default=Factory(unique_id), description=DESCRIPTIONS.ID)
    seq = describableAttrib(type=Optional[int], default=None,
                            description="At what version of the profile was this attribute inserted?")
    createdAt = describableAttrib(type=str, factory=utc_timestamp, description=DESCRIPTIONS.CREATED_AT)
    version = describableAttrib(type=str, default=VERSION, description=DESCRIPTIONS.VERSION, internal=True)

    @classmethod
    def from_historic(cls, historic_attr: HistoricProfileAttribute) -> List[Optional['ProfileAttribute']]:
        historic_attr_dict = dict(historic_attr)
        return [
            dict_to_attr_class(
                pydash.merge(
                    pydash.omit(historic_attr_dict, "seqs", "attributeContext", "timeline", "seqs", "ids"),
                    {
                        "id": x[0],
                        "attributeValue": x[1],
                        "createdAt": x[2],
                        "seq": x[3],
                        "context": historic_attr_dict["attributeContext"],

                    }
                ),
                ProfileAttribute
            ) for x in zip(historic_attr_dict["ids"], historic_attr_dict["attributeValues"], historic_attr_dict["timeline"], historic_attr_dict["seqs"])
        ]

@attrs(frozen=True)
class InferredProfileAttribute(ProfileAttribute):
    """
    A Profile Attribute instantiated as an Inferred Attribute.
    """
    classification = describableAttrib(type=str, default=ProfileAttributeClassifications.inferred, description="What is the classification of this profile attribute?")
    context = describableAttrib(type=str, default=ATTRIBUTES.INFERRED_PROFILE_ATTRIBUTE, description=DESCRIPTIONS.CONTEXT)


@attrs(frozen=True)
class ObservedProfileAttribute(ProfileAttribute):
    """
    A Profile Attribute instantiated as an Observed Attribute.
    """
    classification = describableAttrib(type=str, default=ProfileAttributeClassifications.observed, description="What is the classification of this profile attribute?")
    context = describableAttrib(type=str, default=ATTRIBUTES.OBSERVED_PROFILE_ATTRIBUTE, description=DESCRIPTIONS.CONTEXT)


@attrs(frozen=True)
class DeclaredProfileAttribute(ProfileAttribute):
    """
    A Profile Attribute instantiated as an Declared Attribute.
    """
    classification = describableAttrib(type=str, default=ProfileAttributeClassifications.declared, description="What is the classification of this profile attribute?")
    context = describableAttrib(type=str, default=ATTRIBUTES.DECLARED_PROFILE_ATTRIBUTE, description=DESCRIPTIONS.CONTEXT)


@attrs(frozen=True)
class AssignedProfileAttribute(ProfileAttribute):
    """
   A Profile Attribute instantiated as an Assigned Attribute.
   """
    classification = describableAttrib(type=str, default=ProfileAttributeClassifications.assigned, description="What is the classification of this profile attribute?")
    context = describableAttrib(type=str, default=ATTRIBUTES.ASSIGNED_PROFILE_ATTRIBUTE, description=DESCRIPTIONS.CONTEXT)
    # attributeContext = describableAttrib(type=str, description="What is the context of the attribute?")


ProfileAttributeType = Union[
    DeclaredProfileAttribute,
    ObservedProfileAttribute,
    InferredProfileAttribute,
    AssignedProfileAttribute,
]

ProfileAttributeTypes: Tuple[Any, ...] = ProfileAttributeType.__args__  # type: ignore

OptionalProfileAttributeType = Optional[Union[
    DeclaredProfileAttribute,
    ObservedProfileAttribute,
    InferredProfileAttribute,
    AssignedProfileAttribute,
]]

def load_profile_attribute_from_dict(d: dict) -> OptionalProfileAttributeType:
    """
    Uses the context to load the appropriate profile attribute from a dict.
    :param d:
    :return:
    """
    context_to_attribute_type = {
        attr.fields(x).context.default: x
        for x in ProfileAttributeTypes
    }
    attribute_type_to_use = context_to_attribute_type.get(d.get("context"), None)
    if attribute_type_to_use is None:
        print("Unrecognized Attribute Type: {}".format(d.get("context")))
        return None
    return attribute_type_to_use(**d)
