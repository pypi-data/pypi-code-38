#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import struct

MSG_MARK = 0xabccba

MSG_HEADER_SIZE = 8

ACK_BIT = 0b10000000

MSG_TYPE_IDX = 5

DEVICE_ID_DEFAULT = 1
DEVICE_ID_MAX     = 127

MCP_SUCCESS                        = 0x00
MCP_INVALID_FORMAT                 = 0x01
MCP_INVALID_CRC                    = 0x02
MCP_INVALID_COMMAND_PAYLOAD_SIZE   = 0x03
MCP_INVALID_MSG_TYPE               = 0x04
MCP_INVALID_COMMAND_PAYLOAD        = 0x05
MCP_INVALID_OPERATION              = 0x06
MCP_INVALID_MSG_SIZE               = 0x07
MCP_RECV_TIMEOUT                   = 0x08
MCP_OUT_OF_POSITION_LIMIT          = 0x09
MCP_ABS_ENCODER_ERROR              = 0x80
MCP_INC_ENCODER_ERROR              = 0x90
MCP_MOTOR_ERROR                    = 0xa0
MCP_OTHER_ERROR                    = 0xff


MSG_TYPE_QUERY_SERVO_STATUS_CMD = 0x01
MSG_TYPE_GET_LOG_INFO_CMD       = 0x05
MSG_TYPE_GET_LOG_CMD            = 0x06
MSG_TYPE_CLEAR_LOG_CMD          = 0x07
MSG_TYPE_GET_LIFE_LOG_CMD       = 0x08
MSG_TYPE_CLEAR_LIFE_LOG_CMD     = 0x09
MSG_TYPE_READY_CMD              = 0x10
MSG_TYPE_FREE_CMD               = 0x11
MSG_TYPE_HOLD_CMD               = 0x12
MSG_TYPE_CLEAR_FAULT_CMD        = 0x13
MSG_TYPE_PROTECTION_STOP_CMD        = 0x14
MSG_TYPE_SET_REF_CURRENT_CMD    = 0x20
MSG_TYPE_GET_REF_CURRENT_CMD    = 0x21
MSG_TYPE_SET_REF_VELOCITY_CMD   = 0x22
MSG_TYPE_GET_REF_VELOCITY_CMD   = 0x23
MSG_TYPE_SET_REF_POSITION_CMD   = 0x24
MSG_TYPE_GET_REF_POSITION_CMD   = 0x25
MSG_TYPE_SET_PARAM_CMD          = 0x30
MSG_TYPE_GET_PARAM_CMD          = 0x31
MSG_TYPE_RESET_ROTATION_CMD     = 0x32
MSG_TYPE_RESET_CMD              = 0x3c
MSG_TYPE_FAULT_CMD              = 0x3d
MSG_TYPE_DEBUG_CMD              = 0x3f
MSG_TYPE_WRONG_CMD              = 0x7f
MSG_TYPE_NACK                   = 0xff

PARAM_ID_CURRENT_KP           = 0x10
PARAM_ID_CURRENT_KI           = 0x11
PARAM_ID_CURRENT_MAX_ITERM    = 0x12
PARAM_ID_CURRENT_MIN_ITERM    = 0x13
PARAM_ID_CURRENT_MAX_LIMIT    = 0x14
PARAM_ID_CURRENT_MIN_LIMIT    = 0x15

PARAM_ID_VELOCITY_KP          = 0x20
PARAM_ID_VELOCITY_KI          = 0x21
PARAM_ID_VELOCITY_KD          = 0x22
PARAM_ID_VELOCITY_MAX_ITERM   = 0x23
PARAM_ID_VELOCITY_MIN_ITERM   = 0x24
PARAM_ID_VELOCITY_MAX_LIMIT   = 0x25
PARAM_ID_VELOCITY_MIN_LIMIT   = 0x26

