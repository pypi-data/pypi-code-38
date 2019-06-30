"""解决数学问题"""

introduce = '''    以下是该模块所有属性的介绍：
（1）变量：
    1. introduce：该模块的所有属性的介绍

（2）函数：
    1. enumerating_factor(a: int, *, ornament=True)：用于列举a的所有因数，当ornament为True时，
返回一个字符串；当ornament为False时，返回一个列表

    2. enumerated_prime_numbers(stop: int, *, start=0, ornament=True)：用于求出start到stop中的
所有质数，当ornament为True时，返回一个字符串；当ornament为False时，返回一个列表

    3. decomposition_prime_factor(a: int, *, ornament=True)：用于将a分解质因数，当ornament为
True时，返回一个字符串；当ornament为False时，返回一个列表

    4. maximum_common_factor(*a: int, ornament=True)：用于求出a中所有元素的最大公因数，当
ornament为True时，返回一个字符串；当ornament为False时，返回一个整数

    5. minimum_common_multiple(*a: int, ornament=True)：用于求出a中所有元素的最小公倍数，当
ornament为True时，返回一个字符串；当ornament为False时，返回一个整数

    6. find_defective_products(a: int, *, ornament=True)：用于计算用天平在a个物品中找出一个次品
（知道比正品重还是比正品轻）时要称的次数，当ornament为True时，返回一个字符串；当ornament为False
时，返回一个整数

    7. calculated_average(*a: int, ornament=True)：用于求出a中所有元素的平均数，当ornament为
True时，返回一个字符串；当ornament为False时，返回一个整数

    8. sum_multiple_problem(s, m, *, ornament=True)：用于计算和为s，并且大数为小数的m倍的两个数
分别是多少，当ornament为True时，返回一个字符串；当ornament为False时，返回一个整数

    9. difference_multiple_problem(d, m, *, ornament=True)：用于计算差为d，并且大数为小数的m倍
的两个数分别是多少，当ornament为True时，返回一个字符串；当ornament为False时，返回一个整数

    10. sum_difference_problem(s, d, *, ornament=True)：用于计算和为s，差为d的两个数分别是多
少，当ornament为True时，返回一个字符串；当ornament为False时，返回一个整数

（3）类：
    1. Square（正方形）：
        a. brief_introduction：类属性，正方形的简介

        b. __init__(self, a, unit='cm')：a表示正方形的边长，unit表示单位

        c. perimeter(self, *, ornament=True)：用于计算指定的正方形的周长，当ornament为True时，
    返回一个字符串；当ornament为False时，返回一个整数

        d. area(self, *, ornament=True)：用于计算指定的正方形的面积，当ornament为
    True时，返回一个字符串；当ornament为False时，返回一个整数

    2. Rectangle（长方形）：
        a. brief_introduction：类属性，长方形的简介

        b. __init__(self, a, b, unit='cm')：a表示长方形的长，b表示长方形的宽，unit表示单位

        c. perimeter(self, *, ornament=True)：用于计算指定的长方形的周长，当ornament为True时，
    返回一个字符串；当ornament为False时，返回一个整数

        d. area(self, *, ornament=True)：用于计算指定的长方形的面积，当ornament为
    True时，返回一个字符串；当ornament为False时，返回一个整数

    3. Triangle（三角形）：
        a. brief_introduction：类属性，三角形的简介

        b. __init__(self, a, h, unit='cm')：a表示三角形的底，h表示三角形的高，unit表示单位

        c. area(self, *, ornament=True)：用于计算指定的三角形的面积，当ornament为
    True时，返回一个字符串；当ornament为False时，返回一个整数

    4. Parallelogram（平行四边形）：
        a. brief_introduction：类属性，平行四边形的简介

        b. __init__(self, a, h, unit='cm')：a表示平行四边形的底，h表示平行四边形的高，unit表示
    单位

        c. area(self, *, ornament=True)：用于计算指定的平行四边形的面积，当ornament
    为True时，返回一个字符串；当ornament为False时，返回一个整数

    5. Trapezoid（梯形）：
        a. brief_introduction：类属性，梯形的简介

        b. __init__(self, a, b, h, unit='cm')：a表示梯形的上底，b表示梯形的下底，h表示梯形的
    高，unit表示单位

        c. area(self, *, ornament=True)：用于计算指定的梯形的面积，当ornament为True
    时，返回一个字符串；当ornament为False时，返回一个整数

    6. Cube（正方体）：
        a. brief_introduction：类属性，正方体的简介

        b. __init__(self, a, unit='cm')：a表示棱长，unit表示单位

        c. edge_length_summation(self, *, ornament=True)：用于计算指定的正方体的棱长总和，当
    ornament为True时，返回一个字符串；当ornament为False时，返回一个整数

        d. surface_area(self, *, ornament=True)：用于计算指定的正方体的表面积，当ornament为True
    时，返回一个字符串；当ornament为False时，返回一个整数

        e. volume(self, *, ornament=True)：用于计算指定的正方体的体积，当ornament为True时，返回
    一个字符串；当ornament为False时，返回一个整数

    7. Cuboid（长方体）：
        a. brief_introduction：类属性，长方体的简介

        b. __init__(self, a, b, h, unit='cm')：a表示长方体的长，b表示长方体的宽，h表示长方体的
    高，unit表示单位

        c. edge_length_summation(self, *, ornament=True)：用于计算指定的长方体的棱长总和，当
    ornament为True时，返回一个字符串；当ornament为False时，返回一个整数

        d. surface_area(self, *, ornament=True)：用于计算指定的长方体的表面积，当ornament为True
    时，返回一个字符串；当ornament为False时，返回一个整数

        e. volume(self, *, ornament=True)：用于计算指定的长方体的体积，当ornament为True时，返回
    一个字符串；当ornament为False时，返回一个整数'''


