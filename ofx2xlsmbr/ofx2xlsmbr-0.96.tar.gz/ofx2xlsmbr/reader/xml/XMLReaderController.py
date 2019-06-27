from ofx2xlsmbr.reader.IReaderController import IReaderController

from ofx2xlsmbr.model.BankStatement import BankStatement

from typing import List
import xml.etree.ElementTree as ET
from lxml import etree

import logging

logger = logging.getLogger(__name__)

# XML Reader Controller esta acoplado demais ao OFX Reader Controller, por isso so recebe uma lista
# com um objeto
class XMLReaderController(IReaderController):
    def read(self, factory, files=[]) -> List[BankStatement]:
        data = ''
        tree = None

        if (files):
            file = files[0]
            data = self.readFile(file)
            parser = etree.XMLParser(recover=True)
            tree = etree.fromstring(data, parser=parser)
        
        bsReader = factory.createReaderBankStatement()
        bs = bsReader.read(factory, tree)
        return bs

    def readFile(self, file):
        data = str(file.read())
        data = data[data.find('<OFX>'):]
        return data