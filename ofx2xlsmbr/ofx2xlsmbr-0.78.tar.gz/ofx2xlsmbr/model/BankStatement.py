from typing import List
from .CashFlow import CashFlow

class BankStatement:
    def __init__(self, 
                inflows: List[CashFlow] = [], 
                outflows: List[CashFlow] = []):
        self.inflows = inflows
        self.outflows = outflows

    def __repr__(self):
        bs = 'BankStatement:'
            
        bs += '\n\n\t = Inflows: = \n\t'
        for cs in self.inflows:
            bs += '\n' + str(cs)
        bs += '\n\n\t = Outflows: =\n\t'
        for cs in self.outflows:
            bs += '\n' + str(cs)
        return bs

    def merge(self, other):
        self.inflows.append(other.inflows)
        self.outflows.append(other.outflows)