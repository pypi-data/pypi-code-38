# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import collections

# TODO: docstrings and eval text should match better.
ARITHMETICS_OPS = [
    ("+ (plus)", "${signal0} + ${signal1}", "Plus"),
    ("- (minus)", "${signal0} - ${signal1}", "Minus"),
    ("* ", "${signal0} * ${signal1}",
     "mtimes - Matrix Multiplication\n\n"
     "This MATLAB function is the matrix product of A and B.\n"
     "C = A*B\n"
     "C = mtimes(A,B)"),
    (".*", "${signal0} .* ${signal1}",
     "times - Element-wise multiplication\n\n"
     "This MATLAB function multiplies arrays A and B element by element and\n "
     "returns the result in C.\n\n"
     "C = A.*B\n"
     "C = times(A,B)"),
    ("^", "${signal0} ^ ${signal1}",
     "mpower - Matrix power\n\n"
     "This MATLAB function computes A to the B power and returns the result in"
     " C.\n\n"
     "C = A^B\n"
     "C = mpower(A,B)"),
    (".^ ", "${signal0} .^ ${signal1}",
     "power - Element-wise power\n\n"
     "This MATLAB function raises each element of A to the corresponding power"
     " in B.\n\n"
     "C = A.^B\n"
     "C = power(A,B)"),
    ("/", "${signal0} / ${signal1}",
     "mrdivide - Solve systems of linear equations xA = B for x\n\n"
     "This MATLAB function solves the system of linear equations x*A = B for "
     "x.\n\n"
     "x = B/A\n"
     "x = mrdivide(B,A)"),
    ("./", "${signal0}./${signal1}",
     "rdivide - Right array division\n\n"
     "This MATLAB function divides each element of A by the corresponding "
     "element of B.\n\n"
     "x = A./B\n"
     "x = rdivide(A,B)"),
    ("sqrt", "sqrt(${signal0})", "sqrt - Square root\n"
                                 "This MATLAB function returns the square root"
                                 " of each element of the array X.\n\n"
                                 "B = sqrt(X)"),
    ("mod", "mod(${signal0}, value)",
     "mod - Remainder after division (modulo operation) \n"
     "This MATLAB function returns the remainder after division of a by m, "
     "where a is \n"
     "the dividend and m is the divisor. \n \n"
     "b = mod(a,m) \n"),
    ("idivide", "idivide(int32(${signal0}), int32(${signal1}))",
     "idivide - Integer division with rounding option \n"
     "This MATLAB function is the same as A./B for integer classes except "
     "that \n fractional quotients are rounded to integers using the "
     "optional rounding mode \n"
     "specified by opt.\n\n "
     "C = idivide(A, B, opt)\n"
     "C = idivide(A, B) \n"
     "C = idivide(A, B, 'fix')\n"
     "C = idivide(A, B, 'round')\n"
     "C = idivide(A, B, 'floor')\n"
     "C = idivide(A, B, 'ceil')"),
]

# TODO: docstrings and eval text should match better.
COMPARATORS = [
    ("== (equal)", "${signal0} == ${signal1}",
     "eq - Determine equality\n\n"
     "This MATLAB function returns a logical array with elements set to "
     "logical 1\n (true) where arrays A and B are equal; otherwise, "
     "it returns logical 0 (false).\n\n"
     "A == B\n"
     "eq(A,B)"),
    ("~= (not equal)", "${signal0} != ${signal1}",
     "ne - Determine inequality \n\n"
     "This MATLAB function returns a logical array with elements set to "
     "logical 1\n (true) where arrays A and B are not equal; otherwise, "
     "it returns logical 0\n"
     "(false). \n\n"
     "A ~= B\n"
     "ne(A,B"),
    ("> (more than)", "${signal0} > ${signal1}",
     "gt - Determine greater than\n\n"
     "This MATLAB function returns a logical array with elements set to "
     "logical 1\n (true) where A is greater than B; otherwise, it returns "
     "logical 0 (false).\n\n"
     "A > B\n"
     "gt(A,B)"),
    ("< (less than)", "${signal0} < ${signal1}",
     "lt - Determine less than \n\n"
     "This MATLAB function returns an array with elements set to logical 1 "
     "(true)\n where A is less than B; otherwise, it returns logical 0 ("
     "false).\n"
     "A < B\n"
     "lt(A,B)"),
    (">= (more or equal)", "${signal0} >= ${signal1}",
     "ge - Determine greater than or equal to\n\n"
     "This MATLAB function returns a logical array with elements set to "
     "logical 1\n (true) where A is greater than or equal to B; otherwise, "
     "it returns logical 0\n"
     "(false).\n\n"
     "A >= B\n"
     "ge(A,B)"),
    ("<= (less or equal)", "${signal0} <= ${signal1}",
     "le - Determine less than or equal to\n\n"
     "This MATLAB function returns a logical array with elements set to "
     "logical 1\n (true) where A is less than or equal to B; otherwise, "
     "it returns logical 0\n (false).\n\n"
     "A <= B\n"
     "le(A,B)"),
]

