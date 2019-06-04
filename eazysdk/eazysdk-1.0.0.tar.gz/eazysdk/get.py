from .session import Session
from .settings import Settings as s
from warnings import warn
from .exceptions import common_exceptions_decorator
from .exceptions import InvalidParameterError

class Get:
    def __init__(self):
        """
        A collection of GET requests made to the ECM3 API
        """
        self.sdk = Session()

    @common_exceptions_decorator
    def callback_url(self,):
        """
        Get the current callback URL from ECM3

        :Example:
        callback_url()

        :Returns:
        'The current callback url is example.com'
        """
        self.sdk.endpoint = 'BACS/callback'
        response = self.sdk.get()
        # NULL will be returned if a callback URL does not exist
        if str(response) == '{"Message":null}':
            return 'A callback URL has not been set'
        else:
            # Use requests.json to get the part of the response we need.
            return 'The callback URL is {}'.format(response['Message'])

    @common_exceptions_decorator
    def customers(self, email='', title='', search_from='', search_to='',
                  date_of_birth='', customer_reference='', first_name='',
                  surname='', company_name='', post_code='', account_number='',
                  sort_code='', account_holder_name='', home_phone='',
                  work_phone='', mobile_phone='',):
        """
        Search for an individual or a group of customers in ECM3

        NOTE: When searching for customers without using any parameters,
        a warning will be rendered to the user. This can be disabled
        by setting warnings['customer_search'] to false.

        :Args:
        - email - The full email of a customer or group of
             customers in ECM3.
        - title - The title of a single customer or a set of customers
        - search_from - Search for customers added to ECM3 after a given
             date
        - search_to - Search for customers added to ECM3 before a given
             date
        - date_of_birth - The full date of birth of a customer or a set
             of customers
        - customer_reference - The full customer reference of a customer
            or a set of customers
        - first_name - The full or partial first name of a customer or a
            set of customers
        - surname - The full or partial surname of a customer or a set
            of customers
        - company_name - The full or partial company name of a customer
            or a set of customers
        - post code - The full or partial post code of a customer or a
            set of customers
        - account_number - The full account number of a customer
        - sort_code - The full sort code of a customer or a set of
            customers
        - account_holder_name - The full or partial account holder name
            for a customer or a set of customers
        - home phone - The full or partial home phone number of a
            customer or a set of customers
        - work_phone - The full or partial work phone number of a
            customer or a set of customers
            A full or partial work telephone number of a customer
        - mobile_phone - The full or partial mobile phone number of a
            customer or a set of customers

        :Example:
        customers(email='test@email.com', surname='Test')

        :Returns:
        customer json object(s)
        """
        # Get all method arguments
        method_arguments = locals()
        # We will not be passing self into ECM3
        del method_arguments['self']
        # A set of pythonic arguments and their ECM3 counterparts
        conversions = {
            'email': 'email',
            'title': 'title',
            'date_of_birth': 'dateOfBirth',
            'search_from': 'from',
            'search_to': 'to',
            'customer_reference': 'customerRef',
            'first_name': 'firstName',
            'surname': 'surname',
            'company_name': 'companyName',
            'post_code': 'postCode',
            'account_number': 'accountNumber',
            'sort_code': 'bankSortCode',
            'account_holder_name': 'accountHolderName',
            'home_phone': 'homePhoneNumber',
            'work_phone': 'workPhoneNumber',
            'mobile_phone': 'mobilePhoneNumber',
        }

        parameters = {}
        key = None
        if s.warnings['customer_search'] and all(
                value == '' for value in method_arguments.values()):
            warn('Retrieving customers without using any search times '
                 'may take some time.')

        try:
            for key, value in method_arguments.items():
                if value != '':
                    parameters.update({conversions[key]: value})
        except KeyError:
            # Raise custom error if the passed parameter is not defined
            raise InvalidParameterError(
                '%s is not an acceptable argument for this call, refer'
                'to the man page for all available arguments' % key
            )

        self.sdk.endpoint = 'customer'
        self.sdk.params = parameters
        response = self.sdk.get()

        if str(response) != '{"Customers":[]}':
            return response
        else:
            return 'No customers could be found using the search terms:' \
                   '%s' % parameters

    @common_exceptions_decorator
    def contracts(self, customer):
        """
        Return all contracts belonging to a specified customer.

        :Args:
        - customer - The GUID of the customer to be queried.

        :Example:
        contracts('ab09362d-f88e-4ee8-be85-e27e1a6ce06a')

        :Returns:
        contract json objects
        """
        self.sdk.endpoint = 'customer/%s/contract' % customer
        response = self.sdk.get()

        if '"Contracts":[]' in str(response):
            return 'The customer %s does not own any contracts' % customer
        else:
            return response

    @common_exceptions_decorator
    def payments(self, contract, number_of_rows=100):
        """
        Return all payments belonging to a contract.

        :Args:
        - contract - The GUID of the contract to be queried.
        - number_of_rows - The number of payment rows to be returned.
            The maximum number of returned rows is 100. By default, this
            is set to 100.

        :Example:
        payments('ab09362d-f88e-4ee8-be85-e27e1a6ce06a')

        :Returns:
        payment json objects
        """
        self.sdk.endpoint = '/contract/%s/payment' % contract
        self.sdk.params = {'rows': number_of_rows}
        response = self.sdk.get()

        if response == '{"Payments":[]}':
            return 'This contract does not own any payments.'

        return response

    @common_exceptions_decorator
    def payments_single(self, contract, payment):
        """
        Return an individual payment from a specific contract

        :Args:
        - contract - The GUID of the contract to be queried.
        - payment - The GUID of the payment to be queried.

        :Example:f
        payments_single('ab09362d-f88e-4ee8-be85-e27e1a6ce06a',
                        '36bb4f4f-9a7f-4ead-82dc-9295c6fb9e8b')

        :Returns:
        payment json objects
        """
        self.sdk.endpoint = '/contract/%s/payment/%s/' % (contract, payment)
        response = self.sdk.get()

        return response

    @common_exceptions_decorator
    def schedules(self):
        """
        Return all available schedules from ECM3

        NOTE: You should not need to run this command manually without
        exceptional circumstance. The SDK will automatically get a list
        of available schedules when first ran, and place them in the
        /includes folder, named sandbox.csv and ecm3.csv respectively.

        :Example:
        schedules()

        :Returns:
        schedule json objects
        """
        self.sdk.endpoint = 'schedules'
        response = self.sdk.get()
        return response
