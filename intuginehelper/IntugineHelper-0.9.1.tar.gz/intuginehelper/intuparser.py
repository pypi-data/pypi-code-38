from datetime import datetime

time_fmt = "%Y-%m-%dT%H:%M:%S.%fz"


def get_createdAt(trip):
    """
    :param trip: trip Object
    :return: createdAt datetime object
    """
    time = trip['createdAt']
    if isinstance(time, str):
        time = datetime.strptime(time, time_fmt)
    return time


def get_startTime(trip):
    """
    :param trip: trip Object
    :return: startTime if startTime exists else createdAt datetime object
    """
    if 'startTime' in trip.keys():
        time = trip['startTime']
        if isinstance(time, str):
            time = datetime.strptime(time, time_fmt)
        return time
    else:
        return get_createdAt(trip)


def get_endTime(trip):
    """
    Return the time when trip is ended
    :param trip: Object
    :return: datetime object for trip end Time
    """
    if not get_running(trip):
        trip_keys = trip.keys()
        if 'endTime' in trip_keys:
            end = trip['endTime']
        elif 'end_time' in trip_keys:
            end = trip['end_time']
        elif 'forcedEndTime' in trip_keys:
            end = trip['forcedEndTime']
        else:
            raise Exception('ERR = Parameter for End Time is not defined')
    else:
        end = datetime.now()
    return end


def get_eta_days(trip):
    """
    Returns the Eta Days of the trip
    :param trip: Object
    :return: eta_days of the trip
    """
    if 'eta_days' in trip.keys():
        eta_days = trip['eta_days']
        eta_days = str(eta_days) or eta_days  # to remove that None shit in the eta_days
        try:
            return float(eta_days)
        except ValueError as e:
            # print("ERR {0} {1} in {2}".format(e, 'eta_days', trip['_id']))
            return None
    else:
        # print("ERR No {0} in {1}".format('eta_days', trip['_id']))
        return None


def get_eta_hrs(trip):
    """
    Returns the Eta Hours of the trip if present as eta_days * 24
    :param trip: Object
    :return: eta_hrs of the trip
    """
    eta_days = get_eta_days(trip)
    if eta_days is None:
        if 'eta_hrs' in trip.keys():
            eta_hrs = str(trip['eta_hrs']) or trip['eta_hrs']  # to remove that None shit in the eta_hrs
            try:
                return float(eta_hrs)
            except Exception as e:
                print("ERR {} For Trip {}".format(e, trip['_id']))
    if eta_days is not None:
        return eta_days * 24
    else:
        try:
            return trip['base_google_time'] / 3600
        except KeyError as e:
            print(e)
            return -1


def get_ping_rate(trip):
    """
    :param trip: Trip Object
    :return: ping rate in milliseconds if 'pingrate' exists in trip else 3600000 as default
    """
    if 'pingrate' in trip.keys():
        return int(trip['pingrate'])
    else:
        return 3600000


def get_source(trip):
    """
    Return the source name for the trip
    :param trip: trip Object
    :return: string containing source name
    """
    if 'srcname' in trip.keys():
        return trip['srcname']
    if 'src' in trip.keys():
        if isinstance(trip['src'], list):
            return trip['src'][0]
        elif isinstance(trip['src'], str):
            return trip['src']
        else:
            return ''
    else:
        return ''


def get_destination(trip):
    """
    Return the Destination name for the trip
    :param trip: trip Object
    :return: string containing Destination name
    """
    destination = ''
    if 'destname' in trip.keys():
        destination = trip['destname']
    if destination == '':
        try:
            destination = trip['dest']
        except KeyError as e:
            destination = ''
    return destination


def get_operator(trip):
    """
    Return the operator name for the trip
    :param trip: Object
    :return: operator name
    """
    operator = ''
    try:
        if 'consent' in trip.keys():
            if 'result' in trip['consent']:
                if 'operator' in trip['consent']['result']:
                    operator = trip['consent']['result']['operator']
    except Exception as e:
        operator = ''
        print(e)
    return operator


def get_truck_number(trip):
    """
    Return the Truck number
    :param trip: Object
    :return: string containing truck number
    """
    truck_number = ''
    if 'truck_number' in trip.keys():
        truck_number = trip['truck_number']
    if truck_number == '':
        try:
            truck_number = trip['vehicle']
        except KeyError as e:
            truck_number = ''
    return truck_number


def get_running(trip):
    """
    Return True if trip is running else False
    :param trip: Object
    :return: trip['running']
    """
    return trip['running']


def get_invoice(trip):
    """
    Returns the invoice of the trip
    :param trip: Object
    :return: String containing invoice
    """
    invoice = ''
    if 'invoice' in trip.keys():
        invoice = trip['invoice']
    if invoice == '' and 'jobs' in trip.keys():
        try:
            invoice = trip['jobs']
        except KeyError as e:
            invoice = ''
    else:
        invoice = ''
    return invoice


def get_telephone(trip):
    """
    Returns the telephone number
    :param trip: Object
    :return: string containing telephone number
    """
    tel = trip['tel']
    if isinstance(tel, list):
        tel = tel[0]
    return tel
