#!/usr/bin/env python3

import os
import re
import sys
import stat
import trio
import asks
import requests
import curses
import curses.textpad
import urllib.parse
import configparser
from bs4 import BeautifulSoup

from . import __version__

# Async setup
asks.init('trio')

# Global variables
VERSION = f'mega version {__version__}'
HELP = '''usage: mega [OPTIONS]

mega brings you the latest content as soon as its available.

General options:
    -h, --help         Show this help message and exit
    --version          Show program version and exit
    --config, config   Activate configuration mode
    --search, search   Activate search mode

Configuration options:
   user.name  [NAME]   Show current username or add username to .megarc
   user.pass  [PASS]   Show current password or add password to .megarc
   user.creds          Show current username and password
   defaults            Select categories to request content from
   create              Create a configuration file

Movement:
   Normal and Search mode
      j                Page down
      k                Page up
      b                Back to search (search mode only)
      q                Quit

   Default mode
      j, ↑             Move up a listing or category
      k, ↓             Move down a listing or category
      l, ENTER         Select listing, category, or menu option
      →, ←             Move to menu'''

# Banner
TERM_LENGTH = int(os.popen('stty size', 'r').read().split()[1])
BANNER = """\
{0}███╗   ███╗       ██╗ ██╗
{0}████╗ ████║██╗   ██╔╝██╔╝
{0}██╔████╔██║╚═╝  ██╔╝██╔╝
{0}██║╚██╔╝██║██╗ ██╔╝██╔╝
{0}██║ ╚═╝ ██║╚═╝██╔╝██╔╝    v{1}
{0}╚═╝     ╚═╝   ╚═╝ ╚═╝\
""".format(' ' * (TERM_LENGTH // 2 - 14), __version__)

# Paging direction
UP   = -1
DOWN = 1

# Key codes
KEY_UP    = 65
KEY_DOWN  = 66
KEY_LEFT  = 68
KEY_RIGHT = 67
KEY_ENTER = 10
KEY_B     = 98
KEY_J     = 106
KEY_K     = 107
KEY_L     = 108
KEY_Q     = 113

# All listings, categories, and URL paths
ALL_LISTINGS = {
        'imported': {'Snahp.it':      45,
                     'Megalinks':     46},
        'apps':     {'Windows':       40,
                     'Mac OS':        24,
                     'Linux':         81,
                     'Mobile OS':     47},
        'games':    {'PC/MAC':        41,
                     'Linux':         82,
                     'Console':       25},
        'movies':   {'CAM/TS':        42,
                     'SD/480p':       55,
                     '720p/1080p':    26,
                     'BluRay/REMUX':  29,
                     '3D':            66,
                     '4K':            30,
                     'x265':          56,
                     'Foreign':       72,
                     'Packs':         73},
        'tv':       {'SD':            64,
                     '720p/1080p':    31,
                     'BluRay/REMUX':  32,
                     '4K':            65,
                     'Documentaries': 33,
                     'Sports':        61,
                     'Stand-Up':      62,
                     'x265':          57,
                     'Foreign':       75,
                     'Packs':         74},
        'music':    {'Lossy':         34,
                     'Lossless':      35,
                     'Videos':        36,
                     'Broadway':      58,
                     'Others':        63},
        'anime':    {'Manga':         60},
        'misc':     {'eBooks':        37,
                     'Audiobooks':    38,
                     'Tutorials':     39,
                     'Comics':        43,
                     'Magazines':     44,
                     'Others':        59},
        'dev':      {'Software':      77,
                     'Image':         78,
                     'Video':         79,
                     'Music':         80}
}

class Mega():
    """Class to handle curses and general drawing operations.

    Attributes:
        Pads
            height:         (int)    Height of terminal window.
            width:          (int)    Length of terminal window.
            content_height: (int)    height designated for drawing content.
            pad_banner:     (Window) Pad for drawing the program banner.
            pad_header:     (Window) Pad for drawing the header (listing, category).
            pad_content:    (Window) Pad for drawing content (titles, links).
            pad_menu:       (Window) Pad for drawing key menu and page numbers.

        Defaults
            c_apply         (set)    Listings to apply to config file.
            ch              (int)    Character code of key pressed.
            top             (int)    The highest, unselected category displayed.
            end             (int)    The lowest, unselected category displayed.
            stream_type     (String) Determines keybindings to use.
            menu_type       (String) Determines menu to draw.
            rc              (Megarc) Object for interacting with config file.

        Contents
            c_count:        (int)    Cumulative # of items viewed for current category.
            p_count:        (int)    Cumulative # of items that would have been viewed
                                       on the page previous to the current for current
                                       category.
            c_cat_len:      (int)    Total # of items in current category.
            max_count:      (int)    Max # of content viewable in terminal.
            items_shown:    (int)    # of items shown on current page.

        Listing / Category
            c_list:         (int)    Index of current listing.
            c_cat:          (int)    Index of current category in a listing.
            p_listing:      (int)    Index of previous listing.
            p_cat:          (int)    Index of previous category in a listing.
            p_cat_len:      (int)    Total # of items in previous category.
            cat_lens:       (list)   Total # of items in all categories.

        Pages
            c_page:         (int)    Current page being viewed (relative to category).
            t_pages:        (int)    Total pages in current category.
            pt_pages:       (int)    Total pages in previous category.
    """
    def __init__(self, stdscr, rc):
        """Drawing API.

        Args:
            stdscr:             (Window) Represents the entire screen.
            rc                  (Megarc) Object for interacting with config file.
        """
        # pads
        self.height = curses.LINES
        self.width  = curses.COLS

        if self.height < 25 or self.width < 37:
            fatal('terminal is too small: height must be ≥ 25, width must be ≥ 35')

        self.content_height = self.height - 15  # 13: banner/header, 2: menu

        self.pad_banner  = curses.newpad(6, self.width)  # 6: height of banner
        self.pad_header  = curses.newpad(4, self.width)  # 4: 3 header lines + cursor on next line
        self.pad_content = curses.newpad(self.content_height, self.width)
        self.pad_menu    = curses.newpad(2, self.width)

        # search
        self.content_list = []

        # defaults
        self.c_apply = set()
        self.ch  = 0
        self.top = 0
        self.end = 0
        self.stream_type = 'defaults'
        self.menu_type = 'content'
        self.rc = rc

        # content
        self.c_count = 0
        self.p_count = 0
        self.c_cat_len = 0
        self.max_count = 0
        self.items_shown = 0

        # listing / category
        self.c_listing = 0
        self.c_cat = 0
        self.p_listing = 0
        self.p_cat = 0
        self.p_cat_len = 0
        self.cat_lens = []

        # pages
        self.c_page = 1
        self.t_pages = 1
        self.pt_pages = 1

        # colors
        self.init_colors()

    def __repr__(self):
        num_attr = 27  # 1 less
        mega_obj = 'Mega({}{})'.format('{!r}, ' * num_attr, '{!r}')

        return mega_obj.format(
            self.height,
            self.width,
            self.content_height,
            self.pad_banner,
            self.pad_header,
            self.pad_content,
            self.pad_menu,
            self.c_apply,
            self.ch,
            self.top,
            self.end,
            self.stream_type,
            self.menu_type,
            self.rc,
            self.c_count,
            self.p_count,
            self.c_cat_len,
            self.max_count,
            self.items_shown,
            self.c_listing,
            self.c_cat,
            self.p_listing,
            self.p_cat,
            self.p_cat_len,
            self.cat_lens,
            self.c_page,
            self.t_pages,
            self.pt_pages,)

    def __str__(self):
        return ('Mega:\n'
                '   Pads:\n'
                f'      Height of content area: {self.content_height}\n'
                f'      Banner pad: {self.pad_banner}\n'
                f'      Header pad: {self.pad_header}\n'
                f'      Content pad: {self.pad_content}\n'
                f'      Menu pad: {self.pad_menu}\n'
                '\n   Defaults:\n'
                f'      Selected listings: {self.c_apply}\n'
                f'      Key pressed: {self.ch}\n'
                f'      Index of highest, unselected category: {self.top}\n'
                f'      Index of lowest, unselected category: {self.end}\n'
                f'      Keybindings to use: {self.stream_type}\n'
                f'      Menu to draw: {self.menu_type}\n'
                # f'      Megarc: %r\n' % '{self.rc}'
                '\n   Content:\n'
                f'      Items in current category: {self.c_cat_len}\n'
                f'      Items viewed in current category: {self.c_count}\n'
                f'      Items previously viewed in current category: {self.p_count}\n'
                f'      Items viewable in terminal: {self.max_count}\n'
                f'      Items currently displayed: {self.items_shown}\n'
                '\n   Listing / Category:\n'
                f'      Index of current listing: {self.c_listing}\n'
                f'      Index of current category: {self.c_cat}\n'
                f'      Index of previous listing: {self.p_listing}\n'
                f'      Index of previous category: {self.p_cat}\n'
                f'      Items in previous category: {self.p_cat_len}\n'
                f'      Items in all categories: {self.cat_lens}\n'
                '\n   Pages:\n'
                f'      Current page number: {self.c_page}\n'
                f'      Pages in current category: {self.t_pages}\n'
                f'      Pages in previous category: {self.pt_pages}\n'
                f'      Height of terminal: {self.height}\n'
                f'      Width of terminal: {self.width}\n')

    def init_colors(self):
        """Initialize curses colors."""
        curses.use_default_colors()

        curses.init_pair(1, 9,  -1)  # red  (banner, listings)
        curses.init_pair(2, 31, -1)  # blue (categories)
        curses.init_pair(3, 8,  -1)  # grey (links)
        curses.init_pair(4, 255, 9)  # highlight bg=red, fg=white
        curses.init_pair(5, 255, 31) # highlight bg=green, fg=white

    def run(self, stdscr, display_type, listings=None, categories=None, contents=None, title=None, rc=None):
        """Start TUI.

        Args:
            stdscr:     (Window)  Object representing the entire screen.
            listings:   (list)    All listings.   (FOR DEFAULTS MODE)
            categories: (list)    All categories. (FOR DEFAULTS MODE)
            contents:   (list)    All content.    (FOR DEFAULTS MODE)
        """
        # Hide cursor
        curses.curs_set(0)

        while True:
            if display_type == 'contents':
                self.display_content(listings, categories, contents)
                self.input_stream(display_type, listings, categories, contents)
            elif display_type == 'defaults':
                self.display_defaults()
                self.input_stream(self.stream_type)
            elif display_type == 'search':
                self.menu_type = 'search'
                if not title:
                    search_text = self.display_search()
                    if self.ch == 0 or self.ch == KEY_B:
                        self.get_search(search_text, rc)
                    self.input_stream('search')
                else:
                    self.display_search(title)
                    if self.ch == 0 or self.ch == KEY_B:
                        self.get_search(title, rc)
                    self.input_stream('search', search=title)

    def input_stream(self, display_type, listings=None, categories=None, contents=None, search=None):
        """Display content and wait for input.

        Args:
            listings:   (list) All listings.   (FOR DEFAULTS MODE)
            categories: (list) All categories. (FOR DEFAULTS MODE)
            contents:   (list) All content.    (FOR DEFAULTS MODE)

        TODO:
            1. (MAYBE) Clicking apply should clear current_apply and
                       you have to click back to go back to listings.
            2. (MAYBE) Show defaults.
        """
        self.ch = self.pad_menu.getch()

        if self.ch == KEY_Q:
            sys.exit(0)

        # Contents
        if display_type == 'contents':
            if self.ch == KEY_K:
                self.page(UP)
            elif self.ch == KEY_J:
                self.page(DOWN)

        # Search
        elif display_type == 'search':
            # only have paging if there's hits
            if len(self.content_list) > 0:
                if self.ch == KEY_K:
                    self.page(UP)
                elif self.ch == KEY_J:
                    self.page(DOWN)
            if self.ch == KEY_B:
                self.content_list = []

        # Listings
        elif display_type == 'defaults':
            if self.ch == KEY_DOWN or self.ch ==  KEY_J:
                # Only have downward keys when on listings
                if not self.menu_type == 'exit':
                    self.menu_type = 'listing'
                    self.c_listing = min(len(ALL_LISTINGS) - 1, self.c_listing + 1)
            elif self.ch == KEY_UP or self.ch == KEY_K:
                self.menu_type = 'listing'
                self.c_listing = max(0, self.c_listing - 1)
            elif self.ch == KEY_LEFT or self.ch == KEY_RIGHT:
                self.c_listing = len(ALL_LISTINGS.keys())
                self.menu_type = 'exit'
            # Categories
            elif self.ch == KEY_ENTER or self.ch == KEY_L:
                if self.menu_type == 'exit':
                    sys.exit(0)

                categories = ALL_LISTINGS.get(list(ALL_LISTINGS)[self.c_listing])
                self.c_cat = 0  # reset highlight line (category)
                self.menu_type = 'category'

                while True:
                    self.draw_categories('category')
                    self.ch = self.pad_menu.getch()

                    # Category buttons
                    if self.stream_type == 'defaults':
                        if self.ch == KEY_DOWN or self.ch == KEY_J:
                            # If down on last category, go to apply, else go to next
                            if self.c_cat + 1 == len(categories):
                                self.c_cat = len(categories)
                                self.stream_type = 'menu_cat'
                                self.menu_type = 'apply'
                            else:
                                self.c_cat = min(len(categories) - 1, self.c_cat + 1)
                        elif self.ch == KEY_UP or self.ch == KEY_K:
                            self.c_cat = max(0, self.c_cat - 1)
                        elif self.ch == KEY_ENTER or self.ch == KEY_L:
                            self.c_apply.add(self.c_cat)
                        elif self.ch == KEY_LEFT:
                            self.c_cat = len(categories)
                            self.stream_type = 'menu_cat'
                            self.menu_type = 'back'
                        elif self.ch == KEY_RIGHT:
                            self.c_cat = len(categories)
                            self.stream_type = 'menu_cat'
                            self.menu_type = 'apply'
                    # Back/apply buttons
                    elif self.stream_type == 'menu_cat':
                        if self.ch == KEY_LEFT or self.ch == KEY_J:
                            self.menu_type = 'back'
                        elif self.ch == KEY_RIGHT or self.ch == KEY_K:
                            self.menu_type = 'apply'
                        elif self.ch == KEY_ENTER or self.ch == KEY_L:
                            if self.menu_type == 'apply':
                                self.apply_defaults()

                            # Reset back to listings
                            self.menu_type = 'listing'
                            self.c_apply = set()
                            self.c_listing = 0
                            self.top = 0
                            self.stream_type = 'defaults'
                            break
                        elif self.ch == KEY_UP and len(self.c_apply) != len(categories):
                            self.c_cat = len(categories) - 1
                            self.stream_type = 'defaults'
                            self.menu_type = 'category'

    def apply_defaults(self):
        listing = list(ALL_LISTINGS.keys())[self.c_listing]
        categories = list(ALL_LISTINGS.get(listing))
        defaults = [categories[i] for i in self.c_apply]

        self.rc.defaults[listing] = ', '.join(defaults)

        with open(self.rc.config, 'w') as f:
            f.writelines(['[Credentials]\n',
                          f'user: {self.rc.user}\n',
                          f'pass: {self.rc.pw}\n\n',
                          '[Defaults]\n',
                          f'{self.rc.get_defaults()}'])

    def page(self, direction):
        """Page up or down based on input.

        Args:
            direction: (int) Direction to page.
        """
        # PAGE DOWN
        if direction == DOWN:
            # On last page of category
            if self.c_count + self.items_shown == self.c_cat_len:
                if self.content_list:
                    return
                self.p_cat_len = self.c_cat_len
                self.p_cat = self.c_cat

                self.c_cat += 1
                self.c_count = 0
                self.c_page = 1
                self.t_pages = 0

                # If no more categories
                if self.c_cat == len(self.cat_lens[self.c_listing]):
                    self.p_listing = self.c_listing
                    self.c_listing += 1

                    self.c_cat = 0
                    self.p_cat = 0
                    self.p_count = 0
            # On non-last page of category
            elif self.c_count != self.c_cat_len:
                self.p_count = self.c_count  # for UP

                self.c_count += self.items_shown
                self.c_page += 1

        # PAGE UP
        elif direction == UP:
            # On non-1st page (any listing)
            if self.c_count > 0:
                self.c_count = self.p_count
                self.p_count = max(0, self.c_count - self.max_count)
                self.c_page -= 1
            # On 1st page
            elif self.c_count == 0:
                # On 1st category of 1st listing
                if self.c_listing == 0 and self.c_cat == 0:
                    self.c_count = 0
                    self.p_count = 0
                    self.p_cat_len = 0
                # Between categories in same listing
                elif self.c_count == 0 and self.c_cat > 0:
                    self.c_cat = len(self.cat_lens[self.c_listing][:self.c_cat]) - 1
                    self.p_cat = max(0, self.c_cat - 1)
                    cat_len = self.cat_lens[self.c_listing][self.c_cat]

                    if self.p_cat_len % self.max_count == 0:
                        self.c_page = self.p_cat_len // self.max_count
                        self.p_count = self.max_count * (cat_len // self.max_count - 2)
                    else:
                        self.c_page = self.p_cat_len // self.max_count + 1
                        self.p_count = self.max_count * (cat_len // self.max_count) - self.max_count

                    self.c_count = self.p_count + self.max_count

                    # If paging up to 1st category of a non-1st listing,
                    #   set p_cat_len to length of the last category in
                    #   the listing before the current one. Otherwise,
                    #   just set # it to the previous category.
                    if self.c_cat == 0:
                        self.p_cat_len = self.cat_lens[max(0, self.c_listing - 1)][self.c_cat - 1]
                    else:
                        self.p_cat_len = self.cat_lens[self.c_listing][self.c_cat - 1]
                # On 1st category of non-1st listing
                else:
                    self.c_listing -= 1
                    self.p_listing = max(0, self.p_listing - 1)
                    self.c_cat = len(self.cat_lens[self.c_listing][:-1])
                    self.p_cat = max(0, self.c_cat - 1)
                    cat_len = self.cat_lens[self.c_listing][self.c_cat]

                    if self.p_cat_len % self.max_count == 0:
                        self.c_page = self.p_cat_len // self.max_count
                        self.p_count = self.max_count * (cat_len // self.max_count - 2)
                    else:
                        self.c_page = self.p_cat_len // self.max_count + 1
                        self.p_count = self.max_count * (cat_len // self.max_count) - self.max_count

                    self.c_count = self.p_count + self.max_count
                    prev_cat = -2 if len(self.cat_lens[self.p_listing]) > 1 else -1
                    self.p_cat_len = self.cat_lens[self.p_listing][prev_cat]

    def refresh(self):
        """Refresh pad.

        (y, x): Coordinate of upper-left corner of pad area to show.
        (y, x): Coordinate of upper-left corner of window area to be filled with content.
        (y, x): Coordinate of lower-right corner of window area to be filled with content.
        """
        self.pad_banner.refresh(0, 0, 2, 0, 10, self.width)
        self.pad_header.refresh(0, 0, 10, 0, 13, self.width - 1)
        self.pad_content.refresh(0, 0, 13, 1, self.height - 2, self.width - 1)
        self.pad_menu.refresh(0, 0, self.height - 2, 1, self.height, self.width - 1)

    def display_defaults(self):
        # Erase pads
        self.pad_banner.erase()
        self.pad_header.erase()
        self.pad_content.erase()
        self.pad_menu.erase()

        # Draw pads
        self.draw_banner()
        self.draw_listing('defaults')
        self.draw_header()
        self.draw_listings()
        self.draw_menu(self.menu_type)
        self.refresh()

    def draw_listings(self):
        listings = [f'{listing}:' for listing in ALL_LISTINGS.keys()]
        for i, listing in enumerate(listings):
            if self.width % 2 == 0:
                extra = ''  if len(listing) % 2 == 0 else ' '
            else:
                extra = ''  if len(listing) % 2 != 0 else ' '

            spacing = ' ' * ((self.width - len(listing)) // 2)
            line = f'{spacing}{listing}{spacing}{extra}'
            if i == self.c_listing:
                self.pad_content.addstr(line, curses.color_pair(4))
            else:
                self.pad_content.addstr(line)

        if self.menu_type == 'content':
            self.menu_type = 'listing'

    def draw_categories(self, menu_type):
        # Erase pads
        self.pad_header.erase()
        self.pad_content.erase()
        self.pad_menu.erase()

        # Draw pads
        listing = list(ALL_LISTINGS.keys())[self.c_listing]
        self.draw_listing('defaults')
        self.draw_header(f' {listing} ')

        i = 0
        categories = ALL_LISTINGS.get(listing)
        self.end = len(categories) - 1

        while i < len(categories):
            category = list(categories.keys())[i]
            if self.width % 2 == 0:
                extra = ''  if len(category) % 2 == 0 else ' '
            else:
                extra = ''  if len(category) % 2 != 0 else ' '

            spacing = ' ' * ((self.width - len(category)) // 2)
            line = f'{spacing}{category}{spacing}{extra}'

            # If current line isn't in current_apply
            if i == self.c_cat and i not in self.c_apply:
                self.pad_content.addstr(line, curses.color_pair(4))
            # If applying defaults or going down
            elif i == self.c_cat and i in self.c_apply and \
                 (self.ch == KEY_L or self.ch == KEY_ENTER or \
                  self.ch == KEY_J or self.ch == KEY_DOWN):

                # If going down from last category
                if (self.ch == KEY_L or self.ch == KEY_ENTER) and self.c_cat == self.end:
                    i = 0
                    self.end -= 1
                    self.c_cat = max(self.top, self.c_cat - 1)
                    self.pad_content.erase()
                    continue
                # If going down and everything below is selected
                elif (self.ch == KEY_J or self.ch == KEY_DOWN) and self.c_cat == self.end:
                    self.stream_type = 'menu_cat'
                    self.c_cat = len(categories)
                    self.menu_type = 'apply'
                # If applying
                else:
                    self.c_cat = min(len(categories) - 1, self.c_cat + 1)
                # If the 1st category's selected, make the top the next category
                if i == self.top:
                    self.top += 1

                self.pad_content.addstr(line, curses.color_pair(5))
            # If current line's in current_apply (up)
            elif i == self.c_cat and i in self.c_apply and \
                 (self.ch == KEY_K or self.ch == KEY_UP):
                i = 0
                self.c_cat = max(self.top, self.c_cat - 1)
                self.pad_content.erase()
                continue
            # If non-current line's in current_apply
            elif i != self.c_cat and i in self.c_apply:
                self.pad_content.addstr(line, curses.color_pair(5))
            # If non-current line's not in current_apply
            else:
                self.pad_content.addstr(line)

            i += 1

        # If all are selected, move to menu
        if len(self.c_apply) == len(categories):
            self.stream_type = 'menu_cat'
            self.c_cat = len(categories)
            if self.ch == KEY_K or self.ch == KEY_L or self.ch == KEY_ENTER:
                self.menu_type = 'apply'
            elif self.ch == KEY_J:
                self.menu_type = 'back'

        self.draw_menu(self.menu_type)  # needed since in a while loop in input_stream
        self.refresh()

    def display_content(self, listings, categories, contents):
        """Draw banner, header, content, menu.

        Args:
            listings    (list) All listings.
            categories: (list) All categories.
            contents:   (list) All content.
        """
        # Exit if done with last category in last listing
        if self.c_listing == len(listings):
            sys.exit(0)

        # Erase pads
        self.pad_banner.erase()
        self.pad_header.erase()
        self.pad_content.erase()
        self.pad_menu.erase()

        # Partition listings, categories, and contents
        current_category = categories[self.c_listing][self.c_cat]
        current_contents = contents[self.c_listing][self.c_cat]
        current_contents_leftover = current_contents[1][self.c_count:]
        self.c_cat_len = len(current_contents[1])

        # Draw pad
        self.draw_banner()
        self.draw_listing(listings[self.c_listing])
        self.draw_header(f' {current_category} ')
        self.draw_contents(current_contents_leftover)

        # Get max # of items that can be shown on non-last pages
        # it's here and not in paging b/c we need max_count for total_pages.
        # otherwise, total pages won't be updated till the 2nd page
        if self.c_count == 0:
            self.max_count = self.items_shown

        self.draw_menu(self.menu_type)
        self.refresh()

    def draw_banner(self):
        """Draw program banner."""
        self.pad_banner.addstr(BANNER, curses.color_pair(1))

    def draw_listing(self, listing):
        """Draw current listing.

        Args:
            listing: (list) All Listings.
        """
        self.pad_header.addstr(f'{listing.upper()}\n', curses.color_pair(1))

    def draw_header(self, category=''):
        """Draw current category header.

        Args:
            listing: (list) All listings.
            category: (list) All categories.
        """
        header_l = '─' * (self.width - 4 - len(category))
        header_r = '─' * 4

        self.pad_header.addstr(f'{header_l}')
        self.pad_header.addstr(category, curses.color_pair(2))
        self.pad_header.addstr(f'{header_r}\n')

    def draw_contents(self, contents):
        """Draw content (title, links).

        Args:
            contents: (list) All contents.
        """
        self.items_shown = 0
        current_content_position = 0

        for i in range(len(contents)):
            # If a new item would be directly above the menu, stop drawing
            if current_content_position + 4 > self.content_height:
                break

            title, link = contents[i]

            # Truncate long titles
            # 7 = " " + len(N) + ". " + " ..."
            if len(title) > (self.width - 5):
                number_len = len(str(i + self.c_count + 1))
                title = '{} ...'.format(title[:self.width - 7 - number_len])

            # Truncate long links
            # 13 = (" " * 9) + " ..."
            if len(link) > (self.width - 9):
                link = '{} ...'.format(link[:self.width - 13])

            # Print titles and links
            self.pad_content.addstr(f'{i + self.c_count + 1}. ')
            self.pad_content.addstr(f'{title}\n\t')
            self.pad_content.addstr(f'{link}\n\n', curses.color_pair(3))

            # Update cursor position and items shown counter
            self.items_shown += 1
            current_content_position += 3

    def draw_menu(self, page_type):
        """Draw menu.

        self.t_pages is set here since it needs to be displayed on
          the 1st page, ruling out updating it in mega.page() with
          everything else.

        Args:
            page_type: (String) Determines whether to draw display menu or
                                  defaults menus.
        """
        # Content mode
        if page_type == 'content':
            if self.menu_type == 'search':
                menu = '[q]uit [b]ack [j/k] page'
            else:
                menu = '[q]uit [j/k] page'

            try:
                remainder = self.c_cat_len % self.max_count
                quotient  = self.c_cat_len // self.max_count
                self.t_pages = quotient + 1 if remainder else quotient
                pages = f'({self.c_page}/{self.t_pages})'

                page_len = len(str(self.c_page)) + len(str(self.t_pages))
                spacing = ' ' * (self.width - (len(menu) + 4 + page_len))

                self.pad_menu.addstr(f'{menu}{spacing}{pages}')
            except ZeroDivisionError as e:
                # if we're in here, we probably searched for something
                #   with no results or we hit the timeout or we're not
                #   logged in (i don't think its this).
                menu = '[q]uit [b]ack'
                self.pad_content.addstr('no hits')
                self.pad_menu.addstr(menu)
        elif page_type == 'exit':
            menu = '[exit]'
            spacing = ' ' * ((self.width - len(menu)) // 2)

            self.pad_menu.addstr(spacing)
            self.pad_menu.addstr(menu, curses.color_pair(4))
        # Apply button (colored)
        elif page_type == 'apply':
            m_back = '[back]           '
            m_apply = '[apply]'
            spacing = ' ' * ((self.width - len(m_back) - len(m_apply)) // 2)

            self.pad_menu.addstr(f'{spacing}{m_back}')
            self.pad_menu.addstr(m_apply, curses.color_pair(4))
        # Back button (colored)
        elif page_type == 'back':
            self.pad_menu.erase()

            m_back = '[back]'
            m_apply = '           [apply]'
            spacing = ' ' * ((self.width - len(m_back) - len(m_apply)) // 2)

            self.pad_menu.addstr(f'{spacing}')
            self.pad_menu.addstr(f'{m_back}', curses.color_pair(4))
            self.pad_menu.addstr(m_apply)
        # Default mode
        else:
            menu = '[exit]' if page_type == 'listing' else \
                   '[back]           [apply]'
            spacing = ' ' * ((self.width - len(menu)) // 2)

            self.pad_menu.addstr(f'{spacing}{menu}')

    def display_search(self, title=None):
        # Erase pads
        self.pad_banner.erase()
        self.pad_header.erase()
        self.pad_content.erase()
        self.pad_menu.erase()

        # Draw pads
        self.draw_banner()
        self.draw_listing('search')
        self.draw_header()

        if not title:
            if self.ch == 0 or self.ch == KEY_B:
                search_text = self.draw_searchbox()
                self.refresh()
                return search_text
            else:
                self.draw_contents(self.content_list[self.c_count:])
                self.draw_menu('content')
                self.refresh()
                return None

    def draw_searchbox(self):
        try:
            search_win = curses.newwin(1, 66,
                    (self.content_height - 1) // 2,
                    (self.width - 1) // 2 - 31)

            search_box = curses.textpad.rectangle(self.pad_content,
                    (self.content_height - 1) // 2 - 14,      # start_y
                    (self.width - 1) // 2 - 34,               # start_x
                    (self.content_height - 1) // 2 - 14 + 2,  # end_y
                    (self.width - 1) // 2 - 34 + 68)          # end_x
        except Exception as e:
            fatal('terminal is too short')

        self.refresh()  # refresh search box pad

        textbox = curses.textpad.Textbox(search_win)  # create text box
        textbox.edit()  # get characters
        search_text = textbox.gather()[:-1]  # exclude termination char, which shows up when we try to urlencode

        search_win.erase()
        self.pad_content.erase()
        return search_text

    def get_search(self, search_text, rc):
        # Login
        session = requests.session()
        login = session.post('https://forum.snahp.it/ucp.php?mode=login',
                data= {'username': rc.user,
                       'password': rc.pw,
                       'login': 'Login'})

        # Search
        f = {'keywords': search_text, 'sf': 'titleonly'}
        url = f'https://forum.snahp.it/search.php?{urllib.parse.urlencode(f)}'
        resp = session.get(url)

        # Parse
        soup = BeautifulSoup(resp.text, 'lxml')
        title_pattern = re.compile(r'(\[MEGA\]|\[Mega\]|\[ZS\]|\[MEGA/ZS\]|【MEGA】)\s?(\[(?:ZS|TV|TVPack|MOVIEPACK|FLAC|320|EDUCATION|E-Book|EPUB|PDF)\])?(\s?.*(?=<))')
        link_pattern = re.compile(r'"\./.*"(?=>)')

        for title in soup.find_all('a', class_='topictitle'):
            title_match = re.search(title_pattern, str(title))
            link_match  = re.search(link_pattern, str(title))
            if title_match:
                title_str = title_match.group(3).lstrip()
                path_str  = link_match.group()[2:-1]
                link_str  = f'https://forum.snahp.it{path_str}'.replace('&amp;', '&')
                self.content_list.append((title_str, link_str))

        self.c_cat_len = len(self.content_list)

        self.draw_contents(self.content_list)
        if self.c_count == 0:
            self.max_count = self.items_shown
            self.c_cat = 0
            self.c_listing = 0
            self.cat_lens.append([0])
        self.draw_menu('content')

        self.refresh()


class Megarc():
    """Configuration file interaction handler.

    Attributes:
        config:   (String)       Absolute path of config file.
        creds:    (ConfigParser) Represents parsed config file.
        user:     (String)       Username in the config file.
        pw:       (String)       Password in the config file.
        defaults: (SectionProxy) All defaults in the config file.
    """
    def __init__(self, config):
        """Configuration file API.

        If the config file doesn't exist, we still
          want to be able to create a config file.

        Args:
            config: (String) Absolute path of config file.
        """
        self.config = config

        if os.path.exists(config):
            self.creds = configparser.ConfigParser()
            self.creds.read(self.config)
            self.user = self.creds['Credentials']['user']
            self.pw = self.creds['Credentials']['pass']
            self.defaults = self.creds['Defaults']

    def __repr__(self):
        num_attr = 4  # 1 less
        mega_obj = 'Megarc({}{})'.format('{!r}, ' * num_attr, '{!r}')

        return mega_obj.format(
            self.config,
            self.creds,
            self.user,
            self.pw,
            self.defaults)

    def __str__(self):
        return ('Megarc\n'
                f'   Config file path: {self.config}\n'
                f'   Config file representation: {self.creds}\n'
                f'   Username: {self.user}\n'
                f'   Password: {self.pw}\n'
                f'   Default section representation: {self.defaults}\n')

    def create(self, config):
        """Create empty configuration file.

        Config file has owner read/write.

        Args:
            config:   (String) Absolute path of config file.
        """
        listings = '\n'.join([f'{listing}:' for listing in ALL_LISTINGS.keys()])
        with open(config, 'w') as f:
            f.writelines(['[Credentials]\n',
                          'user:\n',
                          'pass:\n\n',
                          '[Defaults]\n'
                          f'{listings}\n'])
            os.chmod(config, stat.S_IRUSR | stat.S_IWUSR)

    def check_defaults(self):
        """Check if there are any defaults selected."""
        if any([default for default in self.defaults.values()]):
            return
        sys.exit('no listings selected')

    def get_defaults(self):
        """Return all listings and categories."""
        all_defaults = ''
        longest = len(max(ALL_LISTINGS.keys(), key=len))

        for listing, defaults in self.defaults.items():
            spacing = ' ' * (longest - len(listing))
            all_defaults += f'{listing}: {spacing}{defaults}\n'

        return all_defaults

    def show_creds(self, field):
        """Show username and/or password.

        Args:
            field: (String) The field to set.
        """
        if field == 'name':
            print('user:', self.user)
        elif field == 'pass':
            print('pass:', self.pw)
        elif field == 'creds':
            print('user:', self.user)
            print('pass:', self.pw)
        elif field == 'defaults':
            print(self.get_defaults(), end='')

    def set_handler(self, field, new_value):
        """Handler for set functions.

        Args:
            new_value: (String) New account values to set.
        """
        set_funcs = {'name': self.set_user,
                     'pass': self.set_pass}

        set_funcs[field](new_value)

        with open(self.config, 'w') as f:
            f.writelines(['[Credentials]\n',
                          f'user: {self.user}\n',
                          f'pass: {self.pw}\n\n',
                          '[Defaults]\n',
                          f'{self.get_defaults()}'])

    def set_user(self, new_username):
        """Set username.

        Args:
            new_username: (String) New username.
        """
        self.user = new_username

    def set_pass(self, new_password):
        """Set password.

        Args:
            new_password: (String) New password.
        """
        self.pw = new_password


def fatal(err):
    """Exit with a colored error message.

    Args:
        err: (String) The error message.
    """
    sys.exit(f'\u001b[1m\u001b[38;5;9mfatal\u001b[0m: {err}')


async def login(user, pw):
    url = 'https://forum.snahp.it/ucp.php?mode=login'
    payload = {'username': user,
               'password': pw,
               'login': 'Login'}

    """
    We have to make a new session every time otherwise
      we'll be logged out for some requests for some
      reason, which results in no content which means
      categories will be skipped.
    """
    # Persist_cookies needed otherwise we'd log out again
    session = asks.Session(persist_cookies=True, connections=2)
    login = await session.post(url, data=payload)

    # If server is down, exit with the error they'll have up
    if login.status_code == 404:
        req = await session.get('https://forum.snahp.it')
        soup = BeautifulSoup(req.text, 'lxml')
        fatal(str(soup.h3).replace('<h3>', '').replace('</h3>', ''))

    return session


async def parse_content(nursery, result, listing, category, everything):
    """Update :dict: everything with content for the appropriate category.

    Args:
        nursery:    (Nursery)  Trio's nursery.
        result:     (Response) Response of asks.get().
        listing:    (String)   Current listing.
        category:   (String)   Current category.
        everything: (dict)     Dictionary to be updated with content.
    """
    soup = BeautifulSoup(result.text, 'lxml')
    type_pattern = re.compile(r'(mega|zippy|gdrive|android|ios)_icon')
    # title_pattern = re.compile(r'(\[MEGA\]|\[Mega\]|\[ZS\]|\[MEGA/ZS\]|【MEGA】)\s?(\[(?:ZS|TV|TVPack|MOVIEPACK|FLAC|320|EDUCATION|E-Book|EPUB|PDF)\])?(\s?.*(?=<))')
    title_pattern = re.compile(r'(>\s+)(.*(?=<))')
    link_pattern = re.compile(r'"\./.*"(?=>)')
    content_list = []

    for title in soup.find_all('a', class_='topictitle'):
        type_match = re.search(type_pattern, str(title))
        title_match = re.search(title_pattern, str(title))
        link_match  = re.search(link_pattern, str(title))
        if type_match and title_match:
            title_str = title_match.group(2)
            path_str  = link_match.group()[2:-1]
            link_str  = f'https://forum.snahp.it{path_str}'.replace('&amp;', '&')
            content_list.append((title_str, link_str))

        # if title_match:
            # title = title_match.group(3).lstrip()
            # path  = link_match.group()[2:-1]
            # link  = f'https://forum.snahp.it{path}'.replace('&amp;', '&')
            # content_list.append((title, link))

    if content_list:
        everything[listing][category] = [len(content_list), content_list]


async def get_content(nursery, session, path, listing, category, everything):
    """Send request to website and parse out content/links.

    Args:
        nursery:   (Nursery) Trio's nursery.
        session:   (Session) Session object we'll use for all requests.
        path:      (String)  Current category's URL path.
        listing    (String)  Current listing.
        category   (String)  Current category.
        everything (dict)    Contains all listings, categories, and content.
    """
    url = 'https://forum.snahp.it/viewforum.php?f={}'.format(path)
    result = await session.get(url)
    nursery.start_soon(parse_content, nursery, result, listing, category, everything)


async def parse_args(rc, mega):
    """Parse command-line arguments.

    Args:
        rc:   (Megarc) Object that interacts with config file.
        mega: (Mega)   Object that shows Mega contents.

    TODO:
        1. Speed up those parsing lambdas.
    """
    argl = len(sys.argv) - 1
    argv = sys.argv[1:]

    if not argv or \
            ((argv[0] != '--config' or argv[0] != 'config') \
             and argl == 2 and argv[1] != 'create'):
        if not os.path.exists(rc.config):
            fatal('no configuration file found')

    if argv:
        if argv[0] == '--config' or argv[0] == 'config':
            valid_config_modes = ['user.name',
                                  'user.pass',
                                  'user.creds',
                                  'user.defaults',
                                  'defaults',
                                  'create']

            # Invalid --config usage handling
            if argl == 1:
                fatal('missing config arg')
            if argv[1] not in valid_config_modes:
                fatal(f'invalid --config option: {argv[1]}')

            # Create config
            if argv[1] == 'create':
                if argl > 2:
                    fatal(f'unrecognized arguments: {" ".join(argv[2:])}')

                if os.path.exists(rc.config):
                    fatal(f'configuration file already exists')

                rc.create(rc.config)
                sys.exit(f'Created: {rc.config}')

            # Set defaults
            elif argv[1] == 'defaults':
                if argl > 2:
                    fatal(f'unrecognized arguments: {" ".join(argv[2:])}')
                curses.wrapper(mega.run, 'defaults')

            # Creds
            else:
                field = argv[1].split('.')[1]

                if argl > 3 or \
                   (argl == 3 and (field == 'creds' or field == 'defaults')):
                    fatal(f'unrecognized arguments: {" ".join(argv[2:])}')

                # Show creds
                if argl == 2:
                    rc.show_creds(field)
                # Set creds
                elif argl == 3:
                    rc.set_handler(field, argv[2])
        elif argv[0] == '--search' or argv[0] == 'search':
            if argl == 1:
                curses.wrapper(mega.run, 'search', rc=rc)
            elif argl == 2:
                curses.wrapper(mega.run, 'search', title=argv[1], rc=rc)
            else:
                fatal(f'too many args')
        elif argv[0] == '--version':
            sys.exit(VERSION)
        elif argv[0] == '--help' or argv[0] == '-h':
            sys.exit(HELP)
        else:
            fatal(f'unrecognized arguments: {" ".join(argv)}')
    else:
        # Temporary until displaying certain listings/categories is implemented
        if argl > 1:
            fatal('too many args')

        # Check for any defaults
        rc.check_defaults()

        # Get category URL paths
        paths = {}
        for listing, defaults in rc.defaults.items():
            if defaults:
                d_list = defaults.split(', ')
                categories = ALL_LISTINGS.get(listing)
                paths[listing] = list(map(lambda d : (d, categories[d]), d_list))

        # Login
        session = await login(rc.user, rc.pw)

        # Get all listings, categories, and contents wanted
        everything = {}
        async with trio.open_nursery() as nursery:
            for listing, categories_paths in paths.items():
                everything[listing] = {}
                for category, path in categories_paths:
                    await get_content(nursery, session, path, listing, category, everything)

        # Separate everything
        listings      = list(everything.keys())
        categories    = list(map(lambda x : list(x.keys()), everything.values()))
        contents      = list(map(lambda x : list(x.values()), everything.values()))
        mega.cat_lens = list(map(lambda i : list(map(lambda j : j[0], i)), contents))

        curses.wrapper(mega.run, 'contents',
                listings=listings, categories=categories, contents=contents)


def main():
    """Main program.

    Args:
        config: (String) Absolute path of config file.
    """
    mega_dir = os.path.dirname(os.path.realpath(__file__))
    config = os.path.join(mega_dir, '.megarc')
    rc = Megarc(config)

    # if os.path.exists(config) and (not rc.user or not rc.pw):
        # fatal('error: invalid credentials')

    mega = curses.wrapper(Mega, rc)
    trio.run(parse_args, rc, mega)
