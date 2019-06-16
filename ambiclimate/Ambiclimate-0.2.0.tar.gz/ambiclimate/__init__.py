
"""Library to handle connection with Ambiclimate API."""
import asyncio
import json
import logging
import time
from urllib.parse import urlencode

import aiohttp
import async_timeout

DEFAULT_TIMEOUT = 10
API_ENDPOINT = 'https://api.ambiclimate.com/api/v1/'

_LOGGER = logging.getLogger(__name__)


class AmbiclimateConnection:
    """Class to comunicate with the Ambiclimate api."""

    def __init__(self, oauth, token_info,
                 timeout=DEFAULT_TIMEOUT,
                 websession=None):
        """Initialize the Ambiclimate connection."""
        if websession is None:
            async def _create_session():
                return aiohttp.ClientSession()

            loop = asyncio.get_event_loop()
            self.websession = loop.run_until_complete(_create_session())
        else:
            self.websession = websession
        self._timeout = timeout
        self.oauth = oauth
        self.token_info = token_info
        self._devices = []

    async def request(self, command, params, retry=3, get=True):
        """Request data."""
        headers = {
            "Accept": "application/json",
            'Authorization': 'Bearer ' + self.token_info.get('access_token')
        }

        url = API_ENDPOINT + command
        try:
            with async_timeout.timeout(self._timeout):
                if get:
                    resp = await self.websession.get(url, headers=headers, params=params)
                else:
                    resp = await self.websession.post(url, headers=headers, json=params)
        except asyncio.TimeoutError:
            if retry < 1:
                _LOGGER.error("Timed out sending command to Ambiclimate: %s", command)
                return None
            return await self.request(command, params, retry - 1, get)
        except aiohttp.ClientError:
            _LOGGER.error("Error sending command to Ambiclimate: %s", command, exc_info=True)
            return None
        if resp.status != 200:
            _LOGGER.error(await resp.text())
            return None
        return await resp.text()

    def find_device_by_room_name(self, room_name):
        """Get device by room name."""
        for device in self._devices:
            if device.name == room_name:
                return device
        return None

    async def find_devices(self):
        """Get users Ambi Climate device information."""
        res = await self.request('devices', {})
        if not res:
            return False
        res = json.loads(res)
        self._devices = []
        for device in res.get('data', []):
            self._devices.append(AmbiclimateDevice(device.get('room_name'),
                                                   device.get('location_name'),
                                                   device.get('device_id'),
                                                   self))

        return bool(self._devices)

    def get_devices(self):
        """Get users Ambi Climate device information."""
        return self._devices

    async def refresh_access_token(self):
        """Refresh access token."""
        token_info = await self.oauth.refresh_access_token(self.token_info)
        if token_info is None:
            return None
        self.token_info = token_info
        return token_info


