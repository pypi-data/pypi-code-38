#!/usr/bin/python
# -*- coding: utf-8 -*-

from Homevee.Item.ChatMessage import ChatMessage
from Homevee.Utils.Database import Database

class ChatManager:
    def __init__(self):
        return

    def get_chat_messages(self, user, time, limit, db: Database = None):
        """
        Loads the last X chat messages from the database
        :param user:
        :param time:
        :param limit:
        :param db:
        :return:
        """
        if db is None:
            db = Database()
        messages = ChatMessage.load_all_by_time(time, limit)
        return messages

    def get_chat_image(self, user, imageid, db: Database = None):
        if db is None:
            db = Database()
        return {}

    def send_chat_message(self, user, data, db: Database = None):
        """
        Sends a new chat message to all users
        :param user:
        :param data:
        :param db:
        :return:
        """
        if db is None:
            db = Database()
        message = ChatMessage(user.username, data)
        return message.send(db)