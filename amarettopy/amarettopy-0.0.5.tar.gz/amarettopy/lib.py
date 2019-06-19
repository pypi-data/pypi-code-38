#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Buildit Actuator を制御する為のPython3用ライブラリ

インストール方法

```
pip install amarettopy
```

"""

import time
import sys, os, struct
import serial
import crc8
from amarettopy.const import *
import yaml

def toDegree(rawPosition):
    """位置情報の単位を[360/65536 * 度]から[度]に変換する
    """
    return round(rawPosition * 360.0 / float(0x10000), 2)

def fromDegree(degree):
    """位置情報の単位を[度]から[360/65536 * 度]に変換する
    """
    return round(degree/360.0 * 0x10000)

def toRPM(rawVelocity):
    """速度情報の単位を[1/100 * rpm]から[rpm]に変換する
    """
    return rawVelocity / float(100)

def fromRPM(rpm):
    """速度情報の単位を[rpm]から[1/100 * rpm]に変換する
    """
    return round(rpm * 100)

class MCPError(Exception):
    """モーター制御プロトコルエラー用例外ベースクラス
    """
    pass

class MCPTransportError(MCPError):
    """通信層でのエラー用例外ベースクラス
    """
    pass

class MCPApplicationError(MCPError):
    """アプリケーション層でのエラー用例外ベースクラス
    """
    pass

class InvalidFormatError(MCPTransportError):
    """不正なメッセージファーマット例外"""
    pass

class InvalidCRCError(MCPTransportError):
    """不正なCRC例外"""
    pass

class UnexpectedMessageTypeError(MCPTransportError):
    """予想外のメッセージタイプ受信例外"""
    pass

class InvalidCommandPayloadSizeError(MCPTransportError):
    """不正なペイロードサイズ例外"""
    pass

class TimeoutError(MCPTransportError):
    """タイムアウト例外"""
    def __init__(self, e):
        self.args = [e]

class InvalidMessageTypeError(MCPApplicationError):
    """不正なメッセージタイプ例外"""
    pass

class InvalidPayload(MCPApplicationError):
    """不正なペイロード例外"""
    pass

class InvalidOperationError(MCPApplicationError):
    """不正な操作例外"""
    def __init__(self, st):
        self.args = [st]

class OutOfPositionLimitError(MCPApplicationError):
    """位置範囲制限外エラー"""
    pass

class OtherError(MCPApplicationError):
    """その他の例外"""

    def __init__(self, e):
        self.args = [e]

class WaitUntilTimeoutError(Exception):
    """wait_untilメソッド用タイムアウト例外"""
    def __init__(self, e):
        self.args = [e]



class AmarettoPy(object):
    """
    モーター制御プロトコルをカプセル化し、Buildit Actuatorと通信する為のクラス

    Examples
    ---------
    >>> from amarettopy import *
    >>> amaretto = AmarettoPy(port="/dev/ttyUSB0", timeout_ms=3000) #for Linux
    >>> amaretto = AmarettoPy(port="COM8", timeout_ms=3000) #for Win
    >>> deviceId = 1
    >>> (position, velocity, current, referenceValue, temperature, faults) = amaretto.query_servo_status(deviceId)
    >>> print(state2str(amaretto.state()))
    >>> #amaretto.clear_fault(deviceId)
    >>> amaretto.ready(deviceId)
    >>> amaretto.set_ref_velocity(deviceId, fromRPM(42.5))
    >>> amaretto.set_ref_position(deviceId, fromDegree(180))

    """

    def _write(self,msg):
        sendedSize = self._ser.write(msg)
        assert sendedSize == len(msg),"serial write error"

    def _read(self,msg_size):
        return self._ser.read(msg_size)

    def _calcCRC(self,s):
        hash = crc8.crc8()
        hash.update(s)

        return int(hash.hexdigest(), 16)


    def __init__(self, port=os.environ.get('AMARETTO_PORT',"/dev/ttyUSB0"), baud=os.environ.get('AMARETTO_BAUD',115200), timeout_ms=3000):
        """

        指定されたパラメーターでシリアルポートをオープンする

        Parameters
        ----------
        baud : int, default 115200
            ボーレート
        port : str, default "/dev/ttyUSB0"
            シリアルポートの名前(例: Linuxなら/dev/ttyUSB0, WindowsならCOM8等)
        timeout_ms : int, default 3000
            タイムアウト(ミリ秒) 負の値であればはタイムアウトしない

        """
        if timeout_ms < 0:
            self._ser = serial.Serial(port,baud)
        else:
            self._ser = serial.Serial(port,baud,timeout=timeout_ms/1000.0)
        if self.is_open():
            self._ser.reset_input_buffer()
            self._ser.reset_output_buffer()
        self._status = None

    def is_open(self):
        """
        シリアルポートがオープンされていればTrue、そうでなければFalseを返す
        """
        return self._ser.is_open

    def open(self, port=os.environ.get('AMARETTO_PORT',"/dev/ttyUSB0"), baud=os.environ.get('AMARETTO_BAUD',115200)):
        """
        シリアルポートをオープンする

        Parameters
        ----------

        baud : int, default 115200
            ボーレート
        port : str, default "/dev/ttyUSB0"
            シリアルポートの名前(例: Linuxなら/dev/ttyUSB0, WindowsならCOM8等)
        """
        self._ser.baudrate = baud
        self._ser.port = port
        self._ser.open()
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()

    def close(self):
        """
        シリアルポートをクローズする
        """
        self._ser.close()

    def _receive_ack(self):

        header = self._read(MSG_HEADER_SIZE)
        if len(header) != MSG_HEADER_SIZE:
            raise TimeoutError((header, len(header)))

        (mark1, mark2, mark3, crc, devId, msgType, payloadSize) = struct.unpack('BBBBBBB', header[0:7])
        mark = (mark1 << 16) + (mark2 << 8) + mark3

        if mark != MSG_MARK:
            raise InvalidFormatError

        payload = self._read(payloadSize)

        if len(payload) != payloadSize:
            raise TimeoutError((payload, len(payload)))

        if crc != self._calcCRC(header[4:8]+payload):
            raise InvalidCRCError

        #print "recv:", struct.unpack('B' * len(header), header)

        return (msgType, payload)

    def _nack2exception(self, payload):

        (status,err) = struct.unpack('HB',payload)
        self._status = status
        if err == MCP_INVALID_COMMAND_PAYLOAD:
            return InvalidPayload
        elif err == MCP_INVALID_COMMAND_PAYLOAD_SIZE:
            return InvalidCommandPayloadSizeError
        elif err == MCP_INVALID_OPERATION:
            return InvalidOperationError(state2str(self.state()))
        elif err == MCP_INVALID_MSG_TYPE:
            return InvalidMessageTypeError
        elif err == MCP_OUT_OF_POSITION_LIMIT:
            return OutOfPositionLimitError
        else:
            return OtherError(err)

    def _rpc_raw(self, msg, ackfmt):

        self._write(msg)
        (ackType, payload) = self._receive_ack()

        cmdType = struct.unpack('B'*len(msg), msg)[MSG_TYPE_IDX]

        if ackType == MSG_TYPE_NACK:
            raise self._nack2exception(payload)
        elif ackType == (ACK_BIT | cmdType):
            #print (ackfmt, len(payload), payload)
            bs = struct.unpack('<H'+ackfmt, payload)
            self._status = bs[0]
            return bs[1:]
        else:
            raise UnexpectedMessageTypeError

    def _rpc_log_raw(self, msg, ackfmt):

        self._write(msg)
        (ackType, payload) = self._receive_ack()

        cmdType = struct.unpack('B'*len(msg), msg)[MSG_TYPE_IDX]

        if ackType == MSG_TYPE_NACK:
            raise self._nack2exception(payload)
        elif ackType == (ACK_BIT | cmdType):
            status = struct.unpack('<H', payload[0:2])[0]
            startIndex = struct.unpack('<H', payload[2:4])[0]
            readSize = struct.unpack('<H', payload[4:6])[0]

            logRecords = []
            for i in range(readSize):
                index = 6 + i * LOG_RECORD_BYTE_SIZE
                recordBytes = payload[index:(index+LOG_RECORD_BYTE_SIZE)]
                hd = struct.unpack('<IBBBB', recordBytes[0:LOG_RECORD_BYTE_SIZE-LOG_RECORD_PAYLOAD_SIZE])
                logIndex = hd[0]
                logLevel = hd[1]
                group    = hd[2]
                subGroup = hd[3]
                code     = hd[4]
                payload_data = recordBytes[LOG_RECORD_BYTE_SIZE-LOG_RECORD_PAYLOAD_SIZE:LOG_RECORD_BYTE_SIZE]
                (g,sg,c, data) = log_record2str(logLevel, group, subGroup, code, payload_data)
                logRecord = {'index':logIndex, 'level':log_level2str(logLevel), 'group':g, 'subGroup':sg, 'code':c, 'payload':data}
                # print(logRecord)
                logRecords.append(logRecord)

            self._status = status

            logData = {'startIndex':startIndex, 'readSize':readSize, 'logRecords':logRecords}
            #print('logInfo : ', str(logData))
            return logData
        else:
            raise UnexpectedMessageTypeError

    def _rpc_make_msg(self, msgType, devId, payloadSize = None, mark=MSG_MARK, crc = None, payload=bytes()):

        if payloadSize == None:
            payloadSize = len(payload)

        m = struct.pack('BBB', mark >> 16 & 0xff,  mark >> 8 & 0xff, mark & 0xff)

        #print(devId, msgType, payloadSize, 0)
        header = struct.pack('BBH', devId, msgType, payloadSize)

        if crc == None:
            crc = struct.pack('B', self._calcCRC(header + payload))
        else:
            crc = struct.pack('B', crc)

        msg = m + crc + header + payload

        return msg

    def _rpc(self, msgType, devId, payloadSize=None, mark=MSG_MARK, crc=None, payload=bytes(), ackfmt=''):

        msg = self._rpc_make_msg(msgType, devId, payloadSize, mark, crc, payload)

        return self._rpc_raw(msg, ackfmt)

    def _rpc_log(self, msgType, devId, payloadSize=None, mark=MSG_MARK, crc=None, payload=bytes(), ackfmt=''):

        msg = self._rpc_make_msg(msgType, devId, payloadSize, mark, crc, payload)

        return self._rpc_log_raw(msg, ackfmt)

    def servo_cmds_are_acceptable(self):
        return self.state() in [STATE_READY, STATE_CURRENT_SERVO, STATE_VELOCITY_SERVO, STATE_POSITION_SERVO]

    def has_reference(self):
        return self.state() in [STATE_CURRENT_SERVO, STATE_VELOCITY_SERVO, STATE_POSITION_SERVO]

    def unnotified_error(self):
        """
        最新の応答に含まれる未通知のエラーが発生していれば1、そうでなければ0(ただし、一度も通信していなければNone)
        """
        if self._status is None:
            return None
        return (self._status & 0b10000) > 0

    def state(self):
        """
        最新の応答に含まれるBuildit Actuatorの状態を返す(ただし、一度も通信していなければNone)
        """
        if self._status is None:
            return None
        return (self._status) & 0xf

    def wait_until(self, devId, pred, timeout_ms = -1):
        """
        Buildit Actuatorに対するquery_servo_statusの結果が述語を成立させるまで待つ

        Parameters
        ----------

        devId : int
            デバイスID
        pred : function
            第一引数がBuildit Actuatorの状態、第二引数がquery_servo_statusの結果に対する述語
        timeout_ms : int
            タイムアウト値(ミリ秒)

        """

        starttime = time.time()
        timeout_sec = timeout_ms / 1000.0

        while True:
            q = self.query_servo_status(devId)
            if pred(self.state(), q):
                break
            if timeout_sec >= 0 and time.time() - starttime > timeout_sec:
                raise WaitUntilTimeoutError((state2str(self.state()), q))

    def wait_until_state(self, devId, targetState, timeout_ms = -1):
        """
        状態遷移完了をポーリングで待つ

        Parameters
        ----------

        devId : int
            デバイスID
        s : int
            状態ID
        timeout_ms : int
            タイムアウト値(ミリ秒)

        """

        self.wait_until(devId, lambda s,q: s == targetState, timeout_ms)

    # フィールドアクセス可能なオブジェクトにして返すべき
    def query_servo_status(self,devId):
        """
        Buildit Actuatorの状態を問い合わせる

        Parameters
        ----------

        devId : int
            デバイスID

        Returns
        -------
        pos : int
            センサで計測された位置

        vel : int
            センサで計測された速度

        cur : int
            センサで計測された電流値

        ref : int
            現在の制御指令値

        temp : int
            センサで計測された温度

        faults : int
            フォルトフラグ(SERVO_FAULT_XXXX)

        """

        return self._rpc(MSG_TYPE_QUERY_SERVO_STATUS_CMD, devId, ackfmt='ihhiBH')

    def hold(self, devId):
        """
        Buildit Actuatorをhold状態に遷移させる

        Parameters
        ----------

        devId : int
            デバイスID

        """
        return self._rpc(MSG_TYPE_HOLD_CMD, devId, ackfmt='')

    def ready(self, devId):
        """
        Buildit Actuatorをready状態に遷移させる

        Parameters
        ----------

        devId : int
            デバイスID

        """
        return self._rpc(MSG_TYPE_READY_CMD, devId, ackfmt='')

    def forceReady(self, devId):
        """
        Buildit Actuatorをready状態に遷移させる

        Parameters
        ----------

        devId : int
            デバイスID

        """
        self.query_servo_status(devId)
        s = self.state()

        if s in [STATE_CURRENT_SERVO, STATE_VELOCITY_SERVO, STATE_POSITION_SERVO]:
            self.stop(devId)
            self.wait_until_state(devId, STATE_READY, timeout_ms = 200)
        elif s == STATE_READY :
            return
        elif s in [STATE_FAULT_FREE, STATE_FAULT_HOLD]:
            self.clear_fault(devId)
            self.ready(devId)
        else:
            self.ready(devId)

    def free(self, devId):
        """
        Buildit Actuatorをfree状態に遷移させる

        Parameters
        ----------

        devId : int
            デバイスID

        """
        return self._rpc(MSG_TYPE_FREE_CMD, devId, ackfmt='')

    def stop(self, devId, timeout_ms=500):
        """
        保護停止

        Parameters
        ----------

        devId : int
            デバイスID

        timeout_ms : int
            タイムアウト[ミリ秒]

        """
        return self._rpc(MSG_TYPE_PROTECTION_STOP_CMD, devId, payload=struct.pack('<H', timeout_ms), ackfmt='')

    def clear_fault(self, devId):
        """
        フォルトフラグをクリアする

        Parameters
        ----------

        devId : int
            デバイスID

        """
        return self._rpc(MSG_TYPE_CLEAR_FAULT_CMD, devId, ackfmt='')

    def reset_rotation(self, devId):
        """
        Buildit Actuatorの累計回転数を初期化する

        Parameters
        ----------

        devId : int
            デバイスID

        """
        return self._rpc(MSG_TYPE_RESET_ROTATION_CMD, devId, ackfmt='')

    def set_ref_current(self, devId, cur):
        """
        電流指令値を設定した上で電流制御状態に遷移させる

        Parameters
        ----------

        devId : int
            デバイスID

        cur : int
            電流指令値

        Returns
        -------
        cur : int
            センサで計測された電流値


        """
        return self._rpc(MSG_TYPE_SET_REF_CURRENT_CMD, devId, payload=struct.pack('h', int(cur)), ackfmt='h')[0]

    def get_ref_current(self, devId):
        """
        電流指令値を取得する
        """
        return self._rpc(MSG_TYPE_GET_REF_CURRENT_CMD, devId, ackfmt='h')[0]

    def set_current_KP(self, devId, v):
        """
        電流制御用比例ゲインを設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bh', PARAM_ID_CURRENT_KP, int(v)), ackfmt='')

    def get_current_KP(self, devId):
        """
        電流制御用比例ゲインを取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_CURRENT_KP), ackfmt='h')[0]

    def set_current_KI(self, devId, v):
        """
        電流制御用積分ゲインを設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bh', PARAM_ID_CURRENT_KI, int(v)), ackfmt='')

    def get_current_KI(self, devId):
        """
        電流制御用積分ゲインを取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_CURRENT_KI), ackfmt='h')[0]

    def set_current_max_Iterm(self, devId, v):
        """
        電流制御用積分項の上限値を設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bi', PARAM_ID_CURRENT_MAX_ITERM, int(v)), ackfmt='')

    def get_current_max_Iterm(self, devId):
        """
        電流制御用積分項の上限値を取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_CURRENT_MAX_ITERM), ackfmt='i')[0]

    def set_current_min_Iterm(self, devId, v):
        """
        電流制御用積分項の下限値を設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bi', PARAM_ID_CURRENT_MIN_ITERM, int(v)), ackfmt='')

    def get_current_min_Iterm(self, devId):
        """
        電流制御用積分項の下限値を取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_CURRENT_MIN_ITERM), ackfmt='i')[0]

    def set_current_max_limit(self, devId, v):
        """
        電流指令値の上限値を設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bh', PARAM_ID_CURRENT_MAX_LIMIT, int(v)), ackfmt='')

    def get_current_max_limit(self, devId):
        """
        電流指令値の上限値を取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_CURRENT_MAX_LIMIT), ackfmt='h')[0]

    def set_current_min_limit(self, devId, v):
        """
        電流指令値の下限値を設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bh', PARAM_ID_CURRENT_MIN_LIMIT, int(v)), ackfmt='')

    def get_current_min_limit(self, devId):
        """
        電流指令値の下限値を取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_CURRENT_MIN_LIMIT), ackfmt='h')[0]

    def set_ref_velocity(self, devId, vel):
        """
        速度指令値を設定した上で速度制御状態に遷移させる

        Parameters
        ----------

        devId : int
            デバイスID

        vel : int
            速度指令値[1/100 * rpm]。符号あり16bit整数値。

        Returns
        -------
        vel : int
            センサで計測された速度[1/100 * rpm]。符号あり16bit整数値。


        """
        return self._rpc(MSG_TYPE_SET_REF_VELOCITY_CMD, devId, payload=struct.pack('h', int(vel)), ackfmt='h')[0]

    def get_ref_velocity(self, devId):
        """
        速度指令値[1/100 * rpm]を取得する 。符号あり16bit整数値。
        """
        return self._rpc(MSG_TYPE_GET_REF_VELOCITY_CMD, devId, ackfmt='h')[0]

    def set_velocity_KP(self, devId, v):
        """
        速度制御用比例ゲインを設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bh', PARAM_ID_VELOCITY_KP, int(v)), ackfmt='')

    def get_velocity_KP(self, devId):
        """
        速度制御用比例ゲインを取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_VELOCITY_KP), ackfmt='h')[0]

    def set_velocity_KI(self, devId, v):
        """
        速度制御用積分ゲインを設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bh', PARAM_ID_VELOCITY_KI, int(v)), ackfmt='')

    def get_velocity_KI(self, devId):
        """
        速度制御用積分ゲインを取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_VELOCITY_KI), ackfmt='h')[0]

    def set_velocity_KD(self, devId, v):
        """
        速度制御用微分ゲインを設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bh', PARAM_ID_VELOCITY_KD, int(v)), ackfmt='')

    def get_velocity_KD(self, devId):
        """
        速度制御用積微分ゲインを取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_VELOCITY_KD), ackfmt='h')[0]

    def set_velocity_max_Iterm(self, devId, v):
        """
        速度制御用積分項の上限値を設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bi', PARAM_ID_VELOCITY_MAX_ITERM, int(v)), ackfmt='')

    def get_velocity_max_Iterm(self, devId):
        """
        速度制御用積分項の上限値を取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_VELOCITY_MAX_ITERM), ackfmt='i')[0]

    def set_velocity_min_Iterm(self, devId, v):
        """
        速度制御用積分項の下限値を設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bi', PARAM_ID_VELOCITY_MIN_ITERM, int(v)), ackfmt='')

    def get_velocity_min_Iterm(self, devId):
        """
        速度制御用積分項の下限値を取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_VELOCITY_MIN_ITERM), ackfmt='i')[0]

    def set_velocity_max_limit(self, devId, v):
        """
        速度指令値の上限値を設定する [1/100 * rpm]
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bh', PARAM_ID_VELOCITY_MAX_LIMIT, int(v)), ackfmt='')

    def get_velocity_max_limit(self, devId):
        """
        速度指令値の上限値を取得する [1/100 * rpm]
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_VELOCITY_MAX_LIMIT), ackfmt='h')[0]

    def set_velocity_min_limit(self, devId, v):
        """
        速度指令値の下限値を設定する [1/100 * rpm]
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bh', PARAM_ID_VELOCITY_MIN_LIMIT, int(v)), ackfmt='')

    def get_velocity_min_limit(self, devId):
        """
        速度指令値の下限値を取得する [1/100 * rpm]
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_VELOCITY_MIN_LIMIT), ackfmt='h')[0]

    def set_ref_position(self, devId, pos):
        """
        位置指令値を設定した上で位置制御状態に遷移させる
        符号あり32bit整数値。

        Parameters
        ----------

        devId : int
            デバイスID

        pos : int
            位置指令値 [360/65536 * 度]

        Returns
        -------
        pos : int
            センサで計測された位置 [360/65536 * 度]


        """
        return self._rpc(MSG_TYPE_SET_REF_POSITION_CMD, devId, payload=struct.pack('i', int(pos)), ackfmt='i')[0]

    def get_ref_position(self, devId):
        """
        位置指令値を取得する [360/65536 * 度] 符号あり32bit整数値。
        """
        return self._rpc(MSG_TYPE_GET_REF_POSITION_CMD, devId, ackfmt='i')[0]

    def set_position_KP(self, devId, v):
        """
        位置制御用比例ゲインを設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bh', PARAM_ID_POSITION_KP, int(v)), ackfmt='')

    def get_position_KP(self, devId):
        """
        位置制御用比例ゲインを取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_POSITION_KP), ackfmt='h')[0]

    def set_position_KI(self, devId, v):
        """
        位置制御用積分ゲインを設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bh', PARAM_ID_POSITION_KI, int(v)), ackfmt='')

    def get_position_KI(self, devId):
        """
        位置制御用積分ゲインを取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_POSITION_KI), ackfmt='h')[0]

    def set_position_KD(self, devId, v):
        """
        位置制御用微分ゲインを設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bh', PARAM_ID_POSITION_KD, int(v)), ackfmt='')

    def get_position_KD(self, devId):
        """
        位置制御用積微分ゲインを取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_POSITION_KD), ackfmt='h')[0]

    def set_position_max_Iterm(self, devId, v):
        """
        位置制御用積分項の上限値を設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bi', PARAM_ID_POSITION_MAX_ITERM, int(v)), ackfmt='')

    def get_position_max_Iterm(self, devId):
        """
        位置制御用積分項の上限値を取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_POSITION_MAX_ITERM), ackfmt='i')[0]

    def set_position_min_Iterm(self, devId, v):
        """
        位置制御用積分項の下限値を設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bi', PARAM_ID_POSITION_MIN_ITERM, int(v)), ackfmt='')

    def get_position_min_Iterm(self, devId):
        """
        位置制御用積分項の下限値を取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_POSITION_MIN_ITERM), ackfmt='i')[0]

    def set_position_max_limit(self, devId, v):
        """
        位置指令値の上限値を設定する [360/65536 * 度]
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bi', PARAM_ID_POSITION_MAX_LIMIT, int(v)), ackfmt='')

    def get_position_max_limit(self, devId):
        """
        位置指令値の上限値を取得する [360/65536 * 度]
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_POSITION_MAX_LIMIT), ackfmt='i')[0]

    def set_position_min_limit(self, devId, v):
        """
        位置指令値の下限値を設定する [360/65536 * 度]
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bi', PARAM_ID_POSITION_MIN_LIMIT, int(v)), ackfmt='')

    def get_position_min_limit(self, devId):
        """
        位置指令値の下限値を取得する [360/65536 * 度]
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_POSITION_MIN_LIMIT), ackfmt='i')[0]

    def set_position_offset(self, devId, v):
        """
        位置センサのユーザーオフセットを設定する [360/65536 * 度]
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<Bh', PARAM_ID_POSITION_OFFSET, int(v)), ackfmt='')

    def get_position_offset(self, devId):
        """
        位置センサのユーザーオフセットを取得する [360/65536 * 度]
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_POSITION_OFFSET), ackfmt='h')[0]

    def set_device_id(self, devId, v):
        """
        デバイスIDを設定する
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<BB', PARAM_ID_DEVICE_ID, int(v)), ackfmt='')

    def get_device_id(self, devId):
        """
        デバイスIDを取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_DEVICE_ID), ackfmt='B')[0]

    def find_device_id(self):
        """
        接続中の応答可能なデバイスのうち最も小さなデバイスIDを返す
        """
        timeout = self._ser.timeout
        self._ser.timeout = 0.05    # sec
        foundId = None
        try:
            for id in range(DEVICE_ID_MAX+1):
                try:
                    self.query_servo_status(devId=id)
                    foundId = id
                    break
                except:
                    pass
        finally:
            self._ser.timeout = timeout

        return foundId

    def get_servo_params(self,devId):
        """
        サーボパラメーターを取得する
        """
    
        params= dict(
        PARAM_ID_CURRENT_KP = self.get_current_KP(devId),
        PARAM_ID_CURRENT_KI = self.get_current_KI(devId),
        PARAM_ID_CURRENT_MAX_ITERM = self.get_current_max_Iterm(devId),
        PARAM_ID_CURRENT_MIN_ITERM = self.get_current_min_Iterm(devId),
        PARAM_ID_CURRENT_MAX_LIMIT = self.get_current_max_limit(devId),
        PARAM_ID_CURRENT_MIN_LIMIT = self.get_current_min_limit(devId),
        
        PARAM_ID_VELOCITY_KP = self.get_velocity_KP(devId),
        PARAM_ID_VELOCITY_KI = self.get_velocity_KI(devId),
        PARAM_ID_VELOCITY_KD = self.get_velocity_KD(devId),
        PARAM_ID_VELOCITY_MAX_ITERM = self.get_velocity_max_Iterm(devId),
        PARAM_ID_VELOCITY_MIN_ITERM = self.get_velocity_min_Iterm(devId),
        PARAM_ID_VELOCITY_MAX_LIMIT = self.get_velocity_max_limit(devId),
        PARAM_ID_VELOCITY_MIN_LIMIT = self.get_velocity_min_limit(devId),
        
        PARAM_ID_POSITION_KP = self.get_position_KP(devId),
        PARAM_ID_POSITION_KI = self.get_position_KI(devId),
        PARAM_ID_POSITION_KD = self.get_position_KD(devId),
        PARAM_ID_POSITION_MAX_ITERM = self.get_position_max_Iterm(devId),
        PARAM_ID_POSITION_MIN_ITERM = self.get_position_min_Iterm(devId),
        PARAM_ID_POSITION_MAX_LIMIT = self.get_position_max_limit(devId),
        PARAM_ID_POSITION_MIN_LIMIT = self.get_position_min_limit(devId),

        PARAM_ID_POSITION_OFFSET = self.get_position_offset(devId)
        )
        #print(params)
        return params

    def set_servo_params(self, devId, params): 
        """
        サーボパラメーターを設定する
        """
       
        self.set_current_KP(devId, params['PARAM_ID_CURRENT_KP'])
        self.set_current_KI(devId, params['PARAM_ID_CURRENT_KI']),
        self.set_current_max_Iterm(devId, params['PARAM_ID_CURRENT_MAX_ITERM']),
        self.set_current_min_Iterm(devId, params['PARAM_ID_CURRENT_MIN_ITERM']),
        self.set_current_max_limit(devId, params['PARAM_ID_CURRENT_MAX_LIMIT']),
        self.set_current_min_limit(devId, params['PARAM_ID_CURRENT_MIN_LIMIT']),
        
        self.set_velocity_KP(devId, params['PARAM_ID_VELOCITY_KP']),
        self.set_velocity_KI(devId, params['PARAM_ID_VELOCITY_KI']),
        self.set_velocity_KD(devId, params['PARAM_ID_VELOCITY_KD']),
        self.set_velocity_max_Iterm(devId, params['PARAM_ID_VELOCITY_MAX_ITERM']),
        self.set_velocity_min_Iterm(devId, params['PARAM_ID_VELOCITY_MIN_ITERM']),
        self.set_velocity_max_limit(devId, params['PARAM_ID_VELOCITY_MAX_LIMIT']),
        self.set_velocity_min_limit(devId, params['PARAM_ID_VELOCITY_MIN_LIMIT']),
        
        self.set_position_KP(devId, params['PARAM_ID_POSITION_KP']),
        self.set_position_KI(devId, params['PARAM_ID_POSITION_KI']),
        self.set_position_KD(devId, params['PARAM_ID_POSITION_KD']),
        self.set_position_max_Iterm(devId, params['PARAM_ID_POSITION_MAX_ITERM']),
        self.set_position_min_Iterm(devId, params['PARAM_ID_POSITION_MIN_ITERM']),
        self.set_position_max_limit(devId, params['PARAM_ID_POSITION_MAX_LIMIT']),
        self.set_position_min_limit(devId, params['PARAM_ID_POSITION_MIN_LIMIT']),

        self.set_position_offset(devId, params['PARAM_ID_POSITION_OFFSET'])

    def save_servo_params(self, devId, fileName=None):
        """
        サーボパラメーターをファイルに保存する
        """
        
        if fileName == None:
            timestr = time.strftime("%Y%m%d-%H%M%S")       
            fileName = "params-"+timestr+".yml"
        
        with open(fileName, "w") as file:
            params = self.get_servo_params(devId)
            yaml.dump(params, file, default_flow_style=False)
        
    def load_servo_params(self, devId, filepath):         
        """
        サーボパラメーターをファイルから読みだす
        """
        
        with open(filepath, "r") as stream:
            try:
                params= yaml.safe_load(stream)
                self.set_servo_params(devId, params)

            except yaml.YAMLError as exc:
                print(exc)    


class UnsafeAmarettoPy(AmarettoPy):
    """
    意図せぬ危険な動作を行う可能性があるメンテナンス用機能
    """

    def __init__(self, port=os.environ.get('AMARETTO_PORT',"/dev/ttyUSB0"), baud=os.environ.get('AMARETTO_BAUD',115200), timeout_ms=3000):
        super().__init__(port, baud, timeout_ms)


    def set_prot_stop_pin_timeout(self, devId, v):
        """
        保護停止ピンによる停止間上限[ms]を設定する
        """
        return self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<BH', PARAM_ID_PROTECTION_STOP_PIN_TIMEOUT, int(v)), ackfmt='')

    def set_stop_control_error_threshold(self, devId, v):
        """
        停止異常閾値を設定する
        """
        return self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<BH', PARAM_ID_STOP_CONTROL_ERROR_THRESHOLD, int(v)), ackfmt='')

    def reset(self, devId):
        """
        ソフトウェアリセットする
        """
        return self._rpc(MSG_TYPE_RESET_CMD, devId, ackfmt='')

    def fault(self, devId, faults):
        """
        任意のフォルトを発生させる

        Parameters
        ----------

        devId : int
            デバイスID

        faults : int
            フォルトIDの論理和


        """
        return self._rpc(MSG_TYPE_FAULT_CMD, devId, payload=struct.pack('H', int(faults)), ackfmt='')

    def debug(self, devId, mode):
        """
        デバッグイベント発生

        Parameters
        ----------

        devId : int
            デバイスID

        mode : int
            モード(0:none, 1:position, 2:velocity)

        """
        return self._rpc(MSG_TYPE_DEBUG_CMD, devId, payload=struct.pack('H', int(mode)), ackfmt='')

    def get_log_info(self, devId):
        """
        ログ情報を取得する

        Parameters
        ----------

        devId : int
            デバイスID

        Returns
        -------
        readableSize : int
            取得可能なログレコード数


        """
        return self._rpc(MSG_TYPE_GET_LOG_INFO_CMD, devId, ackfmt='h')[0]

        """
        ログを出力する

        Parameters
        ----------

        devId : int
            デバイスID

        startIndex : int
            取得するログレコードの開始番号

        readSize : int
            取得するログレコードの個数

        """
    def print_log(self, devId, startIndex = 0, readSize = -1):
        data = self.get_log(devId, startIndex, readSize)
        if len(data['logRecords']) > 0:
            print('startIndex:', data['startIndex'])
            print('readSize:', data['readSize'])
            for record in data['logRecords']:
                #print(record)
                print("{index:10d}:\t{level:s}:\t{group:17s}\t{subGroup:17s}\t{code:s}\t{payload:s}".format(**record))

    def get_log(self, devId, startIndex = 0, readSize = -1):
        """
        ログを取得する

        Parameters
        ----------

        devId : int
            デバイスID

        startIndex : int
            取得するログレコードの開始番号

        readSize : int
            取得するログレコードの個数

        Returns
        -------
        startIndex : int
            取得したログレコードの開始番号

        readSize : int
            取得したログレコードの個数

        logRecords : bytes
            取得したReadSize個分のログレコード
        """
        records = []
        numOfRecords = self.get_log_info(devId)

        if startIndex < 0 :
            startIndex = 0

        if readSize < 0:
            readSize = numOfRecords

        if startIndex + readSize > numOfRecords:
            readSize = min(readSize, numOfRecords - startIndex)

        offset = startIndex
        remain = readSize

        while remain > 0:
            size = min(remain, 10)
            tmp = self._rpc_log(MSG_TYPE_GET_LOG_CMD, devId, payload=struct.pack('hh', int(offset), int(size)), ackfmt='')
            records = records + tmp['logRecords']
            offset = offset + size
            remain = remain - size

        return {'startIndex': startIndex,
                'readSize'  : readSize,
                'logRecords': records}

    def clear_log(self, devId):
        """
        ログを消去する
        """
        return self._rpc(MSG_TYPE_CLEAR_LOG_CMD, devId, ackfmt='')

    def get_power_on_time(self, devId):
        """
        累計通電時間を取得する

        Parameters
        ----------

        devId : int
            デバイスID

        Returns
        -------
        param : int
            累計通電時間

        """
        return self._rpc(MSG_TYPE_GET_LIFE_LOG_CMD, devId, payload=struct.pack('<B', LIFE_LOG_PARAM_ID_POWER_ON_TIME), ackfmt='I')[0]

    def clear_power_on_time(self, devId):
        """
        累計通電時間を0リセットする

        Parameters
        ----------

        devId : int
            デバイスID

        """
        return self._rpc(MSG_TYPE_CLEAR_LIFE_LOG_CMD, devId, payload=struct.pack('<B', LIFE_LOG_PARAM_ID_POWER_ON_TIME), ackfmt='')

    def set_calibration_data(self, devId, v):
        """
        補正値を設定する
        """
        return self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<BH', PARAM_ID_CALIBRATION, int(v)), ackfmt='')

    def get_calibration_data(self, devId):
        """
        補正値を取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_CALIBRATION), ackfmt='H')[0]

    def get_position_sys_offset(self, devId):
        """
        位置センサのシステムオフセットを取得する [360/65536 * 度]
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_POSITION_SYS_OFFSET), ackfmt='H')[0]

    def get_firmware_version(self, devId):
        """
        ファームウェアのバージョン情報を取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_FIRMWARE_VERSION), ackfmt='16s')[0]

    def set_position_sys_offset(self, devId, v):
        """
        位置センサのシステムオフセットを設定する [360/65536 * 度]
        """
        self._rpc(MSG_TYPE_SET_PARAM_CMD, devId, payload=struct.pack('<BH', PARAM_ID_POSITION_SYS_OFFSET, int(v)), ackfmt='')

    def get_prot_stop_pin_timeout(self, devId):
        """
        保護停止ピンによる停止間上限[ms]を取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_PROTECTION_STOP_PIN_TIMEOUT), ackfmt='H')[0]

    def get_stop_control_error_threshold(self, devId):
        """
        停止異常閾値を取得する
        """
        return self._rpc(MSG_TYPE_GET_PARAM_CMD, devId, payload=struct.pack('<B', PARAM_ID_STOP_CONTROL_ERROR_THRESHOLD), ackfmt='I')[0]

