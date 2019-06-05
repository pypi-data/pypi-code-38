from strongr.core.exception import InvalidParameterException

from strongr.clouddomain.event.intra.saltjobfinished import SaltJobFinished

# try-except for py 2 / 3 compatibility
try:
    basestring
except NameError:
    basestring = str

class IntraDomainEventFactory(object):
    def newSaltJobFinished(self, jid,  ret, retcode):
        if not isinstance(jid, basestring) or len(jid.strip()) == 0:
            raise InvalidParameterException('jid is invalid')
        elif not isinstance(ret, basestring) or len(ret.strip()) == 0:
            raise InvalidParameterException('ret is invalid')
        elif not isinstance(retcode, int):
            raise InvalidParameterException('retcode is invalid')

        return SaltJobFinished(jid, ret, retcode)
