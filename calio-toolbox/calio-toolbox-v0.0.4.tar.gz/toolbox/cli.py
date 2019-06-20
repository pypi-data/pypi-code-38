import argparse


class KeyValueAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        kv = getattr(namespace, self.dest, {}) or {}
        key, value = value.split('=', 1)
        kv[key] = value
        setattr(namespace, self.dest, kv)
