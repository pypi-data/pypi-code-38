#
# Copyright (c) 2019, Nordic Semiconductor ASA
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form, except as embedded into a Nordic
#    Semiconductor ASA integrated circuit in a product or a software update for
#    such product, must reproduce the above copyright notice, this list of
#    conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
#
# 3. Neither the name of Nordic Semiconductor ASA nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# 4. This software, with or without modification, must only be used with a
#    Nordic Semiconductor ASA integrated circuit.
#
# 5. Any software provided in binary form under this license must not be reverse
#    engineered, decompiled, modified and/or disassembled.
#
# THIS SOFTWARE IS PROVIDED BY NORDIC SEMICONDUCTOR ASA "AS IS" AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY, NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NORDIC SEMICONDUCTOR ASA OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Common constants, defined by Zigbee specification.
from enum import Enum

DEFAULT_ZIGBEE_PROFILE_ID = 0x0104 # HA profile ID
BROADCAST_ADDRESS_ALL_DEVICES=0xffff
UNKNOWN_IEEE_ADDRESS = 0xFFFFFFFFFFFFFFFF

BASIC_CLUSTER       = 0x0000
IDENTIFY_CLUSTER    = 0x0003
ON_OFF_CLUSTER      = 0x0006
LVL_CTRL_CLUSTER    = 0x0008
OTA_CLUSTER         = 0x0019
DOOR_LOCK_CLUSTER   = 0x0101
COLOR_CTRL_CLUSTER  = 0x0300
TEMPERATURE_CLUSTER = 0x0402
PRESSURE_CLUSTER    = 0x0403

IDENTIFY_IDENTIFY_TIME_ATTR   = 0x0000
ON_OFF_ONOFF_ATTR             = 0x0000
LVL_CTRL_CURR_LVL_ATTR        = 0x0000
DOOR_LOCK_LOCK_STATE          = 0x0000
COLOR_CTRL_CURR_HUE_ATTR      = 0x0000
COLOR_CTRL_CURR_SAT_ATTR      = 0x0001
OTA_CURRENT_FILE_VERSION_ATTR = 0x0002
OTA_UPGRADE_SERVER_ID_ATTR    = 0x0000

IDENTIFY_IDENTIFY_CMD                = 0x00
IDENTIFY_IDENTIFY_QUERY_CMD          = 0x01
IDENTIFY_EZ_MODE_INVOKE_CMD          = 0x02
IDENTIFY_UPDATE_COMMISSION_STATE_CMD = 0x03

ON_OFF_OFF_CMD              = 0x00
ON_OFF_ON_CMD               = 0x01
LVL_CTRL_MV_TO_LVL_CMD      = 0x00
DOOR_LOCK_LOCK_DOOR_CMD     = 0x00
DOOR_LOCK_UNLOCK_DOOR_CMD   = 0x01
COLOR_CTRL_MV_TO_HUE_CMD    = 0x00
COLOR_CTRL_MV_TO_SAT_CMD    = 0x03
COLOR_CTRL_MV_TO_HUE_SAT_CMD= 0x06

BOOL_TYPE           = 0x10
UINT8_TYPE          = 0x20
UINT16_TYPE         = 0x21
UINT32_TYPE         = 0x23
UINT64_TYPE         = 0x27
SINT8_TYPE          = 0x28
SINT16_TYPE         = 0x29
SINT64_TYPE         = 0x2f
ENUM8_TYPE          = 0x30
MAP8_TYPE           = 0x18
EUI64_TYPE          = 0xF0

class ZCLDirection(Enum):
    DIRECTION_CLI_TO_SRV = 0x00
    DIRECTION_SRV_TO_CLI = 0x01

CLI_ENDPOINT                 = 64    # Default Zigbee CLI endpoint
DOOR_LOCK_ENDPOINT           = 8     # Default Door Lock endpoint
LIGHT_BULB_ENDPOINT          = 10    # Default Light Bulb endpoint
LIGHT_SWITCH_ENDPOINT        = 1     # Default Light Switch endpoint
THINGY_PROXY_THINGY_ENDPOINT = 10    # One of the endpoints of Thingy on the Thingy Proxy
OTA_CLIENT_ENDPOINT          = 10    # Default OTA Client endpoint

DOOR_LOCK_OPEN  = 1
DOOR_LOCK_CLOSE = 0
