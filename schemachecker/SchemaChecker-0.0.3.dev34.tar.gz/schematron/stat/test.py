import os
from time import time
from schematron.stat import StatChecker
from lxml import etree
from pprint import pprint

ROOT = os.path.dirname(os.path.abspath(__file__))


class Input:
    def __init__(self, filename, content):
        self.parser = etree.XMLParser(encoding='utf-8',
                                      recover=True,
                                      remove_comments=True)
        self.filename = filename
        self.xml_obj = etree.fromstring(content, parser=self.parser)


if __name__ == "__main__":
    checker = StatChecker(root=ROOT)
    # checker.gather_compendium()
    checker.setup_compendium()

    # pprint(checker.compendium['0601013'].controls)

    # pprint(checker.compendium['0606010'].sections)

    root_dir = '/home/vasily/PyProjects/FLK/stat/files'
    for root, dirs, files in os.walk(root_dir):
        for file in files[:]:
            with open(os.path.join(root, file), 'rb') as handler:
                data = handler.read()
                st = time()
                input = Input(file, data)
                checker.check_file(input)
                pprint(input.verify_result)
                print(f'{file}, processing time:', time() - st)
