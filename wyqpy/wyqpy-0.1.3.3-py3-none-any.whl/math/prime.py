"""
Created on 2017年8月12日

@author: WYQ
"""

import math


def is_prime(n):
    """
    alter:from mpmath.libmp.libintmath import isprime
    @param n: 大于0
    @return: 判断n是否是质数
    """
    if n <= 1:
        return False
    for i in range(2, math.floor(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def is_composite(n):
    """
    @param n: 大于3
    @return: 判断n是否是合数
    """
    if n < 4 or is_prime(n):
        return False
    return True


def is_odd(n):
    """
    @param n: 大于等于0
    @return: 判断n是否是奇数
    """
    if n % 2 == 1:
        return True
    return False


def is_even(n):
    """
    @param n: 大于等于0
    @return: 判断n是否是偶数
    """
    if n % 2 == 0:
        return True
    return False


def get_max_prime(n):
    """
    @param n: 大于等于2
    @return: 获取最大质数
    """
    if (n < 2):
        return None
    while True:
        if is_prime(n):
            return n
        n = n - 1


def get_max_composite(n):
    """
    @param n: 大于等于4
    @return: 判断n是否是质数
    """
    if (n < 4):
        return None
    while True:
        if is_composite(n):
            return n
        n = n - 1


def get_max_even(n):
    """
    @param n: 大于等于0
    @return: 获取最大偶数
    """
    if (n < 0):
        return None
    return n if is_even(n) else n - 1


def get_max_odd(n):
    """
    @param n: 大于0
    @return: 获取最大奇数
    """
    if (n < 1):
        return None
    return n if is_odd(n) else n - 1


def get_all_primes(minn, maxn):
    """
    @param minn: 大于等于0
    @param maxn: 大于等于minn
    @return: 获取所有质数
    """
    result = [];
    if minn <= 2:
        minn = 2
    if minn > maxn:
        return result;
    for i in range(minn, maxn + 1):
        if is_prime(i):
            result.append(i)
    return result


def get_next_prime(startPrime):
    if startPrime <= 0:
        raise ValueError("startPrime 必须大于0 ")
    n = startPrime + 1
    while not is_prime(n):
        n += 1
    return n


def get_pre_prime(endPrime):
    if endPrime <= 0:
        raise ValueError("endPrime 必须大于0 ")
    n = endPrime - 1
    while not is_prime(n):
        n -= 1
        if n < 2:
            return None
    return n


def get_next_primes(startPrime, count):
    cntu = True
    ps = []
    lp = startPrime
    while len(ps) < count:
        p = get_next_prime(lp)
        ps.append(p)
        lp = p

    return ps


def get_prime_position(p):
    if not is_prime(p):
        return None
    else:
        return len(get_all_primes(0, p))


def get_all_composites(minn, maxn):
    """
    @param minn: 大于等于0
    @param maxn: 大于等于minn
    @return: 获取所有复数
    """
    result = [];
    if minn <= 2:
        minn = 2
    if minn > maxn:
        return result;
    for i in range(minn, maxn + 1):
        if (is_composite(i)):
            result.append(i)
    return result


def get_all_evens(minn, maxn):
    """
    @param minn: 大于等于0
    @param maxn: 大于等于minn
    @return: 获取所有偶数
    """
    result = [];
    if minn <= 0:
        minn = 0
    if minn > maxn:
        return result;
    for i in range(minn, maxn + 1):
        if (is_even(i)):
            result.append(i)
    return result


def get_all_odds(minn, maxn):
    """
    @param minn: 大于等于0
    @param maxn: 大于等于minn
    @return: 获取所有奇数
    """
    result = [];
    if minn <= 0:
        minn = 0
    if minn > maxn:
        return result;
    for i in range(minn, maxn + 1):
        if (is_odd(i)):
            result.append(i)
    return result


def get_ed_primes(n, max=1000):
    """
    获取n左右等距离的所有素数对
    :param n:
    :param max:
    :return:
    """
    d = 0
    l = n - d
    r = n + d
    ps = {}
    count = 0
    while l > 1 and count < max:
        if is_prime(l) and is_prime(r):
            ps[d] = [l, r]
            count += 1
        d = d + 1
        l = n - d
        r = n + d
    return ps


def get_right_ed_prime(p, nmax=100, countmax=100):
    """
    获取p以n左右等距离的所有素数对
    :param p:
    :param max:
    :return:
    """
    count = 0
    d = 0
    n = p + d
    ps = {}
    while count < countmax and n < nmax:
        r = 2 * n - p
        if is_prime(r):
            ps[d] = [p, r, n]
            count = +1
        d += 1
        n = p + d

    return ps


def get_left_ed_prime(p):
    """
    获取p以n左右等距离的所有素数对
    :param p:
    :param max:
    :return:
    """
    d = 0
    n = p - d
    l = n - d
    ps = {}
    while l > 1:
        if is_prime(l):
            ps[d] = [l, p, n]
        d += 1
        n = p - d
        l = n - d
    return ps


def factorial(n):
    """
    @param n: 大于0
    @return: 返回n的阶乘
    """
    return math.factorial(n)


def wilson_top(n):
    """
    @param n: n为质数
    @return: 返回威尔逊分子
    """
    #     if not isPrime(n):
    #         return None
    return math.factorial(n - 1) + 1


def wilson(n):
    """
    @param n: n为质数
    @return: 返回威尔逊数
    """
    if not is_prime(n):
        return None
    return (math.factorial(n - 1) + 1) / n


def get_near_primes(p, evenSpan=2, count=1):
    """
    获取左右等距离素数对
    """
    if evenSpan % 2 != 0 or is_composite(p) or count <= 0:
        return None
    result = []
    while count > 0:
        if is_prime(p):
            if is_prime(p + evenSpan):
                result.append([p, p + evenSpan])
                count -= 1
        p += 1
    return result


def get_mul_prime(length=1):
    """
    获取length个素数乘积
    :param length:
    :return:
    """
    pp = 1;
    for p in get_next_primes(1, length):
        pp = pp * p
    return pp


def get_all_mul_primes(count=1):
    """
    获取count个的length个素数乘积
    :param count:
    :return:
    """
    pps = []
    ps = get_next_primes(1, count)
    for i in range(0, count):
        pp = 1;
        for j in range(0, i + 1):
            pp = pp * ps[j]
        pps.append(pp)

    return pps


"""
Odd Even Composite
"""

"""
factor
"""

import random
from collections import Counter


def gcd(a, b):
    if a == 0:
        return b
    if a < 0:
        return gcd(-a, b)
    while b > 0:
        c = a % b
        a, b = b, c
    return a


def mod_mul(a, b, n):
    result = 0
    while b > 0:
        if (b & 1) > 0:
            result = (result + a) % n
        a = (a + a) % n
        b = (b >> 1)
    return result


def mod_exp(a, b, n):
    result = 1
    while b > 0:
        if (b & 1) > 0:
            result = mod_mul(result, a, n)
        a = mod_mul(a, a, n)
        b = (b >> 1)
    return result


def miller_rabin_prime_check(n):
    if n in {2, 3, 5, 7, 11}:
        return True
    elif (n == 1 or n % 2 == 0 or n % 3 == 0 or n % 5 == 0 or n % 7 == 0 or n % 11 == 0):
        return False
    k, u = 0, n - 1
    while not (u & 1) > 0:
        k += 1
        u = (u >> 1)
    random.seed(0)
    s = 5
    for i in range(s):
        x = random.randint(2, n - 1)
        if x % n == 0:
            continue
        x = mod_exp(x, u, n)
        pre = x
        for j in range(k):
            x = mod_mul(x, x, n)
            if (x == 1 and pre != 1 and pre != n - 1):
                return False
            pre = x
        if x != 1:
            return False
        return True


def pollard_rho(x, c):
    (i, k) = (1, 2)
    x0 = random.randint(0, x)
    y = x0
    while 1:
        i += 1
        x0 = (mod_mul(x0, x0, x) + c) % x
        d = gcd(y - x0, x)
        if d != 1 and d != x:
            return d
        if y == x0:
            return x
        if i == k:
            y = x0
            k += k


def prime_factors_list_generator(n):
    result = []
    if n <= 1:
        return None
    if miller_rabin_prime_check(n):
        return [n]
    p = n
    while p >= n:
        p = pollard_rho(p, random.randint(1, n - 1))
    result.extend(prime_factors_list_generator(p))
    result.extend(prime_factors_list_generator(n // p))
    return result


def prime_factors_list_cleaner(n):
    return Counter(prime_factors_list_generator(n))


def prime_factors_list_cleaner_sorted(n):
    d = prime_factors_list_cleaner(n);
    ks = sorted(d.keys())
    nd = {}
    for k in ks:
        nd[k] = d[k]
    return nd
