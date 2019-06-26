from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation

from io import BytesIO
from tempfile import NamedTemporaryFile

from ofx2xlsmbr.model.BankStatement import BankStatement
from ofx2xlsmbr.model.CashFlow import CashFlow

from ofx2xlsmbr.writer.IWriterController import IWriterController

import os

class XLSMWriterController(IWriterController):
    def write(self, data: BankStatement, factory, outputFilename=''):
        # create worksheet
        wb = Workbook()
        ws = wb.active

        formula = '"Profissão,Habitação,Transporte,Dependentes,Saúde,Bem-estar,Outros"'

        # create data validation
        dv = DataValidation(type="list", formula1=formula, allow_blank=True)
        ws.add_data_validation(dv)

        writerBS = factory.createWriterBankStatement()
        writerBS.write(data, factory, [ws, dv])

        if (outputFilename == ''):
            with NamedTemporaryFile() as tmp:
                wb.save(tmp.name)
                output = BytesIO(tmp.read())
                os.unlink(tmp.name)
                wb.close()
                return output
        else:
            wb.save(filename = outputFilename + '.xlsm')