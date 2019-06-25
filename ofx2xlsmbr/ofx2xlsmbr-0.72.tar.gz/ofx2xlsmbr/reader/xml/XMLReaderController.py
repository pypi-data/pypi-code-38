from ofx2xlsmbr.reader.IReaderController import IReaderController

from ofx2xlsmbr.model.BankStatement import BankStatement

import xml.etree.ElementTree as ET
from lxml import etree

import logging

logger = logging.getLogger(__name__)

class XMLReaderController(IReaderController):
    def read(self, factory, inputFilename='', file=None) -> BankStatement:
        data = ''
        tree = None

        if file is not None:
            data = self.readFile(file)
            parser = etree.XMLParser(recover=True)
            tree = etree.fromstring(data, parser=parser)
        else:
            with open(inputFilename, 'r', encoding='iso-8859-1') as inputFile:
                data = self.readFile(inputFile)
                tree = ET.fromstring(data)
        
        bsReader = factory.createReaderBankStatement()
        bs = bsReader.read(factory, tree)
        return bs

    def readFile(self, file):
        data = str(file.read())
        data = data[data.find('<OFX>'):]
        return data