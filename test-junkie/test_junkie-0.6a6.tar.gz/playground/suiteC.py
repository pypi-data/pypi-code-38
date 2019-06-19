import time
from random import randint


from test_junkie.decorators import Suite, test, beforeClass, beforeTest, afterTest, afterClass
from test_junkie.meta import meta, Meta
from tests.junkie_suites.TestListener import TestListener


@Suite(retry=2,
       listener=TestListener,
       parameters=[1, 2],
       parallelized=False,
       feature="API")
class AuthApiSuite:

    @test(component="Auth", tags=["api", "auth", "basic_auth"], owner="Victor")
    def authenticate_via_basic_auth_api(self):
        pass

    @test(component="Auth", tags=["api", "auth", "two_factor"], owner="Victor")
    def authenticate_via_two_factor_api(self):
        pass

    @test(component="Auth", tags=["api", "auth", "sso"], owner="Victor")
    def authenticate_via_sso(self):
        pass

    @test(component="Auth", tags=["api", "auth", "sso"], owner="Victor")
    def sso_hit_negative_auth_limit(self):
        time.sleep(randint(0, 4))

    @test(component="Auth", tags=["api", "auth", "basic_auth"], owner="Victor")
    def auth_hit_negative_auth_limit(self):
        time.sleep(randint(0, 4))

    @test(component="Auth", tags=["api", "auth", "two_factor"], owner="Victor")
    def two_factor_hit_negative_auth_limit(self):
        time.sleep(randint(0, 4))