def enumerating_factor(a: int, *, ornament=True) -> str or list:
    """列举一个数的所有因数"""
    all_factors = []  # 初始化一个列表用于储存所有的因数
    # 使用for-in循环列举所有可能是这个数的因数的数
    for factor in range(1, a + 1):
        # 使用if语句判断该数是不是a的因数，如果是
        if not a % factor:
            # 则将该数储存到列表里
            all_factors.append(factor)
    # 使用if语句判断是否要修饰返回值，如果要
    if ornament:
        # 则按“{a}的因数有：{all_factors[0], all_factors[1], ..., all_factors[-1]}”的格式返回
        return '{}的因数有：{}'.format(a, ', '.join(map(str, all_factors)))
    # 如果不要
    else:
        # 则直接返回all_factors
        return all_factors


def enumerated_prime_numbers(stop: int, *, start=0, ornament=True) -> str or list:
    """求出范围内的所有质数"""
    all_prime_numbers = []  # 初始化一个列表用于储存所有的质数
    # 使用for-in循环列举范围内的所有数
    for number1 in range(start, stop + 1):
        # 使用if语句判断该数是否等于0或1，如果等于
        if number1 <= 1:
            # 则退出本次循环
            continue
        # 使用for-in循环列举所有可能是这个数的因数的数
        for number2 in range(2, number1):
            # 使用if语句判断该数是不是number1的因数，如果是
            if not number1 % number2:
                # 则退出整个循环
                break
        # 如果循环正常结束，则找到了一个质数
        else:
            # 将该数储存到列表里
            all_prime_numbers.append(number1)
    # 使用if语句判断是否要修饰返回值，如果要
    if ornament:
        # 则按“{start}到{stop}之间的质数有：
        # {all_prime_numbers[0], all_prime_numbers[1], ..., all_prime_numbers[-1]}”的格式返回
        return '{}到{}之间的质数有：{}'.format(start, stop, ', '.join(map(str,
                                                              all_prime_numbers)))
    # 如果不要
    else:
        # 则直接返回all_prime_numbers
        return all_prime_numbers


