from .ReaderAbstractFactory import ReaderAbstractFactory

from ofx2xlsmbr.reader.IReaderCashFlow import IReaderCashFlow
from ofx2xlsmbr.reader.IReaderBankStatement import IReaderBankStatement
from ofx2xlsmbr.reader.IReaderController import IReaderController

from ofx2xlsmbr.reader.xls.XLSReaderController import XLSReaderController
from ofx2xlsmbr.reader.xls.XLSReaderBankStatement import XLSReaderBankStatement
from ofx2xlsmbr.reader.xls.XLSReaderCashFlow import XLSReaderCashFlow

class XLSReaderFactory(ReaderAbstractFactory):
    def createReaderController(self) -> IReaderController:
        return XLSReaderController()

    def createReaderBankStatement(self) -> IReaderBankStatement:
        return XLSReaderBankStatement()
    
    def createReaderCashFlow(self) -> IReaderCashFlow:
        return XLSReaderCashFlow()