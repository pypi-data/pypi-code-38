# -*- coding: utf-8 -*-
class AfipError:
    
    @classmethod
    def parse_error(cls, error):
        return Exception("Error {}: {}".format(
            error.Errors.Err[0].Code,
            error.Errors.Err[0].Msg.encode('latin-1')),
        )