def decomposition_prime_factor(a: int, *, ornament=True) -> str or list:
    """将一个数分解质因数"""
    all_prime_factors = []  # 初始化一个列表用于储存所有的质因数
    c = a                   # 将a赋值给c，以便以后打印
    # 使用for-in循环列举所有可能是这个数的质因数的数
    for factor in enumerated_prime_numbers(a, ornament=False):
        # 使用while循环反复判断该数是不是a的质因数，如果是
        while not a % int(factor):
            # 则将该数储存到列表里
            all_prime_factors.append(int(factor))
            # 再用a除以该数
            a /= int(factor)
    # 使用if语句判断是否要修饰返回值，如果要
    if ornament:
        # 则先使用内置函数map将all_prime_factors的所有元素转换为字符串类型，再按
        # “{c} = {all_prime_factors[0] * all_prime_factors[1] * ... * all_prime_factors[-1]}”
        # 的格式返回
        return '{} = {}'.format(c, ' * '.join(map(str, all_prime_factors)))
    # 如果不要
    else:
        # 则直接返回all_prime_factors
        return all_prime_factors


def maximum_common_factor(*a: int, ornament=True) -> str or int:
    """求多个数的最大公因数"""
    if len(a) < 2:
        return '数字的个数必须大于2'
    b = 1
    for c in range(sorted(a)[1] + 1, 1, -1):
        for d in a:
            if d % c:
                break
        else:
            b = c
            break
    # 使用if语句判断是否要修饰返回值，如果要
    if ornament:
        # 则按“{a[0]、a[1]、...、a[-2]}和{a[-1]}的最大公因数是{b}”的格式返回
        return '{}和{}的最大公因数是{}'.format('、'.join(map(str, a[0:-1])),
                                       a[-1], b)
    # 如果不要
    else:
        # 则直接返回b
        return b


def minimum_common_multiple(*a: int, ornament=True) -> str or int:
    """求多个数的最小公倍数"""
    if len(a) < 2:
        return '数字的个数必须大于2'
    b = 1
    for c in a:
        b *= c
    d = b
    for e in range(sorted(a)[-1], b + 1):
        for f in a:
            if e % f:
                break
        else:
            d = e
            break
    # 使用if语句判断是否要修饰返回值，如果要
    if ornament:
        # 则按“{a[0]、a[1]、...、a[-2]}和{a[-1]}的最小公倍数是{d}”的格式返回
        return '{}和{}的最小公倍数是{}'.format('、'.join(map(str, a[0:-1])),
                                       a[-1], d)
    # 如果不要
    else:
        # 则直接返回b
        return d


def find_defective_products(a: int, *, ornament=True) -> str or int:
    """解决找次品的问题"""
    if a < 2:
        return '数量至少要为2'
    b = 1
    while not 3 ** (b - 1) < a <= 3 ** b:
        b += 1
    if ornament:
        return '至少要称{}次才能保证找到这个次品'.format(b)
    else:
        return b


def calculated_average(*a: int, ornament=True):
    """计算多个数的平均数"""
    if len(a) < 2:
        return '数字的个数必须大于2'
    b = 0
    for c in a:
        b += c
    b /= len(a)
    if ornament:
        return '{}和{}的平均数是{}'.format('、'.join(map(str, a[0:-1])), a[-1],
                                     int(b) if ((str(b)[-2] == '.') and
                                                (str(b)[-1] == '0')) else b)
    else:
        return int(b) if ((str(b)[-2] == '.') and (str(b)[-1] == '0')) else b


