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

from typing import Optional

from attr import attrs
from cortex_common.constants import DESCRIPTIONS
from cortex_common.utils import describableAttrib

__all__ = [
    'ProfileSummary',
    'ProfileVersionSummary',
    'ProfileAttributeSummary'
]

@attrs(frozen=True)
class ProfileSummary(object):
    """
    Summary of a Profile ...
    """
    profileId = describableAttrib(type=str, description="What is the id for this profile?")
    profileSchema = describableAttrib(type=str, description="What is the id of the schema applied to this profile?")
    version = describableAttrib(type=int, description="How many modifications have been made to the profile?")
    updatedAt = describableAttrib(type=str, description="When was the most recent attribute appended to this profile?")
    createdAt = describableAttrib(type=Optional[str], default=None, description="When was the first attribute appended to this profile?")


@attrs(frozen=True)
class ProfileVersionSummary(object):
    """
    Summary of a specific version of a profile ...
    """
    profileId = describableAttrib(type=str, description="What is the id of the profile this version is relevant to?")
    schemaId = describableAttrib(type=str, description="What is the id of the schema that the profile adheres to?")
    version = describableAttrib(type=str, description="What is the version number of the profile?")
    createdAt = describableAttrib(type=str, description=DESCRIPTIONS.CREATED_AT)


@attrs(frozen=True)
class ProfileAttributeSummary(object):
    """
    Summary of an attribute ...
    """
    profileId = describableAttrib(type=str, description="What is the id of the profile this attribute is relevant to?")
    schemaId = describableAttrib(type=str, description="What is the id of the schema that the profile adheres to?")
    attributeKey = describableAttrib(type=str, description=DESCRIPTIONS.ATTRIBUTE_KEY)
    attributeType = describableAttrib(type=str, description="What type is this attribute?")
    attributeValueType = describableAttrib(type=str, description="What type is the value associated with this attribute?")
    createdAt = describableAttrib(type=str, description=DESCRIPTIONS.CREATED_AT)
    updatedAt = describableAttrib(type=str, description=DESCRIPTIONS.UPDATED_AT)