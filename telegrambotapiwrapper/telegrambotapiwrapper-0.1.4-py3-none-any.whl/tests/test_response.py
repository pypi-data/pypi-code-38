import unittest

from telegrambotapiwrapper.annotation import AnnotationWrapper
from telegrambotapiwrapper.typelib import *
from telegrambotapiwrapper.response import to_api_type, dataclass_fields_to_jdict
from telegrambotapiwrapper import utils



def dataclass_fields_to_jdict_for_testing(obj: dict):
    return utils.replace_from_word(dataclass_fields_to_jdict(obj))


class TestToApiTypeFunction(unittest.TestCase):
    """Тестирование работы функции to_api_type."""

    def test_to_user(self):
        user1 = User(
            id=1234566,
            is_bot=False,
            first_name="John",
            last_name="Doe",
            username="hdvjkdcjkf123sdbvmdjfvn",
            language_code='ru')

        user2 = User(
            id=1234566,
            is_bot=False,
            first_name="John",
        )

        user3 = User(
            id=1234566, is_bot=False, first_name="John", language_code='en')
        for user_obj in [user1, user2, user3]:
            g_type = to_api_type(
                dataclass_fields_to_jdict_for_testing(user_obj._fields_items),
                AnnotationWrapper("User"))
            self.assertEqual(g_type, user_obj)

    def test_to_chat(self):
        # 1
        chat_photo = ChatPhoto(
            small_file_id='1fdf235643', big_file_id='3454sdfds56546')
        chat1 = Chat(
            id=123,
            type='group',
            title='dsdvfvdvxfve',
            all_members_are_administrators=True,
            photo=chat_photo)
        # 2
        chat2 = Chat(
            id=1234,
            type="sdfdsfds",
            title="fvgfgfd",
            username="regfrefre",
            first_name="regfrefre",
            last_name="regfrefre",
            all_members_are_administrators=False,
        )
        # 3
        pinned_message_chat = Chat(
            id=12344332534, type="sddsfdsf", title="fjhdkjfhskdlhsj")
        pinned_message = Message(
            message_id=123214234,
            date=12435324,
            chat=pinned_message_chat,
        )
        chat3 = Chat(
            id=1234,
            type="sdfdsfds",
            title="fvgfgfd",
            username="regfrefre",
            first_name="regfrefre",
            all_members_are_administrators=True,
            pinned_message=pinned_message)

        for chat in [chat1, chat2, chat3]:
            to_convert = chat._fields_items
            self.assertEqual(
                chat,
                to_api_type(
                    dataclass_fields_to_jdict_for_testing(to_convert),
                    anno=AnnotationWrapper('Chat')))

    def test_to_message(self):

        # 1
        pinned_message_chat = Chat(
            id=12344332534, type="sddsfdsf", title="fjhdkjfhskdlhsj")
        pinned_message = Message(
            message_id=123214234,
            date=12435324,
            chat=pinned_message_chat,
        )
        chat = Chat(
            id=1234,
            type="sdfdsfds",
            title="fvgfgfd",
            username="regfrefre",
            first_name="regfrefre",
            all_members_are_administrators=True,
            pinned_message=pinned_message)

        user = User(
            id=1232343,
            is_bot=False,
            first_name="23fdvfvdsc",
            last_name="gjfdkjglkfjglkjf",
        )

        message1 = Message(
            message_id=12312321,
            date=4584979847685478,
            chat=chat,
            from_=user,
        )

        for message in [
                message1,
        ]:
            to_convert = message._fields_items
            self.assertEqual(
                message,
                to_api_type(
                    dataclass_fields_to_jdict_for_testing(to_convert),
                    anno=AnnotationWrapper('Message')))

    def test_to_callback_query(self):

        user = User(
            id=12323432,
            is_bot=True,
            first_name="dsfvdfdgf",
        )

        callback_query = CallbackQuery(
            id="dfgrewregfrewfgd",
            from_=user,
            chat_instance="3243543",
        )

        to_convert = callback_query._fields_items

        self.assertEqual(
            callback_query,
            to_api_type(
                dataclass_fields_to_jdict_for_testing(to_convert),
                anno=AnnotationWrapper('CallbackQuery')))
