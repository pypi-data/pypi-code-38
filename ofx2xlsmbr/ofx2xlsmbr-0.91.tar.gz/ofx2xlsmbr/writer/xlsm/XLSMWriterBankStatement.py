from ofx2xlsmbr.writer.IWriterBankStatement import IWriterBankStatement
from ofx2xlsmbr.model.BankStatement import BankStatement

class XLSMWriterBankStatement(IWriterBankStatement):
    def write(self, bankStatement: BankStatement, factory, xlsmOutput):
        writerCS = factory.createWriterCashFlow()

        initialRow = 2
        xlsmOutput.append(initialRow)

        writerCS.writeHeader(xlsmOutput)
        for cs in bankStatement.inflows:
            writerCS.write(cs, factory, xlsmOutput)
            xlsmOutput[2] += 1
        for cs in bankStatement.outflows:
            writerCS.write(cs, factory, xlsmOutput)
            xlsmOutput[2] += 1