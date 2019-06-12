import json
import hashlib
import logging
import time
from sqlalchemy import (Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, func)
from sqlalchemy.orm import relationship
from potnanny_core.database import Base, db_session
from potnanny_core.schemas.outlet import GenericOutletSchema
from potnanny_core.utils import subprocess_cmd
from potnanny_core.models.setting import VesyncAccount
from potnanny_core.models.wireless import WirelessInterface

logger = logging.getLogger(__name__)


class Outlet(Base):
    """Class for storing Wireless RF Outlet data."""

    __tablename__ = 'outlets'

    id = Column(Integer, primary_key=True)
    name = Column(String(48), nullable=False, unique=True)
    type = Column(String(24), nullable=False, default='wireless')
    on_code = Column(String(24), nullable=False)
    off_code = Column(String(24), nullable=False)
    state = Column(Boolean, nullable=False, default=False)
    created = Column(DateTime, default=func.now())

    def __repr__(self):
        return "<Outlet({})>".format(self.name)


class OutletController(object):
    """Class to communicate with and manage various outlet types."""

    def __init__(self, *args, **kwargs):
        logger.debug("initializing outlet controller")
        self.vesync = None


    def init_vesync(self):
        account = VesyncAccount.get()
        if account:
            self.vesync = Vesync(account['username'], account['password'])
        else:
            raise RuntimeError("No Vesync account exists")


    def available_outlets(self):
        """Get list of all available outlets."""

        outlets = []

        # try to gather info from vesync
        try:
            self.init_vesync()
            devices, response = self.vesync.get_outlets()
            if response == 200:
                outlets += GenericOutletSchema(many=True).load(devices)
        except Exception:
            # logger.exception("Failed to get Vesync outlets")
            pass

        # gather info from defined wireless outlets
        results = Outlet.query.all()
        if results:
            outlets += GenericOutletSchema(many=True).load(results)

        return outlets


    def get_outlet(self, id):
        """
        Get details of an outlet with id string.

        args:
            - id (str)
        returns:
            dict (simplified/generic representation of the outlet)
        raises:
            none
        """

        outlets = self.available_outlets()
        if not outlets:
            return None

        for o in outlets:
            if o.id == str(id):
                data, errors = GenericOutletSchema().load(o)
                if len(errors) == 0:
                    return data

                logger.warning(errors)

        return None


    def turn_on(self, outlet):
        """
        Turn an outlet ON

        args:
            - outlet dict, like {'id': '1', type': 'wireless'}
        returns:
            bool
        raises:
            none
        """

        logger.debug("turning outlet '{}' ON".format(outlet))
        outlet['state'] = 1
        return self.switch_outlet(outlet)


    def turn_off(self, outlet):
        """
        Turn an outlet OFF

        args:
            - outlet dict, like {'id': '1', 'type': 'wireless'}
        returns:
            bool
        raises:
            none
        """

        logger.debug("turning outlet '{}' OFF".format(outlet))
        outlet['state'] = 0
        return self.switch_outlet(outlet)


    def switch_outlet(self, outlet):
        """
        Switch outlet to defined state.

        args:
            - dict, like {'id': '1', 'type': 'wireless', 'state': 1}
        returns:
            bool
        raises:
            ValueError if 'state' is not Bool (0|1|True|False)
        """
        state = outlet['state']
        if state not in [0, 1, True, False]:
            raise ValueError("Outlet state must be True or False")

        if outlet['type'] in ['vesync', 'wifi-switch']:
            results, response = self.vesync._switch_outlet(outlet['id'], int(state))
            if response == 200:
                return True

            return False

        if outlet['type'] == 'wireless':
            device = Outlet.query.get(int(outlet['id']))
            if not device:
                raise RuntimeError("Outlet '{}' not found".format(outlet['id']))

            code = device.on_code
            if int(state) == 0:
                code = device.off_code

            wi = WirelessInterface()
            result = wi.send_code(code)
            if result:
                device.state = state
                db_session.commit()

            return result

        else:
            raise RuntimeError("Unknown outlet type '{}'".format(outlet['type']))
