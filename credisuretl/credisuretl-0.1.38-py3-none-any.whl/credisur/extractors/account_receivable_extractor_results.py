

class AccountReceivableExtractorResults:

    def __init__(self,
                 customers, bills,
                 calendar_ops, first_day_of_current_month, last_date_of_month,
                 collections, collections_for_customers,
                 list_of_advance_payments, customers_without_payments_due, customers_in_last_payment):

        self.accounts_to_collect =  {
            "C": [],
            "D": [],
            "I": []
        }

        self.customers = customers
        self.bills = bills

        self.calendar_ops = calendar_ops
        self.last_date_of_month = last_date_of_month
        self.first_day_of_current_month = first_day_of_current_month

        self.errors = []

        self.collections = collections
        self.collections_for_customers = collections_for_customers
        self.list_of_advance_payments = list_of_advance_payments


        self.customers_without_payments_due = customers_without_payments_due
        self.customers_in_last_payment = customers_in_last_payment


    def get_errors(self):
        return self.errors

    def get_calendar_ops(self):
        return self.calendar_ops

    def get_first_day_of_current_month(self):
        return self.first_day_of_current_month

    def get_last_date_of_month(self):
        return self.last_date_of_month

    def get_accounts_to_collect(self):
        return self.accounts_to_collect

    def get_customers(self):
        return self.customers

    def get_bills(self):
        return self.bills

    def get_collections(self):
        return self.collections

    def get_collections_for_customers(self):
        return self.collections_for_customers

    def get_list_of_advance_payments(self):
        return self.list_of_advance_payments

    def get_customers_without_payments_due(self):
        return self.customers_without_payments_due

    def get_customers_in_last_payment(self):
        return self.customers_in_last_payment

    def append_account_to_collect(self, account_receivable):
        account_to_collect = account_receivable.to_dict()

        if not account_to_collect['city'] or not account_to_collect['customer']:
            print("FALTA CIUDAD O CLIENTE:", account_to_collect['city'], account_to_collect['customer'])

        self.accounts_to_collect[account_to_collect['account']].append(account_to_collect)