from typing import Union

import uuid
import base64
import enum

from gumo.core.domain.entity_key import EntityKey
from gumo.core.domain.entity_key import IncompleteKey
from gumo.core.domain.entity_key import EntityKeyFactory

from gumo.core.injector import injector


class KeyGenerateStyle(enum.Enum):
    STR_SHORT = 'short-str'
    STR_LONG = 'long-str'
    INT = 'int'


class KeyIDAllocator:
    def allocate(self, incomplete_key: IncompleteKey) -> EntityKey:
        raise NotImplementedError()


class EntityKeyGenerator:
    KeyGenerateStyle = KeyGenerateStyle

    def __init__(self, key_generate_style: KeyGenerateStyle = KeyGenerateStyle.STR_SHORT):
        self._key_generate_style = key_generate_style

        if self._key_generate_style == KeyGenerateStyle.INT:
            self._id_allocator = self._get_id_allocator()

    def _get_id_allocator(self) -> KeyIDAllocator:
        try:
            import gumo.datastore  # noqa: F401 for dependency checks.
        except ImportError:
            raise RuntimeError(f'gumo.datastore is not imported. Cloud not use KeyGenerateStyle.INT.')

        return injector.get(KeyIDAllocator)

    def generate(self, incomplete_key: IncompleteKey) -> EntityKey:
        return EntityKeyFactory().build(
            kind=incomplete_key.kind,
            name=self.generate_identifier(incomplete_key=incomplete_key),
            parent=incomplete_key.parent,
        )

    def generate_identifier(self, incomplete_key: IncompleteKey) -> Union[str, int]:
        if self._key_generate_style == KeyGenerateStyle.STR_SHORT:
            return self._generate_str_short()
        elif self._key_generate_style == KeyGenerateStyle.STR_LONG:
            return self._generate_str_long()
        elif self._key_generate_style == KeyGenerateStyle.INT:
            return self._generate_int(incomplete_key=incomplete_key)
        else:
            raise NotImplementedError(f'Not implemented pattern of {self._key_generate_style}')

    def _generate_str_short(self) -> str:
        s = base64.b32encode(uuid.uuid4().bytes).decode('utf-8')
        return s.replace('======', '').lower()

    def _generate_str_long(self) -> str:
        return uuid.uuid4().bytes.decode('utf-8')

    def _generate_int(self, incomplete_key: IncompleteKey) -> int:
        key = self._id_allocator.allocate(incomplete_key=incomplete_key)
        return key.name()
