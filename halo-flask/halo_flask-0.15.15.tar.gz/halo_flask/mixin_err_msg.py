#!/usr/bin/env python
import logging

# from cStringIO import StringIO
# aws
# common

from halo_flask.classes import AbsBaseClass
logger = logging.getLogger(__name__)


class ErrorMessages(AbsBaseClass):
    hashx = {}
    # generic halo messages and proprietery api messages
    hashx["MaxTryException"] = {"code": 10100, "message": "Api reached Max Try count"}
    hashx["MaxTryHttpException"] = {"code": 10101, "message": "Api reached Max Try count using http"}
    hashx["MaxTryRpcException"] = {"code": 10102, "message": "Api reached Max Try count using rpc"}
    hashx["ApiTimeOutExpired"] = {"code": 10103, "message": "Api call Timed Out"}
    hashx["ApiError"] = {"code": 10104, "message": "Api call Error"}
    hashx["ConnectionError"] = {"code": 10105, "message": "Api Connection Error"}
    hashx["TypeError"] = {"code": 10106, "message": "Server Type Error"}

    def get_code(self,ex):
        """
        get the proper status code and error msg for exception
        :param ex:
        :return:
        """
        e = type(ex).__name__
        emsg = str(ex)
        logger.debug("e=" + emsg)
        if e in self.hashx:
            code = self.hashx[e]["code"]
            msg = self.hashx[e]["message"]
        else:
            code = 500
            msg = "Server Error"
            if emsg is not None and emsg != 'None' and emsg != "":
                msg = emsg
        return code, msg
