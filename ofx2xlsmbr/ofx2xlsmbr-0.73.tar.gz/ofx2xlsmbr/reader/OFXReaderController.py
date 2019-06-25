from .IReaderController import IReaderController

from ofx2xlsmbr.model.BankStatement import BankStatement
from ofx2xlsmbr.model.CashFlow import CashFlow, CashFlowType

from ofx2xlsmbr.factory.XMLReaderFactory import XMLReaderFactory

import datetime
from pytz import timezone
import pytz

import logging

logger = logging.getLogger(__name__)

import ofxtools
from ofxtools import OFXTree

class OFXReaderController(IReaderController):
    def read(self, factory, inputFilename='', file=None) -> BankStatement:
        try:
            tree = OFXTree()
            if (file is not None):
                tree.parse(file)
            else:
                tree.parse(inputFilename)

            # erros de compatibilidade
            self.treatBradescoException(tree)
            
            convertedTree = tree.convert()

            bsReader = factory.createReaderBankStatement()
            bs = bsReader.read(factory, convertedTree)

            return bs
        except IndexError:
            # ofx nao consegue ler versao 220. Ler como XML
            xmlFactory = XMLReaderFactory()
            xmlReader = xmlFactory.createReaderController()
            return xmlReader.read(xmlFactory, inputFilename, file=file)

    # Este tratamento de erro tem que ser melhor descrito
    def treatBradescoException(self, tree):
        root = tree.getroot()
        dtServer = root.findall("SIGNONMSGSRSV1")[0].findall("SONRS")[0].findall("DTSERVER")[0]
        try:
            if (int(dtServer.text) == 0):
                unknownDateInThePast = datetime.datetime(1985, 10, 21, tzinfo=timezone('Brazil/East'))
                dtServer.text = unknownDateInThePast
        except ValueError:
            pass
            # se dtServer for um datetime, ele da erro na conversao para int
            # logger.info('Correcting DTServer')