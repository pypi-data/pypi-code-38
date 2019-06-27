import time as _time
from datetime import *
import tijd
from errors import *
import sys
t = datetime.today()
import time as _time

def time_zone():
        LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo
        timez_zone = str(LOCAL_TIMEZONE)
        return timez_zone
def time_and_date_now(waarde):
    now = datetime.now()
    
    if waarde.upper() == 'TONEN_TIJD':
        print("de tijd en datum nu is :", end=' ')
        print(now.strftime("%Y-%m-%d %H:%M:%S"), end=' en de tijd in sec sinds 1970 is: ')
        print(_time.time())
        RETURN = str(now.strftime("%Y-%m-%d %H:%M:%S")) + ' tijd sinds 1970: ' + str(_time.time())
        return RETURN
    elif waarde.upper() == 'TONEN_NU':
        print("de tijd en datum nu is :", end=' ')
        print(now.strftime("%Y-%m-%d %H:%M:%S"))
        return now.strftime("%Y-%m-%Y %H:%M:%S")
    elif waarde.upper() == 'RETURN_TIJD':
        RETURN = str(now.strftime("%Y-%m-%d %H:%M:%S")) + ' tijd sinds 1970: ' + str(_time.time())
        return RETURN
        
    elif waarde.upper() == 'RETURN_NU':
        return [int(now.strftime("%Y")), int(now.strftime("%m")), int(now.strftime("%d")), int(now.strftime("%H")), int(now.strftime("%M")), int(now.strftime("%S"))]
    else:
        print('ongeldig commando')


