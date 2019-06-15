# -*- coding: utf-8 -*-
# Copyright (c) 2019 Dzmitry Maliuzhenets; MIT License
"""The module contains various utilities."""
import filetype
import requests
from telegrambotapiwrapper.typelib import Update
from telegrambotapiwrapper.wrapper import Api


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


def download_file(bot, file_path) -> bytes:
    """Get file."""
    url = "https://api.telegram.org/file/bot{}/{}".format(
        bot.token,
        file_path
    )
    u = requests.get(url)
    return u.content


def file_path(bot: Api, file_id: str):
    file_obj = bot.get_file(file_id)
    return file_obj.file_path


def is_bytes_img(obj: bytes):
    """Check whether bytes define an image."""
    try:
        return 'image/' in filetype.guess(obj).MIME
    except AttributeError:
        return False






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

    def is_img(self, bot) -> bool:
        """Проверить, является ли обновление изображениям, переданным как
        document или photo."""
        if self.has_msg_photo_field:
            return True
        elif self.is_file:
            fp = file_path(bot, self.img_id)
            f_bytes = download_file(bot, fp)
            return is_bytes_img(f_bytes)
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

    @property
    def img_id(self) -> str:
        return self._update.message.photo[0].file_id

    def download_img(self, bot) -> bytes:
        fp = file_path(bot, self.img_id)
        return download_file(bot, fp)









