# -*- coding: utf-8 -*-
from l10n_ar_api.documents import invoice
from datetime import date, datetime


class FiscalElectronicBondValidator:

    @classmethod
    def validate_invoice(cls, invoice):
        '''
        Valida que los campos de la factura cumplan con los requisitos de la AFIP
        :param invoices: Factura a validar, objeto FiscalElectronicBond
        '''

        cls._validate_document_date(invoice)
        cls._validate_amount(invoice)

    @staticmethod
    def _validate_document_date(invoice):
        assert invoice.document_date, "El documento no tiene fecha"

        invoice_date = datetime.strptime(invoice.document_date, '%Y%m%d').date()

        if abs(date.today() - invoice_date).days > 5:
            raise AttributeError("La fecha del documento debe ser\
                    mayor o menor a 5 dias de la fecha de generacion")

        date_today = date.today().replace(day=1)
        new_invoice_date = invoice_date.replace(day=1)
        if date_today != new_invoice_date:
            raise AttributeError("La fecha del documento no debe exceder el mes de la fecha de\
                                envío del pedido de autorización")

    @staticmethod
    def _validate_amount(invoice):
        if invoice.get_total_items_amount() > invoice.get_total_amount():
            raise AttributeError("La Suma de los items de la factura\
                                 debe ser menor o igual al total de la misma")

class FiscalElectronicBondItem(object):

    def __init__(self, codigo_prod_ncm, description, quantity = None, measurement_unit = None, unit_price = None, bonification = None, iva_id = None):
        self.codigo_prod_ncm = codigo_prod_ncm
        self.description = description
        self.quantity = quantity
        self.measurement_unit = measurement_unit
        self.unit_price = unit_price
        self.bonification = bonification
        self.iva_id = iva_id

    @property
    def total_price(self):
        assert self.quantity, "No existe cantidad para el item"
        assert self.unit_price, "No existe precio para el item"

        return self.quantity * self.unit_price


class FiscalElectronicBond(invoice.Invoice):

    def __init__(self, document_code):
        self.zone_id = 0
        self.reception_amount = None
        self.municipal_reception_amount = None
        self.array_items = []

        # Cliente
        self.customer_name = None
        self.customer_address = None
        self.customer_document_type = None
        self.customer_document_number = None

        # Tributos
        self.pay_off_tax_amount = None
        self.rni_pay_off_tax_amount = None
        self.internal_tax_amount = None
        self.iibb_amount = None

        # Moneda
        self.mon_id = None
        self.mon_cotiz = None

        super(FiscalElectronicBond, self).__init__(document_code)

    # Override

    def get_total_amount(self):

        total_amount = super(FiscalElectronicBond, self).get_total_amount()

        return total_amount

    def get_total_items_amount(self):
        return sum(item.total_price for item in self.array_items)

    def add_item(self, value):
        self.array_items.append(value)

    @property
    def document_date(self):
        return self._document_date

    @document_date.setter
    def document_date(self, value):
        self._document_date = value.strftime('%Y%m%d')
