from .query import query
import numpy as np
import datetime
import pandas_light
import pandas_flavor as pf


def query_calendar():
    """Return the calendar info table.

    Returns:
        pd.DataFrame: Return as DataFrame.
    """

    sql = '''
SELECT Year(date)              AS year, 
       Month(date)             AS month, 
       Day(date)               AS day, 
       date,
       Date_format(date, '%a') AS weekday, 
       cycleday 
FROM   (SELECT Date(From_unixtime(date)) AS date, 
               name                      AS cycleday 
        FROM   calendar) AS t 
    '''
    df = query(sql)
    df['date'] = np.vectorize(datetime.date)(df['year'], df['month'], df['day'])
    return df


@pf.register_dataframe_method
def pycnet_vmap_cycleday(df, on='date'):
    """vmap cycleday on a date column in a DataFrame.

    Args:
        on (str, optional): The datetime.date column. Defaults to 'date'.
    """
    return df.vmap(query_calendar(), on=on, right_on='date', take='cycleday')


def newest_schyear():
    """Return the newest sch_year in the schooling table.

    Returns:
        int: The sch_year.
    """
    return query('select max(sch_year) as year from schooling').iloc[0][0]


def this_schyear():
    """Return current year is current month >= 9, otherwise, last year.

    Returns:
        int: The sch_year.
    """
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    return year if month >= 9 else year - 1


def now_datetime():
    """Return datetime now in PYC system as '2000-12-31 13:45:30' in string.
    """
    return query('select now() as now')['now'].iloc[0]

def now_date():
    """Return date now in PYC system as '2000-12-31' in string.
    """
    return query('select curdate() as now')['now'].iloc[0]

def now_time():
    """Return time now in PYC system as '13:45:30' in string.
    """
    return query('select curtime() as now')['now'].iloc[0]


def this_cycleday():
    """Return the cycleday of today.
    """
    c = query('''
SELECT *
FROM   (SELECT curdate() AS date) AS n 
       LEFT JOIN (SELECT Date(From_unixtime(date)) AS date, 
                         NAME                      AS cycleday 
                  FROM   calendar) AS c using (date) 
                  ''')['cycleday'].fillna('').iloc[0]
    if c == '':
        c = None
    return c


def this_lesson():
    """Return the lesson now (regular school day timetable).
    """
    q = query("select hhmm,date_format(now(),'%H%i')>hhmm as passed from sch_bell order by hhmm")
    try:
        passed = q['passed'].sum()
        lesson = [1, 1, 2, 2, 3, 4, 4, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6][passed]
    except:
        lesson = None
    return lesson
