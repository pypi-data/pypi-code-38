#!/usr/bin/env python3

import pyperclip

def superEncrypt(translated, mode='encrypt'):
    if mode == 'encrypt':
        for i in range(1, 5):
            translated = encryptor(translated)
    elif mode == 'decrypt':
        for i in range(1, 5):
            translated = encryptor(translated, 'decrypt')
    pyperclip.copy(translated)
    return translated

def encryptor(message, mode='encrypt'):
    key = 13
    SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!?.'
    translated = ''
    for symbol in message:
        if symbol in SYMBOLS:
            symbolIndex = SYMBOLS.find(symbol)

            if mode == 'encrypt':
                translatedIndex = symbolIndex + key
            elif mode == 'decrypt':
                translatedIndex = symbolIndex - key

            if translatedIndex >= len(SYMBOLS):
                translatedIndex = translatedIndex - len(SYMBOLS)
            elif translatedIndex < 0:
                translatedIndex = translatedIndex + len(SYMBOLS)

            translated = translated + SYMBOLS[translatedIndex]
        else:
            translated = translated + symbol

    return translated
