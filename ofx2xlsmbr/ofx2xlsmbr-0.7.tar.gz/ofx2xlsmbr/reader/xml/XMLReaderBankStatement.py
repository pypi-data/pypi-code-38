from ofx2xlsmbr.reader.IReaderBankStatement import IReaderBankStatement
from ofx2xlsmbr.model.BankStatement import BankStatement

import xml.etree.ElementTree as ET

class XMLReaderBankStatement(IReaderBankStatement):
    def read(self, factory, ofx) -> BankStatement:
        bs = BankStatement()

        tranList = ofx.find('BANKMSGSRSV1').find('STMTTRNRS').find('STMTRS').find('BANKTRANLIST')
        txs = tranList.findall('STMTTRN')

        csReader = factory.createReaderCashFlow()
        for tx in txs:
            cs = csReader.read(factory, tx)
            if (cs.value >= 0.0):
                bs.inflows.append(cs)
            else:
                bs.outflows.append(cs)
        
        return bs