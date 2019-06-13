
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

    
    def set_sampling_config(self, ...):
        """...
        (GPG-3100 7. AdSetSamplingConfig)
        
        Parameters
        ----------
        ...
        
        Returns
        -------
        ...
        
        Examples
        --------
        ...

        Exceptions
        ----------
        ...
        """
        return self.driver.set_sampling_config(...)


    def get_sampling_config(self, ...):
        """...
        (GPG-3100 8. AdGetSamplingConfig)
        
        Parameters
        ----------
        ...
        
        Returns
        -------
        ...
        
        Examples
        --------
        ...

        Exceptions
        ----------
        ...
        """
        return self.driver.get_sampling_config(...)


    def get_sampling_data(self, ...):
        """...
        (GPG-3100 9. AdGetSamplingData)
        
        Parameters
        ----------
        ...
        
        Returns
        -------
        ...
        
        Examples
        --------
        ...

        Exceptions
        ----------
        ...
        """
        return self.driver.get_sampling_data(...)


    def read_sampling_buffer(self, ...):
        """...
        (GPG-3100 10. AdReadSamplingBuffer)
        
        Parameters
        ----------
        ...
        
        Returns
        -------
        ...
        
        Examples
        --------
        ...

        Exceptions
        ----------
        ...
        """
        return self.driver.read_sampling_buffer(...)


    def clear_sampling_data(self, ...):
        """...
        (GPG-3100 11. AdClearSamplingData)
        
        Parameters
        ----------
        ...
        
        Returns
        -------
        ...
        
        Examples
        --------
        ...

        Exceptions
        ----------
        ...
        """
        return self.driver.clear_sampling_data(...)

    
    def start_sampling(self, ...):
        """...
        (GPG-3100 12. AdStartSampling)
        
        Parameters
        ----------
        ...
        
        Returns
        -------
        ...
        
        Examples
        --------
        ...

        Exceptions
        ----------
        ...
        """
        return self.driver.start_sampling(...)

    
    def trigger_sampling(self, ...):
        """...
        (GPG-3100 15. AdTriggerSampling)
        
        Parameters
        ----------
        ...
        
        Returns
        -------
        ...
        
        Examples
        --------
        ...

        Exceptions
        ----------
        ...
        """
        return self.driver.trigger_sampling(...)

    
    def stop_sampling(self, ...):
        """...
        (GPG-3100 17. AdStopSampling)
        
        Parameters
        ----------
        ...
        
        Returns
        -------
        ...
        
        Examples
        --------
        ...

        Exceptions
        ----------
        ...
        """
        return self.driver.stop_sampling(...)

    
    def get_status(self, ...):
        """...
        (GPG-3100 18. AdGetStatus)
        
        Parameters
        ----------
        ...
        
        Returns
        -------
        ...
        
        Examples
        --------
        ...

        Exceptions
        ----------
        ...
        """
        return self.driver.get_status(...)

    
    def input_ad(self, ...):
        """...
        (GPG-3100 19. AdInputAd)
        
        Parameters
        ----------
        ...
        
        Returns
        -------
        ...
        
        Examples
        --------
        ...

        Exceptions
        ----------
        ...
        """
        return self.driver.input_ad(...)

    
    def input_di(self, ...):
        """...
        (GPG-3100 22. AdInputDI)
        
        Parameters
        ----------
        ...
        
        Returns
        -------
        ...
        
        Examples
        --------
        ...

        Exceptions
        ----------
        ...
        """
        return self.driver.input_di(...)


    def input_do(self, ...):
        """...
        (GPG-3100 22. AdInputDO)
        
        Parameters
        ----------
        ...
        
        Returns
        -------
        ...
        
        Examples
        --------
        ...

        Exceptions
        ----------
        ...
        """
        return self.driver.input_do(...)

