
"""
公式ドライバ GPG-3100 に対応するインターフェースです。
各機能の実装は、個別のボードのドライバにあります。


メソッド一覧
----------

.. list-table:: 
  :header-rows: 1

  * - メソッド
    - 公式ドライバの対応する関数
    - 機能
  
  * - `initialize() <#pyinterface.gpg3100.gpg3100.initialize>`_
    - AdOpen
    - ボードを初期化します


"""

class gpg3100(object):
    def __init__(self, driver):
        self.driver = driver
        self.board_id = driver.board_id
        self.available_ranges = driver.available_ranges
        self.available_ad_channel_num = driver.available_ad_channel_num
        self.available_di_channel_num = driver.available_di_channel_num
        self.available_do_channel_num = driver.available_do_channel_num
        pass
    
    
    def initialize(self):
        """ボードを初期化します
        
        Notes
        -----
        - 以下の処理を実行します:
        
            - ...
        
        - DioOpen 関数に概ね対応しますが、pyinterface には open の概念がありませんので
          initialize() を実行しなくともドライバへアクセス可能です。
        - initialize() を実行しない場合、直前のボード状況が反映されています。
        """
        self.driver.initialize()
        return

    
    def set_sampling_config(self, smpl_ch_req=None, sampling_mode=None, 
                            single_diff=None, smpl_num=None,
                            smpl_event_num=None, smpl_freq=None,
                            trig_point=None, trig_mode=None, trig_delay=None,
                            trig_ch=None, trig_level1=None, trig_level2=None,
                            eclk_edge=None, atrg_pulse=None, trig_edge=None,
                            trig_di=None, fast_mode=None):
        """サンプリング条件を設定します
        (GPG-3100 7. AdSetSamplingConfig)
        
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
                '0_2V'     : 電圧 ユニポーラ 0-2V
                '0_0p125V' : 電圧 ユニポーラ 0-0.125V
                '0_1p25V'  : 電圧 ユニポーラ 0-1.25V
                '0_0P625V' : 電圧 ユニポーラ 0-0.625V
                '0_0P156V' : 電圧 ユニポーラ 0-0.156V
                '0_20mA'   : 電流 ユニポーラ 0-20mA
                '4_20mA'   : 電流 ユニポーラ 4-20mA
                '20mA'     : 電流 バイポーラ +/-20mA
                '1V'       : 電圧 バイポーラ +/-1V
                '2P5V'     : 電圧 バイポーラ +/-2.5V
                '5V'       : 電圧 バイポーラ +/-5V
                '10V'      : 電圧 バイポーラ +/-10V
                '20V'      : 電圧 バイポーラ +/-20V
                '50V'      : 電圧 バイポーラ +/-50V
                '0P125V'   : 電圧 バイポーラ +/-0.125V
                '1P25V'    : 電圧 バイポーラ +/-1.25V
                '0P625V'   : 電圧 バイポーラ +/-0.625V
                '0P156V'   : 電圧 バイポーラ +/-0.156V
                '1P25V_AC'  : 電圧 バイポーラ +/-1.25V (ACカップリング)
                '0P625V_AC' : 電圧 バイポーラ +/-0.625V (ACカップリング)
                '0P156V_AC' : 電圧 バイポーラ +/-0.156V (ACカップリング)
                'GND'       : 内部GND接続
            
            例 : [{'ch_no': 1, 'range': '1V'},
                  {'ch_no': 2, 'range': '1_5V'}]
        
        sampling_mode : str
            サンプリング方式
            'IO'   : I/O 方式
            'FIFO' : FIFO 方式
            'MEM'  : メモリ方式
            'BM'   : バスマスタ方式
            
        single_diff : str
            入力仕様
            'INGLE' : シングルエンド入力
            'DIFF'  : 作動入力
            
        smpl_num : int
            サンプリングするデータの個数
        
        smpl_event_num : int
            通知サンプリング件数
            サンプリングしたデータの個数が smpl_event_num に達するたびに
            イベントが通知されます
            
        smpl_freq : float
            サンプリング周波数 (単位 Hz)
        
        trig_point : str
            トリガポイント
            'START' : スタートトリガ
            'STOP'  : ストップトリガ
            'START_STOP' : スタートストップトリガ
        
        trig_mode : str
            トリガモード
            'FREERUN'   : トリガ無し
            'EXTTRG'    : 外部トリガ
            'EXTTRG_DI' : 外部+DIトリガ
            'LEVEL_P'   : レベルトリガプラス
            'LEVEL_M'   : レベルトリガマイナス
            'LEVEL_D'   : レベルトリガデュアル
            'INRANGE'   : レベルトリガインレンジ
            'OUTRANGE'  : レベルトリガアウトレンジ
            'ETERNITY'  : 無限サンプリング
            'START_P1'  : レベル1立ち上がり
            'START_M1'  : レベル1立ち下がり
            'START_D1'  : レベル1両方
            'START_P2'  : レベル2立ち上がり
            'START_M2'  : レベル2立ち下がり
            'START_D2'  : レベル2両方
            'STOP_P1'  : レベル1立ち上がり
            'STOP_M1'  : レベル1立ち下がり
            'STOP_D1'  : レベル1両方
            'STOP_P2'  : レベル2立ち上がり
            'STOP_M2'  : レベル2立ち下がり
            'STOP_D2'  : レベル2両方
            'ANALOG_FILTER' : アナログトリガフィルタ

        trig_delay : int
            トリガディレイ
        
        trig_ch : int
            トリガ判定を行うチャンネル番号
        
        trig_level1 : float
            トリガレベル1 (単位 V もしくは mA)

        trig_level2 : float
            トリガレベル2 (単位 V もしくは mA)
            
        eclk_edge : str
            外部クロックのエッジ極性
            'DOWN' : 立ち下がり
            'UP'   : 立ち上がり
        
        atrg_pulse : int
            アナログトリガ出力パルス極性
            'LOW'  : LOW パルス
            'HIGH' : HIGH パルス
        
        trig_edge : int
            外部トリガのエッジ極性
            'DOWN' : 立ち下がり
            'UP'   : 立ち上がり
        
        trig_di : int
            汎用デジタル入力端子による外部トリガのマスク
            有効にするDIチャンネル番号のビットを1に設定してください
        
        fast_mode : str
            倍速モードを設定します
            'NORMAL' : 通常モード
            'FAST'   : 倍速モード
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> ad.set_sampling_config([{'ch_no': 1, 'range': '0_1V'}], 'IO',
                                   'SINGLE', 1024, 0, 0.0, 'START', 'FREERUN',
                                   0, 1, 0.0, 0.0, 'DOWN', 'LOW', 'DOWN', 1,
                                   'NORMAL')

        Exceptions
        ----------
        ...
        """
        return self.driver.set_sampling_config(smpl_ch_req, sampling_mode,
                                               single_diff, smpl_num,
                                               smpl_event_num, smpl_freq,
                                               trig_point, trig_mode,
                                               trig_delay, trig_ch, trig_level1,
                                               trig_level2, eclk_edge,
                                               atrg_pulse, trig_edge, trig_di,
                                               fast_mode)


    def get_sampling_config(self):
        """現在設定されているサンプリング条件を取得します
        (GPG-3100 8. AdGetSamplingConfig)
        
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
        >>> ad.get_sampling_config()
        {'smpl_ch_req': [{'ch_no': 1, 'range': '0_1V'}],
        'sampling_mode': 'IO', 'single_diff': 'SINGLE', 'smpl_num': 1024,
        'smpl_event_num': 0, 'smpl_freq': 0.0, 'trig_point': 'START',
        'trig_mode': 'FREERUN', 'trig_delay': 0, 'trig_ch': 1,
        'trig_level1': 0.0, 'trig_level2': 0.0, 'eclk_edge': 'DOWN',
        'atrg_pulse': 'LOW', 'trig_edge': 'DOWN', 'trig_di': 1, 
        'fast_mode': 'NORMAL'}

        Exceptions
        ----------
        ...
        """
        return self.driver.get_sampling_config()


    def get_sampling_data(self, smpl_num):
        """サンプリングデータを取得します
        取得したデータはサンプリングバッファからクリアされます
        (GPG-3100 9. AdGetSamplingData)
        
        Parameters
        ----------
        smpl_num : int
            取得を試みるデータ数
        
        Returns
        -------
        smpl_data : list of float
            取得されたデータ列
        
        Examples
        --------
        >>> ad.get_sampling_data(100)
        [0.12, 0.134, 0.12, ...., 0.145]

        Exceptions
        ----------
        ...
        """
        return self.driver.get_sampling_data(smpl_num)


    def read_sampling_buffer(self, smpl_num, offset):
        """サンプリングバッファからデータを読み取ります
        取得したデータはサンプリングバッファからクリアされません
        (GPG-3100 10. AdReadSamplingBuffer)
        
        Parameters
        ----------
        smpl_num : int
            取得を試みるデータ数
        
        offset : int
            バッファ内のデータ取得を開始するオフセットアドレス
        
        Returns
        -------
        smpl_data : list of float
            取得されたデータ列
        
        Examples
        --------
        >>> ad.read_sampling_buffer(100, 100)
        [0.12, 0.134, 0.12, ...., 0.145]

        Exceptions
        ----------
        ...
        """
        return self.driver.read_sampling_buffer(smpl_num, offset)


    def clear_sampling_data(self):
        """サンプリングバッファをクリアします
        (GPG-3100 11. AdClearSamplingData)
        
        Parameters
        ----------
        なし
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> ad.clear_sampling_data()

        Exceptions
        ----------
        ...
        """
        return self.driver.clear_sampling_data()

    
    def start_sampling(self, sync_flag):
        """サンプリングをスタートします
        (GPG-3100 12. AdStartSampling)
        
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
        >>> ad.start_samplint('SYNC')

        Exceptions
        ----------
        ...
        """
        return self.driver.start_sampling(sync_flag)

    
    def trigger_sampling(self, ch_no, smpl_num):
        """外部トリガモードを設定します
        EXTRG IN トリガが入力されるたびに、1件のサンプリングを行います
        事前にset_sampling_config 関数で、trig_mode='EXTTRG' を指定してください
        (GPG-3100 15. AdTriggerSampling)
        
        Parameters
        ----------
        ch_no : int
            外部トリガを設定するチャンネル
        
        smpl_num : int
            サンプリングを行う件数
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> conf = ad.get_sampling_config()
        >>> conf['trig_mode'] = 'EXTTRG'
        >>> ad.set_sampling_config(conf)
        >>> ad.trigger_sampling(1, 100)

        Exceptions
        ----------
        ...
        """
        return self.driver.trigger_sampling(ch_no, smpl_num)

    
    def stop_sampling(self):
        """サンプリングを停止します
        (GPG-3100 17. AdStopSampling)
        
        Parameters
        ----------
        なし
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> ad.stop_sampling()

        Exceptions
        ----------
        ...
        """
        return self.driver.stop_sampling()

    
    def get_status(self):
        """サンプリング動作状態を取得します
        (GPG-3100 18. AdGetStatus)
        
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
                'NOW_SAMPLING'  : サンプリング動作中
            'smpl_count'  : int : サンプリング済み件数
            'avail_count' : int : サンプリング残り件数
        
        Examples
        --------
        >> ad.get_status()
        {'smpl_status': 'NOW_SAMPLING', 'smpl_count': 123, 'avail_count': 3}

        Exceptions
        ----------
        ...
        """
        return self.driver.get_status()

    
    def input_ad(self, single_diff, smpl_ch_req):
        """1件のサンプリングを行います
        (GPG-3100 19. AdInputAd)
        
        Parameters
        ----------
        single_diff : str
            'SINGLE' : シングルエンド入力
            'DIFF'   : 作動入力
        
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
                '0_2V'     : 電圧 ユニポーラ 0-2V
                '0_0p125V' : 電圧 ユニポーラ 0-0.125V
                '0_1p25V'  : 電圧 ユニポーラ 0-1.25V
                '0_0P625V' : 電圧 ユニポーラ 0-0.625V
                '0_0P156V' : 電圧 ユニポーラ 0-0.156V
                '0_20mA'   : 電流 ユニポーラ 0-20mA
                '4_20mA'   : 電流 ユニポーラ 4-20mA
                '20mA'     : 電流 バイポーラ +/-20mA
                '1V'       : 電圧 バイポーラ +/-1V
                '2P5V'     : 電圧 バイポーラ +/-2.5V
                '5V'       : 電圧 バイポーラ +/-5V
                '10V'      : 電圧 バイポーラ +/-10V
                '20V'      : 電圧 バイポーラ +/-20V
                '50V'      : 電圧 バイポーラ +/-50V
                '0P125V'   : 電圧 バイポーラ +/-0.125V
                '1P25V'    : 電圧 バイポーラ +/-1.25V
                '0P625V'   : 電圧 バイポーラ +/-0.625V
                '0P156V'   : 電圧 バイポーラ +/-0.156V
                '1P25V_AC'  : 電圧 バイポーラ +/-1.25V (ACカップリング)
                '0P625V_AC' : 電圧 バイポーラ +/-0.625V (ACカップリング)
                '0P156V_AC' : 電圧 バイポーラ +/-0.156V (ACカップリング)
                'GND'       : 内部GND接続
            
            例 : [{'ch_no': 1, 'range': '1V'},
                  {'ch_no': 2, 'range': '1_5V'}]
                
        Returns
        -------
        data : list of float
            取得されたデータ
        
        Examples
        --------
        >>> ad.input_ad('SINGLE', [{'ch_no': 1, 'range': '1V'},
                                   {'ch_no': 2, 'range': '1V'},
                                   {'ch_no': 3, 'range': '1V'},
                                   {'ch_no': 4, 'range': '1V'}])
        [0.12, 0.134, 0.12, 0.145]
        
        Exceptions
        ----------
        ...
        """
        return self.driver.input_ad(single_diff, smpl_ch_req)

    
    def input_di(self):
        """DIを読み出します
        (GPG-3100 22. AdInputDI)
        
        Parameters
        ----------
        なし
        
        Returns
        -------
        data : list of int
            DI の状態
        
        Examples
        --------
        >>> ad.input_di()
        [0, 0, 0, 0]

        Exceptions
        ----------
        ...
        """
        return self.driver.input_di()


    def output_do(self, data):
        """DOを設定します
        (GPG-3100 22. AdOutputDO)
        
        Parameters
        ----------
        data : list of int
            DO でアウトプットするチャンネルに1を指定します
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> ad.output_do([0, 0, 1, 1])

        Exceptions
        ----------
        ...
        """
        return self.driver.output_do(data)
