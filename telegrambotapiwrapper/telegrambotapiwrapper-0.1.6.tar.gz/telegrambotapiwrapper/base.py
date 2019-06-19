# -*- coding: utf-8 -*-
# Copyright (c) 2019 Dzmitry Maliuzhenets; MIT License
"""A module containing a class that is the parent for all types of APIs."""

import dataclasses
from typing import List, Optional, Dict

from telegrambotapiwrapper.annotation import AnnotationWrapper


class Base:  # pylint: disable=R0903
    """Base class for all types of APIs."""

    @classmethod
    def _get_classname(cls):
        """Get name of the class."""
        return cls.__name__

    @classmethod
    def _get_simple_fields(cls) -> dict:
        """Get the dataclass fields that are int, str, bool, float.

        Note:
            1) It does not matter whether the field is optional or not.
        """
        return {
            name: tp
            for name, tp in cls._annotations().items()
            if AnnotationWrapper(tp).is_simple_in_opt_and_not_opt
        }

    @classmethod
    def _get_not_simple_fields(cls) -> Dict[str, str]:
        """Get fields that are not int, bool, str, float.

        Notes:
            Optional or non-optional does not matter

        Example:
            1)
                @dataclass
                class Document(Base):
                    file_id: str
                    thumb: Optional[PhotoSize] = None
                    file_name: Optional[str] = None
                    mime_type: Optional[str] = None
                    file_size: Optional[int] = None

                Returns:
                    {'thumb': 'Optional[PhotoSize]'}
        """


        return {
            name: anno
            for name, anno in cls._annotations().items()
            if not AnnotationWrapper(anno).is_simple_in_opt_and_not_opt
        }

    @classmethod
    def _is_simple_type(cls):
        """Does the class contain only fields that are int, bool, str, float.

        Notes:
            Optional or non-optional does not matter

        Example:
            1)
                @dataclass
                class User(Base):
                    id: int
                    is_bot: bool
                    first_name: str
                    last_name: Optional[str] = None
                    username: Optional[str] = None
                    language_code: Optional[str] = None

                Returns:
                    True
            2)
                @dataclass
                class Document(Base):
                    file_id: str
                    thumb: Optional[PhotoSize] = None
                    file_name: Optional[str] = None
                    mime_type: Optional[str] = None
                    file_size: Optional[int] = None

                Returns:
                    False
            """
        return all([
            AnnotationWrapper(anno).is_simple_in_opt_and_not_opt
            for anno in cls._used_annotations()
        ])

    @classmethod
    def _fields_names(cls) -> List:
        """Get a list of dataclass fields names.


        Example:
            @dataclass
            class User(Base):
                id: int
                is_bot: bool
                first_name: str
                last_name: Optional[str] = None
                username: Optional[str] = None
                language_code: Optional[str] = None

            Returns:
                ['id', 'is_bot', 'first_name', 'last_name', 'username',
                'language_code']
        """
        return list(field.name for field in dataclasses.fields(cls))

    @classmethod
    def _annotations(cls) -> dict:
        """Get annotations.

        Example:
            @dataclass
            class User(Base):
                id: int
                is_bot: bool
                first_name: str
                last_name: Optional[str] = None
                username: Optional[str] = None
                language_code: Optional[str] = None

            Returns: {'id': 'int',
                      'is_bot': 'bool',
                      'first_name': 'Optional[str]',
                      'last_name': 'Optional[str]',
                      'username': 'Optional[str]',
                      'language_code': 'Optional[str]'}
        """
        return {field.name: field.type for field in dataclasses.fields(cls)}

    @classmethod
    def _used_annotations(cls) -> set:
        """Get all used annotations.

        Example:
            @dataclass
            class User(Base):
                id: int
                is_bot: bool
                first_name: str
                last_name: Optional[str] = None
                username: Optional[str] = None
                language_code: Optional[str] = None

            Returns: {'int', 'str', 'bool', 'Optional[str]'}
        """
        return set(field.type for field in dataclasses.fields(cls))

    @classmethod
    def _field_type(cls, field_name: str) -> Optional[str]:
        """Get field annotation.

        Args:
            field_name (str): name of field
        Returns:
            (str): field annotation
        """
        for field in dataclasses.fields(cls):
            if field.name == field_name:
                return field.type
        return None

    @property
    def _fields_items(self) -> dict:
        """Get a dict of dataclass fields, as name: value pairs.

        Notes:
            Use only for instances.
        """
        return dataclasses.asdict(self)