class AmbiclimateDevice:
    """Instance of Ambiclimate device."""
    # pylint: disable=too-many-public-methods

    def __init__(self, room_name, location_name, device_id, ambiclimate_control):
        """Initialize the Ambiclimate device class."""
        self._room_name = room_name
        self._location_name = location_name
        self._device_id = device_id
        self.control = ambiclimate_control
        self.ir_features = None
        self.ac_data = None
        self._mode = None

    @property
    def device_id(self):
        """Return a device ID."""
        return self._device_id

    @property
    def name(self):
        """Return a device name."""
        return self._room_name

    async def request(self, command, params, retry=3, get=True):
        """Request data."""
        if 'multiple' in params:
            params['multiple'] = 'True' if params['multiple'] else 'False'
        params['room_name'] = self._room_name
        params['location_name'] = self._location_name
        res = await self.control.request(command, params, retry, get)
        try:
            res = json.loads(res)
            if isinstance(res, dict) and res.get('error'):
                _LOGGER.error(res.get('error'))
            return res
        except TypeError:
            if isinstance(res, dict):
                status = res.get('status')
                if status is not None:
                    if status == 'ok':
                        return True
                    return False
        return None

    async def set_power_off(self, multiple=False):
        """Power off your AC."""
        return await self.request('device/power/off', {'multiple': multiple})

    async def set_comfort_mode(self, multiple=False):
        """Enable Comfort mode on your AC."""
        return await self.request('device/mode/comfort', {'multiple': multiple})

    async def set_comfort_feedback(self, value):
        """Send feedback for Comfort mode."""
        valid_comfort_feedback = ['too_hot', 'too_warm', 'bit_warm', 'comfortable',
                                  'bit_cold', 'too_cold', 'freezing']
        if value not in valid_comfort_feedback:
            _LOGGER.error("Invalid comfort feedback")
            return
        return await self.request('user/feedback', {'value': value})

    async def set_away_mode_temperature_lower(self, value, multiple=False):
        """Enable Away mode and set an lower bound for temperature."""
        return await self.request('device/mode/away_temperature_lower',
                                  {'multiple': multiple, 'value': value})

    async def set_away_mode_temperature_upper(self, value, multiple=False):
        """Enable Away mode and set an upper bound for temperature."""
        return await self.request('device/mode/away_temperature_upper',
                                  {'multiple': multiple, 'value': value})

    async def set_away_humidity_upper(self, value, multiple=False):
        """Enable Away mode and set an upper bound for humidity."""
        return await self.request('device/mode/away_humidity_upper',
                                  {'multiple': multiple, 'value': value})

    async def set_temperature_mode(self, value, multiple=False):
        """Enable Temperature mode on your AC."""
        return await self.request('device/mode/temperature',
                                  {'multiple': multiple, 'value': value})

    async def get_sensor_temperature(self):
        """Get latest sensor temperature data."""
        res = await self.request('device/sensor/temperature', {})
        if res is None:
            return None
        return res[0].get('value')

    async def get_sensor_humidity(self):
        """Get latest sensor humidity data."""
        res = await self.request('device/sensor/humidity', {})
        val = res[0].get('value')
        if val is None:
            return None
        return round(val, 1)

    async def get_mode(self):
        """Get Ambi Climate's current working mode."""
        res = await self.request('device/mode', {})
        if res is None:
            return None
        return res.get('mode', '')

    async def get_ir_feature(self):
        """Get Ambi Climate's appliance IR feature."""
        return await self.request('device/ir_feature', {})

    async def get_appliance_states(self, limit=1, offset=0):
        """Get Ambi Climate's last N appliance states."""
        return await self.request('device/appliance_states',
                                  {'limit': limit, 'offset': offset})

    async def set_target_temperature(self, temperature):
        """Set target temperature."""
        if self._mode and self._mode.lower() != 'manual':
            _LOGGER.error("Mode has to be sat to manual in the "
                          "Ambiclimate app. Current mode is %s.", self._mode)
            return

        data = self.ac_data[0]
        params = {"mode": data['mode'].lower(),
                  "power": data['power'].lower(),
                  "feature": {
                      "temperature": str(int(temperature)),
                      "fan": data['fan'].lower(),
                      "louver": data.get('louver', "auto").lower(),
                      'swing': data['swing'].lower()
                  }}
        return await self.request('device/deployments', params, get=False)

    async def turn_off(self):
        """Turn off."""
        return await self.set_power_off()

    async def turn_on(self):
        """Turn on."""
        data = self.ac_data[0]
        feature = {}
        feature["temperature"] = str(data.get('target_temperature', data.get('temperature', 20)))
        feature['fan'] = data['fan'].lower() if data.get('fan') else 'med-high'
        feature['louver'] = data['louver'].lower() if data.get('louver') else 'auto'
        feature['swing'] = data['swing'].lower() if data.get('swing') else 'oscillate'
        params = {"mode": data.get('mode', 'Heat').lower(),
                  "power": 'on',
                  "feature": feature}
        return await self.request('device/deployments', params, get=False)

    def get_min_temp(self):
        """Get min temperature."""
        res = 1000
        data = self.ir_features['data'][self.ac_data[0].get('mode').lower()]['temperature']['value']
        for temp in data:
            if float(temp) < res:
                res = float(temp)
        return res

    def get_max_temp(self):
        """Get max temperature."""
        res = -1000
        data = self.ir_features['data'][self.ac_data[0].get('mode').lower()]['temperature']['value']
        for temp in data:
            if float(temp) > res:
                res = float(temp)
        return res

    async def update_device_info(self):
        """Update device info."""
        self.ir_features = await self.get_ir_feature()

    async def update_device(self):
        """Update device."""
        data = dict()
        data['target_temperature'] = None
        states = await self.get_appliance_states()
        if states:
            self.ac_data = states.get('data', [{}])
            data['target_temperature'] = self.ac_data[0].get('temperature')
            data['power'] = self.ac_data[0].get('power')
        temp = await self.get_sensor_temperature()
        data['temperature'] = round(temp, 1) if temp else None
        humidity = await self.get_sensor_humidity()
        data['humidity'] = round(humidity, 1) if humidity else None
        self._mode = await self.get_mode()
        return data


