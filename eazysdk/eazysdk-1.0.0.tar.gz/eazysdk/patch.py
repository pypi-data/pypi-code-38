from .session import Session
from .exceptions import common_exceptions_decorator
from .exceptions import InvalidParameterError
from .exceptions import ResourceNotFoundError
from .exceptions import ParameterNotAllowedError
from .utils import customer_checks
from .utils import contract_checks
from .utils import payment_checks


class Patch:
    def __init__(self):
        """
        A collection of PATCH requests made to the EazyCustomerManager
        API
        """
        self.sdk = Session()

    @common_exceptions_decorator
    def customer(self, customer, email='', title='', date_of_birth='',
                 first_name='', surname='', company_name='', line1='',
                 post_code='', account_number='', sort_code='',
                 account_holder_name='', home_phone='', mobile_phone='',
                 work_phone='', line2='', line3='', line4='', initials=''):
        """
        Modify a customer in EazyCustomerManager

        :Required args:
        - customer - The GUID of the customer to be modified within
            EazyCustomerManager.

        :Optional args:
        - email - The email address of the customer. This must be unique
        - title - The title of the customer
        - first_name - The first name of the customer
        - surname - The surname of the customer
        - line1 - The first line of the customers address
        - post_code - The post code of the customer
        - account_number - The bank account number of the customer
        - sort_code - The sort code of the customer
        - account_holder_name - The customers full name as it appears
            on their bank account
        - line2 - The second line of the customers address
        - line3 - The third line of the customers address
        - line4 - The fourth line of the customers address
        - company_name - The name of the company the customer represents
        - date_of_birth - The date of birth of the customer,
            formatted to ISO standards (YYYY-MM-DD)
        - initials - The initials of the customer
        - home_phone - The home phone number of the customer
        - work_phone - The work phone number of the customer
        - mobile_phone - The mobile phone number of the customer

        :Example:
        customer(email='test@email.com')

        :Returns:
        'customer {guid} updated successfully'
        """
        # Get all method arguments
        method_arguments = locals()
        # We will not be passing self into EazyCustomerManager
        del method_arguments['self']
        # A set of pythonic arguments and EazyCustomerManager counterparts
        conversions = {
            'email': 'email',
            'title': 'title',
            'customer_reference': 'customerRef',
            'first_name': 'firstName',
            'surname': 'surname',
            'line1': 'line1',
            'post_code': 'postCode',
            'account_number': 'accountNumber',
            'sort_code': 'bankSortCode',
            'account_holder_name': 'accountHolderName',
            'line2': 'line2',
            'line3': 'line3',
            'line4': 'line4',
            'company_name': 'companyName',
            'date_of_birth': 'dateOfBirth',
            'initials': 'initials',
            'home_phone': 'homePhone',
            'work_phone': 'workPhone',
            'mobile_phone': 'mobilePhone',
        }

        # A blank list of parameters to be updated later
        parameters = {}
        # We reference the key to avoid localization issues
        key = None

        try:
            for key, value in method_arguments.items():
                if key == 'customer':
                    pass
                else:
                    parameters.update({conversions[key]: value})
        except KeyError:
            # Throw custom error for more verbose details on cause
            raise ParameterNotAllowedError(
                '%s is not an acceptable argument for this call, refer'
                'to the man page for all available arguments' % key
            )

        # As none of the params are required, we manually reference them
        if post_code != '':
            customer_checks.check_postcode_is_valid_uk_format(post_code)
        elif email != '':
            customer_checks.check_email_address_format(email)
        elif account_number != '':
            # We provide dummy data here as we are only testing against
            # the account number
            customer_checks.check_bank_details_format(
                account_number, '123456', 'Dummy data'
            )
        elif sort_code != '':
            customer_checks.check_bank_details_format(
                '12345678', sort_code, 'Dummy data'
            )
        elif account_holder_name != '':
            customer_checks.check_bank_details_format(
                '12345678', '123456', account_holder_name
            )

        self.sdk.endpoint = 'customer/%s' % customer
        self.sdk.params = parameters
        response = self.sdk.patch()

        if 'Customer updated' in response:
            return 'customer %s updated successfully' % customer

        return response

    @common_exceptions_decorator
    def contract_amount(self, contract, collection_amount, comment):
        """
        Modify a contract_amount in EazyCustomerManager. It is
        important to note that if the contract is already within the
        cut-off date for the next collection, this will not be amended
        until the following month.

         :Required args:
         - contract - The GUID of the contract to be modified within
             EazyCustomerManager.
         - collection_amount - The new collection amount of the contract
            modified within EazyCustomerManager.
         - comment - A comment to go along with the amendment

         :Example:
         contract('36bb4f4f-9a7f-4ead-82dc-9295c6fb9e8b', 10.50,
         'A comment')

         :Returns:
         'Contract {guid} collection amount has been updated to
         {collection_amount}'
         """
        # Get all method arguments
        method_arguments = locals()
        # We will not be passing self into EazyCustomerManager
        del method_arguments['self']
        # A set of pythonic arguments and EazyCustomerManager counterparts
        parameters = {
            'amount': collection_amount,
            'comment': comment,
        }

        for key, value in method_arguments.items():
            if value == '':
                raise InvalidParameterError(
                    '%s cannot be empty.' % key
                )
        payment_checks.check_collection_amount(collection_amount)

        self.sdk.endpoint = 'contract/%s/amount' % contract
        self.sdk.params = parameters
        response = self.sdk.patch()

        if 'Contract updated' in response:
            return 'Contract %s collection amount has been updated to %s' \
                   % (contract, collection_amount)
        elif 'Contract not found' in response:
            raise ResourceNotFoundError(
                '%s is not a contract belonging to this client.' % contract
            )
        return response

    @common_exceptions_decorator
    def contract_day_weekly(self, contract, new_day, comment,
                            amend_next_payment, next_payment_amount=''):
        # Get all method arguments
        method_arguments = locals()
        # We will not be passing self into EazyCustomerManager
        del method_arguments['self']
        # A set of pythonic arguments and EazyCustomerManager counterparts
        parameters = {
            'day': new_day,
            'comment': comment,
            'patchNextPayment': amend_next_payment,
            'nextPaymentPatchAmount': next_payment_amount,
        }

        for key, value in method_arguments.items():
            if value == '' and key != 'next_payment_amount':
                raise InvalidParameterError(
                    '%s cannot be empty.' % key
                )
        if amend_next_payment and next_payment_amount == '':
            raise InvalidParameterError(
                'next_payment_amount cannot be empty if amend_next_payment is'
                ' set to true.'
            )

        #contract_checks.check_payment_day_in_week(new_day)
        self.sdk.endpoint = 'contract/%s/weekly' % contract
        self.sdk.params = parameters
        response = self.sdk.patch()

        if 'Contract updated' in response:
            return 'Contract %s day updated to %s' % (contract, str(new_day))
        elif 'Contract not found' in response:
            print(response)
            raise ResourceNotFoundError(
                '%s is not a contract belonging to this client.' % contract
            )
        return response

    @common_exceptions_decorator
    def contract_date_monthly(self, contract, new_day, comment,
                              amend_next_payment, next_payment_amount=''):
        """
        Modify the collection date on a monthly contract in
        EazyCustomerManager. It is important to note that if the
        contract is already within the cut-off date for the next
        collection, this will not be amended until the following month.

        :Required args:
        - contract - The GUID of the customer to be modified within
            EazyCustomerManager.
        - new day - The new collection day for the contract
        - comment - A comment to go along with the amendment
        - amend_next_payment - Whether or not the next collection
            amount should be amended due to the change in collection
            date

        :Optional args:
        - next_payment_patch_amount - The collection amount of next
            payment. This should only be passed if amend_next_payment
            is set to True.

        :Example:
        'contract_date_monthly('36bb4f4f-9a7f-4ead-82dc-9295c6fb9e8b',
        15, 'A comment', False)

        :Returns:
        'Contract {guid} day updated to {day}'
        """
        # Get all method arguments
        method_arguments = locals()
        # We will not be passing self into EazyCustomerManager
        del method_arguments['self']
        # A set of pythonic arguments and EazyCustomerManager counterparts
        parameters = {
            'monthDay': new_day,
            'comment': comment,
            'patchNextPayment': amend_next_payment,
            'nextPaymentPatchAmount': next_payment_amount,
        }

        for key, value in method_arguments.items():
            if value == '' and key != 'next_payment_amount':
                raise InvalidParameterError(
                    '%s cannot be empty.' % key
                )
        if amend_next_payment and next_payment_amount == '':
            raise InvalidParameterError(
                'next_payment_amount cannot be empty if amend_next_payment is'
                ' set to true.'
            )

        contract_checks.check_payment_day_in_month(new_day)
        self.sdk.endpoint = 'contract/%s/monthly' % contract
        self.sdk.params = parameters
        response = self.sdk.patch()

        if 'Contract updated' in response:
            return 'Contract %s day updated to %s' % (contract, str(new_day))
        elif 'Contract not found' in response:
            raise ResourceNotFoundError(
                '%s is not a contract belonging to this client.' % contract
            )
        return response

    @common_exceptions_decorator
    def contract_date_annually(self, contract, new_day, new_month, comment,
                               amend_next_payment, next_payment_amount=''):
        """
        Modify the collection date on an annual contract in
        EazyCustomerManager. It is important to note that if the
        contract is already within the cut-off date for the next
        collection, this will not be amended until the following year.

        :Required args:
        - contract - The GUID of the customer to be modified within
            EazyCustomerManager.
        - new day - The new collection day for the contract
        - new_month - The new collection month for the contract
        - comment - A comment to go along with the amendment
        - amend_next_payment - Whether or not the next collection
            amount should be amended due to the change in collection
            date

        :Optional args:
        - next_payment_patch_amount - The collection amount of next
            payment. This should only be passed if amend_next_payment
            is set to True.

        :Example:
        'contract_date_annually('36bb4f4f-9a7f-4ead-82dc-9295c6fb9e8b',
        15, 6, 'A comment', False)

        :Returns:
        'Contract {guid} day updated to {day} and month updated to
        {month}'
        """
        # Get all method arguments
        method_arguments = locals()
        # We will not be passing self into EazyCustomerManager
        del method_arguments['self']
        # A set of pythonic arguments and EazyCustomerManager counterparts
        parameters = {
            'monthDay': new_day,
            'month': new_month,
            'comment': comment,
            'patchNextPayment': amend_next_payment,
            'nextPaymentPatchAmount': next_payment_amount,
        }

        for key, value in method_arguments.items():
            if value == '' and key != 'next_payment_amount':
                raise InvalidParameterError(
                    '%s cannot be empty.' % key
                )
        if amend_next_payment and next_payment_amount == '':
            raise InvalidParameterError(
                'next_payment_amount cannot be empty if amend_next_payment is'
                ' set to true.'
            )
        contract_checks.check_payment_day_in_month(new_day)
        self.sdk.endpoint = 'contract/%s/annual' % contract
        self.sdk.params = parameters
        response = self.sdk.patch()

        if 'Contract updated' in response:
            return 'Contract %s day updated to %s and month updated to %s' \
                % (contract, str(new_day), str(new_month))
        elif 'Contract not found' in response:
            raise ResourceNotFoundError(
                '%s is not a contract belonging to this client.' % contract
            )
        return response

    @common_exceptions_decorator
    def payment(self, contract, payment, collection_amount, collection_date,
                comment):
        """
        Modify a payment in EazyCustomerManager. It is important to note
        that once a payment has been submitted to BACS, it is too late
        to amend the payment.

         :Required args:
         - contract - The GUID of the contract to be modified within
             EazyCustomerManager.
         - payment - The GUID of the payment to be modified within
             EazyCustomerManager.
         - collection_amount - The new collection amount of the payment
         - collection_date - The new collection date of the payment
         - comment - A comment to accompany the amended payment

         :Example:
         payment('36bb4f4f-9a7f-4ead-82dc-9295c6fb9e8b',
         '36bb4f4f-9a7f-4ead-82dc-9295c6fb9e8b', 10.50, '2019-06-04',
         'A comment')

         :Returns:
         'Payment updated'
         """
        # Get all method arguments
        method_arguments = locals()
        # We will not be passing self into EazyCustomerManager
        del method_arguments['self']
        del method_arguments['contract']
        del method_arguments['payment']
        # A set of pythonic arguments and EazyCustomerManager counterparts
        payment_checks.check_collection_amount(collection_amount)
        collection = payment_checks.check_collection_date(collection_date)

        parameters = {
            'amount': collection_amount,
            'date': collection_date,
            'comment': comment,
        }

        if collection:
            del parameters['date']
            parameters.update({'date': collection})

        self.sdk.endpoint = 'contract/%s/payment/%s' % (contract, payment)
        self.sdk.params = parameters
        response = self.sdk.patch()

        return response
