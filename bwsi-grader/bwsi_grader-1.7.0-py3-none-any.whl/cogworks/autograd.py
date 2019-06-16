from numbers import Real
from bwsi_grader.errors import StudentError, DeveloperError

__all__ = ["grade_op", "grade_arithmetic", "grade_backprop", "grade_op_backprop"]
__seed__ = ["op", "arithmetic", "backprop", "opbackprop"]


def _rand_in_range(left, right):
    """Returns random number in [left, right] rounded to
    one decimal."""
    from random import random
    if right <= left:
        raise ValueError("`_rand_in_range` received invalid bounds")
    return round(random() * (right - left) + left, 1)


def try_init(obj, val, creator=None):

    try:
        o = obj(val, creator=creator)
    except Exception as e:
        raise StudentError(f"Calling"
                           f"\n\t`Number({val}, creator={creator})`"
                           f"\nraised the following error:"
                           f"\n"
                           + str(e))
    return o


def grade_op(*, student_Number, student_Add, student_Multiply):
    from bwsi_grader.print import print_passed
    from hashlib import sha224

    def check_type(inst, sig):
        if not isinstance(inst, student_Number):
            raise StudentError(
                 f"Calling `{sig}` should return an instance of:"
                 f"\n\t{student_Number}\n"
                 f"Instead, returned type:"
                 f"\n\t{type(z)}")

    def check_creator(inst, type_, sig):
        if not hasattr(inst, "creator"):
            raise StudentError(f"The result of {sig} does not have a creator "
                               f"attribute defined. Every instance of Number should "
                               f"have this attribute."
                               f"\nThe attribute should return "
                               f"`None` in the case that the instance was created by a user and "
                               f"not an operations")
        if isinstance(inst.creator, type):
            raise StudentError(f"The creator of `{sig}` is expected to be an *instance* of:"
                               f"\n\t{type_}\n"
                               f"Instead, found that it is of type:"
                               f"\n\t{type(inst.creator)}"
                               f"\n\n"
                               f"You most likely set the creator to be the operation *class object*. "
                               f"Instead it should be set to the operation *instance* that was used.")
        if not isinstance(inst.creator, type_):
            raise StudentError(f"The creator of `{sig}` is expected to be an instance of:\n\t{type_}\n"
                               f"Instead, found that it is of type:\n\t{type(inst.creator)}")
        if not isinstance(inst, student_Number):
            raise StudentError(
                 f"Calling {sig} should return an instance of {student_Number}, "
                 f"instead returned type: {type(z)}")

    for op, symbol in [(student_Add, "+"), (student_Multiply, "*")]:
        for i in range(20):
            x_ = _rand_in_range(-5, 5)
            y_ = _rand_in_range(-5, 5)

            x = try_init(student_Number, x_)
            y = try_init(student_Number, y_)

            try:
                z = student_Number._op(op, x, y)
            except Exception as e:
                raise StudentError(f"Calling"
                                   f"\n\t{student_Number.__name__}._op({op.__name__}, {x}, {y})"
                                   f"\nproduced the following error:\n\t"
                                   + str(e))

            sig = f"Number({x.data}) {symbol} Number({y.data})"
            check_type(z, sig=sig)
            check_creator(z, op, sig=sig)
            for input_, correct in [(z.creator.a, x), (z.creator.b, y)]:
                if input_ is not correct:
                    raise StudentError(f"Calling"
                                       f"\n\t{student_Number.__name__}._op({op.__name__}, {x}, {y})"
                                       f"\ninappropriately creates a new copy of {correct}.\n"
                                       f"Be sure that you only cast the non-`Number` inputs of `Number._op` as `Number`"
                                       f" instances.")

    for order in ["left", "right"]:
        for op, symbol in [(student_Add, "+"), (student_Multiply, "*")]:
            for i in range(20):
                x_ = _rand_in_range(-5, 5)
                y_ = _rand_in_range(-5, 5)

                if order == "left":
                    x = try_init(student_Number, x_)
                    y = y_
                else:
                    x = x_
                    y = try_init(student_Number, y_)

                try:
                    z = student_Number._op(op, x, y)
                except Exception as e:
                    raise StudentError(f"Calling"
                                       f"\n\t{student_Number.__name__}._op({op.__name__}, {x}, {y})"
                                       f"\n"
                                       f"produced the following error:\n\t"
                                       + str(e))

                sig = f"Number({x_}) {symbol} Number({y_})"
                check_type(z, sig=sig)
                check_creator(z, op, sig=sig)

    print_passed(sha224(str.encode(__seed__[0])).hexdigest())


