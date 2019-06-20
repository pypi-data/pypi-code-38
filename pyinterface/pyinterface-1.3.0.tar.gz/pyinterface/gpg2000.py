
"""
公式ドライバ GPG-2000 に対応するインターフェースです。
各機能の実装は、個別のボードのドライバにあります。


メソッド一覧
----------

.. list-table:: 
  :header-rows: 1

  * - メソッド
    - 公式ドライバの対応する関数
    - 機能
  
  * - `initialize() <#pyinterface.gpg2000.gpg2000.initialize>`_
    - DioOpen
    - ボードを初期化します

  * - `input_point(start, num) <#pyinterface.gpg2000.gpg2000.input_point>`_
    - DioInputPoint
    - デジタル入力を任意点数取得します

  * - `input_byte(range_) <#pyinterface.gpg2000.gpg2000.input_byte>`_
    - DioInputByte
    - デジタル入力を1byte単位で取得します

  * - `input_word(range_) <#pyinterface.gpg2000.gpg2000.input_word>`_
    - DioInputWord
    - デジタル入力を2byte単位で取得します

  * - `input_dword() <#pyinterface.gpg2000.gpg2000.input_dword>`_
    - DioInputDword
    - デジタル入力を4byte単位で取得します

  * - `output_point(data, start) <#pyinterface.gpg2000.gpg2000.output_point>`_
    - DioOutputPoint
    - デジタル出力を任意点数設定します

  * - `output_byte(range_) <#pyinterface.gpg2000.gpg2000.output_byte>`_
    - DioOutputByte
    - デジタル出力を1byte単位で設定します

  * - `output_word(range_) <#pyinterface.gpg2000.gpg2000.output_word>`_
    - DioOutputWord
    - デジタル出力を2byte単位で設定します

  * - `output_dword() <#pyinterface.gpg2000.gpg2000.output_dword>`_
    - DioOutputDword
    - デジタル出力を4byte単位で設定します
 
  * - `set_latch_status(enable) <#pyinterface.gpg2000.gpg2000.set_latch_status>`_
    - DioSetLatchStatus
    - ラッチ回路の接続を設定します

  * - `get_latch_status() <#pyinterface.gpg2000.gpg2000.get_latch_status>`_
    - DioGetLatchStatus
    - ラッチ回路の接続状態を取得します

  * - `get_ack_status() <#pyinterface.gpg2000.gpg2000.get_ack_status>`_
    - DioGetAckStatus
    - ACK2, STB2 端子の接続状態を取得します

  * - `set_ack_pulse_command(ack, pulse) <#pyinterface.gpg2000.gpg2000.set_ack_pulse_command>`_
    - DioSetAckPulseCommand
    - ACK1, PULS.OUT1 の出力制御を設定します

  * - `get_stb_status() <#pyinterface.gpg2000.gpg2000.get_stb_status>`_
    - DioGetStbStatus
    - STB1, ACK1 端子の接続状態を取得します

  * - `set_stb_pulse_command(stb, pulse) <#pyinterface.gpg2000.gpg2000.set_stb_pulse_command>`_
    - DioSetStbPulseCommand
    - STB2, PULS.OUT2 の出力制御を設定します

"""

from . import core
import struct

