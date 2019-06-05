class SaltJobFinished(object):
    def __init__(self, jid,  ret, retcode):
        self.jid = jid
        self.ret = ret
        self.retcode = retcode
