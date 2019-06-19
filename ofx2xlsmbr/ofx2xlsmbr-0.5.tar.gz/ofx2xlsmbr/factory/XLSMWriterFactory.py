from .WriterAbstractFactory import WriterAbstractFactory

from ofx2xlsmbr.writer.IWriterCashFlow import IWriterCashFlow
from ofx2xlsmbr.writer.IWriterBankStatement import IWriterBankStatement
from ofx2xlsmbr.writer.IWriterController import IWriterController

from ofx2xlsmbr.writer.xlsm.XLSMWriterCashFlow import XLSMWriterCashFlow
from ofx2xlsmbr.writer.xlsm.XLSMWriterBankStatement import XLSMWriterBankStatement
from ofx2xlsmbr.writer.xlsm.XLSMWriterController import XLSMWriterController

class XLSMWriterFactory(WriterAbstractFactory):
    def createWriterController(self) -> IWriterController:
        return XLSMWriterController()

    def createWriterBankStatement(self) -> IWriterBankStatement:
        return XLSMWriterBankStatement()
    
    def createWriterCashFlow(self) -> IWriterCashFlow:
        return XLSMWriterCashFlow()