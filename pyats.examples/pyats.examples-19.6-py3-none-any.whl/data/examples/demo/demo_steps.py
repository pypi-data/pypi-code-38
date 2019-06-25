'''Demo AEtest Section Scripts

Demonstrate AEtest support for breaking testcases and sections into smaller 
steps, and how functions can also be defined to support step usage, etc.

Run this jobfile in standalone:

    bash$ python demo_steps.py --a 2 --b 3

'''

from pyats import aetest

def function_supporting_steps(steps, a, b, c, d):

    with steps.start('%s * %s' % (a, b)):
        result = a * b
    with steps.start('%s ^ %s' % (result, c)):
        result **= c
    with steps.start('%s + %s' % (result, d)):
        result += d
    return result


class SimpleMath(aetest.Testcase):

    c = 2
    d = 7

    @aetest.test
    def simple_math_test(self, a, b, steps):

        with steps.start("verify input a: '%s' < 10" % a ):
            assert a < 10

        with steps.start("verify input b: '%s' < 10" % b ):
            assert b < 10

        with steps.start("verify %s x %s ^ %s + %s < 100" % (a, b, self.c, 
                                                             self.d)) as step:
            if function_supporting_steps(step, a, b, self.c, self.d) < 100:
                step.passed()
            else:
                step.failed('result was larger than 100!')


# standalone execution
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--a', type = int)
    parser.add_argument('--b', type = int)
    aetest.main(**vars(parser.parse_known_args()[0]))



