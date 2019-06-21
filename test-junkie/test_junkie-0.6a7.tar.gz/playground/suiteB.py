# import datetime
# import time
# from random import randint
#
# from test_junkie.decorators import Suite, test
# from tests.junkie_suites.TestListener import TestListener
#
#
# @Suite(retry=2,
#        listener=TestListener,
#        meta={"name": "Suite B", "known_bugs": []},
#        parameters=[1, 2], priority=1, feature="Store",
#        owner="George")
# class ShoppingCartSuite:
#
#     @test(priority=1,
#           component="Shopping Cart",
#           tags=["ui", "cart", "positive_flow"])
#     def add_to_cart(self):
#         print("Running b")
#         print(datetime.datetime.now())
#         time.sleep(randint(0, 7))
#         print("Finished SUITE B / TEST A")
#
#     @test(priority=1,
#           component="Shopping Cart",
#           tags=["ui", "cart", "positive_flow"])
#     def remove_from_cart(self):
#         time.sleep(randint(0, 4))
#         pass
#
#     @test(priority=1,
#           component="Shopping Cart",
#           tags=["ui", "cart", "positive_flow"])
#     def increase_quantity(self):
#         time.sleep(randint(0, 4))
#         pass
#
#     @test(priority=1,
#           component="Shopping Cart",
#           tags=["ui", "cart", "positive_flow"])
#     def decrease_quantity(self):
#         time.sleep(randint(0, 4))
#         pass
#
#     @test(priority=1,
#           component="Shopping Cart",
#           tags=["ui", "cart", "positive_flow"])
#     def save_for_later(self):
#         time.sleep(randint(0, 4))
#         pass
