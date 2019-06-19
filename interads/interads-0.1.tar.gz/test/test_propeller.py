from models.propeller import PropellerService
import unittest
import httpretty



class test_function(unittest.TestCase):

    @httpretty.activate
    def test_request_adv_statistics(self):

        httpretty.register_uri(httpretty.GET, "https://ssp-api.propellerads.com/v5/adv/statistics", body="abc")
        res = PropellerService().get_adv_statistics()
        self.assertEqual(res, "abc")


if __name__ == '__main__':
    unittest.main()
