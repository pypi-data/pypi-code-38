#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Libervia: a Salut à Toi frontend
Copyright (C) 2013-2016 Adrien Cossa <souliane@mailoo.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Map the messages recipient types to their properties.
RECIPIENT_TYPES = {
    "To": {"desc": "Direct recipients", "optional": False},
    "Cc": {"desc": "Carbon copies", "optional": True},
    "Bcc": {"desc": "Blind carbon copies", "optional": True},
}

# Rich text buttons icons and descriptions
RICH_BUTTONS = {
    "bold": {"tip": "Bold", "icon": "media/icons/dokuwiki/toolbar/16/bold.png"},
    "italic": {"tip": "Italic", "icon": "media/icons/dokuwiki/toolbar/16/italic.png"},
    "underline": {
        "tip": "Underline",
        "icon": "media/icons/dokuwiki/toolbar/16/underline.png",
    },
    "code": {"tip": "Code", "icon": "media/icons/dokuwiki/toolbar/16/mono.png"},
    "strikethrough": {
        "tip": "Strikethrough",
        "icon": "media/icons/dokuwiki/toolbar/16/strike.png",
    },
    "heading": {"tip": "Heading", "icon": "media/icons/dokuwiki/toolbar/16/hequal.png"},
    "numberedlist": {
        "tip": "Numbered List",
        "icon": "media/icons/dokuwiki/toolbar/16/ol.png",
    },
    "list": {"tip": "List", "icon": "media/icons/dokuwiki/toolbar/16/ul.png"},
    "link": {"tip": "Link", "icon": "media/icons/dokuwiki/toolbar/16/linkextern.png"},
    "horizontalrule": {
        "tip": "Horizontal rule",
        "icon": "media/icons/dokuwiki/toolbar/16/hr.png",
    },
    "image": {"tip": "Image", "icon": "media/icons/dokuwiki/toolbar/16/image.png"},
}

# Define here your rich text syntaxes, the key must match the ones used in button.
# Tupples values must have 3 elements : prefix to the selection or cursor
# position, sample text to write if the marker is not applied on a selection,
# suffix to the selection or cursor position.
# FIXME: must not be hard-coded like this
RICH_SYNTAXES = {
    "markdown": {
        "bold": ("**", "bold", "**"),
        "italic": ("*", "italic", "*"),
        "code": ("`", "code", "`"),
        "heading": ("\n# ", "Heading 1", "\n## Heading 2\n"),
        "link": ("[desc](", "link", ")"),
        "list": ("\n* ", "item", "\n    + subitem\n"),
        "horizontalrule": ("\n***\n", "", ""),
        "image": ("![desc](", "path", ")"),
    },
    "bbcode": {
        "bold": ("[b]", "bold", "[/b]"),
        "italic": ("[i]", "italic", "[/i]"),
        "underline": ("[u]", "underline", "[/u]"),
        "code": ("[code]", "code", "[/code]"),
        "strikethrough": ("[s]", "strikethrough", "[/s]"),
        "link": ("[url=", "link", "]desc[/url]"),
        "list": ("\n[list] [*]", "item 1", " [*]item 2 [/list]\n"),
        "image": ('[img alt="desc\]', "path", "[/img]"),
    },
    "dokuwiki": {
        "bold": ("**", "bold", "**"),
        "italic": ("//", "italic", "//"),
        "underline": ("__", "underline", "__"),
        "code": ("<code>", "code", "</code>"),
        "strikethrough": ("<del>", "strikethrough", "</del>"),
        "heading": ("\n==== ", "Heading 1", " ====\n=== Heading 2 ===\n"),
        "link": ("[[", "link", "|desc]]"),
        "list": ("\n  * ", "item\n", "\n    * subitem\n"),
        "horizontalrule": ("\n----\n", "", ""),
        "image": ("{{", "path", " |desc}}"),
    },
    "XHTML": {
        "bold": ("<b>", "bold", "</b>"),
        "italic": ("<i>", "italic", "</i>"),
        "underline": ("<u>", "underline", "</u>"),
        "code": ("<pre>", "code", "</pre>"),
        "strikethrough": ("<s>", "strikethrough", "</s>"),
        "heading": ("\n<h3>", "Heading 1", "</h3>\n<h4>Heading 2</h4>\n"),
        "link": ('<a href="', "link", '">desc</a>'),
        "list": ("\n<ul><li>", "item 1", "</li><li>item 2</li></ul>\n"),
        "horizontalrule": ("\n<hr/>\n", "", ""),
        "image": ('<img src="', "path", '" alt="desc"/>'),
    },
}

# Define here the commands that are supported by the WYSIWYG edition.
# Keys must be the same than the ones used in RICH_SYNTAXES["XHTML"].
# Values will be used to call execCommand(cmd, False, arg), they can be:
# - a string used for cmd and arg is assumed empty
# - a tuple (cmd, prompt, arg) with cmd the name of the command,
#   prompt the text to display for asking a user input and arg is the
#   value to use directly without asking the user if prompt is empty.
COMMANDS = {
    "bold": "bold",
    "italic": "italic",
    "underline": "underline",
    "code": ("formatBlock", "", "pre"),
    "strikethrough": "strikeThrough",
    "heading": ("heading", "Please specify the heading level (h1, h2, h3...)", ""),
    "link": ("createLink", "Please specify an URL", ""),
    "list": "insertUnorderedList",
    "horizontalrule": "insertHorizontalRule",
    "image": ("insertImage", "Please specify an image path", ""),
}

# These values should be equal to the ones in plugin_misc_text_syntaxes
# FIXME: should the plugin import them from here to avoid duplicity? Importing
# the plugin's values from here is not possible because Libervia would fail.
PARAM_KEY_COMPOSITION = "Composition"
PARAM_NAME_SYNTAX = "Syntax"
