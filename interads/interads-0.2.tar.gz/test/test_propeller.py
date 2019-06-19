from services.propeller import PropellerService
import unittest
import httpretty

class test_function(unittest.TestCase):
    @httpretty.activate
    def test_request_adv_statistics(self):
        body_test = '{"result": "abc",  "meta": "xyz"}'
        httpretty.register_uri(httpretty.GET, "https://ssp-api.propellerads.com/v5/adv/statistics", body=body_test)
        res = PropellerService().get_adv_statistics()
        self.assertEqual(str(res), 'abc - xyz')


if __name__ == '__main__':
    unittest.main()

