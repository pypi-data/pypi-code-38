"""
Created on Tue May 21 2018

@author: a.teffal

"""

import pandas as pd
from . import Effectifs as eff
import inspect
import matplotlib.pyplot as plt
import numpy as np


def project_salaries(employees_proj_, salaries, MAX_YEARS, salaries_new_emp=None, sal_evol=0):
    """
        Returns a DataFrame containing annual projection of the salaries.
  
        Parameters: 
            employees_proj_ (dic): a dic containing projected employees in the form of those 
                                   returned by simulerEffectif.
                                   
            salaries (DataFrame) : A DataFrame containing for each employee (including new employees if 
                                   salaries_new_emp is None ) his salary at year 0 (at year of entrance 
                                   if it's a new employee).

            MAX_YEARS (int): Number of years of projection.

        Optional parameters:
            salaries_new_emp (function) : A function accepting as parameter a DataFrame containing all 
                                          columns data for new employees plus a column 'entrance' (the year this new 
                                          employee entered  the population) and returning a DataFrame containing 
                                          projected salaries for each new employee.

        sal_evol (numeric) : annual increase of the salaire. Salary at year i+1 = (Salary at year i)*(1+sal_evol)
        
        Returns: 
            DataFrame: A DataFrame containing projected salaries for each employee
    """

    # Getting new employees
    df_new = eff.new_employees(employees_proj_, MAX_YEARS)

    # if salaries_new_emp is not None, get salaries of new employees and add them to salaries
    if not salaries_new_emp is None:
        if not df_new is None:
            salaries_new_emp_df = salaries_new_emp(df_new)
            salaries = pd.concat([salaries, salaries_new_emp_df])

    # Getting individual projected lives and types for employees
    indiv_numbers = eff.individual_employees_numbers(employees_proj_)
    lives = indiv_numbers[0]
    type_ = indiv_numbers[3]
    # lives = eff.individual_employees_numbers(employees_proj_)[0]
    # type_ = eff.individual_employees_numbers(employees_proj_)[3]

    # Join lives and salaries
    # df_temp = lives.join(salaries.set_index('id'), on='id', how='inner', lsuffix='_lives', rsuffix='_salaries')
    df_temp = lives.merge(salaries, on='id', how='inner')

    df_temp.to_csv('./results/df_temp_avant.csv', sep=';', index=False, decimal=',')

    # Get years columns
    years_columns = [c for c in df_temp.columns if c.startswith('year_')]

    type_ = type_.set_index('id')

    # Get the number of rows
    n = len(df_temp)

    # Project salary
    for i in range(n):
        # id 
        id_ = df_temp.loc[i, 'id']

        # year_entrance
        year_entrance = int(employees_proj_[id_]['entrance'])
        for c in years_columns:
            # year
            y = int(c[5:])
            # salaries are not zero for actives only
            if type_.loc[id_, c] == 'active':
                df_temp.loc[i, c] = df_temp.loc[i, c] * df_temp.loc[i, 'salary'] * ((1 + sal_evol) ** (y-year_entrance))
            else:
                df_temp.loc[i, c] = 0

    df_temp.to_csv('./results/df_temp_apres.csv', sep=';', index=False, decimal=',')

    return df_temp[df_temp.columns[:-1]]


def project_contributions(projected_salaries, contribution_rate, MAX_YEARS):
    """
            Returns a DataFrame containing annual projection of the contributions.

            Parameters:
                projected_salaries (DataFrame): a DataFrame containing projected salaries.

                contribution_rate (Number, DataFrame or Function) : Number, DataFrame or Function giving the rate of contribution.
                If it's a DataFrame, then it's an annual rate of contribution and therefore the DataFrame has two columns :
                year and rate.
                If it's a function, then the names of its parameters must exist in data columns of projected_salaries and return a rate
                of contribution. It can alse have year as last parameter which represent the year of projection. 

                MAX_YEARS (int): Number of years of projection.

    """

    # copy the Dataframe so we have the same structure
    df_contributions = projected_salaries.copy()

    # Set id as index in projected_salaries
    projected_salaries = projected_salaries.set_index('id')

    # Get the number of rows
    n = len(df_contributions)

    # Get years columns
    years_columns = [c for c in df_contributions.columns if c.startswith('year_')]

    # Project contributions
    for i in range(n):
        # id
        id_ = df_contributions.loc[i, 'id']

        for c in years_columns:
            # year
            y = int(c[5:])

            # Calculate contribution
            if isinstance(contribution_rate, (int, float)):
                df_contributions.loc[i, c] = projected_salaries.loc[id_, c] * contribution_rate
            elif isinstance(contribution_rate, pd.DataFrame):
                contribution_rate.set_index('year')
                df_contributions.loc[i, c] = projected_salaries.loc[id_, c] * contribution_rate.loc[y, 'rate']
            elif callable(contribution_rate):
                # Get parameters of the function contribution_rate
                params_ = inspect.getfullargspec(contribution_rate)[0]
                if 'year' in params_:
                    args_ = tuple([df_contributions.loc[i, z] for z in params_[:-1]]) + (y,)
                else:
                    args_ = tuple([df_contributions.loc[i, z] for z in params_])
                df_contributions.loc[i, c] = projected_salaries.loc[id_, c] * contribution_rate(*args_)
            else:
                df_contributions.loc[i, c] = 0

    return df_contributions


