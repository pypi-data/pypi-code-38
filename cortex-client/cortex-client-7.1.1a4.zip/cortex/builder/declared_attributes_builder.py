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

from typing import List, Optional, Union, Callable

import pandas as pd

from cortex_common.types import DeclaredProfileAttribute, IntegerAttributeValue, DecimalAttributeValue, \
    StringAttributeValue, BooleanAttributeValue, ListAttributeValue
from cortex_common.utils import df_to_records, utc_timestamp, state_modifier, unique_id

__all__ = [
    'DeclaredAttributesBuilder',
]


def built_in_attribute_value_constructor(value:Union[int, float, str, bool, list]) -> Union[IntegerAttributeValue,
                                                                                            DecimalAttributeValue,
                                                                                            StringAttributeValue,
                                                                                            BooleanAttributeValue,
                                                                                            ListAttributeValue,
                                                                                            StringAttributeValue]:
    """
    Turns general python values into Basic Profile Attribute Values ...
    :param value:
    :return:
    """
    if isinstance(value, int):
        return IntegerAttributeValue(value=value)
    if isinstance(value, float):
        return DecimalAttributeValue(value=value)
    if isinstance(value, str):
        return StringAttributeValue(value=value)
    if isinstance(value, bool):
        return BooleanAttributeValue(value=value)
    if isinstance(value, list):
        return ListAttributeValue(value=value)


def derive_declared_attributes_from_key_value_df(
        df:pd.DataFrame,
        schema_id:str,
        profile_id_column:str="profileId",
        key_column:str="key",
        value_column:str="value",
        attribute_value_class:Union[type, Callable]=built_in_attribute_value_constructor
    ) -> List[DeclaredProfileAttribute]:
    """
    Derives attributes from a dataframe that is structured as follows ....
    >>> import pandas as pd
    >>> df = pd.DataFrame([
    >>>    {"profileId": "p1", "key": "profile.name", "value": "Jack"},
    >>>    {"profileId": "p1", "key": "profile.age", "value": 25},
    >>>    {"profileId": "p2", "key": "profile.name", "value": "Jill"},
    >>>    {"profileId": "p2", "key": "profile.age", "value": 26},
    >>> ])

    :param df: The data frame with all of the attributes ...
    :param schema_id: The type of the profile that these attributes are representing.
    :param profile_id_column: The column with the profile Id
    :param key_column: The column containing the key we want to use as the attributeKey
    :param value_column: The column that contains the value of the attribute
    :param attribute_value_class: The constructor to construct the attribute Value Class with the Value column in the df.
    :return: List of Declared Attributes derived from the dataframe.
    """
    return [
        DeclaredProfileAttribute(
            id=unique_id(),
            profileId=str(rec[profile_id_column]),
            profileSchema=schema_id,
            attributeKey=rec[key_column],
            createdAt=utc_timestamp(),
            attributeValue=attribute_value_class(rec[value_column]),
        )
        for rec in df_to_records(df)
    ]


def derive_declared_attributes_from_value_only_df(
        declarations:pd.DataFrame,
        schema_id: str,
        profile_id_column:str="profileId",
        key:Optional[str]=None,
        value_column:str="value",
        attribute_value_class:Union[type, Callable]=built_in_attribute_value_constructor
    ) -> List[DeclaredProfileAttribute]:
    """
    Derives attributes from a dataframe that is structured as follows ....
    >>> import pandas as pd
    >>> df = pd.DataFrame([
    >>>     {"profileId": "p3", "name": "Adam", "age": 45},
    >>>     {"profileId": "p4", "name": "Eve", "age": 46},
    >>> ])

    :param df: The data frame with all of the attributes ...
    :param schema_id: The type of the profile that these attributes are representing.
    :param profile_id_column: The column with the profile Id
    :param key: The key to use as the attribute key ... if no key is specified, the name of the value column is used ...
    :param value_column: The column that contains the value of the attribute
    :param attribute_value_class: The constructor to construct the Attribute Value Class from the value
                                  stored in the value column for a particular attribute.
    :return: List of Declared Attributes derived from the dataframe.
    """
    return [
        DeclaredProfileAttribute(
            id=unique_id(),
            profileId=str(rec[profile_id_column]),
            profileSchema=schema_id,
            attributeKey=key if key else value_column,
            createdAt=utc_timestamp(),
            attributeValue=attribute_value_class(rec[value_column])
        )
        for rec in df_to_records(declarations)
    ]


class DeclaredAttributesBuilder(object):
    """
    Helps with building declared attributes from various sources including pandas dataframes.
    """

    def __init__(self):
        self.attributes = [ ]

    @state_modifier(derive_declared_attributes_from_key_value_df, (lambda self, results: self.attributes.extend(results)))
    def append_attributes_from_kv_df(self, *args, **kwargs):
        """
        See :func:`.derive_declared_attributes_from_key_value_df` for input argument instructions.
        :return: The builder itself, after its state has been modified with the appended attributes ...
        """
        return self

    @state_modifier(derive_declared_attributes_from_value_only_df, (lambda self, results: self.attributes.extend(results)))
    def append_attributes_from_column_in_df(self, *args, **kwargs):
        """
        See :func:`.derive_declared_attributes_from_value_only_df` for input argument instructions.
        :return: The builder itself, after its state has been modified with the appended attributes ...
        """
        return self

    def get(self) -> List[DeclaredProfileAttribute]:
        return self.attributes


if __name__ == '__main__':

    # TODO ... turn this into an example ...

    kv_df = pd.DataFrame([
       {"profileId": "p1", "key": "profile.name", "value": "Jack"},
       {"profileId": "p1", "key": "profile.age", "value": 25},
       {"profileId": "p2", "key": "profile.name", "value": "Jill"},
       {"profileId": "p2", "key": "profile.age", "value": 26},
    ])

    value_only_df = pd.DataFrame([
        {"profileId": "p3", "name": "Adam", "age": 45},
        {"profileId": "p4", "name": "Eve", "age": 46},
    ])

    attributes = (
        DeclaredAttributesBuilder()
            .append_attributes_from_kv_df(kv_df, "cortex/Account")
            .append_attributes_from_column_in_df(value_only_df, "cortex/Account", key="profile.name", value_column="name")
            .append_attributes_from_column_in_df(value_only_df, "cortex/Account", key="profile.age", value_column="age")
            .get()
    )

    print("{} total attributes generated.".format(len(attributes)))
    for attribute in attributes:
        print(attribute)

    # print(DeclaredAttributesBuilder().append_attributes_from_kv_df.__doc__)
    # print(DeclaredAttributesBuilder().append_attributes_from_column_in_df.__doc__)
