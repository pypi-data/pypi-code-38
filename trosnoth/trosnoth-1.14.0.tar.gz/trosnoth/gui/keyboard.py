import pygame
import collections


def mouseButton(button):
    return -button


# 1. We want to be able to represent a shortcut as a string.
def shortcutName(key, modifiers=0):
    try:
        name = NAMED[key]
    except KeyError:
        if key < 0:
            name = 'Mouse%d' % (-key,)
        else:
            name = pygame.key.name(key)

    # Add the modifiers.
    modString = ''
    for kmod, modName in KMOD_NAMES:
        if modifiers & kmod:
            modString = '%s%s+' % (modString, modName)

    return '%s%s' % (modString, name)

NAMED = {
    -1: 'L.Click', -2: 'M.Click', -3: 'R.Click',

    pygame.K_BACKSPACE: 'Backspace', pygame.K_BREAK: 'Break',
    pygame.K_CAPSLOCK: 'Capslock', pygame.K_CLEAR: 'Clear', pygame.K_DELETE:
    'Del', pygame.K_DOWN: 'Down', pygame.K_END: 'End', pygame.K_ESCAPE:
    'Escape', pygame.K_EURO: 'Euro', pygame.K_F1: 'F1', pygame.K_F2: 'F2',
    pygame.K_F3: 'F3', pygame.K_F4: 'F4', pygame.K_F5: 'F5', pygame.K_F6:
    'F6', pygame.K_F7: 'F7', pygame.K_F8: 'F8', pygame.K_F9: 'F9',
    pygame.K_F10: 'F10', pygame.K_F11: 'F11', pygame.K_F12: 'F12',
    pygame.K_F13: 'F13', pygame.K_F14: 'F14', pygame.K_F15: 'F15',
    pygame.K_FIRST: 'First', pygame.K_HELP: 'Help', pygame.K_HOME: 'Home',
    pygame.K_INSERT: 'Ins', pygame.K_LALT: 'L.Alt', pygame.K_LCTRL:
    'L.Ctrl', pygame.K_LEFT: 'Left', pygame.K_LMETA: 'L.Meta',
    pygame.K_LSHIFT: 'L.Shift', pygame.K_LSUPER: 'L.Super', pygame.K_MENU:
    'Menu', pygame.K_MODE: 'Mode', pygame.K_NUMLOCK: 'Numlock',
    pygame.K_PAGEDOWN: 'PgDn', pygame.K_PAGEUP: 'PgUp', pygame.K_PAUSE:
    'Pause', pygame.K_POWER: 'Power', pygame.K_PRINT: 'Print',
    pygame.K_RALT: 'R.Alt', pygame.K_RCTRL: 'R.Ctrl', pygame.K_RETURN:
    'Return', pygame.K_RIGHT: 'Right', pygame.K_RMETA: 'R.Meta',
    pygame.K_RSHIFT: 'R.Shift', pygame.K_RSUPER: 'R.Super',
    pygame.K_SCROLLOCK: 'Scrolllock', pygame.K_SYSREQ: 'SysRq', pygame.K_TAB:
    'Tab', pygame.K_UP: 'Up', pygame.K_SPACE: 'Space',

    pygame.K_a: 'a', pygame.K_b: 'b', pygame.K_c: 'c', pygame.K_d: 'd',
    pygame.K_e: 'e', pygame.K_f: 'f', pygame.K_g: 'g', pygame.K_h: 'h',
    pygame.K_i: 'i', pygame.K_j: 'j', pygame.K_k: 'k', pygame.K_l: 'l',
    pygame.K_m: 'm', pygame.K_n: 'n', pygame.K_o: 'o', pygame.K_p: 'p',
    pygame.K_q: 'q', pygame.K_r: 'r', pygame.K_s: 's', pygame.K_t: 't',
    pygame.K_u: 'u', pygame.K_v: 'v', pygame.K_w: 'w', pygame.K_x: 'x',
    pygame.K_y: 'y', pygame.K_z: 'z', pygame.K_0: '0', pygame.K_1: '1',
    pygame.K_2: '2', pygame.K_3: '3', pygame.K_4: '4', pygame.K_5: '5',
    pygame.K_6: '6', pygame.K_7: '7', pygame.K_8: '8', pygame.K_9: '9',
    pygame.K_KP0: 'keypad-0', pygame.K_KP1: 'keypad-1', pygame.K_KP2:
    'keypad-2', pygame.K_KP3: 'keypad-3', pygame.K_KP4: 'keypad-4',
    pygame.K_KP5: 'keypad-5', pygame.K_KP6: 'keypad-6', pygame.K_KP7:
    'keypad-7', pygame.K_KP8: 'keypad-8', pygame.K_KP9: 'keypad-9',
    pygame.K_KP_DIVIDE: 'keypad divide', pygame.K_KP_ENTER: 'keypad enter',
    pygame.K_KP_EQUALS: 'keypad equals', pygame.K_KP_MINUS: 'keypad minus',
    pygame.K_KP_MULTIPLY: 'keypad asterisk', pygame.K_KP_PERIOD:
    'keypad full stop', pygame.K_KP_PLUS: 'keypad plus',

    pygame.K_AMPERSAND: '&', pygame.K_ASTERISK: '*', pygame.K_AT: '@',
    pygame.K_BACKQUOTE: '`', pygame.K_BACKSLASH: '\\', pygame.K_CARET: '^',
    pygame.K_COLON: ':', pygame.K_COMMA: ',', pygame.K_DOLLAR: '$',
    pygame.K_EQUALS: '=', pygame.K_EXCLAIM: '!', pygame.K_GREATER: '>',
    pygame.K_LESS: '<', pygame.K_HASH: '#', pygame.K_LEFTBRACKET: '[',
    pygame.K_LEFTPAREN: '(', pygame.K_MINUS: '-', pygame.K_PERIOD: '.',
    pygame.K_PLUS: '+', pygame.K_QUOTE: "'", pygame.K_RIGHTBRACKET: ']',
    pygame.K_RIGHTPAREN: ')', pygame.K_SEMICOLON: ';', pygame.K_SLASH: '/',
    pygame.K_UNDERSCORE: '_'
 }

