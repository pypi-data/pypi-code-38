from time import *

import datetime as _datetime
def fil(x):
    if x == str:
        return True
    else:
        return False
def tijd_zone():
        LOCAL_TIMEZONE = _datetime.datetime.now(_datetime.timezone.utc).astimezone().tzinfo
        LOCAL_TIMEZONE = str(LOCAL_TIMEZONE)
        return LOCAL_TIMEZONE
def chek(a):
        b = time()
        c = b - a
        return c
def now(value):
    
    now = _datetime.datetime.now()
    if waarde.lower() == 'tonen' or 'print':
        print ("de tijd en datum nu is :")
        print (now.strftime("%Y-%m-%d %H:%M:%S"))
        return now.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return now.strftime("%Y-%m-%d %H:%M:%S")
def days_over_this_year(RETURN):
        tijd = time()
        tijd = tijd / 60
        tijd = tijd / 60
        tijd = tijd / 24
        tijd = int(tijd)
        jaren = int(tijd / 365)
        dagen = jaren * 365
        schrik = int(jaren / 4)
        
        tijd = tijd - (dagen + schrik - 1)#omdat het jaar 2000 geen schrikkeljaar was
        if not RETURN.upper() == 'RETURN':
                print(tijd)
        else:
                return tijd


def time_now(uur, minuten, sec):
        now = _datetime.datetime.now()
        nu = ''
        if sec.lower() == 'ja' or 'yes':
                nu = nu +now.strftime('%H')
        if sec.lower() and minuten.lower() or sec.lower() and uur.lower() == 'ja' or 'yes':
                nu = nu + ':'
        if minuten.lower() == 'ja' or 'yes':
                nu = nu + now.strftime('%M')
        if minuten.lower() and uur.lower() == 'ja' or 'yes':
                nu = nu + ':'
        if uur.lower() == 'ja' or 'yes':
                nu = nu + now.strftime('%S')
        return nu
def days_until(dag):
        jaar = 0
        dag = str(dag)
        if dag.lower() == 'nieuw jaar':
                output = 365 - dagen_voorbij_in_dit_jaar('return')
        dag = int(dag)
        if dag >= 365:
                while dag >= 365:
                        jaar = jaar + 1
        else:
                
                output = dag - dagen_voorbij_in_dit_jaar('RETURN')
        if output < 0:
                o = 365 - dagen_voorbij_in_dit_jaar('return')
                no = dag
                output = o + no
        if jaar > 0:
                return [jaar, output]
        elif jaar == 0:
                return output
        else:
                class TimeException(Exception):
                    pass
                raise TimeException('bad date. given data already been')
def loading_c(duur, command):
        a = time()
        
        while chek(a) < duur:
            print('|', end='')
            sleep(0.1)
        print(end='\n')
def loading(duur):
        a = time()
        while chek(a) < duur:
                print('|', end='')
                sleep(0.1)
        print(end='\n')
def times_and_days_pam():
    from time import gmtime, strftime
    import time as _time
    tijd_gmt = _time.strftime("%a, %d %b %Y %I:%M:%S %p %Z", _time.gmtime())
    tijd_local = strftime("%a, %d %b %Y %I:%M:%S %p %Z\n")
    tijd_int_local = [int(strftime("%d")), int(strftime("%m")), int(strftime("%Y")), int(strftime("%H")), int(strftime("%M")), int(strftime("%S"))]
    tijd_int_gmt = [int(_time.strftime("%d", _time.gmtime())), int(_time.strftime("%m", _time.gmtime())), int(_time.strftime("%Y", _time.gmtime())), int(_time.strftime("%H", _time.gmtime())), int(_time.strftime("%M", _time.gmtime())), int(_time.strftime("%S", _time.gmtime()))]

    return [tijd_gmt, tijd_int_gmt, tijd_local, tijd_int_local]
