from pathlib import Path
from ..exceptions import InvalidParameterError
from .schedules import read_available_schedules_file
from ..exceptions import InvalidStartDateError
from ..settings import Settings as s
from datetime import datetime
from .working_days import check_working_days_in_future
from warnings import warn
import json

base_path = Path(__file__).parent
sandbox_schedules = (base_path / '../includes/sandbox.csv').resolve()
ecm3_schedules = (base_path / '../includes/ecm3.csv').resolve()


def check_schedule_name(schedule_name):
    """ Read a file containing all available schedules, and return an
    error if the selected schedule_name cannot be found in the file.

    :Args:
     schedule_name - A schedule_name provided by the post.contract()
        function
    """
    schedules = read_available_schedules_file()

    schedule_names = []
    for name in schedules['schedule']:
        schedule_names.append(name['name'].lower())

    if schedule_name.lower() not in schedule_names:
            raise InvalidParameterError(
                '%s is not a valid schedule. The schedules available are as'
                ' follows: %s' % (schedule_name, schedule_names)
            )


def check_termination_type(termination_type):
    """ Check that the termination_type can be found in the approved
    list of termination_types, and if so, return a number to be used by
    other functions.

    :Args:
    termination type - A termination_type provided by the
        post.contract() function
    """
    termination_type_arguments = {
        'take certain number of debits': 0,
        'until further notice': 1,
        'end on exact date': 2,
    }

    if str(termination_type.lower()) not in termination_type_arguments:
        raise InvalidParameterError(
            '%s is not a valid termination type. Please check the termination'
            ' type and re-submit. The available termination types are: \n'
            '- Take certain number of debits\n'
            '- Until further notice\n'
            '- End on exact date' % termination_type
        )
    else:
        return termination_type_arguments[termination_type.lower()]


def check_at_the_end(at_the_end):
    """ Check that the at_the_end argument can be found in the approved
    list of at_the_end arguments, and if so, return a number to be used
    by other functions.

    :Args:
    at_the_end - An at_the_end argument provided by the post.contract()
        function
    """
    at_the_end_arguments = {
        'expire': 0,
        'switch to further notice': 1,
    }

    if str(at_the_end).lower() not in at_the_end_arguments:
        raise InvalidParameterError(
            '%s is not a valid argument for at_the_end. Please check the'
            ' argument re-submit. The available arguments are: \n'
            '- Expire\n'
            '- Switch to further notice\n'
            '- End on exact date' % at_the_end
        )
    else:
        return at_the_end_arguments[at_the_end.lower()]


def check_payment_day_in_week(payment_day_in_week):
    """ Check that the payment_day_in_week argument can be found in the
    set of payment_day_in_week arguments, and throw an error if it
    cannot be found.

    :Args:
    payment_day_in_week - A payment_day_in_week argument provided by the
        post.contract() function
    """
    payment_day_in_week_arguments = [
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
    ]
    if str(payment_day_in_week).lower() not in payment_day_in_week_arguments:
        raise InvalidParameterError(
            '%s is not a valid payment day in week. Please check the payment'
            ' day in week and re-submit. The available arguments are: \n'
            '- monday\n'
            '- tuesday\n'
            '- wednesday\n'
            '- thursday\n'
            '- friday' % payment_day_in_week
        )
    else:
        pass


def check_payment_day_in_month(payment_day_in_month):
    """ Check that the payment_day_in_month argument can be found in the
    set of payment_day_in_month arguments, and throw an error if it
    cannot be found.

    :Args:
    payment_day_in_month - A payment_day_in_month argument provided by
        the post.contract() function
    """
    try:
        if int(payment_day_in_month) not in range(1, 28) \
                and str(payment_day_in_month).lower() != 'last day of month':
            raise InvalidParameterError(
                '%s is not a valid payment day in month. Please check the'
                ' payment day in month and re-submit. The available arguments'
                ' are: \n'
                '- 1\n'
                '- 2\n'
                '- ...\n'
                '- 28\n'
                '- last day of month' % payment_day_in_month
            )
        else:
            pass
    except ValueError:
        raise InvalidParameterError(
            'payment_day_in_month must be an integer.'
        )