def sum_multiple_problem(s, m, *, ornament=True) -> tuple or str:
    """解决和倍问题"""
    a = s / (m + 1) * m
    b = s / (m + 1)
    if ornament:
        return '这两个数是{}和{}'.format(int(a) if (str(a)[-2] == '.') and
                                             (str(a)[-1] == '0') else a,
                                   int(b) if ((str(b)[-2] == '.') and
                                              (str(b)[-1] == '0')) else b)
    else:
        return int(a) if ((str(a)[-2] == '.') and
                          (str(a)[-1] == '0')) else a,\
               int(b) if ((str(b)[-2] == '.') and
                          (str(b)[-1] == '0')) else b


def difference_multiple_problem(d, m, *, ornament=True) -> tuple or str:
    """解决差倍问题"""
    a = d / (m - 1) * m
    b = d / (m - 1)
    if ornament:
        return '这两个数是{}和{}'.format(int(a) if (str(a)[-2] == '.') and
                                             (str(a)[-1] == '0') else a,
                                   int(b) if ((str(b)[-2] == '.') and
                                              (str(b)[-1] == '0')) else b)
    else:
        return int(a) if ((str(a)[-2] == '.') and
                          (str(a)[-1] == '0')) else a,\
               int(b) if ((str(b)[-2] == '.') and
                          (str(b)[-1] == '0')) else b


def sum_difference_problem(s, d, *, ornament=True) -> tuple or str:
    """解决和差问题"""
    a = (s + d) / 2
    b = (s - d) / 2
    if ornament:
        return '这两个数是{}和{}'.format(int(a) if (str(a)[-2] == '.') and
                                             (str(a)[-1] == '0') else a,
                                   int(b) if ((str(b)[-2] == '.') and
                                              (str(b)[-1] == '0')) else b)
    else:
        return int(a) if ((str(a)[-2] == '.') and
                          (str(a)[-1] == '0')) else a,\
               int(b) if ((str(b)[-2] == '.') and
                          (str(b)[-1] == '0')) else b


class Square(object):
    """解决关于正方形的所有问题"""
    brief_introduction = '''正方形简介：
（1）有四条长度都相等的边；
（2）四个角都为直角。'''

    def __init__(self, a, unit='cm'):
        self.a = a          # 边长
        self.unit = unit    # 单位

    def __str__(self):
        return '一个边长为{}{}的正方形'.format(self.a, self.unit)

    __repr__ = __str__

    def __getattr__(self, item):
        return "该属性或方法不存在，能访问的属性有：'a'、'unit'，能访问的方法有：'perimeter()'\
、'area()'"

    __slots__ = ('a', 'unit')

    def perimeter(self, *, ornament=True) -> str or int:
        """计算周长"""
        # 使用if语句判断是否要修饰返回值，如果要
        if ornament:
            # 则按“边长为{a}{unit}的正方形的周长为{a * 4}{unit}”的格式返回
            return '边长为{}{}的正方形的周长为{}{}'.format(self.a, self.unit, self.a * 4,
                                                self.unit)
        # 如果不要
        else:
            # 则直接返回a * 4
            return self.a * 4

    def area(self, *, ornament=True) -> str or int:
        """计算面积"""
        # 使用if语句判断是否要修饰返回值，如果要
        if ornament:
            # 则按“边长为{a}{unit}的正方形的面积为{a ** 2}{unit}²”的格式返回
            return '边长为{}{}的正方形的面积为{}{}²'.format(self.a, self.unit, self.a ** 2,
                                                 self.unit)
        # 如果不要
        else:
            # 则直接返回a ** 2
            return self.a ** 2


