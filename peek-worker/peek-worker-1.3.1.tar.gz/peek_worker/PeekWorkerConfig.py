'''
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
 * Website : http://www.synerty.com
 * Support : support@synerty.com
 *
'''
import logging

from peek_platform.file_config.PeekFileConfigABC import PeekFileConfigABC
from peek_platform.file_config.PeekFileConfigOsMixin import PeekFileConfigOsMixin
from peek_platform.file_config.PeekFileConfigPeekServerClientMixin import \
    PeekFileConfigPeekServerClientMixin
from peek_platform.file_config.PeekFileConfigPlatformMixin import \
    PeekFileConfigPlatformMixin
from peek_platform.file_config.PeekFileConfigSqlAlchemyMixin import \
    PeekFileConfigSqlAlchemyMixin
from peek_platform.file_config.PeekFileConfigWorkerMixin import PeekFileConfigWorkerMixin

logger = logging.getLogger(__name__)


class PeekWorkerConfig(PeekFileConfigABC,
                       PeekFileConfigPeekServerClientMixin,
                       PeekFileConfigPlatformMixin,
                       PeekFileConfigOsMixin,
                       PeekFileConfigSqlAlchemyMixin,
                       PeekFileConfigWorkerMixin):
    """
    This class creates a basic worker configuration
    """