LOGIC_OPS = [
    ("not", "not(${signal0})",
     "not - Find logical NOT\n\n"
     "This MATLAB function performs a logical NOT of input array A, "
     "and returns an\n array containing elements set to either logical 1 "
     "(true) or logical 0 (false).\n\n"
     "~A\n"
     "not(A)"),
    ("and", "and(${signal0}, ${signal1})",
     "and - Find logical AND\n\n"
     "This MATLAB function performs a logical AND of all input arrays A, "
     "B, etc., and\n returns an array containing elements set to either "
     "logical 1 (true) or logical 0\n"
     "(false).\n\n"
     " A & B & ...\n"
     "and(A, B)"),
    ("or", "or(${signal0}, ${signal1})",
     "or - Find logical OR\n\n"
     "This MATLAB function performs a logical OR of all input arrays A, "
     "B, etc., and\n returns an array containing elements set to either "
     "logical 1 (true) or logical 0\n (false).\n\n"
     "A | B | ...\n"
     "or(A, B)"),
    ("all", "all(${signal0})",
     "all - Determine if all array elements are nonzero or true\n\n"
     "This MATLAB function tests along the first array dimension of A "
     "whose size does\n not equal 1, and determines if the elements are all "
     "nonzero or logical 1 (true).\n\n"
     "B = all(A)\n"
     "B = all(A,dim)"),
    ("any", "any(${signal0})",
     "any - Determine if any array elements are nonzero\n\n"
     "This MATLAB function tests along the first array dimension of A "
     "whose size does\n not equal 1, and determines if any element is a "
     "nonzero number or logical 1\n (true).\n\n"
     "B = any(A)\n"
     "B = any(A,dim)"),
    ("xor", "xor(${signal0}, ${signal1})",
     "xor - Logical exclusive-OR\n\n"
     "This MATLAB function performs an exclusive OR operation on the "
     "corresponding\n elements of arrays A and B.\n\n"
     "C = xor(A, B)"),
]

# TODO: docstrings and eval text should match better.
BITWISE = [
    ("bitnot", "bitnot(${signal0})",
     "bitnot - .NET enumeration object bit-wise NOT instance method\n\n"
     "This MATLAB function reverses all bits of the .NET enumeration objects "
     "netobj.\n\n"
     "objout = bitnot(netobj)"),
    ("bitand", "bitand(${signal0}, ${signal1})",
     "bitand - Bit-wise AND\n\n"
     "This MATLAB function returns the bit-wise AND of values integ1 and "
     "integ2.\n\n"
     "intout = bitand(integ1,integ2)\n"
     "intout = bitand(integ1,integ2,assumedtype)\n"
     "objout = bitand(netobj1,netobj2)"),
    ("bitor", "bitor(${signal0}, ${signal1})",
     "bitor - Bit-wise OR\n\n"
     "This MATLAB function returns the bit-wise OR of integ1 and integ2.\n\n"
     "intout = bitor(integ1,integ2)\n"
     "intout = bitor(integ1,integ2,assumedtype)\n"
     "objout = bitor(netobj1,netobj2)"),
    ("bitxor", "bitxor(${signal0}, ${signal1})",
     "bitxor - Bit-wise XOR\n\n"
     "This MATLAB function returns the bit-wise XOR of integ1 and integ2.\n"
     "intout = bitxor(integ1,integ2)\n"
     "intout = bitxor(integ1,integ2,assumedtype)\n"
     "objout = bitxor(netobj1,netobj2)"),
    ("bitshift", "bitshift(${signal0})",
     "bitshift - Shift bits specified number of places\n\n"
     "This MATLAB function returns A shifted to the left by k bits, "
     "equivalent to\n"
     "multiplying by 2k.\n\n"
     "intout = bitshift(A,k)\n"
     "intout = bitshift(A,k,assumedtype)\n"
     "intout = bitshift(A,k,N)"),
    ("bitcmp", "bitcmp(${signal0})",
     "bitcmp - Bit-wise complement\n\n"
     "This MATLAB function returns the bit-wise complement of A.\n\n"
     "cmp = bitcmp(A)\n"
     "cmp = bitcmp(A,assumedtype)\n"
     "cmp = bitcmp(A,N)"),
]


