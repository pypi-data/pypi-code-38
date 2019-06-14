# -*- coding: utf-8 -*-
# Copyright (c) 2019 Dzmitry Maliuzhenets; MIT License
"""The module contains various utilities."""
import filetype
import requests
from telegrambotapiwrapper.typelib import Update

def replace_from__word(d: dict):
    """Replace recursive keys in the object from_ to from."""
    res = {}
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [replace_from__word(v) for v in d]

    for key, value in d.items():
        if key == 'from_':
            res['from'] = replace_from__word(d['from_'])
        else:
            res[key] = replace_from__word(d[key])
    return res


def replace_from_word(d: dict) -> dict:
    """Replace recursive keys in the object from to from_."""
    res = {}
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [replace_from_word(v) for v in d]

    for key, value in d.items():
        if key == 'from':
            res['from_'] = replace_from_word(d['from'])
        else:
            res[key] = replace_from_word(d[key])
    return res


def is_str_int_float_bool(value):
    """Is value str, int, float, bool."""
    return isinstance(value, (int, str, float))


def is_ends_with_underscore(value: str):
    """Does value end with underscore."""
    if value == "":
        return False
    else:
        return value[-1] == '_'


def get_file(bot, file_path) -> bytes:
    """Get file."""
    url = "https://api.telegram.org/file/bot{}/{}".format(
        bot.token,
        file_path
    )
    u = requests.get(url)
    return u.content

def is_bytes_img(obj: bytes):
    """Check whether bytes define an image."""
    return 'image/' in filetype.guess(obj).MIME





class UpdateWrapper:
    """Обертка вокруг типа Update API телеграмма."""

    def __init__(self, update: Update):
        self._update = update

    def __getattr__(self, name):
        return getattr(self._update, name)

    def is_start_command(self):
        return self._update.message.text == '/start'

    @property
    def has_msg_photo_field(self) -> bool:
        """Check whether the update has a Photo field."""
        return self._update.message.photo is not None

    @property
    def has_msg_document_field(self) -> bool:
        return self._update.message.document is not None

    @property
    def is_file(self) -> bool:
        """Проверить, представляет ли собой обновловление document.

        Notes:
            document может быть и изображением
        """
        return self._update.message.document is not None


    def is_image(self, bot) -> bool:
        """Проверить, является ли обновление изображением, переданным как
        document или photo.

        TODO: распостранить на большое количество фотографий
        """
        if self.has_msg_photo_field:
            return True
        elif self.is_file:
            file_obj = bot.get_file(self._update.message.document.file_id)

            file_path = file_obj.file_path
            f_bytes = get_file(bot, file_path)
            if is_bytes_img(f_bytes):
                return True
            else:
                return False
        else:
            return False

    @property
    def chat_id(self) -> int:
        return self._update.message.chat.id

    @property
    def poll_id(self) -> str:
        return self._update.message.poll.id

    @property
    def msg_text(self) -> str:
        return self._update.message.text








