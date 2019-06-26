from ..IReaderBankStatement import IReaderBankStatement
from ofx2xlsmbr.model.BankStatement import BankStatement

import logging

logger = logging.getLogger(__name__)


class XLSReaderBankStatement(IReaderBankStatement):
    def read(self, factory, ofx) -> BankStatement:
        bs = BankStatement()
        bs.inflows = []
        bs.outflows = []

        ws = ofx
        
        csReader = factory.createReaderCashFlow()
        headerRow = True
        for row in ws.values:
            # Pulando o cabecalho
            if (headerRow):
                headerRow = False
                continue
            
            cs = csReader.read(factory, row)
            if (cs.value >= 0.0):
                bs.inflows.append(cs)
            else:
                bs.outflows.append(cs)

        return bs