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

from attr import attrs, validators

from cortex_common.utils import describableAttrib, dict_to_attr_class, attr_class_to_dict, time_converter


__all__ = [
    'EventSource',
    'EntityEvent',
]

@attrs(frozen=True)
class EventSource(object):
    """
    Representing the source of an Entity Event ...
    """
    title = describableAttrib(type=str)
    description = describableAttrib(type=Optional[str])
    rights = describableAttrib(type=Optional[str])
    category = describableAttrib(type=Optional[str])
    sector = describableAttrib(type=Optional[str])
    region = describableAttrib(type=Optional[str])
    creator = describableAttrib(type=Optional[str])
    publisher = describableAttrib(type=Optional[str])
    language = describableAttrib(type=Optional[str])
    url = describableAttrib(type=Optional[str])


@attrs(frozen=True)
class EntityEvent(object):
    """
    Representing an Event that Modifies a representation of an Entity.
    """
    event = describableAttrib(type=Optional[str], default=None, description="What is the name of the event?")
    entityId = describableAttrib(type=Optional[str], default=None, description="Does this event relate an entity to another entity?")
    entityType = describableAttrib(type=Optional[str], default=None, description="What is the type of the entity?")
    properties = describableAttrib(type=dict, factory=dict, description="What are the properties associated with this event?")
    meta = describableAttrib(type=dict, factory=dict, description="What is custom metadata associated with this event?")
    # With Defaults ...
    targetEntityId = describableAttrib(type=Optional[str], default=None, description="Does this event relate an entity to another entity?")
    targetEntityType = describableAttrib(type=Optional[str], default=None, description="What is the type of entity this event relates to?")
    eventLabel = describableAttrib(type=Optional[str], default=None, description="What is the name of the event?")
    eventTime = describableAttrib(
        type=Optional[int],
        default=None,  # The timestamp used in node is 1k times the arrow timestamp.
        converter=time_converter,
        description="When did the event occur?"
    )
    source = describableAttrib(
        type=Optional[EventSource],
        default=None,  # The timestamp used in node is 1k times the arrow timestamp.
        converter=lambda x: dict_to_attr_class(x, EventSource),
        description="What is the name of the event?"
    )

    def __iter__(self):
        # Skipping nulls ... so that the JS defaults kick into place ...
        return iter(attr_class_to_dict(self, hide_internal_attributes=True, skip_nulls=True).items())