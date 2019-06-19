from datetime import date, timedelta

def check(diary):
    dates_found = set()
    for dtrange in diary.expected:
        for dt in dtrange:
            if not dt in diary.entries:
                raise Exception('Missing entry {}'.format(dt))
            dates_found.add(dt)

    print('OK found {} days'.format(len(dates_found)))
