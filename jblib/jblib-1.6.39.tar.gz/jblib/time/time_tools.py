import datetime

def build_date_array(days=1, start_date=str(datetime.date.today()), date_format='%Y-%m-%d', mon=True, tues=True, wed=True, thur=True, fri=True, sat=True, sun=True, weekend=True):
    dates = []
    
    start_date = datetime.datetime.strptime(start_date, date_format)
    
    start_year = int(start_date.strftime('%Y'))
    start_month = int(start_date.strftime('%m'))
    start_day = int(start_date.strftime('%d'))
    date = datetime.date(start_year, start_month, start_day)
    
    counter = 0
    
    if not weekend:
        sat = False
        sun = False
    
    while len(dates) < days:
        start_year = int(date.strftime('%Y'))
        start_month = int(date.strftime('%m'))
        start_day = int(date.strftime('%d'))
        #date = datetime.date(start_year, start_month, start_day) + datetime.timedelta(days=counter)
    
        ### Return the day of the week as an integer, where Monday is 0 and Sunday is 6
        day_of_the_week = datetime.date(start_year, start_month, start_day).weekday()

        if mon == True and day_of_the_week == 0:
            dates.append(date.strftime('%Y-%m-%d'))
        if tues == True and day_of_the_week == 1:
            dates.append(date.strftime('%Y-%m-%d'))
        if wed == True and day_of_the_week == 2:
            dates.append(date.strftime('%Y-%m-%d'))
        if thur == True and day_of_the_week == 3:
            dates.append(date.strftime('%Y-%m-%d'))
        if fri == True and day_of_the_week == 4:
            dates.append(date.strftime('%Y-%m-%d'))
        if sat == True and day_of_the_week == 5:
            dates.append(date.strftime('%Y-%m-%d'))
        if sun == True and day_of_the_week == 6:
            dates.append(date.strftime('%Y-%m-%d'))
            
        counter += 1
        
        date = datetime.date(start_year, start_month, start_day) + datetime.timedelta(days=1)
    
    return dates