KMOD_NAMES = ((pygame.KMOD_CTRL, 'Ctrl'), (pygame.KMOD_ALT, 'Alt'),
              (pygame.KMOD_META, 'Meta'), (pygame.KMOD_SHIFT, 'Shift'))


# VirtualKeySet is a mapping from name -> default value.
class VirtualKeySet(collections.UserDict):
    pass

# KeyboardMapping is a mapping from key -> virtual key name.
class KeyboardMapping(collections.UserDict):
    def __init__(self, virtualKeys):
        self.virtualKeys = virtualKeys
        collections.UserDict.__init__(self, ((default, vk) for (vk, default) in
                virtualKeys.items()))

    def load(self, string):
        '''
        Restores a keyboard mapping from a configuration string.
        '''
        # Reset to defaults.
        self.data = {}

        # Update from string.
        unmappedKeys = dict(self.virtualKeys)
        for record in string.split('\n'):
            if record == '':
                continue
            key, vk = record.split(':')
            self.data[int(key)] = vk
            if vk in unmappedKeys:
                del unmappedKeys[vk]

        # Fill in any unmapped keys from the defaults if possible.
        for vk, default in unmappedKeys.items():
            if default not in self.data:
                self.data[default] = vk

    def save(self):
        '''
        Returns a configuration string for this keyboard mapping.
        '''
        records = ['%d:%s' % item for item in self.data.items()]
        return '\n'.join(records)

    def getkey(self, action):
        '''
        Returns one key that results in the given action or raises KeyError.
        '''
        for k, v in self.data.items():
            if v == action:
                return k
        raise KeyError(action)
