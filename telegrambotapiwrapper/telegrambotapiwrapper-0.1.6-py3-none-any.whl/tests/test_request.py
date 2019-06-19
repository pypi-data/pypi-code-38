import unittest

import jsonpickle

from telegrambotapiwrapper.typelib import *
from telegrambotapiwrapper.request import json_payload


class TestRequest(unittest.TestCase):
    def test_json_payload(self):
        btn1 = InlineKeyboardButton(text='add', url='http://lenta.ru')
        btn2 = InlineKeyboardButton(text='sub', url='http://topwar.ru')
        btn3 = InlineKeyboardButton(text='mul', url='http://waralbum.ru')
        btn4 = InlineKeyboardButton(text='div', url='http://anio.ru')
        inline_kb = InlineKeyboardMarkup([[btn1, btn2], [btn3, btn4]])
        payload = json_payload(inline_kb)

        res = {
            "inline_keyboard": [[{
                "text": "add",
                "url": "http://lenta.ru"
            }, {
                "text": "sub",
                "url": "http://topwar.ru"
            }],
                [{
                    "text": "mul",
                    "url": "http://waralbum.ru"
                }, {
                    "text": "div",
                    "url": "http://anio.ru"
                }]]
        }

        self.assertEqual(jsonpickle.loads(payload), res)