OPERATORS = collections.OrderedDict([
    ("Arithmetics", ARITHMETICS_OPS),
    ("Comparators", COMPARATORS),
    ("Logics", LOGIC_OPS),
])


STATISTICS = [
    ("Sum", "sum(${signal0})",
     "sum - Sum of array elements \n\n"
     "This MATLAB function returns the sum of the elements of A along the "
     "first array \n dimension whose size does not equal 1: \n \n"
     "S = sum(A) \n"
     "S = sum(A,dim) \n"
     "S = sum(___,type)"),
    ("Min", "min(${signal0})",
     "min - Smallest elements in array \n\n"
     "This MATLAB function returns the smallest elements of A.If A is a "
     "vector, then \n min(A) returns the smallest element of A.If A is a "
     "matrix, then min(A) treats \n the columns of A as vectors and returns a"
     "row vector of smallest elements.If A \n is a multidimensional array, "
     "then min(A) treats the values along the first array \n"
     "dimension whose size does not equal 1 as vectors.\n \n"
     "M = min(A)\n"
     "M = min(A,[],dim) \n"
     "[M,I] = min(___) \n"
     "C = min(A,B)"),
    ("Max", "max(${signal0})",
     "max - Largest elements in array \n\n"
     "This MATLAB function returns the largest elements of A.If A is a vector,"
     " then \n max(A) returns the largest element of A.If A is a matrix, "
     "then max(A) treats the \n"
     "columns of A as vectors and returns a row vector of largest elements."
     "If A is a \n multidimensional array, then max(A) treats the values "
     "along the first array \n"
     "dimension whose size does not equal 1 as vectors and returns an array "
     "of maximum \n"
     "values. \n \n"
     "M = max(A) \n"
     "M = max(A,[],dim) \n"
     "[M,I] = max(___) \n"
     "C = max(A,B)"),
    ("Mean", "mean(${signal0})",
     "mean - Average or mean value of array \n\n"
     "This MATLAB function returns the mean value along the first array "
     "dimension of A \n whose size does not equal 1. \n \n"
     "M = mean(A) \n"
     "M = mean(A,dim) \n"
     "M = mean(___,type)"),
    ("Standard deviation", "std(${signal0})",
     "std - Standard deviation \n\n"
     "This MATLAB function, where X is a vector, returns the standard "
     "deviation using \n (1) above. \n \n"
     "s = std(X) \n"
     "s = std(X,flag) \n"
     "s = std(X,flag,dim"),
    ("Median", "median(${signal0})",
     "median - Median value of array \n\n"
     "This MATLAB function returns the median value of A.If A is a vector, "
     "then \n median(A) returns the median value of A.If A is a nonempty "
     "matrix, then \n median(A) treats the columns of A as vectors and "
     "returns a row vector of median \n "
     "values.If A is an empty 0-by-0 matrix, median(A) returns NaN."
     "If A is a \n multidimensional array, then median(A) treats the values "
     "along the first array \n dimension whose size does not equal 1 as "
     "vectors and returns an array of median \n values. \n \n"
     "M = median(A) \n"
     "M = median(A,dim)"),
]


GUI_DICT = collections.OrderedDict([
    ("Operators", OPERATORS),
    ("Statistics", STATISTICS),
])
