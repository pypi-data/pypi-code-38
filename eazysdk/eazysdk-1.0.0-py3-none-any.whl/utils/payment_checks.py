from datetime import datetime
from .contract_checks import check_working_days_in_future
from ..settings import Settings as s
from warnings import warn
from ..exceptions import InvalidParameterError


def check_collection_date(collection_date):
    """ Check that the collection_date argument is a valid ISO date and
    is at least x working days in the future, where x is the
    pre-determined bacs_processing_days setting. Throw an error if this
    is not the case.

    :Args:
    collection_date - A collection_date argument provided by the
        post.payment() function
    """
    date_format = '%Y-%m-%d'
    desired_date = datetime.strptime(collection_date, date_format).date()
    ongoing_days = s.direct_debit_processing_days['ongoing']
    first_date = check_working_days_in_future(ongoing_days)

    if desired_date < first_date:
        if s.payments['auto_fix_payment_date']:
            warn(
                '%s is not a valid start date. The earliest start date '
                'available is %s. This date has automatically been'
                ' selected.'
                % (desired_date, first_date)
            )
            return str(first_date)
        raise InvalidParameterError(
            '%s is not a valid collection date. The earliest collection date'
            ' available is %s. Please change this and re-submit.'
            % (desired_date, first_date)
        )
    else:
        pass


def is_credit_allowed_check():
    """ Check whether or not is_credit is enabled for a client. This
    function does not check whether is_credit is enabled through
    EazyCustomerManager, instead it checks the setting in settings.py.
    Regardless of the setting, is_credit will be disallowed if it is
    disallowed on EazyCustomerManager.
    """
    if s.payments['is_credit_allowed']:
        pass
    else:
        warn(
            'This client cannot use the is_credit function. It has been'
            ' automatically disabled.'
        )
        return False


def check_collection_amount(collection_amount):
    """ Check that the collection_amount argument is a float and is
    above 0.00. If collection_amount is not a float and above 0.00,
    throw and error.

    :Args:
    collection_amount - A collection_amount argument provided by
        the post.payment() function
    """
    try:
        if float(collection_amount) >= 0.01:
            pass
        else:
            raise InvalidParameterError(
                'The collection amount must be positive. Zero or'
                ' non-negative amounts are not allowed.'
            )
    except:
        raise InvalidParameterError(
            'collection_amount must be a number.'
        )
