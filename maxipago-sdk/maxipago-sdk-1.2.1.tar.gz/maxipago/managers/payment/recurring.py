# coding: utf-8
from maxipago.managers.base import ManagerTransaction, ManagerApi
from maxipago.requesters.payment import PaymentRecurringRequester
from maxipago.resources.payment import PaymentResource
from maxipago.resources.cancel import CancelResource

class PaymentRecurringManager(ManagerTransaction):

    def add(self, **kwargs):
        fields = (
            ('processor_id', {'translated_name': 'processorID'}),
            ('reference_num', {'translated_name': 'referenceNum'}),
            ('ip_address', {'translated_name': 'ipAddress', 'required': False}),
            ('order_id', {'translated_name': 'orderID', 'required': False}),

            ('card_number', {'translated_name': 'transactionDetail/payType/creditCard/number', 'required': False}),
            ('card_expiration_month', {'translated_name': 'transactionDetail/payType/creditCard/expMonth', 'required': False}),
            ('card_expiration_year', {'translated_name': 'transactionDetail/payType/creditCard/expYear', 'required': False}),
            ('card_cvv', {'translated_name': 'transactionDetail/payType/creditCard/cvvNumber', 'required': False}),

            ('charge_total', {'translated_name': 'payment/chargeTotal'}),
            ('currency_code', {'translated_name': 'payment/currencyCode', 'required': True}),

            ('recurring_action', {'translated_name': 'recurring/action', 'default': 'new'}),
            ('recurring_start', {'translated_name': 'recurring/startDate', 'required': False}),
            ('recurring_last', {'translated_name': 'recurring/lastDate', 'required': False}),
            ('recurring_frequency', {'translated_name': 'recurring/frequency'}),
            ('recurring_period', {'translated_name': 'recurring/period'}),
            ('recurring_first_amount', {'translated_name': 'recurring/firstAmount', 'required': False}),
            ('recurring_last_amount', {'translated_name': 'recurring/lastAmount', 'required': False}),
            ('recurring_installments', {'translated_name': 'recurring/installments'}),
            ('recurring_failure_threshold', {'translated_name': 'recurring/failureThreshold', 'required': False}),
        )
        
        requester = PaymentRecurringRequester(fields, kwargs)
        resource = PaymentResource
        if kwargs['recurring_action'] == 'modify':
            resource = CancelResource
        return self.send(command='recurringPayment', requester=requester, resource=resource)

    def delete(self, **kwargs):
        fields = (
            ('order_id', {'translated_name': 'orderID'}),
        )

        requester = PaymentRecurringRequester(fields, kwargs)
        
        manager = ManagerApi(maxid=self.maxid, api_key=self.api_key, api_version=self.api_version, sandbox=self.sandbox)
        return manager.send(command='cancel-recurring', requester=requester, resource=CancelResource)
