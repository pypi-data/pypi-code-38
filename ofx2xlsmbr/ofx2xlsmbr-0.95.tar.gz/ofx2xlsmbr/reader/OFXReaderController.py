from .IReaderController import IReaderController

from ofx2xlsmbr.model.BankStatement import BankStatement
from ofx2xlsmbr.model.CashFlow import CashFlow, CashFlowType

from ofx2xlsmbr.factory.XMLReaderFactory import XMLReaderFactory

from typing import List
import datetime
from pytz import timezone
import pytz

import logging

logger = logging.getLogger(__name__)

import ofxtools
from ofxtools import OFXTree

class OFXReaderController(IReaderController):
    def read(self, factory, files=[]) -> List[BankStatement]:
        logger.debug(files)

        bankStmts = []
        bsReader = factory.createReaderBankStatement()

        if (files):
            for file in files:
                try:
                    tree = OFXTree()
                    tree.parse(file)
                    self.treatBradescoException(tree)
                    convertedTree = tree.convert()
                    bs = bsReader.read(factory, convertedTree)
                    bankStmts.append(bs)
                except IndexError:
                    # ofx nao consegue ler versao 220. Ler como XML
                    file.seek(0)
                    xmlFactory = XMLReaderFactory()
                    xmlReader = xmlFactory.createReaderController()
                    bs = xmlReader.read(xmlFactory, files=[file])
                    bankStmts.append(bs)
            return bankStmts

        bsNull = BankStatement([], [])
        return [bsNull]

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