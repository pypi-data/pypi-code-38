
NUEVO = "nuevo"

class Bill:

    def __init__(self, document_type, document, raw_code, amount, errors):
        self.errors = False
        self.skip = False

        if document_type == "Factura":
            document_type = "Factura de Venta"

        document_type_and_number = "%s N° %s" % (document_type, document)

        self.document_type = document_type
        self.document = document
        self.raw_code = raw_code
        self.amount = amount
        self.document_type_and_number = document_type_and_number

        if not raw_code:
            self.append_error(errors, "Factura sin descripción. Documento: %s" % document)
            return

        if len(raw_code.split("-")) < 4:
            self.append_error(errors, "Factura con código incorrecto (%s). Documento: %s" % (raw_code, document))
            return

        _, _, self.sales_order, self.payment_code, *_ = raw_code.split("-")

        if "de" in self.payment_code:
            self.skip = True
            return
        '''
        if self.sales_order == "NO":
            self.skip = True
            return
        '''

        if not self.sales_order:
            error = "Factura sin orden de compra. Documento: %s" % document
            self.append_error(errors, error)
            return

        self.version = NUEVO

        if self.sales_order != "NO" and len(self.sales_order) != 5:
            error = "Factura con orden de compra errónea (%s). Documento: %s" % (self.sales_order, self.document)            
            print(error)
            self.append_error(errors, error)
            return

    def append_error(self, errors, error):
        self.errors = True
        errors.append(error)

    def is_duplicated_bill(self, bills, errors):
        if self.document_type_and_number in bills and self.version == NUEVO:
            errors.append("Orden de compra repetida. Documento: %s. Orden de compra: %s" % (self.document, self.sales_order))
            return True
        return False

    def should_skip(self):
        return self.errors or self.skip

    def get_document_type_and_number(self):
        return self.document_type_and_number

    def get_amount(self):
        return self.amount
