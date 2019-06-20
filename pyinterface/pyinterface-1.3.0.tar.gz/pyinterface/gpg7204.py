
"""
公式ドライバ GPG-7204 に対応するインターフェースです。
各機能の実装は、個別のボードのドライバにあります。
"""


class gpg7204(object):
    def __init__(self, driver):
        self.driver = driver
        pass

    def initialize(self, axis=1):
        return self.driver.initialize(axis)

    def off_inter_lock(self, axis=1):
        """ソフトウェアインタロックを解除します。
        インタロック信号が入力されるとデバイスはロックされます。
        インタロック信号を解除した後、off_inter_lock() を実行し、
        ソフトウェアロックを解除する事で、起動関数を実行できるようになります。
        (GPG-7204 4. MtrOffInterLock)
        
        Parameters
        ----------
        axis : int
            設定する軸
         
        Returns
        -------
        なし
         
        Examples
        --------
        >>> # 軸 2 のソフトウェアインタロックを解除する
        >>> mtr.off_inter_lofck(2)
         
        Exceptions
        ----------
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。
        """
        return self.driver.off_inter_lock(axis)

    
    def set_base_clock(self, clock, axis=1):
        """基準クロック/速度倍率を設定します。
        (GPG-7204 5. MtrSetBaseClock)
        
        Parameters
        ----------
        clock : str or int
            xxx-7204 の場合:
                基準クロックを文字列で指定します。
                'CLOCK_1M' :  基準クロック 1 MHz
                'CLOCK_1_4M' :  基準クロック 1/4 MHz
                'CLOCK_1_16M' :  基準クロック 1/16 MHz (default)
            
            xxx-742020 の場合:
                速度倍率を int で指定します。
                範囲 : 1 - 65535
        
        axis : int
            設定する軸
         
        Returns
        -------
        なし
         
        Examples
        --------
        >>> # 軸 1 の clock を 1/16 MHz にする
        >>> mtr.set_base_clock('CLOCK_1_16M', 1)
         
        Exceptions
        ----------
        clock が指定可能な文字列/数字出ない場合、ValueError となります。
        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.set_base_clock(axis)

    
    def set_pulse_out(self, mode, config, axis=1):
        """パルス出力の設定を行います。
        (GPG-7204 6. MtrSetPulseOut)
        
        Parameters
        ----------
        mode : str
            設定項目
            'METHOD' : パルス出力モードを設定します
            'FINISH_FLAG' : 動作完了フラグのタイミングを設定します
                            (xxx-742020/Tx のみ)
        
        config : str
            設定内容
            
            mode = 'METHOD' の場合:
                出力方式、論理をスペースで区切って指定します。
                例) 'CW/CCW N', 'OUT/DIR OUT-N DIR-N'
        
                xxx-7204:
                    出力方式
                        'CW/CCW' : 2 パルス方式 (default)
                        'OUT/DIR' : パルス/ディレクション方式
                    論理
                        'N' : 負論理 (default)
                        'P' : 正論理
                
                xxx-742020/Tx:
                    出力方式
                        'CW/CCW' : 2 パルス方式 (default)
                        'OUT/DIR' : パルス/ディレクション方式
                    OUT論理
                        'OUT-N' : 負論理 (default)
                        'OUT-P' : 正論理                    
                    DIR論理
                        'DIR-N' : 負論理 (default)
                        'DIR-P' : 正論理
                    
            mode = 'FINISH_FLAG' の場合:
                'PULSE_OUT' : パルス出力後に動作完了フラグ ON (default)
                'INP' : パルス出力後、INP 信号入力により、動作完了フラグ ON
        
        axis : int
            設定する軸
         
        Returns
        -------
        なし
         
        Examples
        --------
        >>> # 軸 1 を CW/CCW, 負論理に設定する
        >>> mtr.set_pulse_out('METHOD', 'CW/CCW N', 1)
         
        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.set_pulse_out(mode, config, axis)

    
    def set_limit_config(self, mode, config, axis=1):
        """制御信号の設定を行います。
        (GPG-7204 7. MtrSetLimitConfig)
        
        Parameters
        ----------
        mode : str
            設定項目
            'MASK' : 入力マスクを設定します (xxxx-7204 のみ)
            'LOGIC' : 入力論理を設定します
        
        config : str
            設定内容
            
            mode = 'MASK' の場合:
                無効にする入力をスペースで区切って指定します。
                default は有効です。指定しなければ有効になります。
                入力 : +SD -SD +EL -EL ORG ALM
                例) 全て有効 : ''
                    全て無効 : '+SD -SD +EL -EL ORG ALM'
                    ORG だけ無効 : 'ORG'
        
            mode = 'LOGIC' の場合:
                入力論理を正にする論理スペースで区切って指定します。
                default は負です。指定しなければ負論理になります。
                入力 : +SD -SD +EL -EL ORG ALM
                例) 全て負論理 : ''
                    全て正論理 : '+SD -SD +EL -EL ORG ALM'
                    ALM だけ正論理 : 'ALM'
        
        axis : int
            設定する軸
         
        Returns
        -------
        なし
         
        Examples
        --------
        >>> # 軸 1 の 入力を全て有効にする
        >>> mtr.set_limit_config('MASK', '', 1)

        >>> # 軸 1 の 入力を +EL -EL だけ全て無効にする
        >>> mtr.set_limit_config('MASK', '+EL -EL', 1)
         
        >>> # 軸 1 の 入力を +SD -EL ORG だけ全て正論理にする
        >>> mtr.set_limit_config('LOGIC', '+SD -EL ORG', 1)
        
        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.set_limit_config(mode, config, axis)

    
    def set_motion(self, mode, acc_mode, low_speed, speed, acc, step, axis=1):
        """動作パラメータを設定します
        (GPG-7204 10. MtrSetMotion)
        
        Parameters
        ----------
        mode : str
            設定する動作
            'JOG' : 連続動作のパラメータを設定します
            'ORG' : 原点復帰動作のパラメータを設定します
            'PTP' : PTP 動作のパラメータを設定します
        
        acc_mode : str
            加減速の種類
            'NORMAL' : 直線加減速
            'SIN' : S字加減速
            'ORIGINAL' : 自由曲線加減速 (xxx-7204 のみ)
        
        low_speed : int
            移動速度 (pps)

        speed : int
            移動速度 (pps)
        
        acc : int
            加速パルス数 (pps)

        dec : int
            減速パルス数 (pps)

        step : int
            移動パルス数 (pps)
            JOG, ORG の場合、+ (CW) 方向は 1, - (CCW) 方向は -1 を指定する。
        
        axis : int
            設定する軸
         
        Returns
        -------
        なし
         
        Examples
        --------
        >>> # + 方向に JOG 動作
        >>> mtr.set_motion('JOG', 'SIN', 100, 1000, 500, 1, 1)
        
        >>> # -500 パルス動かす
        >>> mtr.set_motion('PTP', 'SIN', 100, 1000, 500, -500, 1)
        
        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.set_motion(mode, acc_mode, low_speed, speed, acc,
                                      step, axis)
    

    def get_base_clock(self, axis=1):
        """基準クロック/速度倍率を取得します
        (GPG-7204 11. MtrGetBaseClock)
        
        Parameters
        ----------
        axis : int
            取得する軸
         
        Returns
        -------
        xxx-7204 の場合:
            clock : str
                'CLOCK_1M' : 1 MHz
                'CLOCK_1_4M' : 1/4 MHz
                'CLOCK_1_16M' : 1/16 MHz
        
        xxx-742020/Tx の場合:
            clock : int
                速度倍率
         
        Examples
        --------
        >>> mtr.get_base_clock(1)
        'CLOCK_1_16M'
        
        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.get_base_clock(axis)


    def get_pulse_out(self, mode, axis=1):
        """パルス出力の設定を取得します
        (GPG-7204 12. MtrGetPulseOut)
        
        Parameters
        ---------- 
        mode : str
            確認項目
            'METHOD' : パルス出力モードを設定します
            'FINISH_FLAG' : 動作完了フラグのタイミングを設定します
                            (xxx-742020/Tx のみ)
        
        axis : int
            取得する軸
         
        Returns
        -------
        config : str
            設定内容
            
            mode = 'METHOD' の場合:
                出力方式、論理をスペースで区切って表示します。
                例) 'CW/CCW N', 'OUT/DIR OUT-N DIR-N'
        
                xxx-7204:
                    出力方式
                        'CW/CCW' : 2 パルス方式 (default)
                        'OUT/DIR' : パルス/ディレクション方式
                    論理
                        'N' : 負論理 (default)
                        'P' : 正論理
                
                xxx-742020/Tx:
                    出力方式
                        'CW/CCW' : 2 パルス方式 (default)
                        'OUT/DIR' : パルス/ディレクション方式
                    OUT論理
                        'OUT-N' : 負論理 (default)
                        'OUT-P' : 正論理                    
                    DIR論理
                        'DIR-N' : 負論理 (default)
                        'DIR-P' : 正論理
                    
            mode = 'FINISH_FLAG' の場合:
                'PULSE_OUT' : パルス出力後に動作完了フラグ ON (default)
                'INP' : パルス出力後、INP 信号入力により、動作完了フラグ ON
         
        Examples
        --------
        >>> mtr.get_pulse_out('METHOD', 1)
        'CW/CCW N'
        
        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.get_pulse_out(mode, axis)
    
    
    def get_limit_config(self, mode, axis=1):
        """制御信号の設定を取得します
        (GPG-7204 13. MtrGetLimitConfig)
        
        Parameters
        ---------- 
        mode : str
            取得項目
            'MASK' : 入力マスクを設定します (xxxx-7204 のみ)
            'LOGIC' : 入力論理を設定します
        
        axis : int
            取得する軸
         
        Returns
        -------
        config : str
            設定内容
            
            mode = 'MASK' の場合:
                無効にする入力をスペースで区切って指定します。
                default は有効です。指定しなければ有効になります。
                入力 : +SD -SD +EL -EL ORG ALM
                例) 全て有効 : ''
                    全て無効 : '+SD -SD +EL -EL ORG ALM'
                    ORG だけ無効 : 'ORG'
        
            mode = 'LOGIC' の場合:
                入力論理を正にする論理スペースで区切って指定します。
                default は負です。指定しなければ負論理になります。
                入力 : +SD -SD +EL -EL ORG ALM
                例) 全て負論理 : ''
                    全て正論理 : '+SD -SD +EL -EL ORG ALM'
                    ALM だけ正論理 : 'ALM'

        Examples
        --------
        >>> mtr.get_limit_config('MASK', 1)
        ''
        
        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.get_limit_config(mode, axis)
    

    def get_motion(self, mode, axis=1):
        """動作パラメータを取得します
        (GPG-7204 16. MtrGetMotion)
        
        Parameters
        ---------- 
        mode : str
            取得する動作
            'JOG' : 連続動作のパラメータを設定します
            'ORG' : 原点復帰動作のパラメータを設定します
            'PTP' : PTP 動作のパラメータを設定します
        
        axis : int
            取得する軸
         
        Returns
        -------
        config : dict
            設定内容
            
            'acc_mode' : str
                加減速の種類
                'NORMAL' : 直線加減速
                'SIN' : S字加減速
                'ORIGINAL' : 自由曲線加減速 (xxx-7204 のみ)
        
            'low_speed' : int
                移動速度 (pps)

            'speed' : int
                移動速度 (pps)
        
            'acc' : int
                加速パルス数 (pps)

            'dec' : int
                減速パルス数 (pps)

            'step' : int
                移動パルス数 (pps)
                JOG, ORG の場合、+ (CW) 方向は 1, - (CCW) 方向は -1 を指定する。

        Examples
        --------
        >>> mtr.get_motion('JOG', 1)
        {'acc_mode': 'SIN', 'low_speed': 100, 'speed': 1000,
        'acc': 500, 'step': 1}
        
        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.get_motion(mode, axis)
    
    
    def start_motion(self, mode, axis=1):
        """動作を起動します
        (GPG-7204 17. MtrStartMotion)
        
        Parameters
        ---------- 
        mode : str
            起動する動作
            'JOG' : 連続動作のパラメータを設定します
            'ORG' : 原点復帰動作のパラメータを設定します
            'PTP' : PTP 動作のパラメータを設定します
        
        axis : int
            起動する軸
         
        Returns
        -------
        なし

        Examples
        --------
        >>> mtr.start_motion('JOG', 1)
        
        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.start_motion(mode, axis)
    

    def single_step(self, direction, axis=1):
        """1パルス出力します
        (GPG-7204 18. MtrSingleStep)
        
        Parameters
        ---------- 
        direction : str or int
            移動方向
            str の場合 : 
                'CW' : + 方向
                'CCW' : - 方向
        
            int の場合 :
                1 : CW 方向
                -1 : CCW 方向
        
        axis : int
            移動する軸
         
        Returns
        -------
        なし

        Examples
        --------
        >>> CW に駆動
        >>> mtr.single_step(1, 1)

        >>> CW に駆動
        >>> mtr.single_step('CW', 1)

        >>> CCW に駆動
        >>> mtr.single_step(-1, 1)

        >>> CCW に駆動
        >>> mtr.single_step('CCW', 1)
        
        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.single_step(direction, axis)
    

    def stop_motion(self, mode='IMMEDIATE', axis=1):
        """動作を停止します
        (GPG-7204 20. MtrStopMotion)
        
        Parameters
        ---------- 
        mode : str
            停止方法
            'DEC' :  減速停止
            'IMMEDIATE' : 即時停止 (default)
        
        axis : int
            停止する軸
         
        Returns
        -------
        なし

        Examples
        --------
        >>> # 減速停止
        >>> mtr.stop_motion('DEC', 1)

        >>> # 即時停止
        >>> mtr.stop_motion('IMMEDIATE', 1)
        
        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.stop_motion(mode, axis)
    
    
    def change_speed(self, speed, mode='ACCDEC', axis=1):
        """移動速度変更します
        (GPG-7204 21. MtrChangeSpeed)
        
        Parameters
        ---------- 
        speed : int
            変更後の速度 (pps)
        
        mode : str
            速度変更方法
            'IMMEDIATE' : 即時変更
            'ACCDEC' :  加減速変更 (default)
        
        axis : int
            変更する軸
         
        Returns
        -------
        なし

        Examples
        --------
        >>> # 加減速変更
        >>> mtr.change_speed('ACCDEC', 1)

        >>> # 即時速変更
        >>> mtr.change_speed('IMMEDIATE', 1)
        
        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.change_speed(speed, mode, axis)
    

    def get_status(self, mode='ALL', axis=1):
        """ステータスを取得します
        (GPG-7204 22. MtrGetStatus)
        
        Parameters
        ---------- 
        mode : str
            取得する項目
            'BUSY' : 動作状態
            'FINISH' : 終了ステータス
            'LIMIT' : 制御信号の入力状態
            'INTERLOCK' : インタロックの入力状態
            'ERROR' : エラーステータス
            'ALL' :  全て取得 (default)
        
        axis : int
            取得する軸
         
        Returns
        -------
        status : dict

        Examples
        --------
        >>> mtr.get_status('ALL', 1)
        {'busy': ..., 'interlock': ..., 'limit': ..., 'error': ...}
        
        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.get_status(mode, axis)
    

    def read_counter(self, axis=1):
        """パルスカウンタ値を取得します
        (GPG-7204 24. MtrReadCounter)
        
        Parameters
        ---------- 
        axis : int
            取得する軸
         
        Returns
        -------
        count : int
            現在位置

        Examples
        --------
        >>> mtr.read_counter(1)
        1234

        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.read_counter(axis)

    
    def write_counter(self, count, axis=1):
        """パルスカウンタ値を書き込みます
        (GPG-7204 25. MtrWriteCounter)
        
        Parameters
        ---------- 
        count : int
            書き込むカウント値
        
        axis : int
            取得する軸
         
        Returns
        -------
        なし

        Examples
        --------
        >>> mtr.write_counter(12345, 1)

        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.write_counter(count, axis)

    
    def clear_counter(self, axis=1):
        """パルスカウンタ値をクリアします
        (GPG-7204 26. MtrClearCounter)
        
        Parameters
        ---------- 
        axis : int
            取得する軸
         
        Returns
        -------
        なし

        Examples
        --------
        >>> mtr.clear_counter(1)

        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.clear_counter(axis)

    
    def output_do(self, do, axis=1):
        """DO を設定します
        (GPG-7204 27. MtrOutputDO)
        
        Parameters
        ---------- 
        do : list
            DO の出力を 0 high, 1 low で設定します
            リスト長 : xxx-7204 = 4, xxx-742020/Tx = 16
        
        axis : int
            取得する軸
         
        Returns
        -------
        なし

        Examples
        --------
        >>> mtr.output_do([0,1,1,0], 1)

        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.output_do(do, axis)

    
    def input_di(self, axis=1):
        """DO を設定します
        (GPG-7204 27. MtrOutputDO)
        
        Parameters
        ---------- 
        axis : int
            取得する軸
         
        Returns
        -------
        di : list
            DI の入力を 0 high, 1 low で設定します
            リスト長 : xxx-7204 = 4, xxx-742020/Tx = 16

        Examples
        --------
        >>> mtr.output_do(1)
        [0,0,1,1]

        Exceptions
        ----------        
        axis がボードの軸数を越す場合 ValueError となります。
        ボードの軸数は、num_axis に格納されています。        
        """
        return self.driver.input_di(axis)

    
