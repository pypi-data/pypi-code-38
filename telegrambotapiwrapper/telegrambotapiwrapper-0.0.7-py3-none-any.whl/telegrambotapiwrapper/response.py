# -*- coding: utf-8 -*-
# Copyright (c) 2019 Dzmitry Maliuzhenets; MIT License
"""Response functionality from Telegram Bot Api."""
import jsonpickle
from telegrambotapiwrapper import utils
from telegrambotapiwrapper.annotation import AnnotationWrapper
from telegrambotapiwrapper.errors import RequestResultIsNotOk
from telegrambotapiwrapper.request import json_payload
from telegrambotapiwrapper.utils import is_str_int_float_bool
import telegrambotapiwrapper.typelib as types_module

def dataclass_fields_to_jdict(fields: dict) -> dict:
    """Get a json-like dict from the dataclass fields."""
    jstr = json_payload(fields)
    res = jsonpickle.decode(jstr)
    return res


def to_api_type(obj, anno: AnnotationWrapper):
    """Convert object to api type

    Convert the result of the request to the Telegram Bot API into the
    appropriate type.

    Notes:
        1)
            In the current versions of Telegram Bot Api (4.2), the following
            values ​​can be returned:
                'Chat',
                'ChatMember',
                'File',
                'List[ChatMember]',
                'List[GameHighScore]',
                'List[Update]',
                'Message',
                'Pool',
                'StickerSet',
                'Union[Message, bool]',
                'User',
                'UserProfilePhotos',
                'WebhookInfo',
                'bool',
                'int',
                'str'
            For the current version of Telegram Bot Api (4.2), the following
            union-annotations are used to create types.:
                'Optional[Union[InputFile, str]]'
            For the current version of Telegram Bot Api (4.2), the following
            `List`-annotations are used to create types:
                'List[EncryptedPassportElement]',
                'List[LabeledPrice]',
                'List[PhotoSize]',
                'List[PollOption]',
                'List[Sticker]',
                'List[str]',
            For the current version of Telegram Bot Api (4.2), the following
            `List [List [` - annotations are used to create types:
                'List[List[InlineKeyboardButton]]',
                'List[List[KeyboardButton]]',
                'List[List[PhotoSize]]',
            For the current version of Telegram Bot Api (4.2), return values ​​
            may have the following `union`- annotations:
                'Union [Message, bool]'
        2)
    """

    def list_to_api_type(obj: list, anno: AnnotationWrapper) -> list:
        """Convert list to api type."""
        inner_part = anno.inner_part_of_list.sanitized.data
        api_type = getattr(types_module, inner_part)

        res = []
        for item in obj:
            to_type = {}
            for field_name, field_type in api_type._annotations().items():
                try:
                    to_type[field_name] = to_api_type(
                        item[field_name], AnnotationWrapper(field_type))
                except KeyError:
                    continue
            res.append(api_type(**to_type))
        return res

    def list_of_list_to_api_type(obj: list, anno: AnnotationWrapper):
        """Convert list of list to api type."""
        res = []
        for lst in obj:
            res.append(list_to_api_type(lst, anno.inner_part_of_list))
        return res

    def union_to_api_type(obj, anno: AnnotationWrapper):
        """Convert union to api type."""
        if anno == 'Union[Message, bool]':
            return to_api_type(obj, AnnotationWrapper('Message'))
        elif anno == 'Union[InputFile, str]]':
            return to_api_type(obj, AnnotationWrapper('InputFile'))

    if is_str_int_float_bool(obj):
        return obj

    if anno.is_optional:
        anno = anno.inner_part_of_optional

    if anno.is_list:
        return list_to_api_type(obj, anno)
    elif anno.is_list_of_list:
        return list_of_list_to_api_type(obj, anno)
    elif anno.is_union:
        return union_to_api_type(obj, anno)

    if isinstance(obj, dict):
        to_type = {}
        api_type = getattr(types_module, anno.sanitized.data)

        for field_name, field_type in api_type._annotations().items():
            try:
                to_type[field_name] = to_api_type(
                    obj[field_name], AnnotationWrapper(field_type))
            except KeyError:
                continue
        return api_type(**to_type)


def get_result(raw_response: str):
    """Extract the result from the raw response from the Bot API telegram.

    Args:
        raw_response (str): `raw` response from Bot API telegram

    Raises:
        RequestResultIsNotOk: if the answer contains no result

    Note:
        If raw_response does not contain an `ok` field, then we assume that this
        is an extracted result, for example, for testing purposes.
    """
    response = jsonpickle.loads(raw_response)
    try:
        is_ok = response["ok"]
    except KeyError:
        return response
    if is_ok:
        return response['result']

    else:
        raise RequestResultIsNotOk("error_code: {}, description: {}".format(
            response['error_code'], response['description']))


def handle_response(raw_response: str,
                    method_response_type: AnnotationWrapper):
    """Parse a string that is a response from the Telegram Bot API.

    Args:
        raw_response (str): response from Telegram Bot API
        method_response_type (AnnotationWrapper): annotation of the expected
            response

    Raises:
        RequestResultIsNotOk: if the answer contains no result
    """
    res = get_result(raw_response)
    res = utils.replace_from_word(res)
    return to_api_type(res, method_response_type)
