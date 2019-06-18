class CustomClassOne(object):
    def custom_method_one(self):
        return True


class CustomClassTwo(object):
    def custom_method_two(self):
        return True


class CustomClassThree(object):
    def custom_method_three(self):
        return True


class CustomClassFour(object):
    def custom_method_four(self):
        return True


class CustomClassFive(object):
    def custom_method_five(self):
        return True


class CustomClassSix(object):
    def custom_method_six(self):
        return True


class CustomClassSeven(object):
    def custom_method_seven(self):
        CustomClassOne().custom_method_one()
        return True


class CustomClassEight(object):
    def custom_method_eight(self):
        raise Exception('Some exception')
        return True
