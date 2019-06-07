from rigidbody import (Matrix, Vector, approx, approx_jacobian)


def test_approx_jacobian_identity():

    def f(x):
        return x

    x = Vector(0, 0, 0)

    assert(approx(approx_jacobian(f, x), Matrix.identity(3)))


def test_approx_jacobian_permutation():

    def f(x):
        return Vector(x[0], x[2], x[1])

    x = Vector(0, 0, 0)
    J = Matrix(3, 3)

    J[0, 0] = 1
    J[2, 1] = 1
    J[1, 2] = 1

    assert(approx(approx_jacobian(f, x), J))


def test_approx_jacobian_lorenz():

    def f(x):

        vx = x[1] - x[0]
        vy = x[0] * (1 - x[2]) - x[1]
        vz = x[0] * x[1] - x[2]

        return Vector(vx, vy, vz)

    x = Vector(1, 2, 3)
    J = Matrix(3, 3)

    J[0, :] = [-1, 1 - x[2], x[1]]
    J[1, :] = [1, -1, x[0]]
    J[2, :] = [0, -x[0], -1]

    assert(approx(approx_jacobian(f, x), J))
