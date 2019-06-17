import urwid

ATTR_EDIT_NORMAL = 'edit normal'
ATTR_EDIT_SELECT = 'edit select'
ATTR_BUTTON_NORMAL = 'button normal'
ATTR_BUTTON_SELECT = 'button select'
ATTR_DARK_RED_BG = 'dark red bg'
ATTR_DARK_BLUE_BG = 'dark blue bg'
ATTR_DARK_GREEN_BG = 'dark green bg'
ATTR_WHITE_BG = 'white bg'
ATTR_BLACK_BG = 'black bg'
ATTR_QUESTION = 'question'
ATTR_HEADER = 'header'
ATTR_FOOTER = 'footer'


def calc_btn_label_width(btn: urwid.Button):
    return len(btn.label) + 4


design_path = ''
