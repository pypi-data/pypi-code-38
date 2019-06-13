from coolsignup.command_line_args import get_option
import json
import motor
import pymongo
import os.path
from coolsignup.translator import get_locale_directory, Translator

from naval import (
    Schema, Type, Length, Email, Domain, Optional, Url, Default, Range, Assert
)

email_account_schema = Schema(
    ['from', Email],
    ['smtpServer', Domain],
    ['port', Default(587), Type(int), Range(min=1)],
    ['username', Type(str), Length(min=1)],
    ['password', Type(str)],
    ['senderName', Optional, Type(str)]
)

mongo_schema = Schema(
    ["host", Default("localhost"), Type(str)],
    ["port", Default(27017), Type(int), Range(min=1)]
)

conf_schema = Schema(
    ["smtp", email_account_schema],
    ["serviceName", Type(str), Length(min=1)],
    ["secretKey", Type(str), Length(min=60)],
    ["emailCodeLink", Url],
    ["passwordStrength", Default(9.0), float],
    ["passwordMinLength", Default(8), int],
    ["tokenDurationSeconds", Default(30*24*3600), Type(int), Range(min=0)],
    ["maxTokensPerUser", Default(20), Type(int), Range(min=1)],
    ["codeDurationSeconds", Default(3600), Type(int), Range(min=0)],
    ["localeDirectory",
        Default(lambda d: get_locale_directory()),
        Type(str),
        Assert(os.path.isdir, error_message = "Directory not found")
    ],
    ["mongo",
        Default({
            'host': 'localhost',
            'port': 27017
        }),
        Schema(
            ['host', Type(str)],
            ['port', Type(int), Range(min=1)]
        )
    ]
)


class Conf(object):
    def __init__(self):
        conf_path = get_option('-c')
        with open(conf_path) as fp:
            conf_document = json.load(fp)
            self._conf = conf_schema.validate(conf_document)
        self._translator = Translator(self._conf['localeDirectory'])
        self._motor_client = motor.motor_tornado.MotorClient(**self._conf["mongo"])
        pymongo_client = pymongo.MongoClient(**self._conf["mongo"])
        accounts_collec = pymongo_client['coolsignup']['accounts']
        accounts_collec.create_index(
            # currently hashed indexes in MongoDB cannot guarantee uniqueness.
            # Also, they actually prevent from finding the data which is annoying
            [('email', pymongo.ASCENDING)],
            sparse = True,
            unique = True
        )
        accounts_collec.create_index(
            [('emailLower', pymongo.ASCENDING)],
            sparse = True,
            unique = True
        )
        accounts_collec.create_index(
            [('authTokens.authToken', pymongo.ASCENDING)],
            background = True
        )
        accounts_collec.create_index(
            [('authTokens.timestamp', pymongo.ASCENDING)],
            background = True
        )

    def get(self, item):
        return self._conf[item]

    @property
    def mongo_accounts(self):
        return self._motor_client['coolsignup']['accounts']

    def translation_func(self, to_lang):
        return self._translator.translation_func(to_lang)

conf = Conf()