def grade_arithmetic(*,
                     student_Number,
                     student_Subtract,
                     student_Divide,
                     student_Power):
    import operator as op
    from bwsi_grader.print import print_passed
    from hashlib import sha224

    from bwsi_grader.compare import mismatch_error
    for obj, symb, f, bounds in [(student_Subtract, "-", op.sub, [(-10, 10), (-10, 10)]),
                                 (student_Divide, "/", op.truediv, [(-10, 10), (1, 10)]),
                                 (student_Power, "**", op.pow, [(1, 10), (-10, 10)])]:
        x_bnds, y_bnds = bounds
        for i in range(20):
            x_ = _rand_in_range(*x_bnds)
            y_ = _rand_in_range(*y_bnds)

            x = try_init(student_Number, x_)
            y = try_init(student_Number, y_)

            try:
                correct = f(x_, y_)
            except Exception:
                raise DeveloperError("Invalid operation: {f}({x}, {y})")

            try:
                inst = obj()
                out = inst.__call__(x, y)
            except Exception as e:
                raise StudentError(
                    f"Calling"
                    f"\n\t{obj.__name__}().__call__({x}, {y})"
                    f"\nraised the following error:"
                    f"\n\t{e}")

            mismatch = mismatch_error(actual=out, desired=correct)
            if mismatch:
                raise StudentError(f"Calling"
                                   f"\n\t{obj.__name__}().__call__({x}, {y})\n"
                                   f"produced the wrong result. {mismatch}")

            for correct, attr_name in [(x, "a"), (y, "b")]:
                if not hasattr(inst, attr_name):
                    raise StudentError(f"Calling"
                                       f"\n\top = {obj.__name__}()"
                                       f"\n\top.__call__({x}, {y})\n" 
                                       f"failed to bind {correct} to `op.{attr_name}`")
                attr = getattr(inst, attr_name)
                if not isinstance(attr, student_Number):
                    raise StudentError(f"Calling"
                                       f"\n\top = {obj.__name__}()"
                                       f"\n\top.__call__({x}, {y})\n" 
                                       f"set `{attr}` to `op.{attr_name}`. Instead, it should have "
                                       f"set `{correct}` (type: Number).")
                if attr is not correct:
                    raise StudentError(f"Calling"
                                       f"\n\top = {obj.__name__}()"
                                       f"\n\top.__call__({x}, {y})\n" 
                                       f"\ninappropriately creates a new copy of {correct}.\n"
                                       f"op.{attr_name} should return the same instance of {correct}")
    print_passed(sha224(str.encode(__seed__[1])).hexdigest())


