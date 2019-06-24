import lxml.etree as et
import lxml.objectify as objectify
import json


class TemplateXML:

    def __init__(self, body=""):
        if body == '':
            self._body = body
        else:
            self._body = et.fromstring(body.encode())
        self._xpath = {}

    def __getitem__(self, name):
        xpath = self.get_xpath(name)
        return self.get_value_xpath(xpath)

    def __setitem__(self, key, value):
        xpath = self.get_xpath(key)
        self.set_value_xpath(xpath, value)

    def set_body_from_file(self, path):
        with open(path, 'r') as file:
            self._body = et.fromstring(file.read().encode())

    @staticmethod
    def __format(xml):
        root = et.fromstring(xml.encode())
        return et.tostring(root, method="xml").decode()

    @property
    def body(self):
        return et.tostring(self._body, method="xml").decode()

    @property
    def body_format(self):
        obj = objectify.fromstring(self.body.encode())
        return et.tostring(obj, method="xml").decode()

    def get_value_xpath(self, xpath):
        return self._body.xpath(xpath)[0].text

    def get_attribute_xpath(self, xpath, attr_name):
        return self._body.xpath(xpath)[0].attrib[attr_name]

    def set_value_xpath(self, xpath, value):
        self._body.xpath(xpath)[0].text = str(value)

    def set_xpath_mask(self, path):
        with open(path, 'r') as file:
            self._xpath = json.load(file)

    def get_xpath(self, key):
        return self._xpath[key]

    # def __generate_xpath(self, xml):
    #     if xml != "":
    #         xpath = {}
    #         root = et.fromstring(xml.encode())
    #         tree = et.ElementTree(root)
    #         for e in root.iter():
    #             item = tree.getelementpath(e)
    #             xpath[item.split('}')[-1].split('/')[-1]] = item
    #         return xpath