PARAM_ID_POSITION_KP          = 0x30
PARAM_ID_POSITION_KI          = 0x31
PARAM_ID_POSITION_KD          = 0x32
PARAM_ID_POSITION_MAX_ITERM   = 0x33
PARAM_ID_POSITION_MIN_ITERM   = 0x34
PARAM_ID_POSITION_MAX_LIMIT   = 0x35
PARAM_ID_POSITION_MIN_LIMIT   = 0x36
PARAM_ID_POSITION_OFFSET      = 0x3a

PARAM_ID_DEVICE_ID            = 0x80
PARAM_ID_FIRMWARE_VERSION     = 0x81

PARAM_ID_CALIBRATION          = 0xa0
PARAM_ID_POSITION_SYS_OFFSET  = 0xa1

PARAM_ID_PROTECTION_STOP_PIN_TIMEOUT     = 0xd0
PARAM_ID_STOP_CONTROL_ERROR_THRESHOLD    = 0xd1

LIFE_LOG_PARAM_ID_POWER_ON_TIME = 0x00  

STATE_HOLD = 0
STATE_FREE = 1
STATE_READY = 2
STATE_CURRENT_SERVO = 3
STATE_VELOCITY_SERVO = 4
STATE_POSITION_SERVO = 5
STATE_PROTECTION_STOPPING = 12
STATE_PROTECTION_STOP     = 13
STATE_FAULT_FREE = 14
STATE_FAULT_HOLD = 15
STATE_UNKNOWN=16


SERVO_FAULT_FOC_DURATION = 0x0001
SERVO_FAULT_OVER_VOLT    = 0x0002
SERVO_FAULT_UNDER_VOLT   = 0x0004
SERVO_FAULT_OVER_TEMP    = 0x0008
SERVO_FAULT_BREAK_IN     = 0x0040
SERVO_FAULT_STOP_CONTROL_ERROR   = 0x0100
SERVO_FAULT_STOP_TIMEOUT = 0x0200
SERVO_FAULT_DUMMY        = 0x0800

LOG_RECORED_BYTE_SIZE             = 16
GET_LOG_CMD_MAX_LOG_RECORED_SIZE  = 10

LOG_LEVEL_FATAL = 0x01
LOG_LEVEL_ERROR = 0x02
LOG_LEVEL_WARN  = 0x03
LOG_LEVEL_INFO  = 0x04
LOG_LEVEL_DEBUG = 0x05
LOG_LEVEL_TRACE = 0x06

LOG_GROUP_SYSTEM                         = 0x01
LOG_GROUP_MAIN                           = 0x02
LOG_GROUP_AMARETTO                       = 0x03
LOG_GROUP_HANDLE_CMD                     = 0x04
LOG_GROUP_NACK                           = 0x05
LOG_GROUP_DOMAIN_BLDC_MOTOR_CONTROL      = 0x10
LOG_GROUP_DOMAIN_HALL_EDGE_ALIGNMENT     = 0x11
LOG_GROUP_DOMAIN_LOG                     = 0x12
LOG_GROUP_DOMAIN_MCP_MESSAGE             = 0x13
LOG_GROUP_DOMAIN_MCP_SERVER              = 0x14
LOG_GROUP_DOMAIN_MOTOR_ABS_ENC_ALIGNMENT = 0x15
LOG_GROUP_DOMAIN_MOTOR_INC_ENC_ALIGNMENT = 0x16
LOG_GROUP_PERIPHERAL_BRAKE               = 0x80
LOG_GROUP_PERIPHERAL_COM485              = 0x81
LOG_GROUP_PERIPHERAL_DEBUG               = 0x82
LOG_GROUP_PERIPHERAL_ENCODER             = 0x83
LOG_GROUP_PERIPHERAL_LED                 = 0x84
LOG_GROUP_PERIPHERAL_MRAM                = 0x85
LOG_GROUP_PERIPHERAL_PROTECTION_STOP     = 0x86
LOG_GROUP_PERIPHERAL_SENSOR              = 0x87
LOG_GROUP_PERIPHERAL_STEADY_CLOCK        = 0x88

