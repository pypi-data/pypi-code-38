

class BillExtractorResults:

    def __init__(self):
        self.bills = {}
        self.errors = []
        pass

    def append_bill(self,bill):
        self.bills[bill.get_document_type_and_number()] = bill.get_amount()

    def get_errors(self):
        return self.errors

    def get_bills(self):
        return self.bills