class Rectangle(object):
    """解决关于长方形的所有问题"""
    brief_introduction = '''长方形简介：
（1）相对的两条边长度相等；
（2）四个角都为直角。'''

    def __init__(self, a, b, unit='cm'):
        self.a = a          # 长
        self.b = b          # 宽
        self.unit = unit    # 单位

    def __str__(self):
        return '一个长为{}{}，宽为{}{}的长方形'.format(self.a, self.unit, self.b, self.unit)

    __repr__ = __str__

    def __getattr__(self, item):
        return "该属性或方法不存在，能访问的属性有：'a'、'b'、'unit'，能访问的方法有：\
'perimeter()'、'area()'"

    __slots__ = ('a', 'b', 'unit')

    def perimeter(self, *, ornament=True) -> str or int:
        """计算周长"""
        # 使用if语句判断是否要修饰返回值，如果要
        if ornament:
            # 则按“长为{a}{unit}，宽为{b}{unit}的长方形的周长为{(a + b) * 2}{unit}”
            # 的格式返回
            return '长为{}{}，宽为{}{}的长方形的周长为{}{}'.format(self.a, self.unit, self.b,
                                                      self.unit, (self.a + self.b) * 2, self.unit)
        # 如果不要
        else:
            # 则直接返回(a + b) * 2
            return (self.a + self.b) * 2

    def area(self, *, ornament=True) -> str or int:
        """计算面积"""
        # 使用if语句判断是否要修饰返回值，如果要
        if ornament:
            # 则按“长为{a}{unit}，宽为{b}{unit}的长方形的面积为{a * b}{unit}²”的格式返回
            return '长为{}{}，宽为{}{}的长方形的面积为{}{}²'.format(self.a, self.unit, self.b,
                                                       self.unit, self.a * self.b, self.unit)
        # 如果不要
        else:
            # 则直接返回a * b
            return self.a * self.b


class Triangle(object):
    """解决关于三角形的所有问题"""
    brief_introduction = '''三角形简介：
（1）有三条边；
（2）有两条边长度相等的叫等腰三角形；
（3）有三条边长度相等的叫等边三角形；
（4）三个角都是锐角的叫锐角三角形；
（5）有一个钝角的叫钝角三角形；
（6）有一个直角的叫直角三角形；
（7）三个角的和为180°；
（8）任意两条边的和都大于另一条边；
（9）从一个顶点到相对的边的垂线叫做三角形的高。'''

    def __init__(self, a, h, unit='cm'):
        self.a = a          # 底
        self.h = h          # 高
        self.unit = unit    # 单位

    def __str__(self):
        return '一个底为{}{}，高为{}{}的三角形'.format(self.a, self.unit, self.h, self.unit)

    __repr__ = __str__

    def __getattr__(self, item):
        return "该属性或方法不存在，能访问的属性有：'a'、'h'、'unit'，能访问的方法有：\
'area()'"

    __slots__ = ('a', 'h', 'unit')

    def area(self, *, ornament=True) -> str or int:
        """计算面积"""
        # 使用if语句判断是否要修饰返回值，如果要
        if ornament:
            # 则按“底为{a}{unit}，高为{h}{unit}的三角形的面积为{a * h / 2}{unit}²”的格式返回
            return '底为{}{}，高为{}{}的三角形的面积为{}{}²'.format(self.a, self.unit, self.h,
                                                       self.unit, self.a * self.h / 2, self.unit)
        # 如果不要
        else:
            # 则直接返回a * h / 2
            return self.a * self.h / 2


class Parallelogram(object):
    """解决关于平行四边形的所有问题"""
    brief_introduction = '''平行四边形简介：
（1）有四条边；
（2）相对的两条边平行、长度相等；
（3）四个角的总和为360°；
（4）从一条边上的一个点到相对的边的垂线叫做平行四边形的高。'''

    def __init__(self, a, h, unit='cm'):
        self.a = a          # 底
        self.h = h          # 高
        self.unit = unit    # 单位

    def __str__(self):
        return '一个底为{}{}，高为{}{}的平行四边形'.format(self.a, self.unit, self.h, self.unit)

    __repr__ = __str__

    def __getattr__(self, item):
        return "该属性或方法不存在，能访问的属性有：'a'、'h'、'unit'，能访问的方法有：\
'area()'"

    __slots__ = ('a', 'h', 'unit')

    def area(self, *, ornament=True) -> str or int:
        """计算面积"""
        # 使用if语句判断是否要修饰返回值，如果要
        if ornament:
            # 则按“底为{a}{unit}，高为{h}{unit}的平行四边形的面积为{a * h}{unit}²”的格式返回
            return '底为{}{}，高为{}{}的平行四边形的面积为{}{}²'.format(self.a, self.unit,
                                                         self.h, self.unit, self.a * self.h,
                                                         self.unit)
        # 如果不要
        else:
            # 则直接返回a * h
            return self.a * self.h