LOG_SUB_GROUP_SYSTEM_POWER_ON            = 0x01
LOG_SUB_GROUP_SYSTEM_START_UP            = 0x02
LOG_SUB_GROUP_SYSTEM_ERROR               = 0x10
LOG_SUB_GROUP_SYSTEM_ASSERT              = 0x11
LOG_SUB_GROUP_BLDC_FAULT                 = 0x01
LOG_SUB_GROUP_BLDC_PROTECTION_STOP       = 0x02
LOG_SUB_GROUP_MCP_SERVER_UNNOTIFIED_ERROR= 0x01

LOG_RECORD_INFO_BYTE_SIZE   = 16
LOG_RECORD_BYTE_SIZE        = 16
LOG_RECORD_PAYLOAD_SIZE     = 8

#query servo status result index
QSSR_IDX_POS = 0
QSSR_IDX_VEL = 1
QSSR_IDX_CUR = 2
QSSR_IDX_REF = 3
QSSR_IDX_TEMP = 4
QSSR_IDX_FAULTS = 5

def state2str(s):
    if s == STATE_HOLD:
        return "STATE_HOLD"
    elif s == STATE_FREE:
        return "STATE_FREE"
    elif s == STATE_READY:
        return "STATE_READY"
    elif s == STATE_CURRENT_SERVO:
        return "STATE_CURRENT_SERVO"
    elif s == STATE_FAULT_FREE:
        return "STATE_FAULT_FREE"
    elif s == STATE_FAULT_HOLD:
        return "STATE_FAULT_HOLD"
    elif s == STATE_VELOCITY_SERVO:
        return "STATE_VELOCITY_SERVO"
    elif s == STATE_POSITION_SERVO:
        return "STATE_POSITION_SERVO"
    elif s == STATE_PROTECTION_STOPPING:
        return "STATE_PROTECTION_STOPPING"
    elif s == STATE_PROTECTION_STOP:
        return "STATE_PROTECTION_STOP"
    else:
        return "STATE_UNKNOWN"

def faults2str(s):
    ret = []
    if s & SERVO_FAULT_FOC_DURATION:
        ret.append("SERVO_FAULT_FOC_DURATION")
    if s & SERVO_FAULT_OVER_VOLT   :
        ret.append("SERVO_FAULT_OVER_VOLT")
    if s & SERVO_FAULT_UNDER_VOLT  :
        ret.append("SERVO_FAULT_UNDER_VOLT")
    if s & SERVO_FAULT_OVER_TEMP   :
        ret.append("SERVO_FAULT_OVER_TEMP")
    if s & SERVO_FAULT_STOP_TIMEOUT  :
        ret.append("SERVO_FAULT_STOP_TIMEOUT")
    if s & SERVO_FAULT_BREAK_IN    :
        ret.append("SERVO_FAULT_BREAK_IN")
    if s & SERVO_FAULT_STOP_CONTROL_ERROR    :
        ret.append("SERVO_FAULT_STOP_CONTROL_ERROR")
    if s & SERVO_FAULT_STOP_TIMEOUT    :
        ret.append("SERVO_FAULT_STOP_TIMEOUT")

    if len(ret) == 0:
        return "NO_FAULTS"
    else:
        return ", ".join(ret)

def err2str(e):
    if e == MCP_SUCCESS:
        return "success"
    elif e == MCP_INVALID_FORMAT                :
        return "invalid_format"
    elif e == MCP_INVALID_CRC                   :
        return "invalid_crc"
    elif e == MCP_INVALID_COMMAND_PAYLOAD_SIZE  :
        return "invalid_command_payload_size"
    elif e == MCP_INVALID_MSG_TYPE              :
        return "invalid_msg_type"
    elif e == MCP_INVALID_COMMAND_PAYLOAD       :
        return "invalid_command_payload"
    elif e == MCP_INVALID_OPERATION             :
        return "invalid_operation"
    elif e == MCP_INVALID_MSG_SIZE              :
        return "invalid_msg_size"
    elif e == MCP_RECV_TIMEOUT                  :
        return "timeout"
    elif e == MCP_OUT_OF_POSITION_LIMIT         :
        return "out_of_position_limit"
    elif e == MCP_ABS_ENCODER_ERROR             :
        return "abs_encoder_error"
    elif e == MCP_INC_ENCODER_ERROR             :
        return "inc_encoder_error"
    elif e == MCP_MOTOR_ERROR                   :
        return "motor_error"
    elif e == MCP_OTHER_ERROR                   :
        return "other_error"
    else:
        return "unknown"


