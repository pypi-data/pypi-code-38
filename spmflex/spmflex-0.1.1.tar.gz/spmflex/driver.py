"""
A Python driver for Honeywell's SPM Flex gas detector, using HTTP SOAP.

Distributed under the GNU General Public License v2
Copyright (C) 2019 NuMat Technologies
"""
import aiohttp
import xmltodict


class GasDetector(object):
    """Python driver for Honeywell SPM Flex Gas Detectors.

    This driver uses undocumented HTTP endpoints that are available through the
    Ethernet setting. This is much simpler than working with the Modbus
    TCP interface.
    """

    def __init__(self, address, timeout=0.5):
        """Save the IP address of the device."""
        if not address.startswith('http://'):
            address = 'http://' + address
        if not address.endswith('/'):
            address += '/'
        self.address = address
        self.session = None
        self.timeout = timeout

    async def __aenter__(self):
        """Support `async with` by entering a client session."""
        self.session = aiohttp.ClientSession(read_timeout=self.timeout)
        return self

    async def __aexit__(self, *err):
        """Support `async with` by exiting a client session."""
        await self.close()

    async def close(self):
        """Close the underlying session, if it exists."""
        if self.session is not None:
            await self.session.close()
            self.session = None

    async def get(self, raw=False):
        """Get current state from the SPM Flex gas detector.

        Args:
            raw: If True, returns all avaiable output
        Returns:
            Dictionary of sensor variables
        """
        if self.session is None:
            self.session = aiohttp.ClientSession(read_timeout=self.timeout)
        endpoint = self.address + 'dyn/ContinuingStatus'
        async with self.session.get(endpoint) as response:
            if response.status > 200:
                return {'ip': self.address, 'connected': False}
            xml = await response.read()
        status = xmltodict.parse(xml)['ContinuingStatus']
        if raw:
            return status
        return {
            'ip': self.address,
            'connected': True,
            'concentration': float(status['Concentration']),
            'units': status['Units'],
            'flow': int(status['Flow'].rstrip('cc/min')),
            'gas': status['GasName'],
            'id': status['UnitID'].lstrip('Unit ID: '),
            'low-alarm threshold': float(status['Alarm1Setpoint']),
            'high-alarm threshold': float(status['Alarm2Setpoint']),
            'temperature': int(status['AmbientTemp'].rstrip('C')),
            'life': float(status['CCDaysRemaining'].split(' ')[-1]),
            'fault': 'Fault' if status['FaultDetails'] else 'No fault'
        }
