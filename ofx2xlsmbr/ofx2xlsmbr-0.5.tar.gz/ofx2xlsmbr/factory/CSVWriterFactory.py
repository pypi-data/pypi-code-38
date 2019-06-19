from .WriterAbstractFactory import WriterAbstractFactory

from ofx2xlsmbr.writer.IWriterCashFlow import IWriterCashFlow
from ofx2xlsmbr.writer.IWriterBankStatement import IWriterBankStatement
from ofx2xlsmbr.writer.IWriterController import IWriterController

from ofx2xlsmbr.writer.csv.CSVWriterCashFlow import CSVWriterCashFlow
from ofx2xlsmbr.writer.csv.CSVWriteBankStatement import CSVWriterBankStatement
from ofx2xlsmbr.writer.csv.CSVWriterController import CSVWriterController

class CSVWriterFactory(WriterAbstractFactory):
    def createWriterController(self) -> IWriterController:
        return CSVWriterController()

    def createWriterBankStatement(self) -> IWriterBankStatement:
        return CSVWriterBankStatement()
    
    def createWriterCashFlow(self) -> IWriterCashFlow:
        return CSVWriterCashFlow()