class Trapezoid(object):
    """解决关于梯形的所有问题"""
    brief_introduction = '''梯形简介：
（1）只用一对平行的边，长的叫下底，短的叫上底；
（2）其他两条边都叫腰；
（3）从上底上的一个点到下底的垂线叫做梯形的高。'''

    def __init__(self, a, b, h, unit='cm'):
        self.a = a          # 上底
        self.b = b          # 下底
        self.h = h          # 高
        self.unit = unit    # 单位

    def __str__(self):
        return '一个上底为{}{}，下底为{}{}，高为{}{}的梯形'.format(self.a, self.unit, self.b,
                                                    self.unit, self.h, self.unit)

    __repr__ = __str__

    def __getattr__(self, item):
        return "该属性或方法不存在，能访问的属性有：'a'、'b'、'h'、'unit'，能访问的方法有：\
'area()'"

    __slots__ = ('a', 'b', 'h', 'unit')

    def area(self, *, ornament=True) -> str or int:
        """计算面积"""
        # 使用if语句判断是否要修饰返回值，如果要
        if ornament:
            # 则按
            # “上底为{a}{unit}，下底为{b}{unit}，高为{h}{unit}²的梯形的面积为{(a + b) * h / 2}”
            # 的格式返回
            return '上底为{}{}，下底为{}{}，高为{}{}的梯形的面积为{}{}²'.format(self.a,
                                                               self.unit, self.b, self.unit,
                                                               self.h, self.unit,
                                                               (self.a + self.b) * self.h / 2,
                                                               self.unit)
        # 如果不要
        else:
            # 则直接返回(a + b) * h / 2
            return (self.a + self.b) * self.h / 2


class Cube(object):
    """解决关于正方体的所有问题"""
    brief_introduction = '''正方体简介：
（1）有十二条长度相等的棱；
（2）有六个完全相同的面，每个面都是正方形；
（3）是长、宽、高都相等的长方体。'''

    def __init__(self, a, unit='cm'):
        self.a = a          # 棱长
        self.unit = unit    # 单位

    def __str__(self):
        return '一个棱长为{}{}的正方体'.format(self.a, self.unit)

    __repr__ = __str__

    def __getattr__(self, item):
        return "该属性或方法不存在，能访问的属性有：'a'、'unit'，能访问的方法有：\
'edge_length_summation()'、'surface_area()'、'volume()'"

    __slots__ = ('a', 'unit')

    def edge_length_summation(self, *, ornament=True) -> str or int:
        """计算棱长总和"""
        # 使用if语句判断是否要修饰返回值，如果要
        if ornament:
            # 则按“棱长为{a}{unit}的正方体的棱长总和为{a * 12}{unit}”的格式返回
            return '棱长为{}{}的正方体的棱长总和为{}{}'.format(self.a, self.unit, self.a * 12,
                                                  self.unit)
        # 如果不要
        else:
            # 则直接返回a * 12
            return self.a * 12

    def surface_area(self, *, ornament=True) -> str or int:
        """计算表面积"""
        # 使用if语句判断是否要修饰返回值，如果要
        if ornament:
            # 则按“棱长为{a}{unit}的正方体的表面积为{a ** 2 * 6}{unit}²”的格式返回
            return '棱长为{}{}的正方体的表面积为{}{}²'.format(self.a, self.unit, self.a ** 2 * 6,
                                                  self.unit)
        # 如果不要
        else:
            # 则直接返回a ** 2 * 6
            return self.a ** 2 * 6

    def volume(self, *, ornament=True) -> str or int:
        """计算体积"""
        # 使用if语句判断是否要修饰返回值，如果要
        if ornament:
            # 则按“棱长为{a}{unit}的正方体的体积为{a ** 3}{unit}³”的格式返回
            return '棱长为{}{}的正方体的体积为{}{}³'.format(self.a, self.unit, self.a ** 3,
                                                 self.unit)
        # 如果不要
        else:
            # 则直接返回a ** 3
            return self.a ** 3


