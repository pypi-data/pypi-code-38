from ofx2xlsmbr.reader.IReaderCashFlow import IReaderCashFlow
from ofx2xlsmbr.model.CashFlow import CashFlow, CashFlowType

from datetime import datetime

class XMLReaderCashFlow(IReaderCashFlow):
    def read(self, factory, ofx) -> CashFlow:
        cs = CashFlow()
        
        cs.name = ofx.find('MEMO').text
        cs.value = float(ofx.find('TRNAMT').text)
        dtposted = ofx.find('DTPOSTED').text

        # YYYYMMDDHHMMSS
        cs.date = datetime.strptime(dtposted[:dtposted.find('[')], '%Y%m%d%H%M%S')
        

        if (ofx.find('TRNTYPE') == 'CREDIT'):
            cs.flowType = CashFlowType.CREDIT
        
        return cs
