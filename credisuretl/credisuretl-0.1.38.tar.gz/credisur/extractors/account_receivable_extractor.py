from credisur.models import AccountReceivable

def account_receivable_extractor(results, unpacker):

    document_date = unpacker.get_value_at(1)
    due_date = unpacker.get_value_at(2)
    document = unpacker.get_value_at(3)
    customer = unpacker.get_value_at(4)
    raw_code = unpacker.get_value_at(9)

    customers = results.get_customers()
    bills = results.get_bills()

    calendar_ops = results.get_calendar_ops()
    last_date_of_month = results.get_last_date_of_month()
    first_day_of_current_month = results.get_first_day_of_current_month()

    collections = results.get_collections()
    collections_for_customers = results.get_collections_for_customers()

    list_of_advance_payments = results.get_list_of_advance_payments()

    customers_without_payments_due = results.get_customers_without_payments_due()
    customers_in_last_payment = results.get_customers_in_last_payment()

    errors = results.get_errors()

    if "Cobranza" in document: return
    if not raw_code: return

    if len(raw_code.split("-")) < 4: return

    line_amount = float(unpacker.get_value_at(8))
    line_balance = unpacker.get_value_at(8)

    customer_data = customers[customer]

    account_receivable = AccountReceivable(document_date, due_date, document,
                                           customer, raw_code, customer_data, line_amount,
                                           line_balance, calendar_ops)

    if not account_receivable.is_historic_and_due_for(last_date_of_month):
        return

    if not account_receivable.validate_payment_plan(errors):
        return

    account_receivable.configure_previous_collections(collections, collections_for_customers)
    account_receivable.compute_last_collection_date()

    account_receivable.compute_due_payment(bills, first_day_of_current_month, last_date_of_month)

    account_receivable.validate_low_advance_payment(100, errors)
    account_receivable.validate_advance_payment(errors)

    account_receivable.add_to_list_if_advance_payments(list_of_advance_payments)

    if not account_receivable.validate_total_sale_amount_and_plan_value(errors):
        return

    if not account_receivable.has_due_payments(customers_without_payments_due):
        return

    if not account_receivable.validate_person(errors):
        return

    account_receivable.add_to_list_if_in_last_payment(customers_in_last_payment, first_day_of_current_month)

    results.append_account_to_collect(account_receivable)