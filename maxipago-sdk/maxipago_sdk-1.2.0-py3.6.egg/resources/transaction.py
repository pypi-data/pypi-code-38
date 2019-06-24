# coding: utf-8
from io import BytesIO
from maxipago.utils import etree
from maxipago.resources.base import Resource
from maxipago.exceptions import PaymentException


class TransactionResource(Resource):

    def process(self):    
        tree = etree.parse(BytesIO(self.data))                
        #print(etree.tostring(tree, pretty_print=False))
        
        error_code = tree.find('errorCode')
        if error_code is not None and error_code.text != '0':
            error_message = tree.find('errorMsg').text
            raise PaymentException(message=error_message)
        
        total_pages = tree.find('totalNumberOfRecords')
        page = tree.find('pageNumber')
        print(total_pages, page)
        self.pages = total_pages
        self.page_number = page
        self.items = []
        
        for _, element in etree.iterparse(tree, tag='record'):
            print('%s -- %s' % (element.findtext('transactionId'), element[1].text))
            element.clear()
        
        return records
        for element in records.iter():
            fields = [
                ('transactionId', 'transaction_id'),
                ('referenceNummber', 'reference_num'),
                ('transactionType', 'transaction_type'),
                ('transactionAmount', 'transaction_amount'),
                ('transactionDate', 'transaction_date'),
                ('orderId', 'order_id'),
                ('responseCode', 'response_code'),
                ('approvalCode', 'approval_code'),
                ('paymentType', 'payment_type'),
                ('transactionStatus', 'transaction_status'),
                ('transactionState', 'transaction_state'),
                ('recurringPaymentFlag', 'recurring_payment_flag'),
                ('creditCardType', 'credit_card_type'),
                ('processorID', 'processor_id'),
                ('dateOfPayment', 'date_of_payment'),
                ('dateOfFunding', 'date_of_funding'),
                ('returnCode', 'return_code'),
                ('numberOfInstallments', 'number_of_installments'),
                ('processorTransactionID', 'processor_transaction_id'),
                ('processorReferenceNumber', 'processor_reference_number')
            ]
            
            for f_name, f_translated in fields:
                field = element.find(f_name)
                if field is not None:
                    item = {}
                    setattr(item, f_translated, field.text)
            result.items.append(item)

