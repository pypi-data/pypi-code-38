# -*- coding: utf-8 -*-
class Tax(object):
    
    def __init__(self, document_code, amount):
        
        self.document_code = document_code
        self.amount = amount

class Iva(Tax):

    def __init__(self, document_code, amount, taxable_base):

        super(Iva, self).__init__(document_code, amount)
        self.taxable_base = taxable_base
            
class Tribute(Tax):
    
    def __init__(self, document_code, amount, taxable_base, aliquot):
        
        super(Tribute, self).__init__(document_code, amount)
        self.taxable_base = taxable_base        
        self.aliquot = aliquot