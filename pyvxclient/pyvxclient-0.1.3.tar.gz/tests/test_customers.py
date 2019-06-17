from unittest import TestCase

from bravado.exception import HTTPNotFound

from pyvxclient.client import Client
from pyvxclient.errors import NotAuthorized, EndpointURLNotFound, WrongCredentials
import requests_mock

from tests.data.spec import spec
from tests.data.customers import customers_limit_5, customer, customers_single


# TODO: improve tests


class TestCustomers(TestCase):

    def setUp(self) -> None:
        requests_mocker = requests_mock.Mocker()
        base_url = 'https://vxapitest-test-test.vx.se/public/not_exist_for_test'
        requests_mocker.get(base_url + '/api/v1/spec', json=spec,
                            status_code=200, headers={'Content-Type': 'application/json'})
        self.api_key = "202803e1003a4b1932701da04ea3d698a73346c47a68f0882c84fc893f843c60"
        requests_mocker.get(base_url + '/api/v1/api/api_key', json={
            "api_key": self.api_key,
            "expires": "2019-05-14T21:25:19.956397+00:00"
        }, status_code=200, headers={'Content-Type': 'application/json'})

        self.base_url = base_url
        self.requests_mocker = requests_mocker
        self.requests_mocker.start()

        # re-raise exception just for documentation
        try:
            # deve finire con /
            client = Client(url=self.base_url + '/', cache_path='/tmp/pyvxclient.swagger.json')
            '''
            err: cannot load vxapi client
            err: expected str, bytes or os.PathLike object, not NoneType
            '''
            token = client.get_token('massimo', 'password')
            # non richiamare la set_api_key
            client.api_key = token['api_key']
            client.setup()
        except NotAuthorized as e:
            print("err: user not authorized, please login again")
            raise e
        except EndpointURLNotFound as e:
            print("err: %s" % e)
            raise e
        except WrongCredentials as e:
            print("err: %s" % e)
            raise e
        except ConnectionError as e:
            print("err: endpoint could not be contacted: %s" % e)
            raise e
        except Exception as e:
            print("err: cannot load vxapi client")
            print("err: %s" % e)
            raise e

        self.client = client

    def tearDown(self) -> None:
        self.requests_mocker.stop()

    def test_get_with_limit(self) -> None:
        self.requests_mocker.get(self.base_url + '/api/v1/customer?per_page=5&page=1&fields=&api_key={}'
                                 .format(self.api_key),
                                 json=customers_limit_5, status_code=200, headers={'Content-Type': 'application/json'})

        ret = self.client.Customer.get(limit=5)
        self.assertTrue(ret['data'][0])

    def test_get_single(self) -> None:
        self.requests_mocker.get(self.base_url + '/api/v1/customer?q=id:123',
                                 json=customers_single,
                                 status_code=200, headers={'Content-Type': 'application/json'})

        ret = self.client.Customer.get(q=["id:123"])
        self.assertTrue(ret['data'])

    def test_get_not_found(self) -> None:
        self.requests_mocker.get(self.base_url + '/api/v1/customer?q=id:123',
                                 json={"message": "No resources found"},
                                 status_code=404, headers={'Content-Type': 'application/json'})

        with self.assertRaises(HTTPNotFound):
            self.client.Customer.get(q=["id:123"])

    def test_post(self) -> None:
        self.requests_mocker.post(self.base_url + '/api/v1/customer',
                                  json=customer,
                                  status_code=201, headers={'Content-Type': 'application/json'})

        ret = self.client.Customer.create(first_name='pluto',
                                          last_name='pluto',
                                          password='ciao#1234',
                                          email='ciao@test.it',
                                          #
                                          province='',
                                          city='',
                                          customer_type='Residential',
                                          postal_code='',
                                          language='English',
                                          mobile_number='',
                                          phone_number='',
                                          street_address='')
        self.assertEqual(ret.data['id'], 'D28E299D-8673-41AB-89B4-1B20F64F8E02')

    def test_post_not_valid(self) -> None:
        err = "Missing required parameter in the JSON body or the post body or the query string"
        self.requests_mocker.post(self.base_url + '/api/v1/customer',
                                  json={
                                      "message":
                                      {
                                          "province": err,
                                          "city": err,
                                          "customer_type": err,
                                          "postal_code": err,
                                          "language": err,
                                          "mobile_number": err,
                                          "phone_number": err,
                                          "street_address": err
                                      }
                                  },
                                  status_code=400, headers={'Content-Type': 'application/json'})

        ret = self.client.Customer.create(first_name='pluto',
                                          last_name='pluto',
                                          password='ciao#1234',
                                          email='ciao@test.it')
        self.assertEqual(ret.status_code, 400)

    def test_put(self) -> None:
        self.requests_mocker.put(self.base_url + '/api/v1/customer',
                                 json=customer,
                                 status_code=200, headers={'Content-Type': 'application/json'})

        ret = self.client.Customer.update(id='D28E299D-8673-41AB-89B4-1B20F64F8E02', first_name='pluto')
        self.assertEqual(ret.data['id'], 'D28E299D-8673-41AB-89B4-1B20F64F8E02')
