# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Palm OS Application Interface
"""

from __future__ import absolute_import

import os
import os.path
import socket
import getpass
import datetime
import logging

from rattail.config import make_config
from rattail.csvutil import DictWriter

try:
    import pythoncom
except ImportError:
    # Mock out for Linux.
    class Object(object):
        pass
    pythoncom = Object()
    pythoncom.CLSCTX_LOCAL_SERVER = 4


log = logging.getLogger(__name__)


class PalmConduit(object):
    """
    Implements a conduit for Palm's HotSync Manager.
    """

    _reg_clsid_ = '{F2FDDEEC-254F-42C3-8801-C41E8A243F13}'
    _reg_progid_ = 'Rattail.PalmConduit'
    _reg_desc_ = "Rattail Conduit for Palm HotSync Manager"

    # Don't let pythoncom guess this, for several reasons.  This way Python
    # will go about determining its path etc. as normal, and __name__ will be
    # "rattail.palm" instead of just "palm".
    _reg_class_spec_ = 'rattail.palm.PalmConduit'

    # Don't let HotSync Manager run our code in-process, so that we may launch
    # wxPython dialogs as needed for configuration etc.
    _reg_clsctx_ = pythoncom.CLSCTX_LOCAL_SERVER

    _typelib_guid_ = '{6FD7A7A0-FA1F-11D2-AC32-006008E3F0A2}'
    _typelib_version_ = 1, 0
    _com_interfaces_ = ['IPDClientNotify']

    _public_methods_ = ['BeginProcess', 'CfgConduit',
                        'ConfigureConduit', 'GetConduitInfo']

    def BeginProcess(self):
        """
        Called by HotSync Manager when synchronization is ready to happen.
        This method implements the actual data sync.
        """

        from win32com.client import Dispatch

        config = make_config()
        data_dir = config.require('rattail.palm', 'collection_dir')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        db_query = Dispatch('PDDirect.PDDatabaseQuery')
        db = db_query.OpenRecordDatabase('Rattail_Scan', 'PDDirect.PDRecordAdapter')
        if db.RecordCount:
            
            sys_adapter = Dispatch('PDDirect.PDSystemAdapter')
            fname = '%s,%s,%s,%s.csv' % (socket.gethostname(), getpass.getuser(),
                                         sys_adapter.PDUserInfo.UserName,
                                         datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S'))
            data_path = os.path.join(data_dir, fname)
            log.info("PalmConduit.BeginProcess: writing %u handheld records to file: %s" %
                     (db.RecordCount, data_path))

            data_file = open(data_path, 'wb')
            writer = DictWriter(data_file, ['upc', 'cases', 'units'])
            writer.writeheader()
            for i in range(db.RecordCount):
                rec, unique_id, category, attrs = db.ReadByIndex(i)

                writer.writerow({
                        'upc': rec[:15].rstrip('\x00'),
                        'cases': rec[15:19].rstrip('\x00'),
                        'units': rec[19:23].rstrip('\x00'),
                        })

            data_file.close()

            log.info("PalmConduit.BeginProcess: removing all records from handheld")
            db.RemoveSet(0)
            log.info("PalmConduit.BeginProcess: done")

        else:
            log.info("PalmConduit.BeginProcess: nothing to do")

        return False

    def CfgConduit(self, nCreatorId, nUserId, bstrUserName, bstrPathName,
                   nSyncPerm, nSyncTemp, nSyncNew, nSyncPref):
        pass

    def ConfigureConduit(self, pPathName, pRegistry, nSyncPref, nSyncType):
        pass

    def GetConduitInfo(self, infoType, dwCreatorID, dwUserID, bstrUsername):
        return None


def get_conduit_manager():
    """
    Load an instance of the Palm Conduit Manager.
    """

    from win32com.client import Dispatch
    from pywintypes import com_error
    from winerror import CO_E_CLASSSTRING
    from rattail.exceptions import PalmConduitManagerNotFound

    try:
        conduit_mgr = Dispatch('PDStandard.PDSystemCondMgr')
    except com_error as error:
        if error.hresult == CO_E_CLASSSTRING: # "Invalid class string"
            raise PalmConduitManagerNotFound()
        raise

    return conduit_mgr


def get_creator_id(conduit_mgr=None):
    """
    Get the "creator ID" for the Rattail Palm conduit.
    """

    if conduit_mgr is None:
        conduit_mgr = get_conduit_manager()
    return conduit_mgr.StringToCreatorID('RTTL')


def conduit_is_registered(conduit_mgr=None):
    """
    Check if the Rattail Palm conduit is registered with HotSync Manager.
    """

    if conduit_mgr is None:
        conduit_mgr = get_conduit_manager()
    rattail_id = get_creator_id(conduit_mgr)
    for creator_id in conduit_mgr.GetConduitList():
        if creator_id == rattail_id:
            return True
    return False


def register_com_server():
    """
    Registers the COM server class which implements the Rattail Palm conduit.
    """

    from win32com.client.gencache import EnsureModule
    from win32com.server.register import RegisterClasses
    from rattail.exceptions import PalmClassicDatabaseTypelibNotFound

    # First we must make sure the Palm Classic Database type library is
    # available to Python.  Note that we specify version 1.0 here.  I'm not
    # sure if that matters or not, but 1.0 was the only registry key found
    # below the type library GUID when I last checked:
    #
    #    HKEY_CLASSES_ROOT\TypeLib\{6FD7A7A0-FA1F-11D2-AC32-006008E3F0A2}
    #
    # TODO: Unfortunately I don't even remember why (or indeed, if) this
    # EnsureModule business is necessary.  If I ever (re)discover that, I
    # should make mention of it here...
    if not EnsureModule('{6FD7A7A0-FA1F-11D2-AC32-006008E3F0A2}', 0, 1, 0):
        raise PalmClassicDatabaseTypelibNotFound()

    RegisterClasses(PalmConduit, quiet=True)


def register_conduit():
    """
    Registers the Rattail Palm conduit with HotSync Manager.
    """

    from win32com.client import Dispatch
    from rattail.exceptions import PalmConduitAlreadyRegistered

    register_com_server()

    conduit_mgr = get_conduit_manager()
    if conduit_is_registered(conduit_mgr):
        raise PalmConduitAlreadyRegistered()

    info = Dispatch('PDStandard.PDConduitInfo')
    info.COMClassID = 'Rattail.PalmConduit'
    info.CreatorID = get_creator_id(conduit_mgr)
    info.DesktopDataDirectory = 'Rattail'
    info.DisplayName = 'Rattail'
    conduit_mgr.RegisterConduit(info)


def unregister_conduit():
    """
    Unregisters the Rattail Palm conduit from HotSync Manager.
    """

    from rattail.exceptions import PalmConduitNotRegistered

    conduit_mgr = get_conduit_manager()
    if not conduit_is_registered(conduit_mgr):
        raise PalmConduitNotRegistered()

    rattail_id = get_creator_id(conduit_mgr)
    conduit_mgr.UnregisterConduit(rattail_id)

    unregister_com_server()


def unregister_com_server():
    """
    Unregisters the COM server class which implements the Rattail Palm conduit.
    """

    from win32com.client import Dispatch
    from pywintypes import com_error
    from winerror import CO_E_CLASSSTRING
    from rattail.exceptions import PalmConduitNotRegistered

    try:
        conduit = Dispatch('Rattail.PalmConduit')
    except com_error as error:
        if error.hresult == CO_E_CLASSSTRING: # "Invalid class string"
            raise PalmConduitNotRegistered()
        raise

    from win32com.server.register import UnregisterClasses
    UnregisterClasses(PalmConduit, quiet=True)
