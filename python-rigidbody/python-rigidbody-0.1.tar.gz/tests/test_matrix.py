from rigidbody import (Matrix, svd, approx)

def test_matrix_equality():

    A = Matrix(3, 3)
    B = Matrix(3, 3)

    assert(A == B)

    A = Matrix.identity(3, 3)
    B = Matrix.identity(3, 3)

    assert(A == B)

    A = Matrix.zero(3, 3)
    B = Matrix.zero(3, 3)

    assert(A == B)


def test_matrix_identities():

    A = Matrix.identity(3, 3)
    A[0, 1] = 1

    assert(A + Matrix.zero(3, 3) == A)
    assert(Matrix.zero(3, 3) + A == A)

    assert(A * Matrix.identity(3, 3) == A)
    assert(Matrix.identity(3, 3) * A == A)


def test_matrix_addition():

    A = Matrix(3, 3)
    B = Matrix(3, 3)
    C = Matrix(3, 3)

    A[0, 1] = 1
    B[1, 0] = 2

    C[0, 1] = 1
    C[1, 0] = 2

    assert(A + B == C)
    assert(B + A == C)


def test_matrix_subtraction():

    A = Matrix(3, 3)
    B = Matrix(3, 3)
    C = Matrix(3, 3)

    A[0, 1] = 1
    B[1, 0] = 2

    C[0, 1] = 1
    C[1, 0] = 2

    assert(C - A == B)
    assert(C - B == A)


def test_matrix_multiplication():

    A = Matrix(3, 3)
    B = Matrix(3, 3)
    AB = Matrix(3, 3)
    BA = Matrix(3, 3)

    A[0, :] = [1, 0, 0]
    A[1, :] = [0, 0, 1]
    A[2, :] = [0, 1, 0]

    B[0, :] = [1, 2, 3]
    B[1, :] = [4, 5, 6]
    B[2, :] = [7, 8 ,9]

    AB[0, :] = [1, 2, 3]
    AB[1, :] = [7, 8 ,9]
    AB[2, :] = [4, 5, 6]

    assert(A * B == AB)

    BA[0, :] = [1, 3, 2]
    BA[1, :] = [4, 6, 5]
    BA[2, :] = [7 ,9, 8]

    assert(B * A == BA)


def test_matrix_approx():

    A = Matrix(3, 3)
    B = Matrix(3, 3)

    A[0, :] = B[0, :] = [1, 2, 3]
    A[1, :] = B[1, :] = [4, 5, 6]
    A[2, :] = B[2, :] = [7, 8 ,9]


    assert(approx(A, B, tol=0.001))

    A[0, 0] += 0.002

    assert(not approx(A, B, tol=0.001))


def test_matrix_svd():

    A = Matrix(3, 3)

    A[0, :] = [1, 2, 3]
    A[1, :] = [4, 5, 6]
    A[2, :] = [7, 8 ,9]

    U, S, V = svd(A)

    assert(approx(U * S * V.transposed(), A))
