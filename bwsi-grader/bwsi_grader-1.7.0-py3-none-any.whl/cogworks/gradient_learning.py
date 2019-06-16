from typing import *
import numpy as np
from numbers import Real


__seed__ = ["polygrad", "gradientdescent", "lossandgradient"]


def grade_polygrad(student_func: Callable[[Tuple[float, ...], float], float]):
    from bwsi_grader.print import print_passed
    from bwsi_grader import compare_functions
    from hashlib import sha224


    def soln(coeffs, x):
        assert all(isinstance(c, Real) for c in coeffs)
        assert isinstance(x, Real)
        coeffs = coeffs[1:]
        return float(sum(coef * ex * (x ** (ex - 1))
                         for coef, ex in zip(coeffs,
                                             range(1, len(coeffs) + 1))))

    # check some standard cases
    for coeffs, x in zip(((), (1.,), (0, 2., 3.5)), (0., 12.4, 5.2)):
        compare_functions(student=student_func, soln=soln, fn_args=(coeffs, x))

    # check random cases

    for i in range(1000):
        num_coeffs = np.random.randint(0, 10)
        coeffs = tuple(float(i) for i in np.round(np.random.rand(num_coeffs)*10, 2))
        x = np.round(np.random.rand(1)*100, 2).item()
        compare_functions(student=student_func, soln=soln, fn_args=(coeffs, x))

    print_passed(sha224(str.encode(__seed__[0])).hexdigest())


def grade_gradient_descent(student_func: Callable[[List[float], float, int, float], List[float]]):

    from bwsi_grader import compare_functions
    from bwsi_grader.print import print_passed
    from hashlib import sha224

    def soln(poly, step_size=0.1, iterations=10, x=100.):
        """ Returns a list of x-values visited when optimizing `poly` through gradient descent

            Parameters
            ----------
            poly : List[float]
                Polynomial coefficients in increasing order
            step_size : Optional[float], default: 0.1
                The magnitude of the step to take for each update of x
            iterations : Optional[int], default: 10
                After this number of iterations, the grad_descent function should return
            x : Optional[float], default: 100.
                The initial value of x

            Returns
            -------
            x_list : List[float]
                A list of the values of x that were visited, including
                the initial value of x.
        """
        assert isinstance(x, Real)
        assert isinstance(iterations, int)
        assert isinstance(step_size, Real)

        def poly_grad(coeffs, x):
            assert all(isinstance(c, Real) for c in coeffs)
            assert isinstance(x, Real)
            coeffs = coeffs[1:]
            return float(sum(coef * ex * (x ** (ex - 1))
                             for coef, ex in zip(coeffs,
                                                 range(1, len(coeffs) + 1))))
        x_list = [x]
        for _ in range(iterations):
            x -= step_size * poly_grad(poly, x)
            x_list.append(x)
        return x_list

    # test static case
    x = 2.
    coeffs = [1., 2., -4.]
    iterations = 3
    step_size = 0.1

    compare_functions(student=student_func, soln=soln,
                      fn_args=(coeffs,),
                      fn_kwargs=dict(step_size=step_size,
                                     iterations=iterations,
                                     x=x))

    for i in range(1000):
        num_coeffs = np.random.randint(0, 4)
        poly = [float(i) for i in np.random.randint(0, 10, size=(num_coeffs,))]
        x = float((np.random.rand() - 0.5))
        step_size = float(np.random.rand() * 0.01)
        iterations = int(np.random.randint(5, 15))
        _soln = soln(poly, step_size=step_size, iterations=iterations, x=x)

        if not np.isfinite(_soln).all():
            continue # Only test happy paths
        else:
            compare_functions(student=student_func, soln=soln,
                              fn_args=(poly,), fn_kwargs=dict(step_size=step_size,
                                                              iterations=iterations,
                                                              x=x))

    print_passed(sha224(str.encode(__seed__[1])).hexdigest())


def grade_loss_and_gradient(student_func: Callable[[np.ndarray, np.ndarray, np.ndarray], Tuple[float, np.ndarray]]):
    from bwsi_grader import compare_functions
    from bwsi_grader.print import print_passed
    from hashlib import sha224

    def soln(X, A, y):
        """ Given the input data (X), the collection of model parameters (A), and the
            truth data (y). Compute the loss, and the gradient of the loss (evaluated at A).

            Parameters
            ----------
            X : numpy.ndarray (shape = (N, 4))
                The data for all movies, with the first column of the array
                always equal to 1
            A : np.ndarray (shape = (4,))
                The model parameters: A_bias, A_prod, A_prom, A_book
            y : np.ndarray (shape = (N,))
                The true box office sales for each movie

            Returns
            -------
            out : tuple
                The first entry is the calculated loss and the second entry is the gradient
                evaluated at A.

                The loss should be a single floating-point number
                The gradient should be a numpy array of shape-(4,)

            Fun challenge (optional): For both the loss and the gradient try using matrix
            multiplication and broadcasting to avoid using any for-loops.
        """
        import numpy as np

        assert X.ndim == 2
        assert A.ndim == 1
        assert y.ndim == 1

        N = X.shape[0]
        assert X.shape == (N, 4)
        assert A.shape == (4,)
        assert y.shape == (N,)

        assert np.all(X[:, 0] == 1.)

        y_hat = X.dot(A)
        loss = np.mean((y - y_hat) ** 2)
        grad = -2 * np.mean((y - y_hat) * X.T, axis=1)
        return loss, grad

    X = np.array([[1., 2., 0.1, 8.],
                  [1., 5., 2., 6.]])

    A = np.array([.5, 1., 2., 0.])

    y = np.array((20., 30.))

    compare_functions(student=student_func, soln=soln,
                      fn_args=(X, A, y))

    for _ in range(50):
        p = np.random.randint(1, 10)
        X, A, y = np.random.rand(p, 4).round(2), np.random.rand(4).round(2), np.random.rand(p).round(2)
        X[:, 0] = 1.

        compare_functions(student=student_func, soln=soln,
                          fn_args=(X, A, y))
    print_passed(sha224(str.encode(__seed__[2])).hexdigest())
