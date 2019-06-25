import json
import os
import unittest
from decimal import Decimal

import tclambda

from .extras import FunctionBuilder, LambdaContext

TC_THIS_BUCKET = os.getenv("TC_THIS_BUCKET")


def decimal_function():
    return {"decimal": Decimal("1.234"), "integer": 1234, "float": 1.234}


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


class TestHandler(unittest.TestCase):
    def setUp(self):
        self.app = tclambda.LambdaHandler(json_encoder_class=DecimalEncoder)
        self.app.register()(decimal_function)

    @unittest.skipIf(TC_THIS_BUCKET is None, "TC_THIS_BUCKET is None")
    def test_call_handler_sqs_ping(self):
        f = FunctionBuilder("decimal_function")
        self.app(f.sqs, LambdaContext(function_name="tclambda-test"))
        self.assertEqual(
            f.result.result(delay=1, max_attempts=3),
            {"decimal": "1.234", "integer": 1234, "float": 1.234},
        )
