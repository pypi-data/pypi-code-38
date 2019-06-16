class Caesar:
    """
    Summary:
        This is a class for text encryption using Caesar cipher algorithm.

    Attributes:
        crypto()
    """

    def __init__(self, msg: str, key: int, mode: bool):
        """
        The constructor for Caesar class.
        :param msg: The message to be encrypted.
        :param key: Encryption key (must be same for encrypting and decrypting).
        :param mode: If True was used while encrypting then False must be passed while decrypting.
        """
        self.msg = msg
        self.key = key
        self.mode = mode

    def crypto(self):
        """
        The function for encrypting and decrypting the message.
        :return: Encrypted or Decrypted message (based on mode).
        """
        if type(self.mode) is not bool:
            raise ValueError(f"'mode' must be a 'boolean' value (True of False) and not {str(type(self.mode))[1:-1]}")
        if type(self.msg) is not str:
            raise ValueError(f"'msg' must be a 'string' value and not {str(type(self.msg))[1:-1]}")
        if type(self.key) is not int:
            raise ValueError(f"'key' must be an 'integer' value and not {str(type(self.key))[1:-1]}")
        en_msg = ""
        base = "V[3@wof9<A>z?1JH)aXqnm=6G*NBp]{#xR!; |gTy.E$DC}5j4&\dIsWF^ie/u7~lvZh_PS82kYcKULr%(0:MtOb-+Q"
        if self.mode is True:
            for i in (x for x in self.msg if x in base):
                en_msg += base[(base.find(i) + self.key) % len(base)]
        else:
            for i in (x for x in self.msg if x in base):
                en_msg += base[(base.find(i) - self.key) % len(base)]
        return en_msg
