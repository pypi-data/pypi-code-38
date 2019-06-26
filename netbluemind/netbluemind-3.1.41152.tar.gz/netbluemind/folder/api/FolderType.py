#
#  BEGIN LICENSE
#  Copyright (c) Blue Mind SAS, 2012-2016
# 
#  This file is part of BlueMind. BlueMind is a messaging and collaborative
#  solution.
# 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of either the GNU Affero General Public License as
#  published by the Free Software Foundation (version 3 of the License).
# 
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  See LICENSE.txt
#  END LICENSE
#
import requests
from netbluemind.python import serder
from enum import Enum

class FolderType(Enum):
    user_created_folder = 'user_created_folder';
    default_inbox = 'default_inbox';
    default_drafts = 'default_drafts';
    default_trash = 'default_trash';
    default_sent = 'default_sent';
    default_outbox = 'default_outbox';
    default_todolist = 'default_todolist';
    default_calendar = 'default_calendar';
    default_addressbook = 'default_addressbook';
    default_notes = 'default_notes';
    default_journal = 'default_journal';
    user_created_mail = 'user_created_mail';
    user_created_calendar = 'user_created_calendar';
    user_created_addressbook = 'user_created_addressbook';
    user_created_todolist = 'user_created_todolist';
    user_created_journal = 'user_created_journal';
    user_created_notes = 'user_created_notes';
    unknown = 'unknown';
    recipient_information_cache = 'recipient_information_cache';
    system = 'system';
    root = 'root';
    other_mailboxes = 'other_mailboxes';
    other_calendars = 'other_calendars';
    other_addressbooks = 'other_addressbooks';
    other_todolists = 'other_todolists';
    default_mailbox = 'default_mailbox';
    other_mailbox = 'other_mailbox';

class __FolderTypeSerDer__:
    def __init__( self):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = FolderType[value]
        return instance


    def encode(self, value):
        if(value == None):
            return None
        instance = value.value
        return instance