class gpg2000(object):
    num_input = 0
    num_output = 0
    available_input_byte_ranges = []
    available_input_word_ranges = []
    available_input_dword_ranges = []
    available_output_byte_ranges = []
    available_output_word_ranges = []
    available_output_dword_ranges = []
    
    
    def __init__(self, driver):
        self.driver = driver
        pass
    
    
    def initialize(self):
        """ボードを初期化します
        
        Notes
        -----
        - 以下の処理を実行します:
        
            - デジタル出力を全て 0 に
            - ラッチ設定の初期化
            - ACK 設定の初期化
            - STB 設定の初期化
        
        - DioOpen 関数に概ね対応しますが、pyinterface には open の概念がありませんので
          initialize() を実行しなくともドライバへアクセス可能です。
        - initialize() を実行しない場合、直前のボード状況が反映されています。
        """
        self.driver.initialize()
        return

    
    def input_point(self, start, num):
        """デジタル入力を任意点数取得します。
        (GPG-2000 3. DioInputPoint)
        
        Parameters
        ----------
        start : int
           取得する最初のチャンネルを指定します。
           start は 1 から数えます (IN1 は start=1 に対応)。
        num : int
           取得する個数を指定します。
        
        Returns
        -------
        list (int)
           指定したチャンネルのデジタル入力状況のリスト。
           入力状態との対応は下記です:
             1 = 外部回路 ON
             0 = 外部回路 OFF
        
        Examples
        --------
        >>> # IN2 - IN6 のデジタル入力状況を取得します
        >>> dio.input_point(2, 5)
        [1, 0, 1, 0, 1]
        
        Exceptions
        ----------
        start + num がボードの ch 数を越す場合 ValueError となります。
        ボードの ch 数は、num_input に格納されています。
        """
        return self.driver.input_point(start, num)

    
    def output_point(self, data, start):
        """デジタル出力を任意点数設定します。
        (GPG-2000 4. DioOutputPoint)
         
        Parameters
        ----------
        data : list (int)
           設定するデジタル出力状況のリストです。
           1 = ON, 0 = OFF で指定します。
        start : int
           設定する最初のチャンネルを指定します。
           start は 1 から数えます (IN1 は start=1 に対応)。
         
        Returns
        -------
        なし
         
        Examples
        --------
        >>> # OUT3 より 4 チャンネルのデジタル出力を ON にします         
        >>> dio.output_point([1,1,1,1], 3)
         
        Exceptions
        ----------
        start + num がボードの ch 数を越す場合 ValueError となります。
        ボードの ch 数は、num_output に格納されています。
        """
        return self.driver.output_point(data, start)

    
    def input_byte(self, range_):
        """デジタル入力を1byte(8点)単位で取得します。
        (GPG-2000 5. DioInputByte)
                
        Parameters
        ----------
        range_ : str
            デジタル入力状況を取得する範囲を指定します。
            ボードで使用可能なレンジは available_input_byte_ranges に格納されています。
            
            .. list-table:: 
                :header-rows: 1
        
                * - `range_`
                  - 取得するチャンネル
        
                * - 'IN1_8' 
                  - IN1 から IN8 まで
        
                * - 'IN9_16' 
                  - IN9 から IN16 まで
        
                * - 'IN17_24' 
                  - IN17 から IN24 まで
        
                * - 'IN25_32' 
                  - IN25 から IN32 まで
        
                * - 'IN33_40' 
                  - IN33 から IN40 まで
        
                * - 'IN41_48' 
                  - IN41 から IN48 まで
        
                * - 'IN49_56' 
                  - IN49 から IN56 まで
        
                * - 'IN57_64' 
                  - IN57 から IN64 まで
        
        Returns
        -------
        list
            指定したチャンネルのデジタル入力状況のリスト (length=8)
        
        Examples
        --------
        >>> # IN9 - IN16 のデジタル入力状況を取得します        
        >>> dio.input_byte('IN9_16')
        [1, 1, 0, 0, 1, 0, 1, 0]
        
        Exceptions
        ----------
        ボードが対応していない range_ が入力されると ValueError となります。
        ボードで使用可能なレンジは available_input_byte_ranges に格納されています。
        """
        return self.driver.input_byte(range_)


    def input_word(self, range_):
        """デジタル入力を2byte(16点)単位で取得します。
        (GPG-2000 6. DioInputWord)
        
        Parameters
        ----------
        range_ : str
            デジタル入力状況を取得する範囲を指定します。
            ボードで使用可能なレンジは available_input_word_ranges に格納されています。
        
            .. list-table:: 
                :header-rows: 1
        
                * - `range`
                  - 取得するチャンネル
        
                * - 'IN1_16' 
                  - IN1 から IN16 まで
        
                * - 'IN17_32' 
                  - IN17 から IN32 まで
        
                * - 'IN33_48' 
                  - IN33 から IN48 まで
        
                * - 'IN49_64' 
                  - IN49 から IN64 まで
        
        Returns
        -------
        list
            指定したチャンネルのデジタル入力状況のリスト (length=16)
        
        Examples
        --------
        >>> # IN1 - IN16 のデジタル入力状況を取得します
        >>> dio.input_word('IN1_16')
        [1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0]
        
        Exceptions
        ----------
        ボードが対応していない range_ が入力されると ValueError となります。
        ボードで使用可能なレンジは available_input_word_ranges に格納されています。
        """
        return self.driver.input_word(range_)


    def input_dword(self, range_):
        """デジタル入力を4byte(32点)取得します。
        (GPG-2000 7. DioInputDword)
        
        Parameters
        ----------
        range_ : str
            デジタル入力状況を取得する範囲を指定します
            ボードで使用可能なレンジは available_input_dword_ranges に格納されています。
            
            .. list-table:: 
                :header-rows: 1
        
                * - `range`
                  - 取得するチャンネル
        
                * - 'IN1_32' 
                  - IN1 から IN32 まで
        
                * - 'IN33_64' 
                  - IN33 から IN64 まで
        
        Returns
        -------
        list
            デジタル入力状況のリスト (length=32)
        
        Examples
        --------
        >>> # IN1 - IN32 のデジタル入力状況を取得します
        >>> dio.input_dword()
        [1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0,
         1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0]
        
        Exceptions
        ----------
        ボードが対応していない range_ が入力されると ValueError となります。
        ボードで使用可能なレンジは available_input_dword_ranges に格納されています。
        """
        return self.driver.input_dword(range_)


    def output_byte(self, range_, data, fmt=''):
        """デジタル出力を1byte(8点)単位で設定します
        (GPG-2000 8. DioOutputByte)
        
        Parameters
        ----------
        range_ : str
            デジタル出力状況を設定する範囲を指定します
            ボードで使用可能なレンジは available_output_byte_ranges に格納されています。
            
            .. list-table:: 
                :header-rows: 1
        
                * - `range_`
                  - 設定するチャンネル
        
                * - 'OUT1_8' 
                  - OUT1 から OUT8 まで
        
                * - 'OUT9_16' 
                  - OUT9 から OUT16 まで
        
                * - 'OUT17_24' 
                  - OUT17 から OUT24 まで
        
                * - 'OUT25_32' 
                  - OUT25 から OUT32 まで
        
                * - 'OUT33_40' 
                  - OUT33 から OUT40 まで
        
                * - 'OUT41_48' 
                  - OUT41 から OUT48 まで
        
                * - 'OUT49_56' 
                  - OUT49 から OUT56 まで
        
                * - 'OUT57_64' 
                  - OUT57 から OUT64 まで
        
        data : list or int
            list の場合
                設定するデジタル出力状況のリストです (1:ON, 0:OFF)。
                length は 8 にしてください。
            int の場合
                signed char の bytes に変換して設定されます。
            unsigned int を設定したい場合
                data に正の int を代入し、fmt に '<B' を指定してください。
        
        fmt : str (option)
            fmt を指定した場合、data を fmt に従って pack しようとします。
            fmt に使用する文字列は、struct モジュールの書式です。
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> # OUT1 より 1 byte 分のチャンネルのデジタル出力を設定します
        >>> dio.output_byte([1,0,1,0,1,0,1,0], 'OUT1_8')
        
        Exceptions
        ----------
        ボードが対応していない range_ が入力されると ValueError となります。
        ボードで使用可能なレンジは available_output_byte_ranges に格納されています。
        
        data が list もしくは tuple の場合、length が 8 でないと ValueError となります。
        """
        if fmt != '':
            d = struct.pack(fmt, data)
            
        elif type(data) in [list, tuple]:
            if len(data) != 8:
                msg = 'data length must be 8, not {0}'.format(len(data))
                raise ValueError(msg)
            d = core.list2bytes(data)
            
        elif type(data) == int:
            d = struct.pack('<b', data)
            
        else:
            msg = 'type of data must be list or int, not {0}'.format(type(data))
            raise ValueError(msg)

        return self.driver.output_byte(range_, d)

    
    def output_word(self, range_, data, fmt=''):
        """デジタル出力を2byte(16点)単位で設定します。
        (GPG-2000 9. DioOutputWord)
        
        Parameters
        ----------
        range_ : str
            デジタル出力状況を設定する範囲を指定します。
            ボードで使用可能なレンジは available_output_word_ranges に格納されています。
            
            .. list-table:: 
                :header-rows: 1
        
                * - `range_`
                  - 設定するチャンネル
        
                * - 'OUT1_16'
                  - OUT1 から OUT16 まで
        
                * - 'OUT17_32'
                  - OUT17 から OUT32 まで
                * - 'OUT33_48' 
                  - OUT33 から OUT48 まで
        
                * - 'OUT49_64' 
                  - OUT49 から OUT64 まで
        
        data : list or int
            list の場合
                設定するデジタル出力状況のリストです (1:ON, 0:OFF)。
                length は 16 にしてください。
            int の場合
                signed short の bytes に変換して設定されます。
            unsigned int を設定したい場合
                data に正の int を代入し、fmt に '<H' を指定してください。
        
        fmt : str (option)
            fmt を指定した場合、data を fmt に従って pack しようとします。
            fmt に使用する文字列は、struct モジュールの書式です。
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> # OUT17 より 2 byte 分のチャンネルのデジタル出力を設定します
        >>> dio.output_word([1,0,1,0,1,0,1,0,1,1,1,1,0,0,0,0], 'OUT17_32')
        
        Exceptions
        ----------
        ボードが対応していない range_ が入力されると ValueError となります。
        ボードで使用可能なレンジは available_output_word_ranges に格納されています。
        
        data が list もしくは tuple の場合、length が 16 でないと ValueError となります。
        """
        if fmt != '':
            d = struct.pack(fmt, data)
            
        elif type(data) in [list, tuple]:
            if len(data) != 16:
                msg = 'data length must be 16, not {0}'.format(len(data))
                raise ValueError(msg)
            d = core.list2bytes(data)
            
        elif type(data) == int:
            d = struct.pack('<h', data)
            
        else:
            msg = 'type of data must be list or int, not {0}'.format(type(data))
            raise ValueError(msg)
        
        return self.driver.output_word(range_, d)
    

    def output_dword(self, range_, data, fmt=''):
        """デジタル出力を4byte(32点)設定します。
        (GPG-2000 10. DioOutputDword)
        
        Parameters
        ----------
        range_ : str
            デジタル入力状況を取得する範囲を指定します
            ボードで使用可能なレンジは available_output_dword_ranges に格納されています。
            
            .. list-table:: 
                :header-rows: 1
        
                * - `range`
                  - 取得するチャンネル
        
                * - 'OUT1_32' 
                  - OUT1 から OUT32 まで
        
                * - 'OUT33_64' 
                  - OUT33 から OUT64 まで
        
        data : list or int or float
            list の場合
                設定するデジタル出力状況のリストです (1:ON, 0:OFF)。
                length は 32 にしてください。
            int の場合
                signed int の bytes に変換して設定されます。
                fmt に '<i' を指定した際と等価です。
            float の場合
                float の bytes に変換して設定されます。
                fmt に '<f' を指定した際と等価です。
            unsigned int を設定したい場合
                data に正の int を代入し、fmt に '<I' を指定してください。
        
        fmt : str (option)
            fmt を指定した場合、data を fmt に従って pack しようとします。
            fmt に使用する文字列は、struct モジュールの書式です。
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> # OUT1 より 4byte 分のチャンネルのデジタル出力を設定します
        >>> d = [1,0,1,0,1,0,1,0,1,1,1,1,0,0,0,0,1,0,1,0,1,0,1,0,1,1,1,1,0,0,0,0]
        >>> dio.output_dword(d)
        
        Exceptions
        ----------
        ボードが対応していない range_ が入力されると ValueError となります。
        ボードで使用可能なレンジは available_output_dword_ranges に格納されています。
        
        data が list もしくは tuple の場合、length が 32 でないと ValueError となります。
        """        
        if fmt != '':
            d = struct.pack(fmt, data)
            
        elif type(data) in [list, tuple]: 
            if len(data) != 32:
                msg = 'data length must be 32, not {0}'.format(len(data))
                raise ValueError(msg)
            d = core.list2bytes(data)
            
        elif type(data) == int:
            d = struct.pack('<i', data)
            
        elif type(data) == float:
            d = struct.pack('<f', data)
            
        else:
            msg = 'type of data must be list, int or float, not {0}'.format(type(data))
            raise ValueError(msg)

        return self.driver.output_dword(range_, d)


    def set_latch_status(self, enable=''):
        """ラッチ回路の接続を設定します。
        (GPG-2000 11. DioSetLatchStatus)
        
        Parameters
        ----------
        enable : str
            ラッチ回路接続を有効にするポートを指定します。
            複数指定する場合、スペースで区切って指定してください。
            指定されなかったポートは、ラッチ回路接続 "無効" になります。
        
            .. list-table:: 
                :header-rows: 1
                
                * - `enable`
                  - 有効にするチャンネル
                
                * - 'PORT0'
                  - IN1 - IN8
            
                * - 'PORT1'
                  - IN9 - IN16
            
                * - 'PORT2'
                  - IN17 - IN24 
        
                * - 'PORT3'
                  - IN25 - IN32
        
                * - 'PORT4'
                  - IN33 - IN40
        
                * - 'PORT5'
                  - IN41 - IN48
        
                * - 'PORT6'
                  - IN49 - IN56
        
                * - 'PORT7'
                  - IN57 - IN64
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> dio.set_latch_status('PORT0 PORT3')
        """
        return self.driver.set_latch_status(enable)


    def get_latch_status(self):
        """ラッチ回路の接続状態を取得します。
        (GPG-2000 12. DioGetLatchStatus)
        
        Returns
        -------
        flagged_bytes
           ラッチ回路の接続状態
             1 = 有効
             0 = 無効

           PORT とデジタル入力 ch との対応
        
            .. list-table:: 
                :header-rows: 1
                * - PORT番号
                  - 対応するチャンネル
                
                * - 'PORT0'
                  - IN1 - IN8
            
                * - 'PORT1'
                  - IN9 - IN16
            
                * - 'PORT2'
                  - IN17 - IN24 
        
                * - 'PORT3'
                  - IN25 - IN32
        
                * - 'PORT4'
                  - IN33 - IN40
        
                * - 'PORT5'
                  - IN41 - IN48
        
                * - 'PORT6'
                  - IN49 - IN56
        
                * - 'PORT7'
                  - IN57 - IN64
        """
        return self.driver.get_latch_status()

    
    def get_ack_status(self):
        """ACK2, STB2 端子の接続状態を取得します
        (GPG-2000 13. DioGetAckStatus)
        """
        return self.driver.get_ack_status()

    
    def set_ack_pulse_command(self, ack='', pulse=''):
        """ACK1, PULS.OUT1 の出力制御を設定します
        (GPG-2000 14. DioSetAckPulseCommand)
        
        Parameters
        ----------
        ack : str 
            ACK 出力制御
        
            .. list-table:: 
                :header-rows: 1
         
                * - `ack`
                  - 動作
        
                * - ''
                  - 何もしません
        
                * - 'ACK10'
                  - clear ACK1 terminal (Low -> High)
        
                * - 'ACK11'
                  - set ACK1 terminal (High -> Low)
        
        pulse : str
            PULSE.OUT1 出力制御
        
            .. list-table:: 
                :header-rows: 1
         
                * - `pulse`
                  - 動作
        
                * - ''
                  - 何もしません
        
                * - 'PO10'
                  - set PULS.OUT1 terminal High
        
                * - 'PO11'
                  - set PULS.OUT1 terminal Low
        
                * - 'PO12'
                  - output Low pulse from PULS.OUT1 terminal
        """
        return self.driver.set_ack_pulse_command(ack, pulse)

    
    def get_stb_status(self):
        """STB1, ACK1 端子の接続状態を取得します
        (GPG-2000 15. DioGetStbStatus)
        """
        return self.driver.get_stb_status()

    
    def set_stb_pulse_command(self, stb='', pulse=''):
        """STB2, PULS.OUT2 の出力制御を設定します。
        (GPG-2000 16. DioSetStbPulseCommand)
        
        Parameters
        ----------
        stb : str
            STB 出力制御
        
            .. list-table:: 
                :header-rows: 1
         
                * - `stb`
                  - 動作
        
                * - ''
                  - 何もしません
        
                * - 'STB20'
                  - clear STB2 terminal (Low -> High)
        
                * - 'STB21'
                  - set STB2 terminal (High -> Low)
        
        pulse : str
            PULSE.OUT2 出力制御
        
            .. list-table:: 
                :header-rows: 1
         
                * - `pulse`
                  - 動作
        
                * - ''
                  - 何もしません
        
                * - 'PO20'
                  - set PULS.OUT2 terminal High
        
                * - 'PO21'
                  - set PULS.OUT2 terminal Low
        
                * - 'PO22'
                  - output Low pulse from PULS.OUT2 terminal
        """
        return self.driver.set_stb_pulse_command(stb, pulse)

    
    def get_reset_in_status(self):
        """外部リセット入力信号の状態を取得します。
        (GPG-2000 17. DioGetResetInStatus)
        """
        return self.driver.get_reset_in_status()

    
