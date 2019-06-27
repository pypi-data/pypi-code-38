# -*- coding: utf-8 -*-
class AfipError:
    
    @classmethod
    def parse_error(cls, error):
        return Exception("Error {}: {}".format(
            error.FEXErr.ErrCode,
            error.FEXErr.ErrMsg),
        )
