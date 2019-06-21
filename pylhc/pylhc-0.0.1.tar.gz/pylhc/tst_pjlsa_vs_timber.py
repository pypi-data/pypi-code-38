from datetime import datetime
import pjlsa
import pytz
import pytimber


tzone = pytz.timezone("Europe/Zurich")
tfmt = "%Y-%m-%d %H:%M:%S.%f"


def strtime(ts):
    """ Convert Timestamp to String """
    utc = datetime.utcfromtimestamp(ts)
    return utc.astimezone(tzone).strftime(tfmt)


if __name__ == '__main__':
    # get lsa data
    LSA = pjlsa.LSAClient()
    lsa_fills = LSA.findBeamProcessHistory(t1='2018-04-10 00:00:00.000000',
                                           t2='2018-04-11 05:00:00.000000',
                                           accelerator='lhc')

    # get timber data
    db = pytimber.LoggingDB()

    for fill in [6536, 6537]:
        timb = db.getLHCFillData(fill)

        # print data
        print(f"Fill {fill:d}")
        print("From pjlsa:")
        print(f"Start: {strtime(lsa_fills[fill][0][0])}")
        print(f"End:   {strtime(lsa_fills[fill][-1][0])}")
        print("")
        print("From pytimber:")
        print(f"Start: {strtime(timb['startTime'])}")
        print(f"End:   {strtime(timb['endTime'])}")
        print("")
        print("")
