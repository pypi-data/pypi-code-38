class PixelException(Exception):
    pass


class InvalidKeyException(PixelException):
    pass


class GuildNotFound(PixelException):
    pass


class PlayerNotInGuild(PixelException):
    pass


class PlayerNotFound(PixelException):
    pass


class NoSessionForPlayer(PixelException):
    pass
