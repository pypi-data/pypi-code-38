from abc import abstractmethod

class ICacheAble:

    @abstractmethod
    def set_cache_value(self, key, value):
        """

        :param key:
        :param value:
        :return:
        """

    @abstractmethod
    def set_cache_value_if_absent(self, key, value):
        """

        :param key:
        :param value:
        :return:
        """

    @abstractmethod
    def get_cache_value(self, key):
        """

        :param key:
        :return:
        """

    @abstractmethod
    def delete_cache_value(self, key):
        """
        
        :param key:
        :return:
        """

    @abstractmethod
    def set_cache_value_from_process(self, key, value):
        """

        :param key:
        :param value:
        :return:
        """

    @abstractmethod
    def set_cache_value_if_absent_from_process(self, key, value):
        """

        :param key:
        :param value:
        :return:
        """

    @abstractmethod
    def get_cache_value_from_process(self, key):
        """

        :param key:
        :return:
        """

    @abstractmethod
    def delete_cache_value_from_process(self, key):
        """

        :param key:
        :return:
        """