import argparse

import channel_access.common as ca
import channel_access.client as cac



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read process values')
    parser.add_argument('pvs', metavar='PV', type=str, nargs='+',
                        help='list of process values')
    args = parser.parse_args()

    with cac.Client() as client:
        # Create list of PVs. They automatically connect in the background.
        # We don't need monitoring or automatic retreival of data.
        pvs = [ client.createPV(name, monitor=False, initialize=cac.InitData.NONE) for name in args.pvs ]
        # Asynchronous requests are queued. In order for all background
        # request to be send we flush here so while waiting for the
        # first pvs to connected the others can also connect in the
        # background.
        client.flush()

        for pv in pvs:
            print(pv.name, end='\t')
            try:
                # Make sure the pvs is connected before calling other
                # functions, this can block for up to one second.
                pv.ensure_connected(timeout=1.0)
                # Retreive the value, this can block for up to
                # one second. This also retreives timestamp, status and severity
                if pv.get(block=1.0) is None:
                    raise RuntimeError('No value')
            except RuntimeError:
                # Something went wrong
                print('NOT FOUND')
            else:
                # We need access to multiple attributes whose values
                # should all be from the same request. For this we need
                # to access the data dictionary ourselfs. ``pv.data``
                # returns a copy of the data dictionary.
                # Using ``pv.timestamp`` and ``pv.value`` does not guarantee that
                # the timestamp belongs to the value.
                data = pv.data
                print("{timestamp}\t{value}".format(**data))
