from scipy import optimize


def principal_component(amount, rate, years, periods):
    """
    Calculates the principal compouding component of a financial application.

    Parameters
    ----------
    amount : float
        The principal component amount, i.e., the initial investment.
    rate : float
        The annualized compouding interest rate.
    years : int
        The number of years of the application.
    periods : int
        The number of compounding periods per years.

    Returns
    -------
    out : float
        The value of the principal components after the given years.
    """
    return amount * (1 + (rate / periods))**(years * periods)

def end_period_contribution_component(amount, rate, years, periods):
    """
    Calculates the periodic contribution component of a financial application.

    The contribution is made at the end of each compouding period.

    Parameters
    ----------
    amount : float
        The contribution component amount, to be considered at the end of each compounding period.
    rate : float
        The annualized compouding interest rate.
    years : int
        The number of years of the application.
    periods : int
        The number of compounding periods per years.

    Returns
    -------
    out : float
        The value of the contribution components after the given years.
    """
    return amount * ((1 + (rate / periods))**(years * periods) - 1) / (rate / periods)

def _rate_solver_func(x, valorization, principal_amount, end_period_contribution_amount, years, periods):
    """
    Defines the function which is to be used by the solver.

    Parameters
    ----------
    x : float
        The the interest rate value.
    valorization : float
        The aplication final valorization.
    principal_amount : float
        The principal component amount, i.e., the initial investment.
    end_period_contribution_amount : float
        The contributio component amount, to be considered at the end of each compouding period.
    years : int
        The number of years of the application.
    periods : int
        The number of compounding periods per years.

    Returns
    -------
    out : float
        The difference between the input valorization and the valorization achieved by the given interest rate value.
    """
    return principal_component(principal_amount, x, years, periods) + end_period_contribution_component(end_period_contribution_amount, x, years, periods) - valorization

def rate(initial_value, valorization, principal_amount, contribution_amount, years, periods):
    """
    Return the annual interest rate of a finacial application with periodic contributions.

    Parameters
    ----------
    initial_value : float
        The solver initial point.
    valorization : float
        The expected valorization of the application.
    principal_amount : float
        The principal amount.
    contribution_amount :float
        The periodic contribution amount, to be considered at the end of each compounding period.
    years : int
        The number of years of the application.
    periods : int
        The number of compounding periods per years.

    Returns
    -------
    out : float
        The interest rate or None if the solver failed to converge.
    
    """

    rate_value = None
    try:
        rate_value = optimize.newton(_rate_solver_func,
                                     initial_value,
                                     args=(valorization,
                                           principal_amount,
                                           contribution_amount,
                                           years,
                                           periods,))
    except:
        pass
    return rate_value

