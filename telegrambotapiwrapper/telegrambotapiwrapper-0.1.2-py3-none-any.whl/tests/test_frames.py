import unittest
from telegrambotapiwrapper.frames import (
    outer_name,
    outer2_name,
    outer3_name,
    outer_args,
    outer2_args,
    outer3_args,
)


class TestFrames(unittest.TestCase):
    """Класс для тестирования функций модуля `test_frames.py`."""

    def test_outer_args_skip_self_true(self_):
        """Протестировать функцию outer_args() c skip_self=True."""

        def foo1():
            adsvdsfvfd = 32454
            bb_sdfd = 3432423

            def func(a, b, c, d):
                fdgmjhhvrfdadsvdsfvfd = 32454
                jkhgvpodfdcbb_sdfd = 3432423
                args = outer_args(skip_self=True)
                r = {'a': 123, 'b': 45.56, 'c': "adc", "d": 23 + 4j}
                self_.assertEqual(args, r)

            func(123, 45.56, "adc", 23 + 4j)

        foo1()

        def foo2():
            adsvdsfvfd = 32454
            bb_sdfd = 3432423

            def func(self, a, b, c, d):
                sdhgfbhjnyjhhadsvdsfvfd = 32454
                hgfhgdvcvftfbb_sdfd = 3432423
                args = outer_args(skip_self=True)
                r = {'a': 123, 'b': 45.56, 'c': "adc", "d": 23 + 4j}
                self_.assertEqual(args, r)

            func('sdfdsfdsfdsfdsfds', 123, 45.56, "adc", 23 + 4j)

        foo2()

        def foo3():
            adsvdsfvfd = 32454
            bb_sdfd = 3432423

            def func(self, a, b, c, d):
                killsdsd = 123
                btdfdf = "234234234"
                args = outer_args(skip_self=True)
                r = {'a': 123, 'b': 45.56, 'c': "adc", "d": 23 + 4j}
                self_.assertEqual(args, r)

            func('sdfdsfdsfdsfdsfds', 123, 45.56, "adc", 23 + 4j)

        foo3()

    def test_outer_args_skip_self_false(self_):
        """Протестировать функцию outer_args() c skip_self=False."""

        def foo1():
            adsvdsfvfd = 32454
            bb_sdfd = 3432423

            def func(a, b, c, d):
                args = outer_args(skip_self=False)
                r = {'a': 123, 'b': 45.56, 'c': "adc", "d": 23 + 4j}
                self_.assertEqual(args, r)

            func(123, 45.56, "adc", 23 + 4j)

        foo1()

        def foo2():
            adsvdsfvfd = 32454
            bb_sdfd = 3432423

            def func(self, a, b, c, d):
                sdfddfdfdsdjhfdsadsvdsfvfd = 32454
                fghgfsdfvcbb_sdfd = 3432423
                args = outer_args(skip_self=False)
                r = {
                    'self': 'sdfdsfdsfdsfdsfds',
                    'a': 123,
                    'b': 45.56,
                    'c': "adc",
                    "d": 23 + 4j
                }
                self_.assertEqual(args, r)

            func('sdfdsfdsfdsfdsfds', 123, 45.56, "adc", 23 + 4j)

        foo2()

    def test_outer2_args_skip_self_true(self_):
        adsvdsfvfd = 32454
        bb_sdfd = 3432423

        def outer_func(aa, bb, cc, dd):
            adsvdsfdfdvfd = 32454
            bb_sddfdfdfd = 3432423

            def nested_func(a, b, c, d):
                sdfdsfdsfhgfbdsscadsvdsfvfd = 32454
                sdfsdfvdscbb_sdfsdfsdfd = 3432423
                args = outer2_args(skip_self=True)
                r = {'aa': 345, 'bb': -88.95, 'cc': "ghgh", "dd": -13 - 8j}
                self_.assertEqual(args, r)

            nested_func(123, 45.56, "adc", 23 + 4j)

        outer_func(345, -88.95, "ghgh", -13 - 8j)

        def outer_func2(self, aa, bb, cc, dd):
            adsvdsdfdfvfd = 32454
            sdssbb_sdfd = 3432423

            def nested_func(a, b, c, d):
                weefwadsvdsfvfd = 32454
                wefwefbb_sdfd = 3432423
                args = outer2_args(skip_self=True)
                r = {'aa': 345, 'bb': -88.95, 'cc': "ghgh", "dd": -13 - 8j}
                self_.assertEqual(args, r)

            nested_func(123, 45.56, "adc", 23 + 4j)

        outer_func2("aaaa_dddd", 345, -88.95, "ghgh", -13 - 8j)

    def test_outer3_args_skip_self_false(self_):
        adsvsdfsdfdsfvfd = 32454
        bb_ssdfsdfdfd = 3432423

        def func3(a, b, c):
            sdfsdfsdfsdf43fdvfdadsvdsfvfd = 32454
            ewfdvgretfdsg56hgfgbb_sdfd = 3432423

            def func2():
                sdfsdadsvdsfdsfsdvfd = 32454
                sdfdhngbdvbb_sdfd = 3432423

                def func():
                    dsvrfdgvfdadsvdsfdsfdsvfd = 32454
                    dfgddfrgfdsvbb_sdfd = 3432423
                    self_.assertEqual(
                        outer3_args(skip_self=False), {
                            'a': 100,
                            'b': 200,
                            'c': 300
                        })

                func()

            func2()

        func3(100, 200, 300)

        def func3(self, a, b, c):
            sdfdsfadsvdsfvfd = 32454
            sdfsdfbb_sdfd = 3432423

            def func2():
                asdfsdfdsvdsfsdfdsfvfd = 32454
                sdfsdfsdfbb_sdfd = 3432423

                def func():
                    fdgfdsfredvadsvdsfvfd = 32454
                    bb_sdfdvgfdgvfdsdfd = 3432423
                    self_.assertEqual(
                        outer3_args(skip_self=False), {
                            'self': 'asd',
                            'a': 100,
                            'b': 200,
                            'c': 300
                        })

                func()

            func2()

        func3('asd', 100, 200, 300)

    def test_outer3_args_skip_self_true(self_):
        def func3(a, b, c):
            def func2():
                def func():
                    self_.assertEqual(
                        outer3_args(skip_self=True), {
                            'a': 100,
                            'b': 200,
                            'c': 300
                        })

                func()

            func2()

        func3(100, 200, 300)

        def func3(self, a, b, c):
            def func2():
                def func():
                    self_.assertEqual(
                        outer3_args(skip_self=True), {
                            'a': 100,
                            'b': 200,
                            'c': 300
                        })

                func()

            func2()

        func3('asd', 100, 200, 300)

    def test_outer_name(self):
        def outer_func():
            self.assertEqual(outer_name(), "outer_func")

        outer_func()

        class A:
            def outer_func(self_):
                self.assertEqual(outer_name(), "outer_func")

        A().outer_func()

    def test_outer2_name(self):
        def outer_outer_func():
            def outer_func():
                self.assertEqual(outer2_name(), "outer_outer_func")

            outer_func()

        outer_outer_func()

    def test_outer3_name(self):
        def outer_outer_outer_func():
            def outer_outer_func():
                def outer_func():
                    self.assertEqual(outer3_name(), "outer_outer_outer_func")

                outer_func()

            outer_outer_func()

        outer_outer_outer_func()


if __name__ == '__main__':
    unittest.main()