class Cuboid(object):
    """解决关于长方体的所有问题"""
    brief_introduction = '''长方体简介：
（1）横的四条棱长度相等，都叫做长；
（2）斜的四条棱长度相等，都叫做宽；
（3）竖的四条棱长度相等，都叫做高；
（4）相对的面完全相同；
（5）每个面都是长方形或正方形。'''

    def __init__(self, a, b, h, unit='cm'):
        self.a = a          # 长
        self.b = b          # 宽
        self.h = h          # 高
        self.unit = unit    # 单位

    def __str__(self):
        return '一个长为{}{}，宽为{}{}，高为{}{}的长方体'.format(self.a, self.unit, self.b,
                                                   self.unit, self.h, self.unit)

    __repr__ = __str__

    def __getattr__(self, item):
        return "该属性或方法不存在，能访问的属性有：'a'、'b'、'h'、'unit'，能访问的方法有：\
'edge_length_summation()'、'surface_area()'、'volume()'"

    __slots__ = ('a', 'b', 'h', 'unit')

    def edge_length_summation(self, *, ornament=True) -> str or int:
        """计算棱长总和"""
        # 使用if语句判断是否要修饰返回值，如果要
        if ornament:
            # 则按“长为{a}{unit}，宽为{b}{unit}，高为{h}{unit}的长方体的棱长总和为
            # {(a + b + h) * 4}{unit}”的格式返回
            return '长为{}{}，宽为{}{}，高为{}{}的长方体的棱长总和为{}{}'.format(self.a,
                                                               self.unit, self.b, self.unit,
                                                               self.h, self.unit, (self.a + self.b +
                                                                                   self.h) * 4,
                                                               self.unit)
        # 如果不要
        else:
            # 则直接返回(a + b + h) * 4
            return (self.a + self.b + self.h) * 4

    def surface_area(self, *, ornament=True) -> str or int:
        """计算表面积"""
        # 使用if语句判断是否要修饰返回值，如果要
        if ornament:
            # 则按“长为{a}{unit}，宽为{b}{unit}，高为{h}{unit}的长方体的表面积为{(a * b + a * h
            # + b * h) * 2}{unit}²”的格式返回
            return '长为{}{}，宽为{}{}，高为{}{}的长方体的表面积为{}{}²'.format(self.a,
                                                               self.unit, self.b, self.unit,
                                                               self.h, self.unit, (self.a * self.b
                                                                                   + self.a * self.h
                                                                                   + self.b *
                                                                                   self.h) * 2,
                                                               self.unit)
        # 如果不要
        else:
            # 则直接返回(a * b + a * h + b * h) * 2
            return (self.a * self.b + self.a * self.h + self.b * self.h) * 2

    def volume(self, *, ornament=True) -> str or int:
        """计算体积"""
        # 使用if语句判断是否要修饰返回值，如果要
        if ornament:
            # 则按“长为{a}{unit}，宽为{b}{unit}，高为{h}{unit}的长方体的体积为
            # {a * b * h}{unit}³”的格式返回
            return '长为{}{}，宽为{}{}，高为{}{}的长方体的体积为{}{}³'.format(self.a,
                                                              self.unit, self.b, self.unit,
                                                              self.h, self.unit, self.a * self.b
                                                              * self.h,
                                                              self.unit)
        # 如果不要
        else:
            # 则直接返回a * b * h
            return self.a * self.b * self.h
