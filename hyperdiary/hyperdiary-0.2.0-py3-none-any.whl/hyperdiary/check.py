from datetime import date, timedelta

def check(diary):
    current = date(2016,1,5)
    today = date.today()
    one_day = timedelta(days=1)

    number_of_days = 0
    while current < today:
        if not current in diary.entries:
            raise Exception('Missing entry {}'.format(current))
        current += one_day
        number_of_days += 1

    print('OK found {} days'.format(number_of_days))
