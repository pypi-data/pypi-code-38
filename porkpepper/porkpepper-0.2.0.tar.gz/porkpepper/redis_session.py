

class RedisSession:
    def __init__(self):
        self.current_db: int = 0
        self.reader = None
        self.write = None
        self.need_auth_event = None
        self.server = None


__all__ = ["RedisSession", ]