def month(ma ,taal):
    now = datetime.now()
    nummer = now.strftime('%m')
    nummer = int(nummer)
    nummer = nummer - 1 #omdat python begint bij lijsten het tellen vanaf 0 inplaats van 1 en het is dan niet 1 tm 12 maar 0 tm 11
    RETURN = True
    if ma.lower() == 'nu': man = True
    else: man = False
    if taal.upper() == 'NL_AF': # NL_AF is een afkorting van NEDERLANDSE_AFKORTINGEN
        maanden = ['jan', 'feb', 'ma', 'ap', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec']
    elif taal.upper() == 'NL':
        maanden = ['januari', 'februarie', 'maaart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december']
    elif taal.upper() == 'FR':
        maanden = ['Janvier', 'Février', 'Mars', 'Avril', 'mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Décembre']
    elif taal.upper() == 'FR_AF': #FR_AF is een afkorting van FRANSE_AFKORTINGEN
        maanden = ['Janvier', 'Fév', 'Mar', 'Avr', 'mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Déc']
    elif taal.upper() == 'ENG':
        maanden = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    elif taal.upper() == 'ENG_AF':
        maanden = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    else:
        RETURN = False
        raise AttributeError('Wrong argument given')
    if RETURN == True:
        if man == True:
            return maanden[nummer]
        else:
            return maanden
    



def day_today():
    print('counting from 1970')
    tijd = _time.time()
    tijd = tijd / 60
    tijd = tijd / 60
    tijd = tijd / 24
    tijd = int(tijd)
    
    return tijd
def day_today_year():
    
    tijd = _time.time()
    tijd = tijd / 60
    tijd = tijd / 60
    tijd = tijd / 24
    tijd = int(tijd)
    times = int(tijd / 365)
    min_ = times * 365
    schrik = int(times / 4)
    schrik = schrik - 1# omdat het jaar 2000 geen schrikkel jaar was
    tijd = tijd - (min_ + schrik)
    return tijd
def day(taal):
    taal = taal.lower()
    if taal == 'eng':
        wochentag = ["Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday"]
    elif taal == 'nl':
        wochentag = ["maandag", "dinsdag", "woensdag",
                "donderdag", "vrijdag", "zaterdag", "zondag"]
    
    elif taal == 'fr':
        wochentag = ["lundi", "mardi", "mercredi",
                "jeudi", "vendredi", "samedi", "dimanche"]

    elif taal == 'de':
        wochentag = ["Montag", "Dienstag", "Mittwoch",
                "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    else:
        wochentag = ["error", "error", "error",
                "error", "error", "error", "error"]
    
    return wochentag[t.weekday()]
def days(taal):
    taal = taal.lower()
    if taal == 'eng':
        wochentag = ["Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday"]
    elif taal == 'nl':
        wochentag = ["maandag", "dinsdag", "woensdag",
                "donderdag", "vrijdag", "zaterdag", "zondag"]
    
    elif taal == 'fr':
        wochentag = ["lundi", "mardi", "mercredi",
                "jeudi", "vendredi", "samedi", "dimanche"]

    elif taal == 'de':
        wochentag = ["Montag", "Dienstag", "Mittwoch",
                "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    else:
        wochentag = ["error", "error", "error",
                "error", "error", "error", "error"]
    
    return wochentag
def day_to(dag):
    var = tijd.dagen_tot(dag)
    return var
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
    tijd_gmt = _time.strftime("%H:%M:%S(gmt)", _time.gmtime())
    tijd_local = strftime("%H:%M:%S")
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
def days_local():
    from time import gmtime, strftime
    import time as _time
    tijd_gmt = _time.strftime("%d/%m/%Y")
    tijd_local = strftime("%d/%m/%Y")
    tijd_int_local = [int(strftime("%d")), int(strftime("%m")), int(strftime("%Y"))]
    tijd_int_gmt = [int(_time.strftime("%d", _time.gmtime())), int(_time.strftime("%m", _time.gmtime())), int(_time.strftime("%Y", _time.gmtime()))]
    return [tijd_local, tijd_int_local]
def times_local():
    from time import gmtime, strftime
    import time as _time
    tijd_gmt = _time.strftime("%H:%M:%S(gmt)", _time.gmtime())
    tijd_local = strftime("%H:%M:%S")
    tijd_int_local = [int(strftime("%H")), int(strftime("%M")), int(strftime("%S"))]
    tijd_int_gmt = [int(_time.strftime("%H", _time.gmtime())), int(_time.strftime("%M", _time.gmtime())), int(_time.strftime("%S", _time.gmtime()))]
    return [tijd_local, tijd_int_local]
def times_local_pam():
    ret = []
    ret.append(times_pam()[2])
    ret.append(times_pam()[3])
    return ret
def times_and_days_local():
    from time import gmtime, strftime
    import time as _time
    tijd_gmt = _time.strftime("%d/%m/%Y  %H:%M:%S %Z(gmt)", _time.gmtime())
    tijd_local = strftime("%d/%m/%Y  %H:%M:%S %Z")
    tijd_int_local = [int(strftime("%d")), int(strftime("%m")), int(strftime("%Y")), int(strftime("%H")), int(strftime("%M")), int(strftime("%S"))]
    tijd_int_gmt = [int(_time.strftime("%d", _time.gmtime())), int(_time.strftime("%m", _time.gmtime())), int(_time.strftime("%Y", _time.gmtime())), int(_time.strftime("%H", _time.gmtime())), int(_time.strftime("%M", _time.gmtime())), int(_time.strftime("%S", _time.gmtime()))]
    return [tijd_local, tijd_int_local]
def info():
        '''
tijd_en_datum_nu(value) = command to retutn or print

tijd_zone() = returns your time zone
times_and_days_pam(): returns the date and time of gmt and local
times_and_days() = returns date and time  of gmt and local in 0 to 24 not in pm or am
times_pam() = returns the time gmt and local in pm or am
times() = returns the time gmt and local not in pm or am
days() = returns the day in gmt and in local
'''
def loop():
    pass
if __name__ == '__main__':
    try:
        print(time_zone())
        work = True
    except Exception as ex:
        print_warn(str(ex))
        work = False
        pass
    if work == True:
        print('func time_zone() state: working.\nmodule importable: True\n')

    
    

