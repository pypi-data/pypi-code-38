update_ts_interval = 24 * 60 * 60       # 1 day


class CollectionNames():

    def __init__(self):
        self.battery_swap_log_b = 'battery_swap_log_b'
        self.battery_swap_log = 'battery_swap_log'
        self.vm_status_b = 'vm_status_b'
        self.vm_status = 'vm_status'


def get_battery_swap_log(start_ts, end_ts=0):
    global update_ts_interval
    if end_ts==0:
        return {
            'exchange_time': {
                '$gte': start_ts,
                '$lt': start_ts + update_ts_interval
            }
        }
    else:
        return {
            'exchange_time': {
                '$gte': start_ts,
                '$lt': end_ts
            }
        }

def get_vm_status(start_ts, end_ts=0):
    global update_ts_interval
    if end_ts==0:
        return {
            'snap_time': {
                '$gte': start_ts,
                '$lt': start_ts + update_ts_interval
            }
        }
    else:
        return {
            'snap_time': {
                '$gte': start_ts,
                '$lt': end_ts
            }
        }
