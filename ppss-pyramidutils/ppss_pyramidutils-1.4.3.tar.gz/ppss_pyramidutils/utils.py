import logging
import types
from six import PY2

l = logging.getLogger("ppss.pyramidutils")


class Utils():
    myconf = []

    @classmethod
    def confended(cls, **kwargs):
        pass

    @classmethod
    def config(cls, settings, prefix=None, defaultval=None):
        string = types.StringTypes if PY2 else str
        resvals = {}
        resdicts = {}
        if not prefix:
            prefix = cls.__name__.lower()
        l.debug("reading conf for {}".format(prefix))
        for k in cls.myconf:
            if isinstance(k, string):
                prop = k
                key = prefix+"."+k
                default = getattr(cls, k, defaultval)
            else:
                try:
                    prop = k[0]
                    key = prefix+"."+k[0]
                    default = k[1]
                except Exception:
                    l.warn("exception reading {}".format(k))
                    continue

            value = settings.get(key, default)
            if "." in prop:
                propparts = prop.split(".")

                dictname = propparts[0]
                dictkey = propparts[1]
                if dictname not in resdicts:
                    resdicts[dictname] = {}
                resdicts[dictname][dictkey] = value
            else:
                setattr(cls, prop, value)
                if key in settings:
                    l.debug("value of {key} set to: {val}".format(
                        key=prop, val=value))

        for key, value in resdicts.items():
            setattr(cls, key, value)
            l.debug("value of {key} set to: {val}".format(key=key, val=value))
            #setattr(cls,k,unicode(settings[key]) )
        for key in cls.myconf:
            l.debug("val for {key} = {val}".format(
                key=key, val=getattr(cls, key)))
        cls.confended()
