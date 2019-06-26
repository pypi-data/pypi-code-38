from .IReaderCashFlow import IReaderCashFlow
from ofx2xlsmbr.model.CashFlow import CashFlow, CashFlowType

class OFXReaderCashFlow(IReaderCashFlow):
    def read(self, factory, ofx) -> CashFlow:
        cs = CashFlow()
        
        cs.name = ofx.memo
        cs.value = ofx.trnamt
        cs.date = ofx.dtposted

        if (ofx.trntype == 'CREDIT'):
            cs.flowType = CashFlowType.CREDIT

        return cs
