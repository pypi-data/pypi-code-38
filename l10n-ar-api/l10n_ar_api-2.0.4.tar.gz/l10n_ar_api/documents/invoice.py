# -*- coding: utf-8 -*-
class Invoice(object):
    
    def __init__(self, document_code):
        
        self.document_code = document_code
        self._document_date = None

        # Importes
        self.taxed_amount = None
        self.untaxed_amount = None
        self.exempt_amount = None

    def get_total_amount(self):
        
        try:
            total_amount = self.taxed_amount + self.untaxed_amount + self.exempt_amount
        
        except TypeError:
            raise AttributeError("Falta especificar algun importe en la factura")
        
        return total_amount
