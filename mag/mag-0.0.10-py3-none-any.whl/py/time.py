import datetime

def current_date(delim:str='-'):
    '''Returns day, month, and year as a string seperated by delim'''
    now = datetime.datetime.now()
    date = now.strftime('%d'+delim+'%m'+delim+'%Y')
    return date

def current_time(delim:str=':'):
    '''Returns hour and minute as a string seperated by delim'''
    now = datetime.datetime.now()
    time = now.strftime('%H'+delim+'%M')
    return time
