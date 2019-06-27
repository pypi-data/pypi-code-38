#!/bin/env python3
import json
import random
import os
import sys
from app.utils import get_dir_root
# class Aword:
#     # Initializer / Instance Attributes
#     def __init__(self, word, know_point=0, example="", noted="", ipa=""):
#         self.word = word
#         self.know_point = know_point
#         self.example = example
#         self.noted = noted
#         self.ipa = iba

class style():
    BLACK = lambda x: '\033[30m' + str(x)
    RED = lambda x: '\033[31m' + str(x)
    GREEN = lambda x: '\033[32m' + str(x)
    YELLOW = lambda x: '\033[33m' + str(x)
    BLUE = lambda x: '\033[34m' + str(x)
    MAGENTA = lambda x: '\033[35m' + str(x)
    CYAN = lambda x: '\033[36m' + str(x)
    WHITE = lambda x: '\033[37m' + str(x)
    UNDERLINE = lambda x: '\033[4m' + str(x)
    RESET = lambda x: '\033[0m' + str(x)

def _load_json_file(path_file_json):
    with open(path_file_json) as f:
        jsondata = json.load(f)
    return jsondata

def load_training_data():
    return _load_json_file(os.path.join(get_dir_root(),'data', '3000words.json' ))

def load_process_data(process_path_data):
    return _load_json_file(process_path_data)

def main():
    process_path_data = os.path.join(get_dir_root(),'data', 'process_3000words.json' )
    wordsdata = load_training_data()
    processdata = load_process_data(process_path_data)
    if not processdata:
        print("Initialize the process data....")
        processdata = [{"word": w['word'], "know_point": 0, "example": "", "noted": "", "ipa": ""} for w in wordsdata]
    print("start learing....")
    length_wordlist = len(processdata)
    number_word = 0
    try:
    # DO THINGS
        while number_word < 1:
            number_word = int(input(style.GREEN("Many the words you want to train? > ")))
        for i in range(number_word):
            word_n = random.randint(0,length_wordlist-1)
            print("------------------------")
            print(style.WHITE('Are you remember it? ') + style.GREEN(processdata[word_n]['word']))
            print("------------------------")
            while True:
                choice = input("y|n|uhm|c|  > ")
                if choice == 'y' :
                    print(style.GREEN("\nGreat!"))
                    print(processdata[word_n]['example'])
                    processdata[word_n]['know_point'] = processdata[word_n]['know_point'] + 1
                    print('\n')
                    input()
                if choice == 'n' :
                    print(style.YELLOW('\nOh no!'))
                    print(style.YELLOW('https://www.google.com/search?q=how+to+pronounce+{}'.format(processdata[word_n]['word'])))
                    print(style.YELLOW('https://www.google.com/search?q={}+l%C3%A0+g%C3%AC'.format(processdata[word_n]['word'])))
                    print('\n')
                    input()
                if choice == 'uhm' :
                    print(style.YELLOW('\n'+processdata[word_n]['ipa']))
                    print(style.YELLOW(processdata[word_n]['noted']))
                    print(style.YELLOW(processdata[word_n]['example']))
                    print(style.YELLOW('Oh no! https://www.google.com/search?q=how+to+pronounce+{}'.format(processdata[word_n]['word'])))
                    print('\n')
                    input()
                if choice == 'c' :
                    break
                break
        print("Ya You're finish challenge!")
        with open(process_path_data,'w', encoding='utf-8') as json_f:
            json.dump(processdata,json_f, ensure_ascii=False, indent=2)
        sys.exit()
    except KeyboardInterrupt:
        print("\nGood bye!")
        with open(process_path_data,'w', encoding='utf-8') as json_f:
            json.dump(processdata,json_f, ensure_ascii=False, indent=2)
        sys.exit()
if __name__ == '__main__':
    main()
