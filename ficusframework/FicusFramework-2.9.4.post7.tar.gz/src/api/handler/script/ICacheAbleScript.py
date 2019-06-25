from api.handler.ICacheAble import ICacheAble
from api.handler.script import ScriptHandlerHolder


class ICacheAbleScript(ICacheAble):

    def set_cache_value(self, key, value):
        handler = ScriptHandlerHolder.cacheHandler()
        if handler is not None:
            handler.set_cache_value(key,value)

    def set_cache_value_if_absent(self, key, value):
        handler = ScriptHandlerHolder.cacheHandler()
        if handler is not None:
            return handler.set_cache_value_if_absent(key, value)
        return False

    def get_cache_value(self, key):
        handler = ScriptHandlerHolder.cacheHandler()
        if handler is not None:
            return handler.get_cache_value(key)
        return None

    def delete_cache_value(self, key):
        handler = ScriptHandlerHolder.cacheHandler()
        if handler is not None:
            handler.delete_cache_value(key)

    def set_cache_value_from_process(self, key, value):
        handler = ScriptHandlerHolder.cacheHandler()
        if handler is not None:
            handler.set_cache_value_from_process(key, value)

    def set_cache_value_if_absent_from_process(self, key, value):
        handler = ScriptHandlerHolder.cacheHandler()
        if handler is not None:
            return handler.set_cache_value_if_absent_from_process(key, value)
        return False

    def get_cache_value_from_process(self, key):
        handler = ScriptHandlerHolder.cacheHandler()
        if handler is not None:
            return handler.get_cache_value_from_process(key)
        return None

    def delete_cache_value_from_process(self, key):
        handler = ScriptHandlerHolder.cacheHandler()
        if handler is not None:
            handler.delete_cache_value_from_process(key)