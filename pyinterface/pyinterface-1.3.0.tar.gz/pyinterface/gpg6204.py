
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
  
  * - `initialize() <#pyinterface.gpg6204.gpg6204.initialize>`_
    - PencOpen
    - ボードを初期化します

  * - `reset(ch) <#pyinterface.gpg6204.gpg6204.reset>`_
    - PencReset
    - 指定したチャンネルのカウンタをリセットします

  * - `set_mode(mode, direction, equal, latch, ch) <#pyinterface.gpg6204.gpg6204.set_mode>`_
    - PencSetMode
    - パルスカウンタの動作モード、カウンタ方向、一致検出機能、ラッチ条件を設定します

  * - `get_mode(ch) <#pyinterface.gpg6204.gpg6204.get_mode>`_
    - PencGetMode
    - パルスカウンタの動作モード、カウンタ方向、一致検出機能、ラッチ条件を取得します

  * - `set_z_mode(clear_condition, latch_condition, z_polarity, l_polarity, ch) <#pyinterface.gpg6204.gpg6204.set_z_mode>`_
    - PencSetZMode
    - Z相の極性、外部信号によるカウンタクリア・ラッチ条件を設定します

  * - `get_z_mode(ch) <#pyinterface.gpg6204.gpg6204.get_z_mode>`_
    - PencGetZMode
    - Z相の極性、外部信号によるカウンタクリア・ラッチ条件を取得します

  * - `enable_count(ch) <#pyinterface.gpg6204.gpg6204.enable_count>`_
    - PencEnableCount
    - カウンタ動作を有効にします

  * - `disable_count(ch) <#pyinterface.gpg6204.gpg6204.disable_count>`_
    - PencDisableCount
    - カウンタ動作を無効にします

  * - `set_counter(count, unsigned, ch) <#pyinterface.gpg6204.gpg6204.set_counter>`_
    - PencSetCounter
    - カウンタ値を設定します

  * - `get_counter(unsigned, ch) <#pyinterface.gpg6204.gpg6204.get_counter>`_
    - PencGetCounter
    - カウンタ値を取得します

  * - `set_comparator(count, unsigned, ch) <#pyinterface.gpg6204.gpg6204.set_comparator>`_
    - PencSetComparator
    - 比較カウンタ値を設定します

  * - `get_comparator(unsigned, ch) <#pyinterface.gpg6204.gpg6204.get_comparator>`_
    - PencGetComparator
    - 比較カウンタ値を取得します。

  * - `get_status(ch) <#pyinterface.gpg6204.gpg6204.get_status>`_
    - PencGetStatus
    - カウンタのステータスを取得します

