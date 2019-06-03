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

from typing import List

from attr import attrs, validators
from cortex_common import validators as custom_validators
from cortex_common.constants import CONTEXTS, VERSION, DESCRIPTIONS
from cortex_common.types.attributes import load_profile_attribute_from_dict
from cortex_common.utils import utc_timestamp
from cortex_common.utils.attr_utils import describableAttrib, dicts_to_classes, attr_class_to_dict

from .attributes import ProfileAttributeType, ProfileAttributeTypes, HistoricProfileAttribute

__all__ = [
    'Profile',
    'HistoricProfile',
]

@attrs(frozen=True)
class _Profile(object):
    """
    Base profile ...
    """
    profileId = describableAttrib(type=str, validator=[validators.instance_of(str)], description="What is the id of the profile?")
    profileSchema = describableAttrib(type=str, description="What schema was used to build this profile?")
    version = describableAttrib(
        type=int,
        validator=[validators.instance_of(int)],
        default=-1,
        description="What version of attributes is this profile based off of?"
    )
    attributes = describableAttrib(
        type=List,  # type: ignore
        factory=list,
        description="What are all the historic version of this attribute?"
    )
    # With Defaults
    createdAt = describableAttrib(type=str, factory=utc_timestamp, description=DESCRIPTIONS.CREATED_AT)
    updatedAt = describableAttrib(type=str, factory=utc_timestamp, description=DESCRIPTIONS.UPDATED_AT)
    # version = describableAttrib(type=str, default=VERSION, description="How many times has this profile been updated?")
    context = describableAttrib(type=str, default=CONTEXTS.PROFILE, description=DESCRIPTIONS.CONTEXT)

    def __iter__(self):
        return iter(attr_class_to_dict(self, hide_internal_attributes=True).items())


@attrs(frozen=True)
class Profile(_Profile):
    """
    A representation of an entity's profile with pointers to specific attributes.
    """
    attributes = describableAttrib(
        type=List[ProfileAttributeType],  # type: ignore
        factory=list,
        validator=[custom_validators.list_items_are_instances_of(ProfileAttributeTypes)],  # type: ignore
        converter=lambda x: dicts_to_classes(x, ProfileAttributeType, dict_constructor=load_profile_attribute_from_dict),  # type: ignore
        description="What are all of the attribute in the profile along with their latest values?"
    )


@attrs(frozen=True)
class HistoricProfile(_Profile):
    """
    A representation of an entity's profile with pointers to specific attributes.
    """
    attributes = describableAttrib(
        type=List[HistoricProfileAttribute],  # type: ignore
        factory=list,
        validator=[custom_validators.list_items_are_instances_of(HistoricProfileAttribute)],  # type: ignore
        converter=lambda x: dicts_to_classes(x, HistoricProfileAttribute),  # type: ignore
        description="What are all of the attribute in the profile along with their historic values?"
    )
