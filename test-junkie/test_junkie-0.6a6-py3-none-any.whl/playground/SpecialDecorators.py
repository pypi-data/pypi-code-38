# from test_junkie.decorators import beforeClass, afterClass, afterTest, beforeTest

#
# class TestRules:
#
#     @beforeClass()
#     def before_class(self):
#         pass
#
#     @beforeTest()
#     def before_test(self):
#         # write your code here
#         pass
#
#     @afterTest()
#     def after_test(self):
#         # write your code here
#         pass
#
#     @afterClass()
#     def after_class(self):
#         # write your code here
#         pass
from playground.suiteA import LoginSuite

GROUP = [LoginSuite]
