from .ReaderAbstractFactory import ReaderAbstractFactory

from ofx2xlsmbr.reader.IReaderCashFlow import IReaderCashFlow
from ofx2xlsmbr.reader.IReaderBankStatement import IReaderBankStatement
from ofx2xlsmbr.reader.IReaderController import IReaderController

from ofx2xlsmbr.reader.xml.XMLReaderCashFlow import XMLReaderCashFlow
from ofx2xlsmbr.reader.xml.XMLReaderBankStatement import XMLReaderBankStatement
from ofx2xlsmbr.reader.xml.XMLReaderController import XMLReaderController

class XMLReaderFactory(ReaderAbstractFactory):
    def createReaderController(self) -> IReaderController:
        return XMLReaderController()

    def createReaderBankStatement(self) -> IReaderBankStatement:
        return XMLReaderBankStatement()
    
    def createReaderCashFlow(self) -> IReaderCashFlow:
        return XMLReaderCashFlow()