class AmbiclimateOauthError(Exception):
    """AmbiclimateOauthError."""


class AmbiclimateOAuth:
    """Implements Authorization Code Flow for Ambiclimate's OAuth implementation."""

    OAUTH_AUTHORIZE_URL = 'https://api.ambiclimate.com/oauth2/authorize'
    OAUTH_TOKEN_URL = 'https://api.ambiclimate.com/oauth2/token'

    def __init__(self, client_id, client_secret, redirect_uri, werbsession):
        """Create a AmbiclimateOAuth object."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.websession = werbsession

    def get_authorize_url(self):
        """Get the URL to use to authorize this app."""
        payload = {'client_id': self.client_id,
                   'response_type': 'code',
                   'redirect_uri': self.redirect_uri}
        return self.OAUTH_AUTHORIZE_URL + '?' + urlencode(payload)

    async def get_access_token(self, code):
        """Get the access token for the app given the code."""
        payload = {'client_id': self.client_id,
                   'redirect_uri': self.redirect_uri,
                   'code': code,
                   'client_secret': self.client_secret,
                   'grant_type': 'authorization_code'}

        try:
            with async_timeout.timeout(DEFAULT_TIMEOUT):
                response = await self.websession.post(self.OAUTH_TOKEN_URL,
                                                      data=payload,
                                                      allow_redirects=True)
                if response.status != 200:
                    raise AmbiclimateOauthError(response.status)
                token_info = await response.json()
                token_info['expires_at'] = int(time.time()) + token_info['expires_in']
                return token_info
        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Timeout calling Ambiclimate to get auth token.")
            return None
        return None

    async def refresh_access_token(self, token_info):
        """Refresh access token."""
        if token_info is None:
            return token_info
        if not is_token_expired(token_info):
            return token_info

        payload = {'client_id': self.client_id,
                   'redirect_uri': self.redirect_uri,
                   'refresh_token': token_info['refresh_token'],
                   'client_secret': self.client_secret,
                   'grant_type': 'refresh_token'}

        refresh_token = token_info.get('refresh_token')

        try:
            with async_timeout.timeout(DEFAULT_TIMEOUT):
                response = await self.websession.post(self.OAUTH_TOKEN_URL,
                                                      data=payload,
                                                      allow_redirects=True)
                if response.status != 200:
                    _LOGGER.error("Failed to refresh access token: %s", response)
                    return None
                token_info = await response.json()
                token_info['expires_at'] = int(time.time()) + token_info['expires_in']
                if 'refresh_token' not in token_info:
                    token_info['refresh_token'] = refresh_token
                return token_info
        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Timeout calling Ambiclimate to get auth token.")
        return None


def is_token_expired(token_info):
    """Check if token is expired."""
    return token_info['expires_at'] - int(time.time()) < 60*60
