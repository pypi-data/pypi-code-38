import argparse
import time

import channel_access.common as ca
import channel_access.client as cac



def callback(pv, data):
    # ``data`` is a data dictionary with the received values. It does
    # not contain all values, e.g. in this example the first callback
    # receives the control values but the following callbacks only
    # receive the time values.
    # If it is not clear what values the callback receives it is safer
    # to access the pv attributes (e.g. pv.value).
    print(pv.name, data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Monitor process value')
    parser.add_argument('pv', metavar='PV', type=str, help='process value')
    args = parser.parse_args()

    try:
        with cac.Client() as client:
            # Create the PV. This automatically connects in the background
            # retreives the control values and monitors the PV for changes by
            # calling ``callback``.
            pv = client.createPV(args.pv, monitor=callback)
            while True:
                time.sleep(1.0)
    except KeyboardInterrupt:
        pass