def check_payment_month_in_year(payment_month_in_year):
    """ Check that the payment_day_in_year argument can be found in the
    set of payment_day_in_year arguments, and throw an error if it
    cannot be found.

    :Args:
    payment_day_in_year - A payment_day_in_year argument provided by
        the post.contract() function
    """
    if int(payment_month_in_year) not in range(1, 12):
        raise InvalidParameterError(
            '%s is not a valid payment month in year. Please check the payment'
            ' month in year and re-submit. The available arguments are: \n'
            '- 1\n'
            '- 2\n'
            '- 3\n'
            '- ...\n'
            '- 12' % payment_month_in_year
        )
    else:
        pass


def check_number_of_debits(number_of_debits):
    """ Check that the number_of_debits argument is an integer and is
    between 1 and 99. If number_of_debits is not an integer between 1
    and 99, throw and error.

    :Args:
    number_of_debits - A number_of_debits argument provided by
        the post.contract() function
    """
    try:
        number = int(number_of_debits)
        if number < 0 or number > 99:
            raise InvalidParameterError(
                'number_of_debits cannot be lower than 1 or greater than'
                '99.'
            )
        else:
            pass
    except TypeError:
        raise InvalidParameterError(
            'number_of_debits must be a positive integer between 1 and 99.'
        )


def check_start_date(start_date):
    """ Check that the start_date argument is a valid ISO date and is
    at least x working days in the future, where x is the pre-determined
    bacs_processing_days setting. Throw an error if this is not the
    case.

    :Args:
    start_date - A start_date argument provided by the post.contract()
        function
    """
    date_format = '%Y-%m-%d'
    start = datetime.strptime(start_date, date_format).date()
    initial_days_in_future = s.direct_debit_processing_days['initial']
    first_date = check_working_days_in_future(initial_days_in_future)

    if start < first_date:
        if s.contracts['auto_start_date']:
            warn(
                '%s is not a valid start date. The earliest start date '
                'available is %s. This date has automatically been'
                ' selected.'
                % (start_date, first_date)
            )
            return str(first_date)
        raise InvalidStartDateError(
            '%s is not a valid start date. The earliest start date available'
            ' is %s. Please change this and re-submit.'
            % (start_date, first_date)
        )
    else:
        pass


def check_termination_date_is_in_future(termination_date, start_date):
    """ Check that the termination_date argument is a valid ISO date and is
    in the future relative to the start_date. Throw an error if this is not
    the case.

    :Args:
    termination_date - A termination_date argument provided by the
        post.contract() function
    start_date - A start_date argument provided by the post.contract()
        function
    """
    date_format = '%Y-%m-%d'
    start = datetime.strptime(start_date, date_format).date()
    termination = datetime.strptime(termination_date, date_format).date()

    if termination < start:
        raise InvalidParameterError(
            '%s is not a valid termination date. The termination date must be'
            'in the future. The given start date is %s'
            % (termination_date, start_date)
        )
    else:
        return True


def ad_hoc_checker(schedule):
    """ Check the status of a schedule by reading the JSON found in
        the includes folder, and whether or not it is ad-hoc. If it is
        ad-hoc, return True, if not, return False.

    :Args:
    schedule - A schedule_name argument provided by the post.contract()
        function
    """
    schedule_type = None
    if s.current_environment['env'] == 'sandbox':
        schedules_json = sandbox_schedules
    else:
        schedules_json = ecm3_schedules

    with open(schedules_json, 'r') as f:
        data = json.load(f)
        for i in data['schedule']:
            if schedule == i['name']:
                schedule_type = i['ad_hoc']
        if not schedule_type:
            return False
        elif schedule_type:
            return True
        else:
            raise InvalidParameterError(
                'Could not find the schedule.'
            )


def payment_time_frame_checker(schedule):
    """ Check the frequency of a schedule by reading the JSON found in
        the includes folder. Return a number depending on the frequency
        used in other functions for validation.

    :Args:
    schedule - A schedule_name argument provided by the post.contract()
        function
    """
    payment_type = None
    if s.current_environment['env'] == 'sandbox':
        schedules_json = sandbox_schedules
    else:
        schedules_json = ecm3_schedules
    with open(schedules_json, 'r') as f:
        data = json.load(f)
        for i in data['schedule']:
            if schedule == i['name']:
                payment_type = i['frequency']
        if payment_type == 'Weekly':
            return 0
        elif payment_type == 'Monthly':
            return 1
        elif payment_type == 'Annually':
            return 2
        else:
            raise InvalidParameterError(
                'Could not find the schedule.'
            )
