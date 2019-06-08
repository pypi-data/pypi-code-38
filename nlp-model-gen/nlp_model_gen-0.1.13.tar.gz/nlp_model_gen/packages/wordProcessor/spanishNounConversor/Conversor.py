# @Vendors
import fnmatch

# [WIP] Esta clase cumple la función de recibir un sustantivo y devolver su plurar
class Conversor:
    def __init__(self, general_configs):
        self.__configs = {
            'noun_groups': general_configs['groups'],
            'exceptions': general_configs['exceptions']
        }

    def set_config(self, general_configs):
        self.__configs = {
            'noun_groups': general_configs['groups'],
            'exceptions': general_configs['exceptions']
        }

    def a_plural(self, noun):
        words = noun.split()
        line = ''
        first_flag = True
        for word in words:
            if first_flag:
                first_flag = False
            else:
                line += ' '
            if not word in self.__configs['exceptions']:
                founded = False
                for group in self.__configs['noun_groups']:
                    if any(fnmatch.fnmatch(word, suffix) for suffix in group['suffixes']):
                        if 'backReplacements' in group.keys():
                            for backReplacement in group['backReplacements']:
                                if fnmatch.fnmatch(word, backReplacement['key']):
                                    word = word[0:len(word) - backReplacement['backCrop']]
                                    word = word + backReplacement['replacement']
                                    break
                        line += word + group['replacement']
                        founded = True
                        break
                if not founded:
                    line += word
            else:
                line += word
        if line == noun:
            return ''
        return line
