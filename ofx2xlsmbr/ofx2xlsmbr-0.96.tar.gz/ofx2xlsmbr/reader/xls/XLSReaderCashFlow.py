from ..IReaderCashFlow import IReaderCashFlow
from ofx2xlsmbr.model.CashFlow import CashFlow, CashFlowType

import logging

logger = logging.getLogger(__name__)

class XLSReaderCashFlow(IReaderCashFlow):
    def read(self, factory, ofx) -> CashFlow:
        cs = CashFlow()

        row = ofx
        
        cellValues = []
        for cellValue in row:
            cellValues.append(cellValue)

        cs.date = cellValues[0]
        cs.name = cellValues[1]
        cs.value = cellValues[2]

        return cs
