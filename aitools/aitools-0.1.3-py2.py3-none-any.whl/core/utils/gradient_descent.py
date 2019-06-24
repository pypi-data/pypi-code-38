"""
    Gradient descent is an optimization algorithm used to minimize some function by iteratively moving in the
    direction of steepest descent as defined by the negative of the gradient. In machine learning, we use gradient
    descent to update the parameters** of our model.

    **Parameters refer to coefficients in Regression and weights in neural networks.
"""


def step(v, direction, step_size):
    """
        move step_size in the direction from v
    :param v: the theta(regression beta values) vector
    :param direction: where the step has to be taken
    :param step_size: size of the step to be taken
    :return: vector of thetas
    """
    return [v_i + step_size * direction_i for v_i, direction_i in zip(v, direction)]


def negate(f):
    """
        return a function that for any input x returns -f(x)
    :param f: f(x)
    :return: -f(x)
    """
    return lambda *args, **kwargs: -f(*args, **kwargs)


def negate_all(f):
    """
        the same when f returns a list of numbers
    :param f: f(x)
    :return: -f(x)
    """
    return lambda *args, **kwargs: [-y for y in f(*args, **kwargs)]


def safe(f):
    """
        A function to except a function and does the same work until
        error occurs
    :param f: f(x)
    :return:  a new function that's the same as f, except that
            it outputs infinity whenever f produces an error
    """

    def safe_f(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            return float('inf')  # this means "infinity" in Python

    return safe_f


def maximize_batch(target_fn, gradient_fn, theta_0, tolerance=0.000001):
    """
        Use to get the most likely coefficients by using gradient decent.
    :param target_fn: the base function which takes the coefficients and
                    returns log likelihood (sum of log of logistic function)
    :param gradient_fn: the gradient function which takes the coefficients and
                    returns the vector og log likelihood
    :param theta_0: coefficients.
    :param tolerance: till when the function should be minimized(an alternate to iterations).
    :return: minimized coefficient of target function.
    """
    return minimize_batch(
        negate(target_fn),
        negate_all(gradient_fn),
        theta_0,
        tolerance
    )


def minimize_batch(target_fn, gradient_fn, theta_0, tolerance=0.000001):
    """
        Use to get the most likely coefficients by using gradient decent.
    :param target_fn: the base function which takes the coefficients and
                    returns log likelihood (sum of log of logistic function)
    :param gradient_fn: the gradient function which takes the coefficients and
                    returns the vector og log likelihood
    :param theta_0: coefficients.
    :param tolerance: till when the function should be minimized(an alternate to iterations).
    :return: minimized coefficient of target function.
    """

    step_sizes = [100, 10, 1, 0.1, 0.01, 0.001, 0.0001, 0.00001]

    theta = theta_0  # set theta to initial value
    target_fn = safe(target_fn)  # safe version of target_fn
    value = target_fn(theta)  # value we're minimizing

    while True:
        gradient = gradient_fn(theta)

        next_thetas = [step(theta, gradient, -step_size) for step_size in step_sizes]

        # choose the one that minimizes the error function
        next_theta = min(next_thetas, key=target_fn)
        next_value = target_fn(list(next_theta))

        # stop if we're "converging"
        if abs(value - next_value) < tolerance:
            return theta
        else:
            theta, value = next_theta, next_value
