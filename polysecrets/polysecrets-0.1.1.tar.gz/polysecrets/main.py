from uuid import uuid4
import random, time, sys, threading
from os import environ


class PolySecrets:
    def __init__(self, secret: str, interval: int = 30, length: int = 10, uuids: int = 1, mix_case: bool = False):
        """
        A completely randomized order of secrets; built with security in mind.
        :param secret: The user provided secret string
        :param interval: The time interval in which to generate a new secret; for the automated process
        :param length: The length of the final secret
        :param uuids: Determine if secret generation should contain UUIDs, Alphanumeric characters or both
        :param mix_case: Switch the case of string between lower or upper case
        """
        self.__os__()
        self.__reqs__(secret, length)
        # variables
        self.secret = secret
        self.interval = interval
        self.length = length
        self.uuids = self.__config__(uuids)
        self.mix_case = mix_case
        self.CLI = False
        # automated process
        self._thread = threading.Thread(target=self.__automated, args=())
        self._thread.daemon = True
        self._RUN_THREAD = True
        # crypto secret
        self._one_uuid = str(uuid4())[:15]
        self._alpha_numeric_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
                                    'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6',
                                    '7', '8', '9']
        self._sec_phrase = self.secret
        self._sec_arr = []

    @staticmethod
    def __config__(obj):
        if not isinstance(obj, int):
            print(f'UUID must be a integer value of 0, 1, or 2. You have {obj}, which is invalid.')
            return
        elif obj == 0:
            return False
        elif obj == 1:
            return True
        elif obj == 2:
            return 'Both'
        else:
            print(f'UUID must be a integer value of 0, 1, or 2. You have {obj}, which is invalid.')
            return

    @staticmethod
    def __os__():
        platforms = {
            'darwin': (3, 5),
            'linux': (3, 5),
            'windows': (3, 5)
        }
        platform_version = platforms.get(sys.platform, 'N/A')
        if platform_version == 'N/A' or not sys.version_info >= platform_version:
            print('MacOS, Linux or Windows running Python 3.5 or higher is required.')
            return

    @staticmethod
    def __reqs__(secret, length):
        if len(secret) < 10:
            print(f'A secret of 10 characters or more is required. You secret has {len(secret)} characters.')
            return
        elif length < 10:
            print(f'The length of the secret must be of 10 or more. You set your length to {length}, '
                  f'this is invalid.')
            return

    def __randomization(self, arr, lst, return_val: bool = False):
        switcher = ['upper', 'lower', 'upper', 'lower', 'upper', 'lower']  # increase probability
        random_item_from_list = str(random.choice(lst))
        case_state = random.choice(switcher)
        if self.mix_case:
            if not random_item_from_list.isnumeric() and case_state == 'upper':
                random_item_from_list.upper()
        if return_val:
            return arr.append(random_item_from_list)
        arr.append(random_item_from_list)

    def __length_confirmation__(self, final_secret):
        if len(final_secret) < self.length:
            for _ in range(self.length - len(final_secret)):
                self.__randomization(self._sec_arr, self._alpha_numeric_list)
            return str(''.join(self._sec_arr))[:self.length]
        return final_secret

    def __secret_generator(self, automated: bool = False):
        for _ in range(len(self._sec_phrase)):
            self.__randomization(self._sec_arr, self._sec_phrase)
            if self.uuids is True:
                self.__randomization(self._sec_arr, self._one_uuid)
            elif self.uuids is False:
                self.__randomization(self._sec_arr, self._alpha_numeric_list)
            else:
                self.__randomization(self._sec_arr, self._one_uuid)
                self.__randomization(self._sec_arr, self._alpha_numeric_list)
        _final_secret = str(''.join(self._sec_arr))[:self.length]
        if not automated:
            return self.__length_confirmation__(_final_secret)
        environ['secret'] = self.__length_confirmation__(_final_secret)
        self._sec_arr.clear()

    def __automated(self):
        while self._RUN_THREAD:
            self._one_uuid = str(uuid4())[:15]
            self.__secret_generator(True)
            if self.CLI:
                print('Secret: ', environ['secret'])
            time.sleep(self.interval)

    def manual(self):
        return self.__secret_generator()

    def automated(self):
        self._thread.start()

    def stop_automated(self):
        self._RUN_THREAD = False
