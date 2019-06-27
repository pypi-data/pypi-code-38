#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# jp: a SAT command line tool
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import base
from sat.core.i18n import _

__commands__ = ["Bookmarks"]

STORAGE_LOCATIONS = ('local', 'private', 'pubsub')
TYPES = ('muc', 'url')

class BookmarksCommon(base.CommandBase):
    """Class used to group common options of bookmarks subcommands"""

    def add_parser_options(self, location_default='all'):
        self.parser.add_argument('-l', '--location', type=str, choices=(location_default,) + STORAGE_LOCATIONS, default=location_default, help=_("storage location (default: %(default)s)"))
        self.parser.add_argument('-t', '--type', type=str, choices=TYPES, default=TYPES[0], help=_("bookmarks type (default: %(default)s)"))

    def _errback(self, failure):
        print (("Something went wrong: [%s]") % failure)
        self.host.quit(1)

class BookmarksList(BookmarksCommon):

    def __init__(self, host):
        super(BookmarksList, self).__init__(host, 'list', help=_('list bookmarks'))

    def start(self):
        data = self.host.bridge.bookmarksList(self.args.type, self.args.location, self.host.profile)
        mess = []
        for location in STORAGE_LOCATIONS:
            if not data[location]:
                continue
            loc_mess = []
            loc_mess.append(u"%s:" % location)
            book_mess = []
            for book_link, book_data in data[location].items():
                name = book_data.get('name')
                autojoin = book_data.get('autojoin', 'false') == 'true'
                nick = book_data.get('nick')
                book_mess.append(u"\t%s[%s%s]%s" % ((name+' ') if name else '',
                                                 book_link,
                                                 u' (%s)' % nick if nick else '',
                                                 u' (*)' if autojoin else ''))
            loc_mess.append(u'\n'.join(book_mess))
            mess.append(u'\n'.join(loc_mess))

        print u'\n\n'.join(mess)


class BookmarksRemove(BookmarksCommon):

    def __init__(self, host):
        super(BookmarksRemove, self).__init__(host, 'remove', help=_('remove a bookmark'))
        self.need_loop = True

    def add_parser_options(self):
        super(BookmarksRemove, self).add_parser_options()
        self.parser.add_argument('bookmark', type=base.unicode_decoder, help=_('jid (for muc bookmark) or url of to remove'))

    def start(self):
        self.host.bridge.bookmarksRemove(self.args.type, self.args.bookmark, self.args.location, self.host.profile, callback = lambda: self.host.quit(), errback=self._errback)


class BookmarksAdd(BookmarksCommon):

    def __init__(self, host):
        super(BookmarksAdd, self).__init__(host, 'add', help=_('add a bookmark'))
        self.need_loop = True

    def add_parser_options(self):
        super(BookmarksAdd, self).add_parser_options(location_default='auto')
        self.parser.add_argument('bookmark', type=base.unicode_decoder, help=_('jid (for muc bookmark) or url of to remove'))
        self.parser.add_argument('-n', '--name', type=base.unicode_decoder, help=_("bookmark name"))
        muc_group = self.parser.add_argument_group(_('MUC specific options'))
        muc_group.add_argument('-N', '--nick', type=base.unicode_decoder, help=_('nickname'))
        muc_group.add_argument('-a', '--autojoin', action='store_true', help=_('join room on profile connection'))

    def start(self):
        if self.args.type == 'url' and (self.args.autojoin or self.args.nick is not None):
            # XXX: Argparse doesn't seem to manage this case, any better way ?
            print _(u"You can't use --autojoin or --nick with --type url")
            self.host.quit(1)
        data = {}
        if self.args.autojoin:
            data['autojoin'] = 'true'
        if self.args.nick is not None:
            data['nick'] = self.args.nick
        if self.args.name is not None:
            data['name'] = self.args.name
        self.host.bridge.bookmarksAdd(self.args.type, self.args.bookmark, data, self.args.location, self.host.profile, callback = lambda: self.host.quit(), errback=self._errback)


class Bookmarks(base.CommandBase):
    subcommands = (BookmarksList, BookmarksRemove, BookmarksAdd)

    def __init__(self, host):
        super(Bookmarks, self).__init__(host, 'bookmarks', use_profile=False, help=_('manage bookmarks'))
