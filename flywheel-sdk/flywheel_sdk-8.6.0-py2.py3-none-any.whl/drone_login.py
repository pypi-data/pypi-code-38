"""Provides Drone-based login credentials"""
import requests
from .rest import ApiException
from .client import Client
from . import util

def create_drone_client(host, secret, method, name, port=443, **kwargs):
    """Create a Client instance using drone credentials.

    :param str host: The hostname of the flywheel instance
    :param str secret: The drone secret
    :param str method: The method (device type)
    :param str name: The name of the device
    :param int port: The optional port (if not 443)
    :param kwargs: Additional arguments to pass to the created Client instance
    :return: The authorized Client instance
    :rtype: flywheel.Client
    """
    with requests.Session() as session:
        util.set_verify_ssl(session)

        # Get auth status to determine device id
        base_uri = 'https://{}:{}/api'.format(host, port)

        session.headers.update({
            'X-SciTran-Auth': secret,
            'X-SciTran-Method': method,
            'X-SciTran-Name': name
        })

        # Get the status
        resp = session.get(base_uri + '/auth/status')
        if not resp.ok:
            raise ApiException(http_resp=resp)

        status = resp.json()
        if not status['is_device'] or not status.get('origin', {}).get('id'):
            raise RuntimeError('Provided login is not a device login')

        # Get the device, with API key
        device_id = status['origin']['id']
        resp = session.get(base_uri + '/devices/' + device_id)
        if not resp.ok:
            raise ApiException(http_resp=resp)

        device = resp.json()
        if 'key' not in device:
            raise RuntimeError('Got device, but could not get key!')

        api_key = '{}:{}:{}'.format(host, port, device['key'])

    return Client(api_key, **kwargs)
