# -*- coding: utf-8 -*-
from datetime import date, datetime
from l10n_ar_api.documents import invoice as inv


class ElectronicInvoiceValidator(object):
        
    def validate_invoice(self, invoice):
        """
        Valida que los campos de la factura cumplan con los requisitos de la AFIP
        :param invoice: Factura a validar, objeto ElectronicInvoice
        """
        
        self._validate_document_date(invoice)
        self._validate_concept(invoice)
        self._validate_mon_cotiz(invoice)

    def _validate_document_date(self, invoice):
        assert invoice.concept, "El documento no tiene concepto"
        assert invoice.document_date, "El documento no tiene fecha"

        invoice_date = datetime.strptime(invoice.document_date, '%Y%m%d').date()

        if (invoice.concept != 1 and abs(date.today() - invoice_date).days > 10 or
            invoice.concept == 1 and abs(date.today() - invoice_date).days > 5):

                raise AttributeError("La fecha del documento debe ser\
                    mayor o menor a 5 dias de la fecha de generacion para concepto\
                    igual a 1, o a 10 dias para concepto 2 o 3")
    
    def _validate_concept(self, invoice):
        if invoice.concept not in (1,2,3):
            raise AttributeError('Concepto invalido')

    def _validate_mon_cotiz(self, invoice):
        if invoice.mon_id == 'PES' and invoice.mon_cotiz != 1:
            raise AttributeError("Para Pesos, la cotizacion debe ser 1")
        
    @property
    def invoices(self):
        return self._invoices


class ElectronicInvoice(inv.Invoice):
    
    def __init__(self, document_code):
        
        self.concept = None
        
        # Fechas
        self._service_from = None
        self._service_to = None
        self._payment_due_date = None        
        
        # Tributos
        self.array_iva = []
        self.array_tributes = []
        
        # Cliente
        self.customer_document_type = None
        self.customer_document_number = None

        # Moneda
        self.mon_id = None
        self.mon_cotiz = None
        
        super(ElectronicInvoice, self).__init__(document_code)
        
    def get_total_iva(self):        
        amount = sum(iva.amount for iva in self.array_iva)

        return amount
        
    def get_total_tributes(self):
        amount = sum(tribute.amount for tribute in self.array_tributes)
        
        return amount
    
    def get_total_amount(self):
        total_amount = super(ElectronicInvoice, self).get_total_amount()
        try:
            total_amount += self.get_total_iva() + self.get_total_tributes()
        
        except TypeError:
            raise AttributeError("Falta especificar algun importe en la factura")
        
        return total_amount

    def add_iva(self, iva):
        self.array_iva.append(iva)
    
    def add_tribute(self, tribute):
        self.array_tributes.append(tribute)
    
    def _parse_date(self, value):
        return value.strftime('%Y%m%d')
        
    @property
    def document_date(self):
        return self._document_date
    
    @document_date.setter
    def document_date(self, value):    
        self._document_date = self._parse_date(value)
    
    @property
    def service_from(self):
        return self._service_from
    
    @service_from.setter
    def service_from(self, value):    
        self._service_from = self._parse_date(value)

    @property
    def service_to(self):
        return self._service_to
    
    @service_to.setter
    def service_to(self, value):    
        self._service_to = self._parse_date(value)
        
    @property
    def payment_due_date(self):
        return self._payment_due_date
    
    @payment_due_date.setter
    def payment_due_date(self, value):    
        self._payment_due_date = self._parse_date(value)     
