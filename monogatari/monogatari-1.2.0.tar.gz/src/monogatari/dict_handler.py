# -*- coding: utf-8 -*-
# Copyright 2019 Bruno Toshio Sugano <brunotoshio@gmail.com>


class DictHandler(object):
    def __init__(self, path):
        self._file_path = path
        self._categories = {}
        self._normal_dict = {}
        self._wildcard_dict = {}
        self.__parse()

    def __parse(self):
        category_part = False
        with open(self._file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if len(line) == 0:
                    continue
                tokens = line.split()
                if tokens[0] == '%':
                    category_part = not category_part
                elif category_part:
                    self._categories[tokens[0].strip()] = tokens[1].strip()
                else:
                    key = tokens[0].strip()
                    if key[-1] == '*':
                        self._wildcard_dict[key] = [self._categories[tk.strip()] for tk in tokens[1:]]
                    else:
                        self._normal_dict[key] = [self._categories[tk.strip()] for tk in tokens[1:]]

    def _wildcard_search(self, term):
        key = ''
        for letter in term:
            key += letter
            if f'{key}*' in self._wildcard_dict:
                return self._wildcard_dict[f'{key}*']
        return []

    def search(self, term):
        if term[-1] == '*':
            return self._wildcard_search(term)
        else:
            if term in self._normal_dict:
                return self._normal_dict[term]
            else:
                return []

    def categories(self):
        return list(self._categories.values())
