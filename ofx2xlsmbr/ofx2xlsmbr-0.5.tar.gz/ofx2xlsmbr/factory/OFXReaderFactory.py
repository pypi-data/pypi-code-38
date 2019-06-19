from .ReaderAbstractFactory import ReaderAbstractFactory

from ofx2xlsmbr.reader.IReaderCashFlow import IReaderCashFlow
from ofx2xlsmbr.reader.OFXReaderCashFlow import OFXReaderCashFlow

from ofx2xlsmbr.reader.IReaderBankStatement import IReaderBankStatement
from ofx2xlsmbr.reader.OFXReaderBankStatement import OFXReaderBankStatement

from ofx2xlsmbr.reader.IReaderController import IReaderController
from ofx2xlsmbr.reader.OFXReaderController import OFXReaderController

class OFXReaderFactory(ReaderAbstractFactory):
    def createReaderController(self) -> IReaderController:
        return OFXReaderController()

    def createReaderBankStatement(self) -> IReaderBankStatement:
        return OFXReaderBankStatement()
    
    def createReaderCashFlow(self) -> IReaderCashFlow:
        return OFXReaderCashFlow()