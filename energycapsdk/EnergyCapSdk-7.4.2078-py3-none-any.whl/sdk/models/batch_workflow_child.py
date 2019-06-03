# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class BatchWorkflowChild(Model):
    """BatchWorkflowChild.

    :param due_date:  <span class='property-internal'>Required</span>
    :type due_date: ~energycap.sdk.models.BillHeaderWorkflowChild
    :param statement_date:  <span class='property-internal'>Required</span>
    :type statement_date: ~energycap.sdk.models.BillHeaderWorkflowChild
    :param invoice_number:  <span class='property-internal'>Required</span>
    :type invoice_number: ~energycap.sdk.models.BillHeaderWorkflowChild
    :param control_code:  <span class='property-internal'>Required</span>
    :type control_code: ~energycap.sdk.models.BillHeaderWorkflowChild
    :param next_reading:  <span class='property-internal'>Required</span>
    :type next_reading: ~energycap.sdk.models.BillHeaderWorkflowChild
    :param account_period_name:  <span
     class='property-internal'>Required</span>
    :type account_period_name: ~energycap.sdk.models.BillHeaderWorkflowChild
    :param account_period_year:  <span
     class='property-internal'>Required</span>
    :type account_period_year: ~energycap.sdk.models.BillHeaderWorkflowChild
    """

    _validation = {
        'due_date': {'required': True},
        'statement_date': {'required': True},
        'invoice_number': {'required': True},
        'control_code': {'required': True},
        'next_reading': {'required': True},
        'account_period_name': {'required': True},
        'account_period_year': {'required': True},
    }

    _attribute_map = {
        'due_date': {'key': 'dueDate', 'type': 'BillHeaderWorkflowChild'},
        'statement_date': {'key': 'statementDate', 'type': 'BillHeaderWorkflowChild'},
        'invoice_number': {'key': 'invoiceNumber', 'type': 'BillHeaderWorkflowChild'},
        'control_code': {'key': 'controlCode', 'type': 'BillHeaderWorkflowChild'},
        'next_reading': {'key': 'nextReading', 'type': 'BillHeaderWorkflowChild'},
        'account_period_name': {'key': 'accountPeriodName', 'type': 'BillHeaderWorkflowChild'},
        'account_period_year': {'key': 'accountPeriodYear', 'type': 'BillHeaderWorkflowChild'},
    }

    def __init__(self, due_date, statement_date, invoice_number, control_code, next_reading, account_period_name, account_period_year):
        super(BatchWorkflowChild, self).__init__()
        self.due_date = due_date
        self.statement_date = statement_date
        self.invoice_number = invoice_number
        self.control_code = control_code
        self.next_reading = next_reading
        self.account_period_name = account_period_name
        self.account_period_year = account_period_year
