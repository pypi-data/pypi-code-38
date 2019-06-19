# import time
# from random import randint
#
# from test_junkie.decorators import Suite, test, beforeClass, beforeTest, afterTest, afterClass
# from test_junkie.meta import meta, Meta
# from tests.junkie_suites.TestListener import TestListener
#
#
# @Suite(retry=2,
#        listener=TestListener,
#        priority=2, feature="Store", owner="Mike")
# class NewProductsSuite:
#
#     @beforeClass()
#     def before_class1(self):
#         pass
#
#     @beforeTest()
#     def before_test2(self):
#         # write your code here
#         pass
#
#     @afterTest()
#     def after_test3(self):
#         # write your code here
#         pass
#
#     @afterClass()
#     def after_class4(self):
#         # write your code here
#         pass
#
#     @test(component="Admin", tags=["store_management"])
#     def add_new_product(self):
#         time.sleep(randint(0, 4))
#
#     @test(component="Admin", tags=["store_management"])
#     def remove_product(self):
#         time.sleep(randint(0, 4))
#
#     @test(component="Admin", tags=["store_management"])
#     def publish_product(self):
#         time.sleep(randint(0, 4))
#
#     @test(component="Admin", tags=["store_management"])
#     def edit_product(self):
#         time.sleep(randint(0, 4))
#         raise Exception("Product not found")
#
#     @test(component="Admin", tags=["store_management"])
#     def archive_product(self):
#         time.sleep(randint(0, 4))
#         raise Exception("Product not found")