def grade_backprop(*, student_Number, student_Add, student_Multiply):
    from bwsi_grader.print import print_passed
    from hashlib import sha224

    def _run(gen): return [i for i in gen]

    def grad_check(inst, expected, seq_steps, name):
        if (inst.grad is not None and not isinstance(inst.grad, (int, float))) or \
           (inst.grad != expected) if expected is not None else (inst.grad is not expected):
            seq_steps = "\n\t".join(seq_steps)
            raise StudentError(
                f"After calling:"
                f"\n\t{seq_steps}"
                f"\n`{name}.grad` should return:"
                f"\n\t{expected}"
                f"\nInstead, it returned:"
                f"\n\t{inst.grad}")

    def mutation_check(inst, expected, seq_steps, name):
        if inst.data != expected:
            seq_steps = "\n\t".join(seq_steps)
            raise StudentError(
                f"Calling:"
                f"\n\t{seq_steps}"
                f"\nmutated the value stored in `{name}`."
                f"\n`{name}` stored {expected}; now it stores {inst.data}")

    def call_check(func, inst, seq_steps):
        try:
            return func(inst)
        except Exception as e:
            seq_steps = "\n\t".join(seq_steps)
            raise StudentError(
                f"Calling:"
                f"\n\t{seq_steps}"
                f"\nraised the following error:"
                f"\n\t{e}")

    def value_check(inst, expected, seq_steps, name):
        from math import isclose
        if not isclose(inst.data, expected, abs_tol=1e-5, rel_tol=1e-5):
            seq_steps = "\n\t".join(seq_steps)
            raise StudentError(
                f"After calling:"
                f"\n\t{seq_steps}"
                f"\n`{name}` should return:"
                f"\n\tNumber({expected})"
                f"\nInstead, it returned:"
                f"\n\tNumber({inst.data})")
    from random import choice

    """
    Checks:
    x = Number(_x)
    x.backprop(g)
    x.grad == g
    """
    for i in range(100):
        _x = _rand_in_range(-10, 10) if i > 0 else 2.
        grad = choice([_rand_in_range(-10, 10), None]) if i > 0 else None
        _g = grad if grad is not None else 1.

        x = try_init(student_Number, _x)
        seq_steps = [f"x = Number({_x})"]
        grad_check(x, expected=None, seq_steps=seq_steps, name="x")

        seq_steps.append(f"x.backprop({grad})" if grad is not None else f"x.backprop()")
        call_check(lambda inst: inst.backprop(_g), inst=x, seq_steps=seq_steps)
        mutation_check(x, expected=_x, seq_steps=seq_steps, name="x")
        grad_check(x, expected=_g, seq_steps=seq_steps, name="x")

        seq_steps.append("x.null_gradients()")
        call_check(lambda inst: inst.null_gradients(), inst=x, seq_steps=seq_steps)
        mutation_check(x, expected=_x, seq_steps=seq_steps, name="x")
        grad_check(x, expected=None, seq_steps=seq_steps, name="x")

    """
    Checks:
    y = Number(_y)
    x = 2 + y
    out = x * x
    out.backprop(g)
    
    out.grad == g
    x.grad == 2*g*x
    y.grad = x.grad
    """
    for i in range(100):
        _y = _rand_in_range(-10, 10) if i > 0 else 3.
        grad = choice([_rand_in_range(-10, 10), None]) if i > 0 else None
        _g = grad if grad is not None else 1.

        y = try_init(student_Number, _y)
        _x = 2 + _y

        _g = grad if grad is not None else 1.

        seq_steps = [f"y = Number({_y})"]
        grad_check(x, expected=None, seq_steps=seq_steps, name="x")
        grad_check(y, expected=None, seq_steps=seq_steps, name="y")

        seq_steps.append(f"x = 2 + y")
        x = call_check(lambda inst: student_Number._op(student_Add, 2, inst), inst=y, seq_steps=seq_steps)
        value_check(x, expected=_x, seq_steps=seq_steps, name="x")

        seq_steps.append(f"out = x * x")
        _out = _x * _x
        out = call_check(lambda inst: student_Number._op(student_Multiply, inst, inst), inst=x, seq_steps=seq_steps)

        vars_ = [y, x, out]
        vals = [_y, _x, _out]
        names = ["y", "x", "out"]

        _run(mutation_check(var, expected=val, seq_steps=seq_steps, name=name)
             for var, val, name in zip(vars_, vals, names))

        value_check(out, expected=_out, seq_steps=seq_steps, name="out")

        seq_steps.append(f"out.backprop({grad})" if grad is not None else f"out.backprop()")
        call_check(func=lambda inst: inst.backprop(_g), inst=out, seq_steps=seq_steps)
        _run(mutation_check(var, expected=val, seq_steps=seq_steps, name=name)
             for var, val, name in zip(vars_, vals, names))

        grad_check(out, expected=_g, seq_steps=seq_steps, name="out")
        grad_check(x, expected=2*_x*out.grad, seq_steps=seq_steps, name="x")
        grad_check(y, expected=x.grad, seq_steps=seq_steps, name="y")

        seq_steps.append("out.null_gradients()")
        call_check(lambda inst: inst.null_gradients(), inst=out, seq_steps=seq_steps)

        _run(mutation_check(var, expected=val, seq_steps=seq_steps, name=name)
             for var, val, name in zip(vars_, vals, names))

        _run(grad_check(var, expected=None, seq_steps=seq_steps, name=name)
             for var, val, name in zip(vars_, vals, names))

    print_passed(sha224(str.encode(__seed__[2])).hexdigest())


