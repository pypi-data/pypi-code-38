# coding: utf-8
from io import BytesIO
from maxipago.utils import etree
from maxipago.resources.base import Resource
from maxipago.exceptions import PaymentException


class TransactionResource(Resource):

    def process(self):    
        tree = etree.parse(BytesIO(self.data))                
        #print(etree.tostring(tree, pretty_print=False))
        
        header = tree.find('header')
        error_code = header.find('errorCode')
        
        if error_code is not None and error_code.text != '0':
            error_message = tree.find('errorMsg').text
            raise PaymentException(message=error_message)
        
        result = tree.find('result')
        conf = result.find('resultSetInfo')
        
        self.pages = conf.find('totalNumberOfRecords').text if conf.find('totalNumberOfRecords') is not None else 0
        self.page_number = conf.find('pageNumber').text if conf.find('pageNumber') is not None else None
        self.page_token = conf.find('pageToken').text if conf.find('pageToken') is not None else None
        self.items = []
        records = result.find('records')
        for element in records.iter('record'):
            #print(etree.tostring(element, pretty_print=False))
            #print('-----')
            fields = [
                ('transactionId', 'transaction_id'),
                ('referenceNummber', 'reference_num'),
                ('transactionType', 'transaction_type'),
                ('transactionAmount', 'transaction_amount'),
                ('shippingAmount', 'shipping_amount'),
                ('transactionDate', 'transaction_date'),
                ('orderId', 'order_id'),
                ('splitPaymentOrderId', 'split_payment_order_id'),
                ('userId', 'user_id'),
                ('customerId', 'customer_id'),
                ('companyName', 'company_name'),                
                ('responseCode', 'response_code'),
                ('approvalCode', 'approval_code'),
                ('paymentType', 'payment_type'),
                ('bankRoutingNumber', 'bank_routing_number'),
                ('achAccountNumber', 'ach_account_number'),
                ('avsResponseCode', 'avs_response_code'),
                ('billingAddress1', 'billing_address1'),
                ('billingName', 'billing_name'),
                ('billingAddress2', 'billing_address2'),
                ('billingCity', 'billing_city'),
                ('billingState', 'billing_state'),
                ('billingCountry', 'billing_country'),
                ('billingZip', 'billing_zip'),
                ('billingPhone', 'billing_phone'),
                ('billingEmail', 'billing_email'),
                ('comments', 'comments'),
                ('transactionStatus', 'transaction_status'),
                ('transactionState', 'transaction_state'),
                ('recurringPaymentFlag', 'recurring_payment_flag'),
                ('processorReturnedData', 'processor_returned_data'),
                ('gatewayDebitNetworkID', 'gateway_debit_network_id'),
                ('creditCardType', 'credit_card_type'),
                ('boletoUrl', 'boleto_url'),
                ('boletoNumber', 'boleto_number'),
                ('expirationDate', 'expiration_date'),
                ('processorID', 'processor_id'),
                ('dateOfPayment', 'date_of_payment'),
                ('dateOfFunding', 'date_of_funding'),
                ('bankOfPayment', 'bank_of_payment'),
                ('branchOfPayment', 'branch_of_payment'),
                ('paidAmount', 'paid_amount'),
                ('bankFee', 'bank_fee'),
                ('netAmount', 'net_amount'),
                ('returnCode', 'return_code'),
                ('clearingCode', 'clearing_code'),
                ('customField1', 'custom_field1'),
                ('customField2', 'custom_field2'),
                ('customField3', 'custom_field3'),
                ('customField4', 'custom_field4'),
                ('customField5', 'custom_field5'),
                ('numberOfInstallments', 'number_of_installments'),
                ('chargeInterest', 'charge_interest'),
                ('processorTransactionID', 'processor_transaction_id'),
                ('processorReferenceNumber', 'processor_reference_number')
            ]
            item = {}
            for f_name, f_translated in fields:
                field = element.find(f_name)
                if field is not None:                    
                    item.update({f_translated: field.text})
            if item is not None:
                self.items.append(item)