def cmd2str(c):
    if   c == MSG_TYPE_QUERY_SERVO_STATUS_CMD :
        return "query_servo_status"
    elif c == MSG_TYPE_READY_CMD              :
        return "ready"
    elif c == MSG_TYPE_FREE_CMD               :
        return "free"
    elif c == MSG_TYPE_HOLD_CMD               :
        return "hold"
    elif c == MSG_TYPE_CLEAR_FAULT_CMD        :
        return "clear_fault"
    elif c == MSG_TYPE_PROTECTION_STOP_CMD    :
        return "protection_stop"
    elif c == MSG_TYPE_SET_REF_CURRENT_CMD    :
        return "set_ref_current"
    elif c == MSG_TYPE_GET_REF_CURRENT_CMD    :
        return "get_ref_current"
    elif c == MSG_TYPE_SET_REF_VELOCITY_CMD   :
        return "set_ref_velocity"
    elif c == MSG_TYPE_GET_REF_VELOCITY_CMD   :
        return "get_ref_velocity"
    elif c == MSG_TYPE_SET_REF_POSITION_CMD   :
        return "set_ref_position"
    elif c == MSG_TYPE_GET_REF_POSITION_CMD   :
        return "get_ref_position"
    elif c == MSG_TYPE_RESET_ROTATION_CMD     :
        return "reset_rotation"
    elif c == MSG_TYPE_SET_PARAM_CMD          :
        return "set_param"
    elif c == MSG_TYPE_GET_PARAM_CMD          :
        return "get_param"
    elif c == MSG_TYPE_RESET_CMD              :
        return "reset"
    elif c == MSG_TYPE_FAULT_CMD              :
        return "fault"
    elif c == MSG_TYPE_DEBUG_CMD              :
        return "debug"
    elif c == MSG_TYPE_GET_LOG_INFO_CMD       :
        return "get_log_info"
    elif c == MSG_TYPE_GET_LOG_CMD            :
        return "get_log"
    elif c == MSG_TYPE_CLEAR_LOG_CMD          :
        return "clear_log"
    elif c == MSG_TYPE_GET_LIFE_LOG_CMD       :
        return "get_life_log"
    elif c == MSG_TYPE_CLEAR_LIFE_LOG_CMD     :
        return "clear_life_log"
    else:
        return "unknown(" + hex(c) + ")"


def log_level2str(lv):
    if lv == LOG_LEVEL_FATAL:
        return "FATAL"
    elif lv == LOG_LEVEL_ERROR :
        return "ERROR"
    elif lv == LOG_LEVEL_WARN  :
        return "WARN"
    elif lv == LOG_LEVEL_INFO  :
        return "INFO"
    elif lv == LOG_LEVEL_DEBUG :
        return "DEBUG"
    elif lv == LOG_LEVEL_TRACE :
        return "TRACE"
    else:
        return "UNKNOWN"