def grade_op_backprop(*, student_Number, student_Subtract, student_Divide, student_Power):
    from bwsi_grader.print import print_passed
    from hashlib import sha224

    import numpy as np
    from math import isclose

    def sub_a(a, b): return 1.

    def sub_b(a, b): return -1.

    def div_a(a, b): return 1. / b

    def div_b(a, b): return -1 * a / (b ** 2)
    
    def pow_a(a, b): return b * (a ** (b - 1))

    def pow_b(a, b): return (a ** b) * np.log(a)

    all_ops = [student_Subtract, student_Divide, student_Power]
    partials = [(sub_a, sub_b), (div_a, div_b), (pow_a, pow_b)]
    bounds = [((-10, 10), (-10, 10)),
              ((-3, 3), (1, 3)),
              ((1, 3), (-2, 2))]
    for Op, partial, (a_bnds, b_bnds) in zip(all_ops, partials, bounds):
        for i in range(100):
            x = student_Number(_rand_in_range(*a_bnds) if i > 0 else 1.)
            y = student_Number(_rand_in_range(*b_bnds) if i > 0 else 3.)

            op = Op()
            op(x, y)
            for n, letter in enumerate(["a", "b"]):
                try:
                    actual = op.partial_a() if n == 0 else op.partial_b()
                except Exception as e:
                    raise StudentError(
                        f"After calling:"
                        f"\n\t>>> f = {Op.__name__}()"
                        f"\n\t>>> f({x}, {y})"
                        f"\n Calling:"
                        f"\n`{'f.partial_a()' if n == 0 else 'f.partial_b()'}` raised the error:"
                        f"\n\t{type(e).__name__}: {e}")
                try:
                    expected = partial[n](x.data, y.data)
                except Exception as e:
                    raise DeveloperError(
                        f"After calling:"
                        f"\n\t>>> f = {Op.__name__}()"
                        f"\n\t>>> f({x}, {y})"
                        f"\n Calling:"
                        f"\n`{'f.partial_a()' if n == 0 else 'f.partial_b()'}` raised the error:"
                        f"\n\t{type(e).__name__}: {e}"
                        f"\nThis is an error with the grader, please contact an instructor")

                if not isinstance(actual, Real):
                    raise StudentError(
                        f"After calling:"
                        f"\n\t>>> f = {Op.__name__}()"
                        f"\n\t>>> f({x}, {y})"
                        f"\n`{'f.partial_a()' if n == 0 else 'f.partial_b()'}` should have returned "
                        f"the floating point number:"
                        f"\n\t{expected}"
                        f"\nInstead, it returned an object of type {type(actual)}:"
                        f"\n\t{actual}")

                if not isclose(actual, expected, rel_tol=1e-5, abs_tol=1e-5):
                    raise StudentError(
                        f"After calling:"
                        f"\n\t>>> f = {Op.__name__}()"
                        f"\n\t>>> f({x}, {y})"
                        f"\n`{'f.partial_a()' if n == 0 else 'f.partial_b()'}` should have returned:"
                        f"\n\t{expected}"
                        f"\nInstead, it returned:"
                        f"\n\t{actual}")
    print_passed(sha224(str.encode(__seed__[3])).hexdigest())
