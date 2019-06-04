from .session import Session
from .settings import Settings as s
from warnings import warn
from .utils import customer_checks
from .utils import contract_checks
from .utils import payment_checks
from .exceptions import EazySDKException
from .exceptions import common_exceptions_decorator
from .exceptions import ParameterNotAllowedError
from .exceptions import InvalidParameterError
from .exceptions import ResourceNotFoundError
from .exceptions import RecordAlreadyExistsError


class Post:
    def __init__(self):
        """
        A collection of POST requests made to the ECM3 API
        """
        self.sdk = Session()

    @common_exceptions_decorator
    def callback_url(self, callback_url):
        """
        Create or update the endpoint for data returned from ECM3

        NOTE: We strongly recommend using a HTTPS secured URL as the
        return endpoint.

        :Example:
        callback_url(callback_url='test.com')

        :Returns:
        'The new callback url is example.com'
        """
        self.sdk.endpoint = 'BACS/callback'
        self.sdk.params = {
            'url': callback_url
        }
        response = self.sdk.post()

        if 'ExceptionMessage' in str(response):
            raise EazySDKException(
                'The API serializer is not enabled for this account. Please'
                'contact us on help@eazycollect.co.uk for assistance'
            )
        elif 'Updated' not in str(response):
            raise EazySDKException(
                'For an unexpected reason, the new callback URL was not'
                'created.'
            )
        return 'The new callback URL is %s' % callback_url

    @common_exceptions_decorator
    def customer(self, email, title, customer_reference, first_name, surname,
                 line1, post_code, account_number, sort_code,
                 account_holder_name, line2='', line3='', line4='',
                 company_name='', date_of_birth='', initials='', home_phone='',
                 work_phone='',  mobile_phone='',):
        """
        Create a customer in ECM3

        :Required args:
        - email - The email address of the new customer. This must be
            unique
        - title - The title of the new customer
        - customer_reference - The customer reference of the new
            customer. This must be unique.
        - first_name - The first name of the new customer
        - surname - The surname of the new customer
        - line1 - The first line of the new customers address
        - post_code - The post code of the new customer
        - account_number - The bank account number of the new customer
        - sort_code - The sort code of the new customer
        - account_holder_name - The new customers full name as it
            appears on their bank account

        :Optional args:
        - line2 - The second line of the new customers address
        - line3 - The third line of the new customers address
        - line4 - The fourth line of the new customers address
        - company_name - The name of the company the new customer
            represents
        - date_of_birth - The date of birth of the new customer,
            formatted to ISO standards (YYYY-MM-DD)
        - initials - The initials of the new customer
        - home_phone - The home phone number of the new customer
        - work_phone - The work phone number of the new customer
        - mobile_phone - The mobile phone number of the new customer

        :Example:
        customer(email='test@email.com', title='Mrs', first_name='Jane',
                 surname='Doe', line1='1 Test Lane',
                 post_code='TE5T 2AW', account_number='12345678',
                 sort_code='123456', account_holder_name='Mrs J Doe',)

        :Returns:
        customer json object
        """
        # Get all method arguments
        method_arguments = locals()
        # We will not be passing self into ECM3
        del method_arguments['self']
        # A set of pythonic arguments and their ECM3 counterparts
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
        parameters = {}

        required_parameters = [
            'email',
            'title',
            'customer_reference',
            'first_name',
            'surname',
            'line1',
            'post_code',
            'account_number',
            'sort_code',
            'account_holder_name',
        ]

        key = None
        try:
            for key, value in method_arguments.items():
                if key in required_parameters and value == '':
                    raise InvalidParameterError(
                        '%s cannot be empty.' % key
                    )
                elif value != '':
                    parameters.update({conversions[key]: value})
        except KeyError:
            raise ParameterNotAllowedError(
                '%s is not an acceptable argument for this call, refer'
                'to the man page for all available arguments' % key
            )

        # A collection of tests against required params
        customer_checks.check_postcode_is_valid_uk_format(post_code)
        customer_checks.check_email_address_format(email)
        customer_checks.check_bank_details_format(
            account_number, sort_code, account_holder_name
        )
        self.sdk.endpoint = 'customer'
        self.sdk.params = parameters
        response = self.sdk.post()
        if 'There is an existing Customer with the same Client and Customer' \
           ' ref in the database already' in str(response):
            raise RecordAlreadyExistsError(
                'A customer with the given customer_reference already exists.'
                ' Please change the customer reference and re-submit.'
            )
        return response

    @common_exceptions_decorator
    def contract(self, customer, schedule_name, start_date, gift_aid,
                 termination_type, at_the_end, number_of_debits='',
                 frequency='', initial_amount='', extra_initial_amount='',
                 payment_amount='', final_amount='', payment_month_in_year='',
                 payment_day_in_month='', payment_day_in_week='',
                 termination_date='', additional_reference='',
                 custom_dd_reference='',):
        """
        Create a contract in ECM3

        :Required args:
        - customer - The GUID of the customer the new contract will
            belong to
        - schedule_name - The name of the schedule the new contract will
            belong to. Schedules can be found via api.get.schedules()
        - start_date - The desired start date of the new contract. This
            must be x working days in the future, where x is the
            agreed amount of working days with Eazy Collect.
        - gift_aid - Whether the contract is eligible for gift aid or
            not
        - termination_type - The method of termination for the new
            contract
        - at_the_end - What happens to the new contract after the
            termination event has been triggered

        :Optional args:
        - number_of_debits - Mandatory if termination type is set to
            'Collect certain number of debits'
        - frequency - Mandatory if the new contract is not ad-hoc. This
            parameter allows you to skip periods (e.g a value of 2 would
            collect every 2 weeks or months)
        - initial_amount - Used if the first collection amount is
            different from the rest. Not to be used on ad-hoc contracts.
        - extra_initial_amount - Used for any additional charges, for
            example, a gym registration fee.
        - payment_amount - Mandatory if the contract is not ad-hoc. The
            regular collection amount for the new contract
        - final_amount - Used if the final collection amount is
            different from the rest. Not to be used on ad-hoc contracts.
        - payment_month_in_year - The collection month for annual
            contracts. Jan = 0, Dec = 11
        - payment_day_in_month - The collection day for monthly
            contracts. Accepts 1-28 or 'last day of month'
        - payment_day_in_week - The collection day for weekly contracts.
            0 = Mon, 6 = Sun
        - termination_date - The termination date of the newly created
            contract.
        - additional_reference - An additional reference for the newly
            created contract.
        - custom_dd_reference - A custom Direct Debit reference for the
            newly created contract.

        :Example:
        contract('42217d45-cf22-4430-ab02-acc1f8a2d020',
        'test_schedule', '2019-05-07', False, 'Until further notice',
        'Switch to further notice' additional_reference='test_123')

        :Returns:
        contract json object
        """
        # Perform several validation checks against arguments provided
        method_arguments = locals()
        # We will not need self or customer when passing parameters
        del method_arguments['self']
        del method_arguments['customer']
        # A set of pythonic arguments and their ECM3 counterparts
        conversions = {
            'schedule_name': 'scheduleName',
            'start_date': 'start',
            'gift_aid': 'isGiftAid',
            'termination_type': 'terminationType',
            'at_the_end': 'atTheEnd',
            'number_of_debits': 'numberOfDebits',
            'frequency': 'every',
            'initial_amount': 'initialAmount',
            'extra_initial_amount': 'extraInitialAmount',
            'payment_amount': 'amount',
            'final_amount': 'finalAmount',
            'payment_month_in_year': 'paymentMonthInYear',
            'payment_day_in_month': 'paymentDayInMonth',
            'payment_day_in_week': 'paymentDayInWeek',
            'termination_date': 'terminationDate',
            'additional_reference': 'additionalReference',
            'custom_dd_reference': 'customDirectDebitRef',
        }
        parameters = {}
        # Contract validations
        sched = contract_checks.check_schedule_name(schedule_name)
        ad_hoc = contract_checks.ad_hoc_checker(schedule_name)
        start = contract_checks.check_start_date(start_date)
        term = contract_checks.check_termination_type(termination_type)
        ate = contract_checks.check_at_the_end(at_the_end)

        # Avoid non-assignment warnings
        key = None
        try:
            for key, value in method_arguments.items():
                if value != '':
                    parameters.update({conversions[key]: value})
        except KeyError:
            raise ParameterNotAllowedError(
                '%s is not an acceptable argument for this call, refer'
                ' to the man page for all available arguments' % key
            )

        if start:
            del parameters['start']
            parameters.update({'start': start})

        if not ad_hoc:
            if termination_type.lower() != 'until further notice':
                if s.contracts['auto_fix_ad_hoc_termination_type']:
                    warn('Termination type must be Until Further Notice on'
                         ' ad_hoc contracts. This has been automatically '
                         'applied.')
                    del parameters['terminationType']
                    parameters.update(
                        {'terminationType': 'until further notice'}
                    )
                else:
                    raise InvalidParameterError(
                        'termination_type must be set to Until Further Notice'
                        ' on ad_hoc contracts'
                    )
            if at_the_end.lower() != 'switch to further notice':
                if s.contracts['auto_fix_ad_hoc_at_the_end']:
                    warn('At the end must be Switch To Further Notice on'
                         ' ad_hoc contracts. This has been automatically '
                         'applied.')
                    del parameters['atTheEnd']
                    parameters.update(
                        {'atTheEnd': 'switch to further notice'}
                    )
                else:
                    raise InvalidParameterError(
                        'at_the_end must be set to Switch to further notice on'
                        'ad_hoc contracts'
                    )
            if initial_amount != '':
                raise ParameterNotAllowedError(
                    'initial_amount cannot be passed on ad_hoc contracts.'
                )
            elif extra_initial_amount != '':
                raise ParameterNotAllowedError(
                    'extra_initial_amount cannot be passed on ad_hoc contracts'
                )
            elif final_amount != '':
                raise ParameterNotAllowedError(
                    'final_amount cannot be passed on ad_hoc contracts'
                )
            else:
                pass
        else:
            freq = contract_checks.payment_time_frame_checker(schedule_name)
            if frequency == '':
                raise InvalidParameterError(
                    'frequency must be passed on non-ad_hoc contracts'
                )
            elif payment_amount == '':
                raise InvalidParameterError(
                    'payment amount must be passed on non-ad_hoc contracts'
                )
            elif freq == 0:
                if payment_day_in_week == '':
                    raise InvalidParameterError(
                        'payment_day_in_week must be passed on weekly'
                        ' contracts'
                    )
                else:
                    contract_checks.check_payment_day_in_week(
                        payment_day_in_week
                    )
            elif freq == 1:
                if str(payment_day_in_month) != parameters['start'][8:10]:
                    if s.contracts['auto_fix_payment_day_in_month']:
                        pdim = parameters['start'][8:10]
                        del parameters['paymentDayInMonth']
                        parameters.update({'paymentDayInMonth': pdim})
                    elif payment_day_in_month == '':
                        raise InvalidParameterError(
                            'payment_day_in_month must be passed on monthly'
                            ' contracts'
                        )
                    else:
                        raise InvalidParameterError(
                            'payment_day_in_month must be set to %s if the'
                            ' start date is set to %s'
                            % (parameters['start'][8:10], parameters['start'])
                        )
                else:
                    contract_checks.check_payment_day_in_month(
                        payment_day_in_month
                    )
            elif freq == 2:
                if str(payment_month_in_year) not in parameters['start'][5:7]:
                    if s.contracts['auto_fix_payment_month_in_year']:
                        pmiy = int(parameters['start'][4:6])
                        del parameters['paymentMonthInYear']
                        parameters.update({'paymentMonthInYear': pmiy})
                    elif payment_month_in_year == '':
                        raise InvalidParameterError(
                            'payment_month_in_year must be passed on monthly'
                            ' contracts'
                        )
                    else:
                        raise InvalidParameterError(
                            'payment_month_in_year must be set to %s if the'
                            ' start date is set to %s'
                            % (parameters['start'][5:7], parameters['start'])
                        )
                else:
                    contract_checks.check_payment_month_in_year(
                        payment_month_in_year
                    )

                if str(payment_day_in_month) != parameters['start'][8:10]:
                    if s.contracts['auto_fix_payment_day_in_month']:
                        pdim = parameters['start'][8:10]
                        del parameters['paymentDayInMonth']
                        parameters.update({'paymentDayInMonth': pdim})
                    elif payment_day_in_month == '':
                        raise InvalidParameterError(
                            'payment_day_in_month must be passed on monthly'
                            ' contracts'
                        )
                    else:
                        raise InvalidParameterError(
                            'payment_day_in_month must be set to %s if the'
                            ' start date is set to %s'
                            % (parameters['start'][8:10], parameters['start'])
                        )
            else:
                contract_checks.check_payment_day_in_month(
                    payment_day_in_month
                )

            if term == 0:
                if number_of_debits == '':
                    raise InvalidParameterError(
                        'number_of_debits must be passed if termination_type'
                        ' is take certain number of debits.'
                    )
                else:
                    contract_checks.check_number_of_debits(number_of_debits)
            elif term == 1:
                if ate != 1:
                    raise InvalidParameterError(
                        'at_the_end must be set to Switch to Further Notice if'
                        ' termination_type is set to Until Further Notice'
                    )
            elif term == 2:
                if termination_date == '':
                    raise InvalidParameterError(
                        'termination_date must be passed if termination_type'
                        ' is set to End on Exact Date.'
                    )
                else:
                    date = contract_checks.check_termination_date_is_in_future(
                        termination_date, start_date
                    )
                    if date:
                        pass

        self.sdk.endpoint = 'customer/%s/contract' % customer
        self.sdk.params = parameters
        response = self.sdk.post()
        return response

    @common_exceptions_decorator
    def cancel_direct_debit(self, contract,):
        """
        Cancel a Direct Debit within ECM3

        NOTE: Cancelling a Direct Debit will not cancel the payment
        creation process. The reason being; There are two parts to a
        contract, the schedule and the Direct Debit. Cancelling the
        Direct Debit will cease future payments to the bank, but it will
        generate payments on the system. These payments will return
        unpaid, though any ad-hoc payments must be manually deleted.


        :Required args:
        - contract - The GUID of the Direct Debit to be cancelled

        :Example:
        cancel_direct_debit('42217d45-cf22-4430-ab02-acc1f8a2d020')

        :Returns:
        contract json object
        """
        self.sdk.endpoint = 'contract/%s/cancel' % contract
        response = self.sdk.post()

        if 'Contract not found' in response:
            raise ResourceNotFoundError(
                'Contract %s not found. No action has been taken.'
            )
        else:
            return response

    @common_exceptions_decorator
    def archive_contract(self, contract):
        """
        Archive a Direct Debit within ECM3

        NOTE: Archiving a contract achieves different results to
        cancelling a Direct Debit. First and most importantly, the
        process is irreversible. Once a contract is archived, it can not
        be unarchived. The process flow works like so; The Direct Debit
        is cancelled, any arrears that are outstanding are written off,
        any future scheduled payments are cancelled and finally, the
        contract status is set to archived. Like cancelling a Direct
        Debit, any ad_hoc payments must be manually cancelled.


        :Required args:
        - contract - The GUID of the contract ot be archived

        :Example:
        archive_contract('42217d45-cf22-4430-ab02-acc1f8a2d020')

        :Returns:
        contract json object
        """
        self.sdk.endpoint = 'contract/%s/archive' % contract
        response = self.sdk.post()

        if 'Contract is already archived' in response:
            return(
                'Contract %s is already archived. No action will be taken.' %
                contract
            )
        return response

    @common_exceptions_decorator
    def reactivate_direct_debit(self, contract):
        """
        Reactivate a Direct Debit within ECM3

        NOTE: Reactivating a contract changes the status of a contract from
        ‘Cancelled’ to ‘Pending to activate’. This will sent a new instruction
        to the bank, generating an 0N charge.

        :Required args:
        - contract - The GUID of the contract to be re-activated

        :Example:
        reactivate_direct_debit('42217d45-cf22-4430-ab02-acc1f8a2d020')

        :Returns:
        contract json object
        """
        self.sdk.endpoint = 'contract/%s/reactivate' % contract
        response = self.sdk.post()
        return response

    @common_exceptions_decorator
    def restart_contract(self, contract, termination_type, at_the_end,
                         collection_amount='', initial_amount='',
                         final_amount='', payment_day_in_month='',
                         payment_month_in_year='', additional_reference=''):
        """
        Restart a contract within ECM3

        NOTE: Restarting a contract is fundamentally different to
        reactivating a contract as it can only be performed if the
        following criteria have been met

        - The original contract was a fixed term which has expired
        - The payment schedule has met its end naturally, and the
            contract status has become 'Expired'

        This call adds a new contract onto the end of the previous
        contract, in effect 'recycling' the previous direct debit at
        the bank which can save on Direct Debit setup charges.

        :Required args:
        - contract - The GUID of the contract to be restarted
        - termination_type - The termination type of the restarted
            contract
        - at_the_end - What happens to the new contract after the
            termination event has been triggered

        :Optional args:
        - payment_amount - Mandatory if the contract is not ad-hoc. The
            regular collection amount for the restated contract
        - initial_amount - Used if the first collection amount is
            different from the rest. Not to be used on ad-hoc contracts.
        - final_amount - Used if the final collection amount is
            different from the rest. Not to be used on ad-hoc contracts.
        - payment_day_in_month - The collection day for monthly
            contracts. Accepts 1-28 or 'last day of month'
        - additional_reference - An additional reference for the newly
            created contract.

        :Example:
        restart_contract(
            '42217d45-cf22-4430-ab02-acc1f8a2d020',
            'Until further notice', 'Switch to further notice'
        )

        :Returns:
        contract json object
        """
        # Perform several validation checks against arguments provided
        method_arguments = locals()
        # We will not need self or customer when passing parameters
        del method_arguments['self']
        del method_arguments['contract']
        # A set of pythonic arguments and their ECM3 counterparts
        conversions = {
            'termination_type': 'terminationType',
            'at_the_end': 'atTheEnd',
            'initial_amount': 'initialAmount',
            'collection_amount': 'amount',
            'final_amount': 'finalAmount',
            'payment_day_in_month': 'paymentDayInMonth',
            'payment_month_in_year': 'paymentMonthInYear',
            'termination_date': 'terminationDate',
            'additional_reference': 'additionalReference',
        }
        parameters = {}
        # Contract validations

        # Avoid non-assignment warnings
        key = None
        try:
            for key, value in method_arguments.items():
                if value != '':
                    parameters.update({conversions[key]: value})
        except KeyError:
            raise ParameterNotAllowedError(
                '%s is not an acceptable argument for this call, refer'
                ' to the man page for all available arguments' % key
            )
        self.sdk.params = parameters
        self.sdk.endpoint = 'contract/%s/restart' % contract
        response = self.sdk.post()

        if 'Contract is not expired.' in response:
            return(
                'The contract %s is not expired, no action has been taken'
                % contract
            )

        return response

    @common_exceptions_decorator
    def payment(self, contract, collection_amount, collection_date,
                comment, is_credit=False):
        """
        Create a payment against a contract in ECM3

        :Required args:
        - contract - The GUID of the contact a payment will be made
            against
        - collection_amount - The total amount to be collected from the
            new payment
        - collection_date - The desired start date of the new contract.
            This must be x working days in the future, where x is the
            agreed amount of working days with Eazy Collect.
        - comment - A comment related to the new payment
        - is_credit - If you have your own SUN and you have made prior
            arrangements with Eazy Collect, this may be passed to issue
            a credit to a customer. By default, it is set to false.

        :Example:
        payment('42217d45-cf22-4430-ab02-acc1f8a2d020', '10.00',
                '2019-05-07', 'A new payment')

        :Returns:
        payment json object
        """
        # Perform several validation checks against arguments provided
        method_arguments = locals()
        # We will not need self or contract when passing parameters
        del method_arguments['self']
        del method_arguments['contract']
        # A set of pythonic arguments and their ECM3 counterparts
        conversions = {
            'collection_amount': 'amount',
            'collection_date': 'date',
            'comment': 'comment',
            'is_credit': 'isCredit',
        }
        parameters = {}
        # Contract validations
        payment_checks.check_collection_amount(collection_amount)
        collection = payment_checks.check_collection_date(collection_date)

        if is_credit:
            e = payment_checks.is_credit_allowed_check()
            if not e:
                is_credit = False

        # Avoid non-assignment warnings
        key = None
        try:
            for key, value in method_arguments.items():
                if value != '':
                    parameters.update({conversions[key]: value})
        except KeyError:
            raise ParameterNotAllowedError(
                '%s is not an acceptable argument for this call, refer'
                ' to the man page for all available arguments' % key
            )

        if collection:
            del parameters['date']
            parameters.update({'date': collection})

        self.sdk.endpoint = 'contract/%s/payment' % contract
        self.sdk.params = parameters
        response = self.sdk.post()

        if 'Contract not found' in response:
            raise InvalidParameterError(
                'The specified contract GUID does not relate to a customer'
                ' within ECM3.'
            )

        return response