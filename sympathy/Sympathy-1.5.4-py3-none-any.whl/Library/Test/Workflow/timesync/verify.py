# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import numpy as np

from sympathy.api import adaf_wrapper
from sympathy.api.exceptions import SyNodeError


class VerifyGoodSync(adaf_wrapper.ADAFWrapper):
    """
    Verify that the sync was performed and that the offset was correct to
    within 1 second.
    """

    def execute(self):
        assert(self.in_adaf.meta['SYNC_PERFORMED_SYSTEM1_SYSTEM0'].value()[0] == True)

        # Check that the offset has been calculated correctly. Correct offset
        # is in the region of 80.8 seconds. Plus/minus half a second is also
        # considered correct.
        if self.in_adaf.meta['SYNC_OFFSET_SYSTEM1_SYSTEM0'].value().dtype.kind == 'm':
            timeunit = np.timedelta64(1000000, 'us')  # 1 second with microsecond resolution
        else:
            timeunit = 1
        assert(80.3*timeunit <
               self.in_adaf.meta['SYNC_OFFSET_SYSTEM1_SYSTEM0'].value()[0] <=
               81.3*timeunit)

        # Check that the offset has been applied.
        assert(self.in_adaf.meta['SYNC_OFFSET_SYSTEM1_SYSTEM0'].value()[0] ==
                (self.in_adaf.sys['system0']['raster']['y'].t[0] -
                 self.in_adaf.sys['system1']['raster']['ref_y'].t[0]))


class VerifyFailedSync(adaf_wrapper.ADAFWrapper):
    """
    Verify that the sync has reported its failure correctly in the meta data.
    """

    def execute(self):
        assert(self.in_adaf.meta['SYNC_PERFORMED_SYSTEM1_SYSTEM2'].value()[0] == False)

        # A failed sync should always have offset 0.
        assert(self.in_adaf.meta['SYNC_OFFSET_SYSTEM1_SYSTEM2'].value()[0] == 0)
