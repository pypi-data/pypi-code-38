# -*- coding: utf-8 -*-
from l10n_ar_api.documents import invoice as inv
from datetime import date, datetime


class ExportationElectronicInvoiceValidator:

    @classmethod
    def validate_invoice(cls, invoice):
        """
        Valida que los campos de la factura cumplan con los requisitos de la AFIP
        :param invoice: Factura a validar, objeto ExportationElectronicInvoice
        """

        cls._validate_document_date(invoice)
        cls._validate_document_code(invoice)
        cls._validate_existent_permission(invoice)
        cls._validate_document_language(invoice)
        cls._validate_exportation_type(invoice)
        cls._validate_amount(invoice)

    @staticmethod
    def _validate_document_date(invoice):

        if invoice.document_date:
            invoice_date = datetime.strptime(invoice.document_date, '%Y%m%d').date()

            if (abs(date.today() - invoice_date).days > 5):
                raise AttributeError("La fecha del documento debe ser\
                    mayor o menor a 5 dias de la fecha de generacion")

            date_today = date.today().replace(day=1)
            new_invoice_date = invoice_date.replace(day=1)
            if date_today != new_invoice_date:
                raise AttributeError("La fecha del documento no debe exceder el mes de la fecha de\
                                            envío del pedido de autorización")

    @staticmethod
    def _validate_amount(invoice):
        items_amount = sum(item.total_price for item in invoice.array_items)
        if items_amount != invoice.get_total_amount():
            raise AttributeError("La Suma de los items de la factura debe ser igual al total de la misma")

    @staticmethod
    def _validate_exportation_type(invoice):
        if invoice.exportation_type not in (1, 2, 4):
            raise AttributeError('Tipo de exportacion invalido')

    @staticmethod
    def _validate_document_language(invoice):
        if invoice.document_language not in (1, 2, 3):
            raise AttributeError("Idioma del comprobante invalido")

    @staticmethod
    def _validate_existent_permission(invoice):
        if invoice.existent_permission not in ('S', 'N', ''):
            raise AttributeError("Permiso de embarque existente invalido")

    @staticmethod
    def _validate_document_code(invoice):
        if invoice.document_code not in (19, 20, 21):
            raise AttributeError("Codigo de tipo de comprobante invalido")


class ExportationElectronicInvoiceItem(object):

    def __init__(self, description):
        self.description = description
        self.quantity = None
        self.measurement_unit = None
        self.unit_price = None
        self.bonification = None

    @property
    def total_price(self):
        assert self.quantity, "No existe cantidad para el item"
        assert self.unit_price, "No existe precio para el item"

        return self.quantity * self.unit_price


class ExportationElectronicInvoice(inv.Invoice):

    def __init__(self, document_code):
        self.exportation_type = None
        self.existent_permission = None
        self.destiny_country = None
        self.destiny_country_cuit = None
        self.customer_name = None
        self.customer_street = None
        self.document_language = None
        self.incoterms = None
        self.array_items = []

        # Moneda
        self.mon_id = None
        self.mon_cotiz = None

        super(ExportationElectronicInvoice, self).__init__(document_code)

    # Override
    def get_total_amount(self):
        return sum(item.total_price for item in self.array_items)

    def add_item(self, value):
        self.array_items.append(value)

    @property
    def document_date(self):
        return self._document_date

    @document_date.setter
    def document_date(self, value):
        self._document_date = value.strftime('%Y%m%d')
