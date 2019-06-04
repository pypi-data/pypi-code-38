from pathlib import Path
from datetime import datetime
from ..settings import Settings as s
from datetime import timedelta
from requests import get


base_path = Path(__file__).parent
bank_holidays_file = (base_path / '../includes/holidays.csv').resolve()


def check_working_days_in_future(number_of_days):
    """ Take X number of working days, and calculate the number of
    working days X is in the future from today. Call
    read_bank_holiday_file_and_check_if_update_needed() to get a list
    of bank holidays.

    :Args:
    number_of_days - The number of days in the future X is
    """
    holidays = read_bank_holiday_file_and_check_if_update_needed()
    working_days = 0
    calendar_days = 0
    today_datetime = datetime.now()
    today_date = today_datetime.date()
    # We want to keep today_date constant for raising errors
    start_date = today_date

    # Check if today is a weekday, if it is not, go to next weekday
    if today_date.isoweekday() == 6 or today_date.isoweekday() == 7 or \
            str(today_date) in holidays:
        # Should never need 10 iterations. We want the next working day
        for i in range(10):
            iter_date = today_date + timedelta(i)
            if iter_date.isoweekday() in range(1, 5) \
                    and str(iter_date) not in holidays:
                start_date += timedelta(i)
                break

    while working_days <= (number_of_days - 1):
        working_date = start_date + timedelta(calendar_days)
        if working_date.isoweekday() != 6 and working_date.isoweekday() != 7 \
                and str(working_date) not in holidays:
            working_days += 1
        calendar_days += 1
    final_date = start_date + timedelta(calendar_days)

    while final_date.isoweekday() == 6 or final_date.isoweekday() == 7 \
            or str(final_date) in holidays:
        final_date += timedelta(1)
        calendar_days += 1
    return final_date


def read_bank_holiday_file_and_check_if_update_needed():
    """ Read the bank holidays file and return a list of all bank
    bank holidays for the current year. If the file has not been updated
    in the pre_determined number of days in the settings file, read
    the bank_holidays.json file and get a list of all bank holidays in
    the current year or later.
    """
    # We need the datetime to access the year element
    today_datetime = datetime.now()
    today_date = today_datetime.date()
    holidays = []
    with open(bank_holidays_file, 'a+') as f:
        f.seek(0)
        try:
            # Check the first line of the file to check last update
            text_date = f.readline().strip('\n')

            # The file stores the date as a string. We need a Date object
            date_formatting = '%Y-%m-%d'
            last_update_date = datetime.strptime(
                text_date, date_formatting
            ).date()
            date_difference = today_date - last_update_date
            day_difference = date_difference.days

            if day_difference >= s.other['bank_holidays_update_days']:
                print(
                    'The bank holidays file has not been updated in over %s'
                    ' days. Updating......' % day_difference
                )
                new_holidays = get('https://www.gov.uk/bank-holidays.json')
                holidays_json = new_holidays.json()['england-and-wales'] \
                    ['events']

                for date in holidays_json:
                    # Add  bank holidays from or after the current year
                    if int(date['date'][0:4]) >= today_datetime.year:
                        holidays.append(date['date'])
                    else:
                        continue
                    update_bank_holidays_file(holidays)
            else:
                for line in f:
                    holidays.append(line.strip('\n'))

            return holidays
        except:
            new_holidays = get('https://www.gov.uk/bank-holidays.json')
            holidays_json = new_holidays.json()['england-and-wales']['events']

            for date in holidays_json:
                # Add  bank holidays from or after the current year
                if int(date['date'][0:4]) >= today_datetime.year:
                    holidays.append(date['date'])
                else:
                    continue
                update_bank_holidays_file(holidays)
        return holidays


def update_bank_holidays_file(bank_holiday_list):
    """ Write the bank_holiday_list to the bank_holidays.csv file,
    prepending it with todays date, which will be used for updating the
    file in the future.

    :Args:
    number_of_days - The number of days in the future X is
    """
    with open(bank_holidays_file, 'w') as f:
        # Update the header
        f.write(str(datetime.now().date()))
        for date in bank_holiday_list:
            f.write('\n%s' % date)
    return 'Updated bank holidays file.'
