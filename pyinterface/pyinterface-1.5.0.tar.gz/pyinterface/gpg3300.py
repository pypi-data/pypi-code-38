"""
公式ドライバ GPG-3300 に対応するインターフェースです。
各機能の実装は、個別のボードのドライバにあります。
"""


class gpg3300(object):
    def __init__(self, driver):
        self.driver = driver
        self.board_id = driver.board_id
        self.available_ranges = driver.available_ranges
        self.available_da_channel_num = driver.available_da_channel_num
        self.available_di_channel_num = driver.available_di_channel_num
        self.available_do_channel_num = driver.available_do_channel_num
        pass

    def initialize(self):
        """ボードを初期化します
        
        Notes
        -----
        - 以下の処理を実行します:
        
            - ...
        
        - DaOpen 関数に概ね対応しますが、pyinterface には open の概念がありませんので
          initialize() を実行しなくともドライバへアクセス可能です。
        - initialize() を実行しない場合、直前のボード状況が反映されています。
        """
        self.driver.initialize()
        return

    
    def set_sampling_config(self, smpl_ch_req=None, sampling_mode=None,
                            smpl_freq=None, smpl_repeat=None, trig_mode=None,
                            trig_point=None, trig_delay=None, eclk_edge=None,
                            trig_edge=None, trig_di=None):
        """アナログ出力条件を設定します
        (GPG-3300 7. DaSetSamplingConfig)
        
        Parameters
        ----------        
        smpl_ch_req : list of dict
            チャンネル毎のサンプリング条件
            辞書のリストで渡します。辞書には、ch_no, range を含めてください。
            
            ch_no : int : 設定するチャンネル番号
            
            range : str : 設定する電圧/電流レンジ
                指定可能な電圧/電流レンジ
                '0_1V'     : 電圧 ユニポーラ 0-1V
                '0_2P5V'   : 電圧 ユニポーラ 0-2.5V
                '0_5V'     : 電圧 ユニポーラ 0-5V
                '0_10V'    : 電圧 ユニポーラ 0-10V
                '1_5V'     : 電圧 ユニポーラ 1-5V
                '0_20mA'   : 電流 ユニポーラ 0-20mA
                '4_20mA'   : 電流 ユニポーラ 4-20mA
                '0_1mA'    : 電流 ユニポーラ 0-1mA
                '0_100mA'  : 電流 ユニポーラ 0-100mA
                '1V'       : 電圧 バイポーラ +/-1V
                '2P5V'     : 電圧 バイポーラ +/-2.5V
                '5V'       : 電圧 バイポーラ +/-5V
                '10V'      : 電圧 バイポーラ +/-10V
                '20mA'     : 電流 バイポーラ +/-20mA
            
            例 : [{'ch_no': 1, 'range': '1V'},
                  {'ch_no': 2, 'range': '1_5V'}]
        
        sampling_mode : str
            サンプリング方式
            'IO'   : I/O 方式
            'FIFO' : FIFO 方式
            'MEM'  : メモリ方式
        
        smpl_freq : float
            サンプリング周波数 (単位 Hz)
        
        smpl_repeat : int
            アナログ出力動作の繰り返し回数
            1-65535 の範囲で指定します。
        
        trig_mode : str
            トリガモード
            'FREERUN'   : トリガ無し
            'EXTTRG'    : 外部トリガ
            'EXTTRG_DI' : 外部+DIトリガ

        trig_point : str
            トリガポイント
            'START' : スタートトリガ
            'STOP'  : ストップトリガ
            'START_STOP' : スタートストップトリガ
        
        trig_delay : int
            トリガディレイ
        
        trig_edge : int
            外部トリガのエッジ極性
            'DOWN' : 立ち下がり
            'UP'   : 立ち上がり
        
        trig_di : int
            汎用デジタル入力端子による外部トリガのマスク
            有効にするDIチャンネル番号のビットを1に設定してください
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> da.set_sampling_config([{'ch_no': 1, 'range': '0_1V'}], 'IO', 0.0,
                                   1, 'FREERUN', 'START', 0, 'DOWN', 'DOWN', 0)
        
        Exceptions
        ----------
        ...        
        
        """
        return self.driver.set_sampling_config(smpl_ch_req, sampling_mode,
                                               smpl_freq, smpl_repeat,
                                               trig_mode, trig_point,
                                               trig_delay, eclk_edge,
                                               trig_edge, trig_di)

    
    def get_sampling_config(self):
        """現在設定されている出力条件を取得します
        (GPG-3300 8. DaGetSamplingConfig)
        
        Parameters
        ----------
        なし
        
        Returns
        -------
        config : dict
            設定されたサンプリング条件の辞書
            辞書の内容は、set_sampling_config 関数のドキュメント参照
        
        Examples
        --------
        >>> da.get_sampling_config()
        {'smpl_ch_req': [{'ch_no': 1, 'range': '0_1V'}],
        'sampling_mode': 'IO', 'smpl_freq': 0.0, 'smpl_repeat': 1,
        'trig_mode': 'FREERUN', 'trig_point': 'START', 'trig_delay': 0,
        'eclk_edge': 'DOWN', 'trig_edge': 'DOWN', 'trig_di': 0}
        
        Exceptions
        ----------
        ...
        """
        return self.driver.get_sampling_config()


    def set_sampling_data(self, data):
        """出力バッファにデータを登録します
        (GPG-3300 11. DaSetSamplingData)
        
        Parameters
        ----------
        data : list of float
            出力するデータ
            出力する回数 x ch 数 の 2 次元配列で指定する
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> da.set_sampling_data([
            [0.0, 0.0, 0.0, 0.0],
            [0.1, 0.1, 0.1, 0.1],
            [0.2, 0.2, 0.2, 0.2],
        ])
        
        Exceptions
        ----------
        ...
        """
        return self.driver.set_sampling_data(data)

    
    def clear_sampling_data(self):
        """出力バッファをクリアします
        (GPG-3300 12. DaClearSamplingData)
        
        Parameters
        ----------
        なし
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> da.clear_sampling_data()
        
        Exceptions
        ----------
        ...
        """
        return self.driver.clear_sampling_data()

    
    def start_sampling(self, sync_flag):
        """出力をスタートします
        (GPG-3300 13. DaStartSampling)
        
        Parameters
        ----------
        sync_flag : str
            同期か非同期を指定します
            'SYNC'  : 同期
            'ASYNC' : 非同期
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> da.start_sampling('ASYNC')
        
        Exceptions
        ----------
        ...
        """
        return self.driver.start_sampling(sync_flag)
    
    
    def stop_sampling(self):
        """出力を停止します
        (GPG-3300 16. DaStopSampling)
        
        Parameters
        ----------
        なし
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> da.stop_sampling()
        
        Exceptions
        ----------
        ...
        """
        return self.driver.stop_sampling()


    def get_status(self):
        """出力状態を取得します
        (GPG-3300 17. DaGetStatus)
        
        Parameters
        ----------  
        なし
        
        Returns
        -------
        conf : dict
            サンプリング動作状態
            'smpl_status': str : サンプリング状態
                'STOP_SAMPLING' : 停止中
                'WAIT_TRIGGER'  : トリガ待ち状態
                'NOW_SAMPLING'  : 出力動作中
            'smpl_count'   : int : アナログ出力済みの件数
            'avail_count'  : int : 出力されずに残ってる件数
            'avail_repeat' : int : 残り繰り返し回数
        
        Examples
        --------
        >>> da.get_status()
        {'smpl_status': 'NOW_SAMPLING', 'smpl_count': 100, 
        'avail_count': 50, 'avail_repeat': 0}
        
        Exceptions
        ----------
        ...
        """
        return self.driver.get_status()
    
    
    def output_da(self, smpl_ch_req, data):
        """アナログ出力を1件行う
        (GPG-3300 19. DaOutputDA)
        
        Parameters
        ----------
        smpl_ch_req : list of dict
            チャンネル毎のサンプリング条件
            辞書のリストで渡します。辞書には、ch_no, range を含めてください。
            
            ch_no : int : 設定するチャンネル番号
            
            range : str : 設定する電圧/電流レンジ
                指定可能な電圧/電流レンジ
                '0_1V'     : 電圧 ユニポーラ 0-1V
                '0_2P5V'   : 電圧 ユニポーラ 0-2.5V
                '0_5V'     : 電圧 ユニポーラ 0-5V
                '0_10V'    : 電圧 ユニポーラ 0-10V
                '1_5V'     : 電圧 ユニポーラ 1-5V
                '0_20mA'   : 電流 ユニポーラ 0-20mA
                '4_20mA'   : 電流 ユニポーラ 4-20mA
                '0_1mA'    : 電流 ユニポーラ 0-1mA
                '0_100mA'  : 電流 ユニポーラ 0-100mA
                '1V'       : 電圧 バイポーラ +/-1V
                '2P5V'     : 電圧 バイポーラ +/-2.5V
                '5V'       : 電圧 バイポーラ +/-5V
                '10V'      : 電圧 バイポーラ +/-10V
                '20mA'     : 電流 バイポーラ +/-20mA
            
            例 : [{'ch_no': 1, 'range': '1V'},
                  {'ch_no': 2, 'range': '1_5V'}]
        
        data : list of float
            出力するデータ
            配列長は ch 数
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> da.output_da([{'ch_no': 1, 'range': '1V'},
                          {'ch_no': 2, 'range': '1V'},
                          {'ch_no': 3, 'range': '1V'},
                          {'ch_no': 4, 'range': '1V'}],
                         [0.5, 0.5, 0.5, 0.5])
        
        Exceptions
        ----------
        ...
        """
        return self.driver.output_da(smpl_ch_req, data)
    
    
    def input_di(self):
        """DIを読み出します
        (GPG-3300 21. DaInputDI)
        
        Parameters
        ----------
        なし
        
        Returns
        -------
        data : list of int
            DI の状態
        
        Examples
        --------
        >>> da.input_di()
        [0, 0, 0, 0]
        
        Exceptions
        ----------
        ...
        """
        return self.driver.input_di()


    def output_do(self, data):
        """DOを設定します
        (GPG-3300 22. DaOutputDO)
        
        Parameters
        ----------
        data : list of int
            DO でアウトプットするチャンネルに1を指定します
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> da.input_do([0, 0, 1, 1])
        
        Exceptions
        ----------
        ...
        """
        return self.driver.input_do(data)


    def set_current_dir(self, direction):
        """電流の出力方向を設定します : CPZ-340516のみ
        (GPG-3300 29. DaSetCurrentDir)
        
        Parameters
        ----------
        direction : flag
            ch1-ch8 の電流の出力方向を設定します
            逆方向に出力する場合、フラグを設定します
            
            例) 全 ch 逆方向にする : 'CH1 CH2 CH3 CH4 CH5 CH6 CH7 CH8'
                ch5, 6 だけ逆方向にする : 'CH5 CH6'
        
        Returns
        -------
        なし
        
        Examples
        --------
        da.set_current_dir('CH1 CH2')
        
        Exceptions
        ----------
        ...
        """
        return self.driver.set_current_dir(direction)


    def get_current_dir(self):
        """電流出力方向を取得します : CPZ-340516のみ
        (GPG-3300 30. DaGetCurrentDir)
        
        Parameters
        ----------
        なし
        
        Returns
        -------
        direction : flag
            電流出力方向のフラグ
            詳細は、set_current_dir を参照
        
        Examples
        --------
        >>> da.get_current_dir()
        ''
        
        Exceptions
        ----------
        ...
        """
        return self.driver.get_current_dir()


    def set_power_supply(self, onoff):
        """外部電源の供給/遮断を設定します : CPZ-340516のみ
        (GPG-3300 31. DaSetPowerSupply)
        
        Parameters
        ----------
        onoff : str
            外部電源の供給/遮断
            'ON' : 供給
            'OFF' : 遮断
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> da.set_power_supply('ON')
        
        Exceptions
        ----------
        ...
        """
        return self.driver.set_power_supply(onoff)


    def get_power_supply(self):
        """外部電源の供給/遮断状況を取得します : CPZ-340516のみ
        (GPG-3300 32. DaGetPowerSupply)
        
        Parameters
        ----------
        なし
        
        Returns
        -------
        onoff : str
            外部電源の供給/遮断状況
            'ON' : 供給
            'OFF' : 遮断
        
        Examples
        --------
        >>> da.get_power_supply()
        'ON'
        
        Exceptions
        ----------
        ...
        """
        return self.driver.get_power_supply()


    def get_relay_status(self):
        """出力リレーの設定状態を取得します : CPZ-340516のみ
        (GPG-3300 33. DaGetRelayStatus)
        
        Parameters
        ----------
        なし
        
        Returns
        -------
        status : flag
            ch1-ch8 の出力リレーの設定状態
            
            例) 全 ch ON の場合 : 'CH1 CH2 CH3 CH4 CH5 CH6 CH7 CH8'
                ch5, 6 だけ ON の場合 : 'CH5 CH6'
        
        Examples
        --------
        >>> da.get_relay_status()
        'CH1 CH2'
        
        Exceptions
        ----------
        ...
        """
        return self.driver.get_relay_status()


    def get_0v_status(self):
        """出力の過電圧状態を取得します : CPZ-340516のみ
        (GPG-3300 34. DaGet0VStatus)
        
        Parameters
        ----------
        なし
        
        Returns
        -------
        status : dict
            'low' : flag : - 過電圧を検出した ch のフラグ
                           例) ch2, ch3 が - 過電圧の時 : 'CH2 CH3'
            'high' : flag : + 過電圧を検出した ch のフラグ
                            例) ch2, ch3 が + 過電圧の時 : 'CH2 CH3'
        
        Examples
        --------
        >>> da.get_0v_status()
        {'low': '', 'high': ''}
        
        Exceptions
        ----------
        ...
        """
        return self.driver.get_0v_status()


    def set_excess_voltage(self, oven, exoven):
        """過電圧検出の有効/無効を切り替えます : CPZ-340516のみ
        (GPG-3300 35. DaSetExcessVoltage)
        
        Parameters
        ----------
        oven : str
            過電圧検出機能の有効/無効
            'ON' : 有効
            'OFF' : 無効
        
        exoven : str
            外部電源の過電圧検出機能の有効/無効
            'ON' : 有効
            'OFF' : 無効
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> da.set_excess_voltage('ON', 'ON')
        
        Exceptions
        ----------
        ...
        """
        return self.driver.set_excess_voltage(oven, exoven)


