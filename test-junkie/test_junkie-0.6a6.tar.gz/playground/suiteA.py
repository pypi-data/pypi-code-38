# import datetime
# import time
# from random import randint
#
# from playground.suiteB import ShoppingCartSuite
# from test_junkie.decorators import Suite, test, beforeTest, beforeClass, afterTest
# from test_junkie.meta import Meta
# from tests.junkie_suites.Constants import Constants
# from tests.junkie_suites.TestListener import TestListener
# from tests.junkie_suites.TestRules import TestRules
#
#
# def test_func():
#     print("evaluating...")
#     # time.sleep(2)
#     return [1, 2]
#
#
# @Suite(feature="Login", owner="Mike", rules=TestRules, listener=TestListener)
# class LoginSuite:
#
#     # @beforeClass()
#     # def before_class(self):
#     #     time.sleep(randint(0, 4))
#     #
#     # @afterTest()
#     # def after_test(self):
#     #     time.sleep(randint(0, 4))
#     #     raise Exception("Winning!")
#
#     # @beforeTest()
#     # def before_test(self):
#     #     time.sleep(randint(0, 4))
#     #     raise Exception("Winning!")
#
#     @test(component="Login Page",
#           tags=["positive_flow", "ui", "auth"], parameters=[1, 2])
#     def positive_login(self, parameter):
#         pass
#         # time.sleep(randint(0, 4))
#
#     # @test(priority=1, skip_before_test=True,
#     #       parallelized_parameters=True,
#     #       component="Login Page",
#     #       tags=["negative_flow", "ui"],
#     #       parameters=[{"pass": ""}, {"pass": "example"}], retry=3)
#     # def negative_login(self, parameter, suite_parameter):
#     #     # time.sleep(1)
#     #     time.sleep(randint(0, 4))
#     #     raise AssertionError("Missing error message on negative login attempt: {}".format(parameter))
#     #
#     # @test(component="Session", owner="Victor", skip_after_test=True,
#     #       tags=["positive_flow", "ui", "auth", "session"])
#     # def session_timeout_after_2h(self):
#     #     pass
#     #
#     # @test(component="Session", owner="Victor",
#     #       tags=["positive_flow", "ui", "auth", "session"])
#     # def session_timeout_after_1h(self):
#     #     pass
#     #
#     # @test(component="Session", owner="Victor",
#     #       tags=["negative_flow", "ui", "auth", "session"])
#     # def logout_after_session_timeout(self):
#     #     print("Running a.a")
#     #     print(datetime.datetime.now())
#     #     # print(time.sleep(7.3))
#     #     time.sleep(randint(0, 7))
#     #
#     # @test(component="Login Page", skip_before_test=True,
#     #       tags=["negative_flow", "ui"], pr=[ShoppingCartSuite.add_to_cart])
#     # def negative_login_attempt_limit(self):
#     #     print("Running a")
#     #     print(datetime.datetime.now())
#     #     # print(time.sleep(7.3))
#     #     time.sleep(randint(0, 7))
#     #     pass