def log_record2str(lv, g,sg,c,payload):

    s0 = hex(g)
    s1 = hex(sg)
    s2 = hex(c)
    s3 = "[" + " ".join(['0x{:02x}'.format(c) for c in payload]) + "]"

    if g == LOG_GROUP_SYSTEM                           :
        s = "system"
        if   sg == LOG_SUB_GROUP_SYSTEM_POWER_ON            :
            return (s, "power_on", s2, s3)
        elif sg == LOG_SUB_GROUP_SYSTEM_START_UP            :
            return (s, "start_up", s2, s3)
        elif sg == LOG_SUB_GROUP_SYSTEM_ERROR               :
            return (s, "error", s2, s3)
        elif sg == LOG_SUB_GROUP_SYSTEM_ASSERT              :
            if lv == LOG_LEVEL_FATAL:
                hd = struct.unpack('<6sH', payload)
                print(hd)
                filename = hd[0].decode('ascii')
                fileline = hd[1]
                ext = "(.c)" if c == 0 else "(.h)"
                return (s, "assert", s2, "file:" + filename + ext + ", line:" + str(fileline))
            else:
                return (s, "assert", s2, s3)
        else:
            return (s, s1, s2, s3)
    elif g == LOG_GROUP_MAIN                           :
        return ("main", s1, s2, s3)
    elif g == LOG_GROUP_AMARETTO                       :
        return ("amaretto", s1, s2, s3)
    elif g == LOG_GROUP_HANDLE_CMD                     :
        return ("cmd_handler", 'cmd_' + cmd2str(sg), s2, s3)
    elif g == LOG_GROUP_NACK                     :
        return ("nack", "-", err2str(c), s3)
    elif g == LOG_GROUP_DOMAIN_BLDC_MOTOR_CONTROL      :
        s = "domain_bldcmc"
        if sg == LOG_SUB_GROUP_BLDC_FAULT                 :
            faults= struct.unpack('<H', payload[0:2])[0]
            return (s, "bldc_fault", "-", faults2str(faults))
        elif sg == LOG_SUB_GROUP_BLDC_PROTECTION_STOP       :
            return (s, "bldc_protection_stop", s2, s3)
        else:
            return (s, s1, s2, s3)
    elif g == LOG_GROUP_DOMAIN_HALL_EDGE_ALIGNMENT     :
        return ("domain_hall_edge_align", s1, s2, s3)
    elif g == LOG_GROUP_DOMAIN_LOG                     :
        return ("domain_log", s1, s2, s3)
    elif g == LOG_GROUP_DOMAIN_MCP_MESSAGE             :
        return ("domain_mcp_msg", s1, s2, s3)
    elif g == LOG_GROUP_DOMAIN_MCP_SERVER              :
        if sg == LOG_SUB_GROUP_MCP_SERVER_UNNOTIFIED_ERROR:
            return ("domain_mcp_server", "unnotified_error", err2str(c), s3)
        return ("domain_mcp_server", s1, s2, s3)
    elif g == LOG_GROUP_DOMAIN_MOTOR_ABS_ENC_ALIGNMENT :
        return ("domain_abs_enc_align", s1, s2, s3)
    elif g == LOG_GROUP_DOMAIN_MOTOR_INC_ENC_ALIGNMENT :
        return ("domain_inc_enc_align", s1, s2, s3)
    elif g == LOG_GROUP_PERIPHERAL_BRAKE               :
        return ("peripheral_brake", s1, s2, s3)
    elif g == LOG_GROUP_PERIPHERAL_COM485              :
        return ("peripheral_com485", s1, s2, s3)
    elif g == LOG_GROUP_PERIPHERAL_DEBUG               :
        return ("peripheral_debug", s1, s2, s3)
    elif g == LOG_GROUP_PERIPHERAL_ENCODER             :
        return ("peripheral_encoder", s1, s2, s3)
    elif g == LOG_GROUP_PERIPHERAL_LED                 :
        return ("peripheral_led", s1, s2, s3)
    elif g == LOG_GROUP_PERIPHERAL_MRAM                :
        return ("peripheral_mram", s1, s2, s3)
    elif g == LOG_GROUP_PERIPHERAL_PROTECTION_STOP     :
        return ("peripheral_protection_stop", s1, s2, s3)
    elif g == LOG_GROUP_PERIPHERAL_SENSOR              :
        return ("peripheral_sensor", s1, s2, s3)
    elif g == LOG_GROUP_PERIPHERAL_STEADY_CLOCK        :
        return ("peripheral_clock", s1, s2, s3)
    else:
        return (s0, s1, s2, s3)


