from functools import reduce

NUEVO = "nuevo"
HISTORICO = "histórico"

class AccountReceivable:

    def __init__(self, document_date, due_date, document,
                 customer, raw_code, customer_data, line_amount,
                 line_balance, calendar_operations):
        # line_amount = float(row_unpacker.get_value_at(8))
        # line_balance = row_unpacker.get_value_at(8)


        self.overdue_balance = 0
        self.past_due_debt = ""
        self.collections_for_order = []
        self.collections_for_customer = []
        self.last_collection_date = "Sin cobranza previa"
        self.current_payment_number = 1

        # inject calendar operations
        self.calendar_operations = calendar_operations

        self.document_date = document_date
        self.due_date = due_date
        self.document = document
        self.customer = customer
        self.raw_code = raw_code
        self.line_amount = line_amount
        self.line_balance = line_balance

        self.city = customer_data['city']
        self.phone = customer_data['phone']
        self.address = customer_data['address']

        self._process_version()
        self._process_collection_codes()


    def _process_version(self):
        self.version = HISTORICO  if ("de" in self.raw_code.split("-")[3]) else NUEVO

    def _process_collection_codes(self):
        self.list_of_codes = self.raw_code.split("-")
        self.collection_account, self.collection_person, self.sales_order, *_ = self.list_of_codes

    def configure_previous_collections(self, collections, collections_for_customers):
        if not self.sales_order:
            return

        if self.sales_order in collections:
            self.collections_for_order = collections[self.sales_order]

        if self.customer in collections_for_customers:
            self.collections_for_customer = collections_for_customers[self.customer]


    def compute_last_collection_date(self):
        if not self.sales_order:
            return

        if len(self.collections_for_customer) > 0:
            self.last_collection_date = sorted(
                self.collections_for_customer,
                key=lambda x: x['date'],
                reverse=True
            )[0]['date'].strftime("%d/%m/%Y")
            return


    def compute_due_payment(self,bills, first_day_of_current_month, last_date_of_month):
        {
            HISTORICO: self._compute_historic_due_payment,
            NUEVO: self._compute_actual_due_payment
        }[self.version](bills, first_day_of_current_month, last_date_of_month)

    def _compute_historic_due_payment(self, bills, first_day_of_current_month, last_date_of_month):
        self.debt_balance = ""
        self.advance_payment = ""

        self.current_payment_number, self.plan = list(map(lambda x: int(x), self.list_of_codes[3].split(" de ")))
        self.payment_amount = self.line_amount
        self.total_purchase_value = self.payment_amount * int(self.plan)

        self.current_payment_description = str(self.current_payment_number)

    def _compute_actual_due_payment(self, bills, first_day_of_current_month, last_date_of_month):
        self.plan = int(self.list_of_codes[3])

        self.payment_amount = float(self.list_of_codes[4])
        self.debt_balance = self.line_balance

        self.total_purchase_value = bills[self.document]
        self.paid_amount = self.total_purchase_value - self.debt_balance
        self.advance_payment = self.total_purchase_value - (self.plan * self.payment_amount)

        past_payments = 0

        if self.paid_amount > self.advance_payment:
            past_payments = int((self.paid_amount - self.advance_payment) // self.payment_amount)

        self.due_dates = self.calendar_operations.list_of_due_date(self.due_date, self.plan)

        self.due_payments = next((
            self.plan - i for i, v in enumerate(
            reversed(self.due_dates)) if v < first_day_of_current_month),
                            0)
        self.due_payments_with_current = next(
            (self.plan - i for i, v in enumerate(reversed(self.due_dates)) if v <= last_date_of_month), 0)

        self.current_payment_number_by_date = self.current_payment_number = next(
            (self.plan - i for i, v in enumerate(reversed(self.due_dates)) if v <= last_date_of_month), 0)

        self.past_due_debt = self.advance_payment + (self.due_payments * self.payment_amount)

        self.overdue_balance = self.past_due_debt - self.paid_amount

        self.overdue_advance_payment_amount = (self.advance_payment - self.paid_amount) if self.advance_payment - self.paid_amount > 0 else 0

        self.missing_payments = self.due_payments_with_current - past_payments

        if not self.missing_payments > 0:
            return

        self.missing_payment_numbers = list(self.current_payment_number_by_date - x for x in range(self.missing_payments))

        if(len(self.missing_payment_numbers) == 0):
            print(self.current_payment_number_by_date, self.missing_payments)

        self.partial_debt_in_payment = self.overdue_balance % self.payment_amount

        self.partial_debt_in_payment_without_advance = self.partial_debt_in_payment - self.overdue_advance_payment_amount

        if self.partial_debt_in_payment_without_advance > 0:
            first_payment_description = "+$%s de cuota %s" % (
                int(self.partial_debt_in_payment_without_advance),
                self.missing_payment_numbers[-1])
            self.missing_payment_numbers[-1] = first_payment_description

        if self.overdue_advance_payment_amount > 0:
            advance_payment_description = "+$%s de anticipo" % (
                int(self.overdue_advance_payment_amount)
            )
            self.missing_payment_numbers.append(advance_payment_description)

        self.current_payment_description = ", ".join(str(i) for i in self.missing_payment_numbers)


    # continue if is not true
    def is_historic_and_due_for(self, last_date_of_month):
        if self.version == NUEVO: return True
        return self.due_date <= last_date_of_month

    def validate_payment_plan(self, errors):
        if (self.version == HISTORICO): return True

        if len(self.list_of_codes) < 5:
            error = "Cuenta a cobrar sin valor de cuota. Documento: %s - Descripción: %s" % (self.document, self.raw_code)
            errors.append(error)
            return False

        return True

    # should continue
    def validate_low_advance_payment(self, tolerance, errors):
        if (self.version == HISTORICO): return True

        if tolerance >= self.advance_payment > 0:
            total_plan_amount = str(int(self.plan * self.payment_amount))
            error = "El valor del anticipo es muy bajo ($ %s). Comprobar que no se trate de un error de carga. " \
                    "%s. Cliente: %s. Orden de Compra: %s. Valor total de Factura: %s. " \
                    "Valor total según plan: %s" % (
                        self.advance_payment, self.document,
                        self.customer, self.sales_order,
                        self.total_purchase_value, total_plan_amount)
            errors.append(error)
            return False

        return True

    # should continue
    def validate_advance_payment(self,errors):
        if (self.version == HISTORICO): return True

        if self.advance_payment < 0:
            error = "El monto de venta es menor al plan de pagos. " \
                    "Documento: %s - Valor: %s. Plan: %s - Cuota: %s. Diferencia: %s" % (
                       self.document, self.total_purchase_value,
                       self.plan, self.payment_amount,
                       self.advance_payment)
            errors.append(error)
            return False

        return True

    def add_to_list_if_advance_payments(self, list_of_advance_payments):
        if self.advance_payment and self.advance_payment > 0:
            list_of_advance_payments.append({
                "document": self.document,
                "customer": self.customer,
                "total_purchase_value": self.total_purchase_value,
                "advance_payment": self.advance_payment
            })

    def validate_total_sale_amount_and_plan_value(self,errors):
        if (self.version == HISTORICO): return True

        if self.total_purchase_value < (self.plan * self.payment_amount):
            error = "El monto de venta es menor al plan de pagos. " \
                    "Documento: %s - Valor: %s. Plan: %s - Cuota: %s. Diferencia: %s" % (
                        self.document, self.total_purchase_value,
                        self.plan, self.payment_amount,
                        self.advance_payment)
            errors.append(error)
            return False

        return True

    def has_due_payments(self, customers_without_payments_due):
        if (self.version == HISTORICO): return True

        if not self.missing_payments > 0:

            customer_without_payment_due = {
                "city": self.city,
                "customer": self.customer,
                "sales_order": self.sales_order,
                "address": self.address or 'Sin dirección',
                "past_due_debt": self.past_due_debt,
                "paid_amount": self.paid_amount,
                "due_date": self.due_date.strftime("%d/%m/%Y"),
                "raw_code": self.raw_code
            }

            customers_without_payments_due.append(customer_without_payment_due)
            return False

        return True

    def validate_person(self, errors):
        if not self.collection_account in ["I", "C", "D"]:
            error = "Error en el código de cobranza: el primer código debe ser 'I', 'C' o 'D'. Documento: %s - Descripción: %s" % (
            self.document, self.raw_code)
            errors.append(error)
            return False

        if self.collection_account == "C":
            if not self.collection_person in ['E']:
                error = "Error en el código de cobranza para crédito: el segundo código debe ser 'E'. Documento: %s - Descripción: %s" % (
                    self.document, self.raw_code)
                errors.append(error)
                return False

        if not self.collection_account == "D":
            return True

        if not self.collection_person in ['H','F']:
            error = "Error en el código de cobranza para débito: el segundo código debe ser 'F' o 'H'. Documento: %s - Descripción: %s" % (
            self.document, self.raw_code)
            errors.append(error)

            return False

        return True

    def get_amount_to_collect(self):
        result = float(self.payment_amount) + float(self.overdue_balance)

        if self.version == HISTORICO: return result

        if self.due_payments_with_current == self.due_payments:
            return result - float(self.payment_amount)

        return result

    def add_to_list_if_in_last_payment(self, customers_in_last_payment, first_day_of_current_month):
        if self.version == HISTORICO:
            return

        if (
                self.plan == self.current_payment_number and
                len(self.missing_payment_numbers) == 1 and
                self.current_payment_number == self.missing_payment_numbers[0]
            ):

            # reduce((lambda x, y: x * y), self.collections_for_customer)

            customer_details = {
                "city": self.city,
                "customer": self.customer,
                "address": self.address or 'Sin dirección',
                "lastcollection": self.last_collection_date,
                "reason": "Última cuota"
            }

            customers_in_last_payment.append(customer_details)

    def get_full_description(self):
        codes = self.raw_code.split("-")

        if self.version == HISTORICO:
            if len(codes) > 4:
                return codes[4]

            return ""

        if len(codes) > 5:
            return codes[5]

        return ""



    def to_dict(self):
        account_to_collect = {}

        document_date_str = self.document_date.strftime("%d/%m/%Y")
        due_date_str = self.due_date.strftime("%d/%m/%Y")

        amount_to_collect = self.get_amount_to_collect()

        account_to_collect['version'] = self.version

        account_to_collect['document'] = self.document
        account_to_collect['date_of_purchase'] = document_date_str

        account_to_collect['due_date_datetime'] = self.due_date
        account_to_collect['due_date'] = due_date_str

        account_to_collect['customer'] = self.customer

        account_to_collect['city'] = self.city
        account_to_collect['address'] = self.address
        account_to_collect['phone'] = self.phone

        account_to_collect['account'] = self.collection_account
        account_to_collect['person'] = self.collection_person

        account_to_collect['order'] = self.sales_order

        account_to_collect['last_collection'] = self.last_collection_date
        account_to_collect['total_purchase_value'] = self.total_purchase_value
        account_to_collect['plan'] = self.plan
        account_to_collect['advance_payment'] = self.advance_payment
        account_to_collect['debt_balance'] = self.debt_balance

        account_to_collect['current_payment'] = self.current_payment_description
        account_to_collect['payment'] = self.payment_amount
        account_to_collect['past_due_debt'] = self.past_due_debt
        account_to_collect['overdue_balance'] = self.overdue_balance

        account_to_collect['amount_to_collect'] = amount_to_collect

        account_to_collect['full_description'] = self.get_full_description()

        return account_to_collect