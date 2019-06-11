import datetime

def epoch2datetime(epochtime, epoch=datetime.datetime(1970,1,1)):
    '''
        Convert epoch time - seconds past since 1970 
        - to year, month, day, hour, minute, second
    '''
    return datetime.datetime.utcfromtimestamp(int(epochtime)).strftime('%Y %m %d %H %M %S').split(' ')

def epoch2dtimeformat(epochtime):
    '''
        convert epoch to 2019 04 16 10:59:20.619 format
    '''
    epoch,nanosecond        = str(epochtime).split('.')
    millisecond,_           = str(float(nanosecond) * (10**-6)).split('.')
    dtime   = epoch2datetime(epoch)
    return "".join((dtime[0],' ',dtime[1],' ',dtime[2],' ',dtime[3],':',dtime[4],':',dtime[5],'.',millisecond))