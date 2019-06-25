from enum import Enum
from datetime import datetime

class CashFlowType(Enum):
    DEBIT = 1
    CREDIT = 2

class CashFlow:
    def __init__(self,
                name = 'N/A',
                flowType: CashFlowType = CashFlowType.DEBIT,
                value: float = 0.0,
                date: datetime = 'N/A'):
        self.name = name
        self.flowType = flowType
        self.value = value
        self.date = date

    def __repr__(self):
        return 'CashFlow: \
                \n\tName: {} \
                \n\tType: {} \
                \n\tValue: {} \
                \n\tDate: {}'.format(self.name,
                                    self.flowType.name, 
                                    self.value,
                                    self.date)