"""

import struct


class gpg6204(object):
    available_ch = []
    
    def __init__(self, driver):
        self.driver = driver
        self.available_ch = driver.available_ch
        pass

    
    def _verify_ch(self, ch):
        if ch not in self.available_ch:
            msg = 'ch must be in {self.available_ch}, not {ch}'.format(**locals())
            raise ValueError(msg)
        return
    
    def _verify_boolint(self, value, name):
        if value not in [0, 1, None]:
            msg = '{name} must be 0 or 1, not {value}'.format(**locals())
            raise ValueError(msg)
        return
    
    def _verify_flags(self, flags, availables):
        if flags is None: return
        for f in flags.split():
            if f not in availables:
                msg = '{flags} must be in {availables}, not {f}'.format(**locals())
                raise ValueError(msg)
            continue
        return
    
    def _verify_list(self, value, name, available):
        if value is None: return
        if value not in available:
            msg = '{name} must be {available}, not {value}'.format(**locals())
            raise ValueError(msg)
        return
    
    
    def initialize(self):
        """ボードを初期化します
        
        Notes
        -----
        - 以下の処理を実行します:
        
            - ...
        
        - PencOpen 関数に概ね対応しますが、pyinterface には open の概念がありませんので
          initialize() を実行しなくともドライバへアクセス可能です。
        - initialize() を実行しない場合、直前のボード状況が反映されています。
        """
        self.driver.initialize()
        return

    
    def reset(self, ch=1):
        """指定されたチャンネルのカウンタをリセットします。
        (GPG-6204 3. PencReset)
        
        Parameters
        ----------
        ch : int
            カウンタをリセットするチャンネルを指定します。
            指定できるチャンネル範囲はボードに依ります。
            利用可能なチャンネルは available_ch に格納されています。
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> enc.reset(2)

        Exceptions
        ----------
        ボードが対応していない ch が指定された場合、ValueError となります。
        ボードで使用可能なチャンネル範囲は available_ch に格納されています。
        """
        self._verify_ch(ch)
        return self.driver.reset(ch)
    
    def set_mode(self, mode=None, direction=None, equal=None, latch=None, ch=1):
        """パルスカウンタの動作モード、カウンタ方向、一致検出機能、ラッチ条件を設定します。
        (GPG-6204 4. PencSetMode)
        
        Parameters
        ----------
        mode : str ('SEL0', 'SEL1', 'MD0' and/or 'MD1')
            動作モードを指定します。フラグの組み合わせと動作モードの対応関係は下記です。
            default = None の時、何も変化しません。
            
            .. list-table:: 
                :header-rows: 1
        
                * - `mode`
                  - 動作モード
                  - カウント逓倍
                  - クリアモード
        
                * - '' 
                  - ゲート付き単相パルス
                  - 1 逓倍
                  - 非同期
        
                * - 'SEL0' 
                  - ゲート付き単相パルス
                  - 2逓倍
                  - 非同期
       
                * - 'MD0'
                  - 位相差パルス
                  - 1 逓倍
                  - 非同期

                * - 'MD0 SEL0'
                  - 位相差パルス
                  - 2 逓倍
                  - 非同期

                * - 'MD0 SEL1'
                  - 位相差パルス
                  - 4 逓倍
                  - 非同期
        
                * - 'MD0 MD1'
                  - 位相差パルス
                  - 1 逓倍
                  - 同期

                * - 'MD0 MD1 SEL0'
                  - 位相差パルス
                  - 2 逓倍
                  - 同期

                * - 'MD0 MD1 SEL1'
                  - 位相差パルス
                  - 4 逓倍
                  - 同期
        
                * - 'MD1'
                  - Up/Down パルス
                  - 1 逓倍
                  - 非同期
        
        direction : int (0 or 1)
            カウンタ方向
            0 = カウンタ Up
            1 = カウンタ Down
            default = None の時、何も変化しません。
        
        equal : int (0 or 1)
            一致検出の有効/無効
            0 = 一致検出を行わない
            1 = 一致検出を行う
            default = None の時、何も変化しません。
        
        latch : int (0 or 1)
            ラッチ方法
            0 = ソフトウェアラッチ
            1 = 外部ラッチ
            default = None の時、何も変化しません。
        
        ch : int 
            設定するチャンネルを指定します。
            指定できるチャンネル範囲はボードに依ります。
            利用可能なチャンネルは available_ch に格納されています。
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> # 位相差パルスカウントモード、4逓倍、非同期クリア、カウンタUP、
        >>> # 一致検出なし、ソフトウェアラッチ、を設定します
        >>> enc.set_mode(mode='MD0 SEL1', direction=0, equal=0, latch=0)

        Exceptions
        ----------
        ボードが対応していない ch が指定された場合、ValueError となります。
        ボードで使用可能なチャンネル範囲は available_ch に格納されています。
        """
        self._verify_ch(ch)
        self._verify_flags(mode, ['MD1', 'MD0', 'SEL1', 'SEL0'])
        self._verify_boolint(direction, 'direction')
        self._verify_boolint(equal, 'equal')
        self._verify_boolint(latch, 'latch')
        return self.driver.set_mode(mode, direction, equal, latch, ch)

    
    def get_mode(self, ch=1):
        """パルスカウンタの動作モード、カウンタ方向、一致検出機能、ラッチ条件を取得します。
        (GPG-6204 5. PencGetMode)
        
        Parameters
        ----------
        ch : int 
            取得するチャンネルを指定します。
            指定できるチャンネル範囲はボードに依ります。
            利用可能なチャンネルは available_ch に格納されています。

        Returns
        -------
        ret : dict
            'mode' : str ('SEL0', 'SEL1', 'MD0' and/or 'MD1')
                動作モードを指定します。フラグの組み合わせと動作モードの対応関係は下記です。
            
                .. list-table:: 
                    :header-rows: 1
            
                    * - `mode`
                      - 動作モード
                      - カウント逓倍
                      - クリアモード
            
                    * - '' 
                      - ゲート付き単相パルス
                      - 1 逓倍
                      - 非同期
            
                    * - 'SEL0' 
                      - ゲート付き単相パルス
                      - 2逓倍
                      - 非同期
           
                    * - 'MD0'
                      - 位相差パルス
                      - 1 逓倍
                      - 非同期
    
                    * - 'MD0 SEL0'
                      - 位相差パルス
                      - 2 逓倍
                      - 非同期
    
                    * - 'MD0 SEL1'
                      - 位相差パルス
                      - 4 逓倍
                      - 非同期
            
                    * - 'MD0 MD1'
                      - 位相差パルス
                      - 1 逓倍
                      - 同期
    
                    * - 'MD0 MD1 SEL0'
                      - 位相差パルス
                      - 2 逓倍
                      - 同期
    
                    * - 'MD0 MD1 SEL1'
                      - 位相差パルス
                      - 4 逓倍
                      - 同期
            
                    * - 'MD1'
                      - Up/Down パルス
                      - 1 逓倍
                      - 非同期
            
            'direction' : int (0 or 1)
                カウンタ方向
                0 = カウンタ Up
                1 = カウンタ Down
            
            'equal' : int (0 or 1)
                一致検出の有効/無効
                0 = 一致検出を行わない
                1 = 一致検出を行う
            
            'latch' : int (0 or 1)
                ラッチ方法
                0 = ソフトウェアラッチ
                1 = 外部ラッチ            
            
        Examples
        --------
        >>> # ch2 のモードを取得します
        >>> enc.get_mode(ch=2)
        {'mode': 'MD0 SEL1', 'direction': 0, 'equal': 0, 'latch': 0}

        Exceptions
        ----------
        ボードが対応していない ch が指定された場合、ValueError となります。
        ボードで使用可能なチャンネル範囲は available_ch に格納されています。
        """
        self._verify_ch(ch)
        return self.driver.get_mode(ch)

    
    def set_z_mode(self, clear_condition=None, latch_condition=None,
                   z_polarity=None, l_polarity=None, ch=1):
        """Z 相の極性、外部信号によるカウンタクリア・ラッチ条件を設定します。
        (GPG-6204 6. PencSetZMode)
        
        Parameters
        ----------
        clear_condition : str ('CLS0' or 'CLS1')
            カウンタクリア条件:
            ''     = 外部信号でカウンタクリアしない
            'CLS0' = Z相のみでカウンタクリアする
            'CLS1' = Z相とラッチ信号が有効の時にカウンタクリアする
        
        latch_condition : str ('LTS0' or 'LTS1')
            カウンタラッチ条件:
            ''     = 外部信号でラッチしない
            'LTS0' = ラッチ信号のみでラッチする
            'LTS1' = ラッチ信号とZ相が有効の時にラッチする
        
        z_polarity : int (0 or 1)
            Z相の極性
            0 = Z相通常 (Highで有効)
            1 = Z相反転 (Lowで有効)
        
        l_polarity : int (0 or 1)
            L信号の極性 (PCI/CPZ/CTP-6204は未対応)
            0 = 反転 (Lowで有効)
            1 = 通常 (Highで有効)
        
        ch : int
            設定するチャンネルを指定します。
            指定できるチャンネル範囲はボードに依ります。
            利用可能なチャンネルは available_ch に格納されています。

        Returns
        -------
        なし
        
        Examples
        --------
        >>> # Z相によるカウンタクリアを有効、Z相反転にする
        >>> enc.set_z_mode(clear_condition='CLS0', z_polarity=1, ch=2)

        Exceptions
        ----------
        ボードが対応していない ch が指定された場合、ValueError となります。
        ボードで使用可能なチャンネル範囲は available_ch に格納されています。
        """
        self._verify_ch(ch)
        self._verify_list(clear_condition, 'clear_condition', ['', 'CLS0', 'CLS1'])
        self._verify_list(latch_condition, 'latch_condition', ['', 'LTS0', 'LTS1'])
        self._verify_boolint(z_polarity, 'z_polarity')
        self._verify_boolint(l_polarity, 'l_polarity')
        return self.driver.set_z_mode(clear_condition, latch_condition,
                                      z_polarity, l_polarity, ch)


    def get_z_mode(self, ch=1):
        """Z 相の極性、外部信号によるカウンタクリア・ラッチ条件を取得します。
        (GPG-6204 7. PencGetZMode)
        
        Parameters
        ----------
        ch : int
            取得するチャンネルを指定します。
            指定できるチャンネル範囲はボードに依ります。
            利用可能なチャンネルは available_ch に格納されています。
        
        Returns
        -------
        ret : dict
            'clear_condition' : str ('CLS0' or 'CLS1')
                カウンタクリア条件:
                ''     = 外部信号でカウンタクリアしない
                'CLS0' = Z相のみでカウンタクリアする
                'CLS1' = Z相とラッチ信号が有効の時にカウンタクリアする
            
            'latch_condition' : str ('LTS0' or 'LTS1')
                カウンタラッチ条件:
                ''     = 外部信号でラッチしない
                'LTS0' = ラッチ信号のみでラッチする
                'LTS1' = ラッチ信号とZ相が有効の時にラッチする
            
            'z_polarity' : int (0 or 1)
                Z相の極性
                0 = Z相通常 (Highで有効)
                1 = Z相反転 (Lowで有効)
            
            'l_polarity' : int (0 or 1)
                L信号の極性 (PCI/CPZ/CTP-6204は未対応)
                0 = 反転 (Lowで有効)
                1 = 通常 (Highで有効)
            
        Examples
        --------
        >>> enc.get_z_mode(ch=1)
        {'clear_condition': 'CLS0', 'latch_condition': '', 
         'z_polarity': 1, 'l_polarity': 0}

        Exceptions
        ----------
        ボードが対応していない ch が指定された場合、ValueError となります。
        ボードで使用可能なチャンネル範囲は available_ch に格納されています。
        """
        self._verify_ch(ch)
        return self.driver.get_z_mode(ch)


    def enable_count(self, ch=1):
        """カウンタ動作を有効にします。
        (GPG-6204 10. PencEnableCount)
        
        Parameters
        ----------        
        ch : int
            カウンタ動作を有効にするチャンネルを指定します。
            指定できるチャンネル範囲はボードに依ります。
            利用可能なチャンネルは available_ch に格納されています。
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> # ch1 のカウンタを有効にする
        >>> enc.enable_count(ch=1)

        Exceptions
        ----------
        ボードが対応していない ch が指定された場合、ValueError となります。
        ボードで使用可能なチャンネル範囲は available_ch に格納されています。 
        """
        self._verify_ch(ch)
        return self.driver.enable_count(ch)

    
    def disable_count(self, ch=1):
        """カウンタ動作を無効にします。
        (GPG-6204 10. PencEnableCount)
        
        Parameters
        ----------        
        ch : int
            カウンタ動作を無効にするチャンネルを指定します。
            指定できるチャンネル範囲はボードに依ります。
            利用可能なチャンネルは available_ch に格納されています。
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> # ch1 のカウンタを無効にする
        >>> enc.disable_count(ch=1)
        
        Exceptions
        ----------
        ボードが対応していない ch が指定された場合、ValueError となります。
        ボードで使用可能なチャンネル範囲は available_ch に格納されています。 
        """
        self._verify_ch(ch)
        return self.driver.disable_count(ch)

    
    def set_counter(self, count, unsigned=True, ch=1):
        """カウンタ値を設定します。
        (GPG-6204 13. PencSetCounter)
        
        Parameters
        ----------
        count : int
            設定するカウント値
        
        unsigned : bool
            True の場合、count は unsigned long として解釈されます。
            False の場合、count は (signed) long として解釈されます。
            default = True です。
        
        ch : int
            設定するチャンネルを指定します。
            指定できるチャンネル範囲はボードに依ります。
            利用可能なチャンネルは available_ch に格納されています。
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> # ch1 のカウンタに 1234 を設定する
        >>> enc.set_counter(1234, ch=1)
        
        Exceptions
        ----------
        ボードが対応していない ch が指定された場合、ValueError となります。
        ボードで使用可能なチャンネル範囲は available_ch に格納されています。 
        """
        self._verify_ch(ch)
        
        if unsigned:
            d = struct.pack('<L', count)
        else:
            d = struct.pack('<l', count)
            pass
            
        return self.driver.set_counter(d, ch)
    

    def get_counter(self, unsigned=True, ch=1):
        """カウンタ値を取得します。
        (GPG-6204 14. PencGetCounter)
        
        Parameters
        ----------
        unsigned : bool
            True の場合、count は unsigned long として解釈されます。
            False の場合、count は (signed) long として解釈されます。
            default = True です。
        
        ch : int
            設定するチャンネルを指定します。
            指定できるチャンネル範囲はボードに依ります。
            利用可能なチャンネルは available_ch に格納されています。
        
        Returns
        -------
        count : int
            ラッチされたカウンタ値を取得します。
            unsigned = True の時、count 値は unsigned long として解釈されます。
            unsigned = False の時、count 値は (signed) long として解釈されます。
        
        Examples
        --------
        >>> # ch1 のカウンタ値を取得する。
        >>> enc.get_count(ch=1)
        1234
        
        Exceptions
        ----------
        ボードが対応していない ch が指定された場合、ValueError となります。
        ボードで使用可能なチャンネル範囲は available_ch に格納されています。 
        """
        self._verify_ch(ch)

        c = self.driver.get_counter(ch)
        
        if unsigned:
            return c.to_uint()
        else:
            return c.to_int()
            
        return 
    

    def set_comparator(self, count, unsigned=True, ch=1):
        """比較カウンタ値を設定します。
        (GPG-6204 17. PencSetComparator)
        
        Parameters
        ----------
        count : int
            設定するカウント値
        
        unsigned : bool
            True の場合、count は unsigned long として解釈されます。
            False の場合、count は (signed) long として解釈されます。
            default = True です。
        
        ch : int
            設定するチャンネルを指定します。
            指定できるチャンネル範囲はボードに依ります。
            利用可能なチャンネルは available_ch に格納されています。
        
        Returns
        -------
        なし
        
        Examples
        --------
        >>> # ch1 の比較カウンタに 1234 を設定する
        >>> enc.set_comparator(1234, ch=1)
        
        Exceptions
        ----------
        ボードが対応していない ch が指定された場合、ValueError となります。
        ボードで使用可能なチャンネル範囲は available_ch に格納されています。 
        """
        self._verify_ch(ch)
        
        if unsigned:
            d = struct.pack('<L', count)
        else:
            d = struct.pack('<l', count)
            pass
            
        return self.driver.set_comparator(d, ch)
    

    def get_comparator(self, unsigned=True, ch=1):
        """比較カウンタ値を取得します。
        (GPG-6204 18. PencGetComparator)
        
        Parameters
        ----------
        unsigned : bool
            True の場合、count は unsigned long として解釈されます。
            False の場合、count は (signed) long として解釈されます。
            default = True です。
        
        ch : int
            設定するチャンネルを指定します。
            指定できるチャンネル範囲はボードに依ります。
            利用可能なチャンネルは available_ch に格納されています。
        
        Returns
        -------
        count : int
            ラッチされたカウンタ値を取得します。
            unsigned = True の時、count 値は unsigned long として解釈されます。
            unsigned = False の時、count 値は (signed) long として解釈されます。
        
        Examples
        --------
        >>> # ch1 のカウンタ値を取得する。
        >>> enc.get_comparator(ch=1)
        1234
        
        Exceptions
        ----------
        ボードが対応していない ch が指定された場合、ValueError となります。
        ボードで使用可能なチャンネル範囲は available_ch に格納されています。 
        """
        self._verify_ch(ch)

        c = self.driver.get_comparator(ch)
        
        if unsigned:
            return c.to_uint()
        else:
            return c.to_int()
            
        return 
    

    def get_status(self, ch=1):
        """カウンタのステータスを取得します。
        (GPG-6204 19. PencGetStatus)
        
        Parameters
        ----------
        ch : int
            取得するチャンネルを指定します。
            指定できるチャンネル範囲はボードに依ります。
            利用可能なチャンネルは available_ch に格納されています。
        
        Returns
        -------
        status : flagged_bytes
        
        Examples
        --------
        >>> enc.get_status(ch=1)

        Exceptions
        ----------
        ボードが対応していない ch が指定された場合、ValueError となります。
        ボードで使用可能なチャンネル範囲は available_ch に格納されています。
        """
        self._verify_ch(ch)
        return self.driver.get_status(ch)
        

