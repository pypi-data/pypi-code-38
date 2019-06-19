# -*- coding: utf-8 -*-
# Copyright (c) 2019 Dzmitry Maliuzhenets; MIT License
"""Module for working with annotations as strings.

Example:
    >>> from telegrambotapiwrapper.annotation import AnnotationWrapper
    >>> anno  = AnnotationWrapper("List[InlineKeyboardButton]")
    >>> anno.is_optional
    False
    >>> anno.is_list
    True
    >>> anno.is_list_of_list
    False
    >>> anno.inner_part_of_list
    'InlineKeyboardButton'
"""

from __future__ import annotations

import re
from collections import UserString
from typing import List


class AnnotationWrapper(UserString):  # pylint: disable=R0901
    """Wrapper around type annotation."""

    opt_field_re = re.compile(r'^Optional\[')
    list_field_re = re.compile(r'^List\[')
    list_of_list_re = re.compile(r'^List\[List\[')
    union_field_re = re.compile(r'^Union\[')
    inner_part_of_list_of_list_re = re.compile(r'^List\[List\[(.+)\]\]$')
    inner_part_of_opt_re = re.compile(r'^Optional\[(.+)\]$')
    inner_part_of_union_re = re.compile(r'^Union\[(.+)\]$')
    inner_part_of_list_re = re.compile(r'^List\[(.+)\]$')

    @property
    def is_simple(self) -> bool:
        """Is int, bool, float or str.

        Whether a type is defined by annotation is one of the following types:
        int, bool, float, str

        Notes:
            1)
                str -> True
                User -> False
                bool -> True
                Message -> False
        """
        return self.data in ('int', 'bool', 'float', 'str')

    @property
    def is_simple_in_opt(self) -> bool:
        """Is int, bool, float, str in Optional.

        Notes:
            1)
                Optional[str] -> True
                Optional[User] -> False
                Optional[bool] -> True
                Optional[Message] -> False

        """
        return self.inner_part_of_optional.is_simple

    @property
    def is_simple_in_opt_and_not_opt(self) -> bool:
        """Is int, bool, float, str in Optional and not Optional.

        Notes:
            1)
                str -> True
                User -> False
                bool -> True
                Message -> False
                Optional[str] -> True
                Optional[User] -> False
                Optional[bool] -> True
                Optional[Message] -> False
        """
        if self.is_optional:  # pylint: disable=R1705
            return self.is_simple_in_opt
        else:
            return self.is_simple

    @property
    def is_list_of_list(self) -> bool:
        """Is List[List[xxx]]

        Whether the type defined by the annotation is of the type of the
        List[List [...]] type.

        Notes:
            1)
                str -> False
                User -> False
                Optional[str] -> False
                Optional[User] -> False
                List[PhotoSize] -> False
                List[List[InlineKeyboardButton]]-> True

        """
        return bool(AnnotationWrapper.list_of_list_re.match(self.data))

    @property
    def is_optional(self) -> bool:
        """Is annotated type optional.

        Notes:
            1)
                ShippingAddress -> False
                bool -> False
                Optional[ShippingAddress] -> True
                Optional[List[PhotoSize]] -> True,
                Optional[Union[InputFile, str]] -> True,
        """
        return bool(AnnotationWrapper.opt_field_re.match(self.data))

    @property
    def inner_part_of_optional(self) -> AnnotationWrapper:
        """The inner part of the annotation type Optional[].

        Notes:
            1)
                Optional[User] -> User
                Optional[int] -> int
                Optional[List[MessageEntity]] -> List[MessageEntity]
        """
        return AnnotationWrapper(
            re.search(AnnotationWrapper.inner_part_of_opt_re,
                      self.data).group(1))

    @property
    def inner_part_of_list_of_list(self) -> AnnotationWrapper:
        """The inner part of the annotation type List[List[xxx]].

        Notes:
            1)
                List[List[KeyboardButton]] -> KeyboardButton
        """
        return AnnotationWrapper(
            re.search(AnnotationWrapper.inner_part_of_list_of_list_re,
                      self.data).group(1))

    @property
    def inner_part_of_union(self) -> AnnotationWrapper:
        """The inner part of the annotation type Union[xxx].

        Notes:
            1)
                Union[User] -> 'User'
                Union[User, bool] -> 'User, bool'
        """
        return AnnotationWrapper(
            re.search(AnnotationWrapper.inner_part_of_union_re,
                      self.data).group(1))

    @property
    def inner_part_of_list(self) -> AnnotationWrapper:
        """The inner part of the annotation type List[xxx].

        Notes:
            1)
                List[User] -> 'User'
                List[User, bool] -> 'User, bool'
                List[List[PhotoSize]] -> List[PhotoSize],
        """
        return AnnotationWrapper(
            re.search(AnnotationWrapper.inner_part_of_list_re,
                      self.data).group(1))

    @property
    def types_in_union(self) -> List[AnnotationWrapper]:
        """Annotations inside annotations like Union[xxx, yyy, zzz, ....].

        Notes:
            1)
                Union[Message, bool] -> ['Message', 'bool']
        """
        return list([
            AnnotationWrapper(word.strip())
            for word in self.inner_part_of_union.split(',')
        ])

    @property
    def sanitized(self) -> AnnotationWrapper:
        """Get annotations from raw type paths and class descriptions.

        Notes:
            1)
                typing.Union[telegrambotapiwrapper.api.types.Message, bool] ->
                    Union[Message, bool],
                <class 'telegrambotapiwrapper.api.types.Message'> -> Message
        """
        res = self.replace('typing.', ''). \
            replace('telegrambotapiwrapper.typelib.', ''). \
            replace("<class '", ""). \
            replace("'>", "")
        return AnnotationWrapper(res)

    @property
    def is_list(self) -> bool:
        """Check is List[xxx].

        Check if annotation is a List[xxx] type annotation, where xxx is not a
        List [yyy] type string.

        Notes:
            1) Caution:
                "List[List[InlineKeyboardButton]] -> False
            2)
                List[ChatMember] -> True
                Union[Message, bool] -> False
        """
        if self.is_list_of_list:  # pylint: disable=R1705
            return False
        else:
            return bool(AnnotationWrapper.list_field_re.match(self.data))

    @property
    def is_union(self) -> bool:
        """Check if annotation is annotation like Union[xxx].

        Notes:
            1)
                Union[Message, bool] -> True
                Optional[Union[InputFile, str]] -> False,
        """
        return bool(AnnotationWrapper.union_field_re.match(self.data))