def times_pam():
    from time import gmtime, strftime
    import time as _time
    tijd_gmt = _time.strftime("%I:%M:%S %p %Z", _time.gmtime())
    tijd_local = strftime("%I:%M:%S %p %Z")
    tijd_int_local = [int(strftime("%d")), int(strftime("%m")), int(strftime("%Y")), int(strftime("%H")), int(strftime("%M")), int(strftime("%S"))]
    tijd_int_gmt = [int(_time.strftime("%d", _time.gmtime())), int(_time.strftime("%m", _time.gmtime())), int(_time.strftime("%Y", _time.gmtime())), int(_time.strftime("%H", _time.gmtime())), int(_time.strftime("%M", _time.gmtime())), int(_time.strftime("%S", _time.gmtime()))]

    return [tijd_gmt, tijd_int_gmt, tijd_local, tijd_int_local]
def times():
    from time import gmtime, strftime
    import time as _time
    tijd_gmt = _time.strftime("%H:%M:%S %Z(gmt)", _time.gmtime())
    tijd_local = strftime("%H:%M:%S %Z")
    tijd_int_local = [int(strftime("%H")), int(strftime("%M")), int(strftime("%S"))]
    tijd_int_gmt = [int(_time.strftime("%H", _time.gmtime())), int(_time.strftime("%M", _time.gmtime())), int(_time.strftime("%S", _time.gmtime()))]
    return [tijd_gmt, tijd_int_gmt, tijd_local, tijd_int_local]
def times_and_days():
    from time import gmtime, strftime
    import time as _time
    tijd_gmt = _time.strftime("%d/%m/%Y  %H:%M:%S %Z(gmt)", _time.gmtime())
    tijd_local = strftime("%d/%m/%Y  %H:%M:%S %Z")
    tijd_int_local = [int(strftime("%d")), int(strftime("%m")), int(strftime("%Y")), int(strftime("%H")), int(strftime("%M")), int(strftime("%S"))]
    tijd_int_gmt = [int(_time.strftime("%d", _time.gmtime())), int(_time.strftime("%m", _time.gmtime())), int(_time.strftime("%Y", _time.gmtime())), int(_time.strftime("%H", _time.gmtime())), int(_time.strftime("%M", _time.gmtime())), int(_time.strftime("%S", _time.gmtime()))]
    return [tijd_gmt, tijd_int_gmt, tijd_local, tijd_int_local]
def days():
    from time import gmtime, strftime
    import time as _time
    tijd_gmt = _time.strftime("%d/%m/%Y")
    tijd_local = strftime("%d/%m/%Y")
    tijd_int_local = [int(strftime("%d")), int(strftime("%m")), int(strftime("%Y"))]
    tijd_int_gmt = [int(_time.strftime("%d", _time.gmtime())), int(_time.strftime("%m", _time.gmtime())), int(_time.strftime("%Y", _time.gmtime()))]
    return [tijd_gmt, tijd_int_gmt, tijd_local, tijd_int_local]
def info():
        '''chek(a) = chek the difference between the time at a and now for while loops that need to go for a time
dagen_voorbij_in_dit_jaar(return) = returns the days that are pass in this year if task not is return he prints it
tijd_nu(hour, min, sec) = returns the time now you say what you want
dagen_tot(dag) = looks how many days to one day in this or next year
nu(value) = prints and returns if value is print or tonen else he only returns
tijd_zone() = returns your time zone
times_and_days_pam(): returns the date and time of gmt and local
times_and_days() = returns date and time  of gmt and local in 0 to 24 not in pm or am
times_pam() = returns the time gmt and local in pm or am
times() = returns the time gmt and local not in pm or am
days() = returns the day in gmt and in local
'''
        return'''chek(a) = chek the difference between the time at a and now for while loops that need to go for a time
dagen_voorbij_in_dit_jaar(return) = returns the days that are pass in this year if task not is return he prints it
tijd_nu(hour, min, sec) = returns the time now you say what you want
dagen_tot(dag) = looks how many days to one day in this or next year
nu(value) = prints and returns if value is print or tonen else he only returns
tijd_zone() = returns your time zone
times_and_days_pam(): returns the date and time of gmt and local
times_and_days() = returns date and time  of gmt and local in 0 to 24 not in pm or am
times_pam() = returns the time gmt and local in pm or am
times() = returns the time gmt and local not in pm or am
days() = returns the day in gmt and in local
'''




