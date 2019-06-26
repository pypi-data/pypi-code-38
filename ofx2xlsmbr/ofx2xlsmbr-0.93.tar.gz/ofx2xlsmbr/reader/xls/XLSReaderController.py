from ..IReaderController import IReaderController

from ofx2xlsmbr.model.BankStatement import BankStatement
from ofx2xlsmbr.model.CashFlow import CashFlow, CashFlowType

from typing import List
from openpyxl import load_workbook

import logging

logger = logging.getLogger(__name__)

class XLSReaderController(IReaderController):
    def read(self, factory, files=[]) -> List[BankStatement]:
        logger.debug(files)

        bankStmts = []
        bsReader = factory.createReaderBankStatement()

        if (files):
            for file in files:
                wb = load_workbook(file)
                ws = wb.active
                bs = bsReader.read(factory, ws)
                bankStmts.append(bs)
            return bankStmts

        bsNull = BankStatement([], [])
        return [bsNull]