from credisur.models import Bill


def bill_row_extractor(results, unpacker):

    errors = results.get_errors()
    bills = results.get_bills()

    document_type = unpacker.get_value_at(3)
    document = unpacker.get_value_at(4)
    raw_code = unpacker.get_value_at(11)
    amount = unpacker.get_value_at(18)

    bill = Bill(document_type, document, raw_code, amount, errors)

    if bill.should_skip():
        return

    if bill.is_duplicated_bill(bills, errors):
        return

    results.append_bill(bill)
