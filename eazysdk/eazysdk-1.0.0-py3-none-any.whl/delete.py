from .session import Session
from .exceptions import common_exceptions_decorator
from .exceptions import ResourceNotFoundError


class Delete:
    def __init__(self):
        """
        A collection of DELETE requests made to the EazyCustomerManager
        API
        """
        self.sdk = Session()

    @common_exceptions_decorator
    def callback_url(self,):
        """
        Delete the current callback URL from EazyCustomerManager

        :Example:
        callback_url()

        :Returns:
        'Callback URL deleted.'
        """
        self.sdk.endpoint = 'BACS/callback'
        response = self.sdk.delete()
        # NULL will be returned if a callback URL does not exist
        if str(response) == '{"Message":null}':
            return 'An unknown error has occurred.'
        else:
            # Use requests.json to get the part of the response we need.
            return 'Callback URL deleted.'

    @common_exceptions_decorator
    def payment(self, contract, payment, comment):
        """
        Delete a payment from EazyCustomerManager, as long as it hasn't
        already been submitted to BACS.

        :Args:
        - contract - The unique GUID of the contract.
        - payment - The unique GUID of the payment.
        - comment - A comment that can be returned when querying the
                    payment

        :Example:
        customers('ab09362d-f88e-4ee8-be85-e27e1a6ce06a',
                  ')

        :Returns:
        customer json object(s)
        """
        parameters = {
            'comment': comment
        }
        self.sdk.params = parameters
        self.sdk.endpoint = 'contract/%s/payment/%s' % (contract, payment)
        response = self.sdk.delete()

        if 'Payment not found' in response:
            raise ResourceNotFoundError(
                'The payment %s either doesn\'t exist or has already been'
                ' deleted.' % payment
            )
        return response
