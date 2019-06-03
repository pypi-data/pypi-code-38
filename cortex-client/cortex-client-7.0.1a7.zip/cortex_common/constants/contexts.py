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

from cortex_common.utils import AttrsAsDict

__all__ = [
    "SCHEMA_CONTEXTS",
    "ATTRIBUTES",
    "ATTRIBUTE_VALUES",
    "CONTEXTS",
]

class SCHEMA_CONTEXTS(AttrsAsDict):
    """
    An "Enum" like class capturing the contexts of classes relevant to profile schemas.
    """
    PROFILE_SCHEMA="cortex/profile-schema"
    PROFILE_ATTRIBUTE_TAG="cortex/profile-attribute-tag"
    PROFILE_ATTRIBUTE_GROUP="cortex/profile-attribute-group"
    PROFILE_ATTRIBUTE_FACET="cortex/profile-attribute-facet"
    PROFILE_ATTRIBUTE_TAXONOMY="cortex/profile-attribute-taxonomy"


class ATTRIBUTES(AttrsAsDict):
    """
    An "Enum" like class capturing the contexts of classes relevant to different types of profile attributes.
    """
    DECLARED_PROFILE_ATTRIBUTE = "cortex/attributes-declared"
    OBSERVED_PROFILE_ATTRIBUTE = "cortex/attributes-observed"
    INFERRED_PROFILE_ATTRIBUTE = "cortex/attributes-inferred"
    ASSIGNED_PROFILE_ATTRIBUTE = "cortex/attributes-assigned"


class ATTRIBUTE_VALUES(AttrsAsDict):
    """
    An "Enum" like class capturing the contexts of classes relevant to different types of values that can be captured in
    profile attributes.
    """
    RELATIONSHIP_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-relationship"
    # OBJECT_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-object"
    LIST_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-list"
    STRING_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-string"
    INTEGER_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-integer"
    DECIMAL_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-decimal"
    BOOLEAN_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-boolean"
    PRIMITIVE_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-primitive"
    NUMERICAL_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-numerical"
    PERCENTILE_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-percentile"
    PERCENTAGE_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-percentage"
    # AVERAGE_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-average"
    TOTAL_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-total"
    COUNTER_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-counter"
    WEIGHTED_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-weighted"
    CLASSIFICATION_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-classification"
    DIMENSIONAL_PROFILE_ATTRIBUTE_VALUE = "cortex/attribute-value-dimensional"
    # CONCEPT_ATTRIBUTE_VALUE = "cortex/attribute-value-concept"
    INSIGHT_ATTRIBUTE_VALUE = "cortex/attribute-value-insight"
    ENTITY_ATTRIBUTE_VALUE = "cortex/attribute-value-entity"
    STATISTICAL_SUMMARY_ATTRIBUTE_VALUE = "cortex/attribute-value-statsummary"


class CONTEXTS(AttrsAsDict):
    """
    An "Enum" like class capturing the contexts of general classes
    """
    SESSION="cortex/session"
    INSIGHT="cortex/insight"
    INSIGHT_CONCEPT_TAG="cortex/insight-concept-tag"
    INSIGHT_TAG_RELATIONSHIP="cortex/insight-concept-relationship"
    INSIGHT_TAG_RELATED_TO_RELATIONSHIP="cortex/insight-relatedTo-concept"
    INTERACTION = "cortex/interaction"
    INSIGHT_INTERACTION="cortex/insight-interaction"
    LINK = "cortex/link"
    PROFILE_ATTRIBUTE_HISTORIC = 'cortex/profile-attribute-historic'
    PROFILE_SNAPSHOT="cortex/profile-snapshot"
    PROFILE="cortex/profile"
    PROFILE_COMMIT="cortex/profile-commit"
    DAY="cortex/time-day"