def project_pensions(employees_proj_, projected_salaries, pensions_retirees, pension_new_retiree, MAX_YEARS,
                     pen_evol=0):
    """ 
        Returns a DataFrame containing annual projection of the pensions.
  
        Parameters: 
            employees_proj_ (dic): a dic containing projected employees in the form of those 
                                   returned by simulerEffectif.

            projected_salaries(DataFrame) : A DataFrame containing projected salaries
                                   
            pensions_retirees (DataFrame) : A DataFrame containing the pension for current retirees.
                                            It must contains an id column and a pension column.

            pension_new_retiree (function) : A function returning a pension (number) and having parameters 
                                            names that exist in the data dic of employees_proj_, 
                                            a parameter named salaries,  a parameter named types_ 
                                            and a parameter named year( year of projection which we want the pension)

            MAX_YEARS (int): Number of years of projection.

        Optional parameters:
            pen_evol (numeric) : annual increase of the pension. Pension at year i+1 = (Pension at year i)*(1+pen_evol)
        
        Returns: 
            DataFrame: A DataFrame containing projected pensions for each employee
    """
    # Getting individual projected lives and types for employees
    indiv_numbers = eff.individual_employees_numbers(employees_proj_)
    lives = indiv_numbers[0]
    types_ = indiv_numbers[3]
    # lives = eff.individual_employees_numbers(employees_proj_)[0]
    # type_ = eff.individual_employees_numbers(employees_proj_)[3]

    # Join lives and pensions
    # df_temp = lives.join(pensions_retirees.set_index('id'), on='id', how='left', lsuffix='_lives', rsuffix='_pensions_retirees')
    df_temp = lives.merge(pensions_retirees, on='id', how='left')

    # Get years columns
    years_columns = [c for c in df_temp.columns if c.startswith('year_')]

    types_ = types_.set_index('id')

    projected_salaries = projected_salaries.set_index('id')

    # Get the number of rows
    n = len(df_temp)

    # Project pensions
    for i in range(n):

        # id 
        id_ = df_temp.loc[i, 'id']

        # actives
        if types_.loc[id_, 'year_0'] == 'active' or types_.loc[id_, 'year_0'] == '':  # for new employees type is empty at year 0
            # get data for that id from employees_proj_
            data_ = employees_proj_[id_]['data']
            salaries_ = list(projected_salaries.loc[id_, years_columns])
            types__ = list(types_.loc[id_, years_columns])
            # year_retirement = types_.index('retired')
            pension_ret = pension_new_retiree(data=data_, salaries=salaries_,
                                              types_=types__)

            # year of retirement
            if 'retired' in types__:
                year_ret = types__.index('retired')
                for c in years_columns:
                    # year
                    y = int(c[5:])
                    # pensions are payed starting from retirement only
                    if types_.loc[id_, c] == 'retired':
                        if y == year_ret:
                            # df_temp.loc[i, c] = df_temp.loc[i, c] * pension_ret
                            df_temp.loc[i, c] = pension_ret
                        else:
                            # df_temp.loc[i, c] = df_temp.loc[i, c] * pension_ret * ((1 + pen_evol) ** (y-year_ret))
                            df_temp.loc[i, c] = pension_ret * ((1 + pen_evol) ** (y-year_ret))
                        
                    else:
                        df_temp.loc[i, c] = 0
            else:
                for c in years_columns:
                    df_temp.loc[i, c] = 0

        else:  # retired
            for c in years_columns:
                # year
                y = int(c[5:])
                # for current retirees get pension from column pension
                df_temp.loc[i, c] = df_temp.loc[i, c] * df_temp.loc[i, 'pension'] * ((1 + pen_evol) ** y)

    return df_temp[df_temp.columns[:-1]]
