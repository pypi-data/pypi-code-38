
"""
Created on Mon May  7 14:08:56 2018

@author: a.teffal

"""

import pandas as pd
# from pop_projection import Actuariat as act
from . import Actuariat as act
from . import tools
import inspect
import matplotlib.pyplot as plt
import numpy as np
import random

def retire(age):
    if age >= 55:
        return True
    else:
        return False

def turnover(age) :
    """
    Return the probability of quitting during the following year at a given age

    """
    if age<30:
        return 0.02
    else:
        if age <45:
            return 0.01
        else:
            return 0

def turnover0(age) :
    """
    Return the probability of quitting during the following year at a given age

    """
    return 0


def probaMariage(age, typeAgent):
    """
    Return the probability of getting married  during the following year at a given age

    """
    if typeAgent=='active':
        if age >= 25 and age <= 54:
            return 0.095
        else :
            return 0
    else:
        return 0


def probaMariage0(age, typeAgent):
    """
    Return the probability of getting married  during the following year at a given age

    """
    return 0
    

def probaNaissance0(age):

    """
    Return the probability of having a new born  during the following year at a given age

    """

    return 0


def probaNaissance(age):
    """
    Return the probability of having a new born  during the following year at a given age

    """
    if age < 23:
        return 0
    if age > 40:
        return 0
    
    # temp = [0.2212, 0.08, 0.0978, 0.115, 0.1305, 0.1419, 0.148, 0.1497, 0.1434, 0.1353, 0.1239, 0.1095, 0.095, 0.08, 0.0653, 0.0516, 0.0408, 0.086]
    temp = [0, 0, 0, 0, 0, 0, 0, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0, 0, 0, 0, 0]
    
    return temp[age -23]
    

def verifyCols(data_, cols):
    '''
    verify that list of cols exist in data_

    '''
    temp = []
    cols_data = list(data_.columns)
    for c in cols:
        if c != 'year_proj':
            if not c in cols_data:
                temp.append(c)
    
    return temp

def simulerEffectif(employees, spouses, children, mortalityTable = 'TV 88-90', MAX_YEARS = 50, law_retirement_ = None, 
                    law_resignation_ = None, law_marriage_ = None, age_diff = 5, marriage_periode = ['active', 'retired'],
                    law_birth_ = None, birth_periode = ['active', 'retired'], law_replacement_ =  None):
    
    """ Main function that project population of a retirement plan (employees their spouses and their children) given laws of :
        mortality, retirement, resignation, marriage, birth and replacement.

    assumes employees, spouses and children are pandas dataframes with at least 6 columns :
        - id   : an unique identifier of the employee
        - type : active or retired for employees. active, or retired or widow or widower for spouses and children.
                 for spouses and children, type is the type of the employee that they are attached to 
                 if it's still alive, or widower otherwise.
        - sex  : male or female
        - familyStatus : married, or not married
        - age
        - group (optional) : a sub-population. ex : group of employees recruted before 2002, group of directors,...

    Parameters
    ----------
    employees : pandas dataframe
                dataframe of employees having at least columns: id, type, sexe, familyStatus, age and group (optional).
    spouses   : pandas dataframe
                dataframe of spouses having at least columns : id, type, sexe, familyStatus and age.
    children   : pandas dataframe
                dataframe of children having at least columns : id, type, sexe, familyStatus and age.
    mortalityTable : string
                name of the mortality table. 
                View existing mortality tables with Actuariat.mortality_tables.
                Add a mortality table with Actuariat.add_mortality_table

    MAX_YEARS  : int
                number of years of projection
    law_retirement_ : function or tuple
                    a function returning a boolean (the employee will retire yes or no), or a 
                    tuple : (function, liste of it's parameters that have same name in the employees data frame)
    law_resignation_ : function or tuple
                    a function returning a number between 0 and 1 (probability that the employee will resign next year), or a 
                    tuple : (function, liste of it's parameters that have same name in the employees data frame)
    law_marriage_ : function or tuple
                    a function returning a number between 0 and 1 (probability that the employee will marry next year), or a 
                    tuple : (function, liste of it's parameters that have same name in the employees data frame)
    age_diff (int) : Age difference between male and female for new marriages
    marriage_periode : list. A sub-list of ['active', 'retired']. Types to which apply law of marriage.
    law_birth_ : function or tuple
                a function returning a number between 0 and 1 (probability that the employee (or spouse)  
                will  give birth next year), or a  tuple : (function, liste of it's parameters 
                that have same name in the employees or spouses data frame)
    birth_periode : list. A sub-list of ['active', 'retired']. Types to which apply law of birth.
    law_replacement_ : function
                    function having parameters :
                    - departures_ : a dic storing number of departures by group of the year year_
                    - year_ : year of projection
                    this function returns a list of employees to add to population. Each
                    employee in this list is a dic with keys : 'key' (to uniquely define the employee), 
                    'number' and 'data' (list of values that corresponds to columns in employee except id)
    
    Returns
    -------
    tuple
        a tuple of projected population as dics: 
        - projected employees, a dic with key id and value is a dic with keys: data, exist, entrance, lives, deaths, res, type.
        - projected spouses, a dic with key (id, rang) and value is a dic with keys : data, exist, entrance, lives, deaths, type.
        - projected children, a dic with key (id, rang) and value is a dic with keys : data, exist, entrance, lives, deaths, type.
        - new retirees a dic : {year : [list of employees that retired that year (their ids)] }
        - n_new_retirees a list storing number of retirees for each year 
    """

    # if group doesn't exist in employees create it and set it to be id
    if not 'group' in list(employees):
        employees['group'] = employees['id']

    #setting law of retirement
    if law_retirement_ == None:
        law_retirement = retire
        cols_ret = ['age'] 
    else:
        law_retirement = law_retirement_[0] if type(law_retirement_) is tuple else law_retirement_
        #cols_ret = law_retirement_[1]
        cols_ret = law_retirement_[1] if type(law_retirement_) is tuple else inspect.getfullargspec(law_retirement)[0]

    # verify that columns exist in dataframe
    unfound_cols = verifyCols(employees, cols_ret)
    if len(unfound_cols) > 0:
        print('Unfound columns in emmloyees : ', unfound_cols)
        return None
        
    #setting law of resignation
    if law_resignation_ == None:
        law_resignation = turnover0
        cols_res = ['age']
    else:
        law_resignation = law_resignation_[0] if type(law_resignation_) is tuple else law_resignation_
        cols_res = law_resignation_[1] if type(law_resignation_) is tuple else inspect.getfullargspec(law_resignation)[0]

    # verify that columns exist in dataframe
    unfound_cols = verifyCols(employees, cols_res)
    if len(unfound_cols) > 0:
        print('Unfound columns in emmloyees : ', unfound_cols)
        return None
        
    #setting law of marriage
    if law_marriage_ == None:
        law_marriage = probaMariage0
        cols_mar = ['age', 'type']
    else:
        law_marriage = law_marriage_[0] if type(law_marriage_) is tuple else law_marriage_
        cols_mar = law_marriage_[1] if type(law_marriage_) is tuple else inspect.getfullargspec(law_marriage)[0]
        
    # verify that columns exist in dataframe
    unfound_cols = verifyCols(employees, cols_mar)
    if len(unfound_cols) > 0:
        print('Unfound columns in emmloyees : ', unfound_cols)
        return None

    #setting law of birth
    if law_birth_ == None:
        law_birth = probaNaissance0
        cols_birth = ['age']
    else:
        law_birth = law_birth_[0] if type(law_birth_) is tuple else law_birth_
        cols_birth = law_birth_[1] if type(law_birth_) is tuple else inspect.getfullargspec(law_birth)[0]
        
    # verify that columns exist in dataframe
    unfound_cols = verifyCols(spouses, cols_birth)
    if len(unfound_cols) > 0:
        print('Unfound columns in spouses : ', unfound_cols)
        return None
    
    # initialization of projected employees, spouses and children
    employees_proj = tools.init_employees_proj(employees, MAX_YEARS)
    spouses_proj = tools.init_spouses_proj(spouses, MAX_YEARS)
    children_proj = tools.init_children_proj(children, MAX_YEARS)

    # dic where to store retired of each year : {year : [list of employees that retired that year (their ids)] }
    new_retirees = dict(zip([i for i in range(1, MAX_YEARS)],list([[]]*(MAX_YEARS - 1))))
    
    #number of retirees for each year
    n_new_retirees = [0] * MAX_YEARS

    def add_new_employee(id_, year_, ponderation, data_emp):
        """Adds a new employee in the employees_proj dic.
        
        Args:
        id_: The id of the employee to be added (key of the dic).
        year_: year of projection when this employee is added : 1, 2,...
        ponderation : if 0.5 for example,add 50% of an employee. This is used to handle 'rate' of replacement 
        data_emp : a list of values corresponding to columns in employee
        
        

        """
        employees_proj[id_] = {'data':dict(zip(employees.columns[1:],data_emp)), 'exist':0, 'entrance':(year_+1), 'lives':[0] * MAX_YEARS, 
        'deaths' : [0]*MAX_YEARS, 'res':[0]*MAX_YEARS, 'type':[''] * MAX_YEARS}
        
        # updating lives and type
        employees_proj[id_]['lives'][year_] = ponderation
        employees_proj[id_]['type'][year_] = 'active'
        
    def add_new_spouse(employee_id, year_, probMar=1):
        """Adds a new spouse in the spouses_proj dic.
        
        Args:
        employee_id: The id of the employee attached to this spouse.
        year_: year of projection when this spouse is added : 1, 2,...
        entrance : year of entrance

        """
        
        if probMar == 0:
            return
        
        # sex of the spouse
        if employees_proj[employee_id]["data"]["sex"] == 'male':
            sex_temp = 'female'
        else:
            sex_temp = 'male'
            
        #live employee (employee will marry only if still alive)
        live_emp = employees_proj[employee_id]["lives"][year_]
        
        #age. It supposed that difference between ages is -/+ age_diff year depending on sex
        if sex_temp == 'female':
            age_temp = employees_proj[employee_id]["data"]["age"] - age_diff
        else:
            age_temp = employees_proj[employee_id]["data"]["age"] + age_diff
        
        #type
        type_temp = employees_proj[employee_id]["type"][i]
        
        #if not already added add it
        rang = year_
        if not (employee_id, rang) in spouses_proj:
            spouses_proj[(employee_id, rang)] = {'data':dict(zip(['sex', 'age', 'type', 'familyStatus'],[sex_temp, age_temp, type_temp,'not married'])), 'exist':1, 
                'entrance':(year_+1), 'lives':[0] * year_ + [live_emp * probMar] + [0] * (MAX_YEARS- year_ - 1), 'deaths' : [0]*MAX_YEARS,  
                'type':[''] * year_ + [type_temp] + [''] * (MAX_YEARS- year_ - 1)}
        else:
            spouses_proj[(employee_id, rang)]['lives'][year_] = spouses_proj[(employee_id, rang)]['lives'][year_] + live_emp * probMar
    
    
    def add_new_child(employee_id, rang_, year_, rang_child):
        """Adds a new child in the children_proj dic.
        
        Args:
        employee_id: The id of the employee attached to this child.
        year_: year of projection when this child is added : 1, 2,...
        
        """
        
        if employees_proj[employee_id]["data"]["type"] == "active" or employees_proj[employee_id]["data"]["type"] == "retired" :
            if employees_proj[employee_id]["data"]["sex"] == 'female':
                args_ = tuple([employees_proj[employee_id]["data"][z] for z in cols_birth])
                probBirth = law_birth(*args_)
            else:
                args_ = tuple([spouses_proj[(employee_id, rang_)]["data"][z] for z in cols_birth])
                probBirth = law_birth(*args_)
        else:
            return
                
        if probBirth == 0:
            return
        
        #live employee (or his spouse) (employee or spouse will give birth only if still alive)
        if employees_proj[employee_id]["data"]["sex"] == 'male':
            live_emp = spouses_proj[(employee_id, rang_)]["lives"][year_]
        else:
            live_emp = employees_proj[employee_id]["lives"][year_]
        
        #type
        type_temp = employees_proj[employee_id]["type"][i]
        
        #if not already added add it
        if not (employee_id, rang_child) in children_proj:
            children_proj[(employee_id, rang_child)] = {'data':dict(zip(['sex', 'age', 'type', 'familyStatus'],['female', 0, type_temp,'not married'])), 'exist':1, 
                'entrance':(year_+1), 'lives':[0] * year_ + [live_emp * probBirth] + [0] * (MAX_YEARS- year_ - 1), 'deaths' : [0]*MAX_YEARS,  
                'type':[''] * year_ + [type_temp] + [''] * (MAX_YEARS- year_ - 1)}
        # else:
        #    children_proj[(employee_id, 1)]['lives'][year_] = children_proj[(employee_id, 1)]['lives'][year_] + live_emp * probBirth
        
        
    # main loop
    for i in range(1, MAX_YEARS):
        # employees
        n_retired = 0.0
        n_death = 0.0
        n_resignation = 0.0
        n_marriage = 0.0
        departures = {} # a dic storing the number of departures for a group each year
        
        #projection of employees
        for id_e, employee in employees_proj.items():
               
            #age of employee
            age = employee["data"]['age']
            
            #probability of surviving
            survie = act.sfs_nPx(age,1, mortalityTable)
            
            #probability of dying
            death = act.sfs_nQx(age,1, mortalityTable)
            if employee["type"][i-1] == "active":
                n_death += death * employee['lives'][i-1]
                # departure by group
                if employee['data']['group'] in departures:
                    departures[employee['data']['group']] += death * employee['lives'][i-1]
                else:
                    departures[employee['data']['group']] = death * employee['lives'][i-1]
               
            #probability of quitting for actives only
            if employee["type"][i-1] == "active" or employee["type"][i-1] == "":
                args_ = tuple([employee["data"][z] for z in cols_res])
                
                resignation = law_resignation(*args_) #turnover(age)
            else:
                resignation = 0
                
            n_resignation += resignation * employee['lives'][i-1]
            
            # departures by group
            if employee['data']['group'] in departures:
                departures[employee['data']['group']] += resignation * employee['lives'][i-1]*(1-death)
            else:
                departures[employee['data']['group']] = resignation * employee['lives'][i-1]*(1-death)
               
            # if the employee is active check if he will retire
            if employee["type"][i-1] == "active" or employee["type"][i-1] == "":
                if not 'year_proj' in cols_ret:
                    args_ = tuple([employee["data"][z] for z in cols_ret])
                else:
                    args_ = tuple([employee["data"][z] for z in cols_ret[:-1]]) + (i,)

                if law_retirement(*args_):
                    #update number of retired
                    n_retired += employee['lives'][i-1] * survie * (1-resignation) # was 1* employee['lives'][i-1]
                    new_retirees[i] = new_retirees[i] + [id_e]  # add id of the employee to the list
                    
                    # departures by group
                    if employee['data']['group'] in departures:
                        departures[employee['data']['group']] += employee['lives'][i-1]*(1-death)*(1-resignation)
                    else:
                        departures[employee['data']['group']] = employee['lives'][i-1]*(1-death)*(1-resignation)
                    
                    #update type
                    employee["type"][i] = "retired"
                    
                    #update lives
                    employee["lives"][i] = employee["lives"][i-1] * survie * (1-resignation)
                    
                    #update deaths
                    employee["deaths"][i] = employee["lives"][i-1] * death * (1-resignation) # was employee["lives"][i-1] * death
                    
                    #update number of new retirees
                    n_new_retirees[i] =  n_retired
                    
                    #if just retired we are done, but before update age
                    employee["data"]['age'] = employee["data"]['age'] + 1
                    continue
      
            #type remains the same as last year
            employee["type"][i] = employee["type"][i-1]
            
            #update lives
            employee["lives"][i] = employee["lives"][i-1] * survie * (1-resignation)
            
            #update deaths
            employee["deaths"][i] = employee["lives"][i-1] * death * (1-resignation) # was employee["lives"][i-1] * death
            
            #update res
            employee["res"][i] = resignation* employee['lives'][i-1]
            
            #handling marriage
            if employee["type"][i] in marriage_periode:
                if employee["data"]["familyStatus"] == "not married" : 
                    args_ = tuple([employee["data"][z] for z in cols_mar])
                    add_new_spouse(id_e, i, law_marriage(*args_))
                    n_marriage += 1
                
            #update age of employee
            employee["data"]['age'] = employee["data"]['age'] + 1
            
        #projection of spouses
        for id_s, spouse in spouses_proj.items():
            
            # if new spouse continue (treate next year)
            if spouse['entrance'] > i:
                continue

            age = spouse["data"]['age']
            
            #probability of surviving
            survie = act.sfs_nPx(age,1, mortalityTable)
            
            #probability of dying
            death = act.sfs_nQx(age,1, mortalityTable)
            
            # the type of spouse is that of his related employee (but only if not widow)
            if spouse["type"][i-1] == "active" or spouse["type"][i-1] == "retired" or spouse["type"][i-1] == '':
                spouse["type"][i] = employees_proj[id_s[0]]["type"][i]
            else:
                spouse["type"][i] = "widow"
            
            #probability of quitting (probability that the related employee will quit
            if spouse["type"][i] == "active":
                # we have to recalculate resignation because employees_proj[id[0]]['res'][i] contains res of many employees (new recrutes)
                 args_ = tuple([employees_proj[id_s[0]]["data"][z] for z in cols_res])
                
                 resignation = law_resignation(*args_)
            else:
                resignation = 0
           
            #update lives
            spouse["lives"][i] = spouse["lives"][i] + spouse["lives"][i-1] * survie * (1-resignation)
            
            #update deaths
            spouse["deaths"][i] = spouse["deaths"][i] + spouse["lives"][i-1] * death
            
            #handling births for active and retired only
            # if spouse["data"]["type"] == "active" or spouse["data"]["type"] == "retired" :
            #     add_new_child(id_s[0],id_s[1], i)

            if spouse["type"][i] in birth_periode:
                add_new_child(id_s[0],id_s[1], i, 500 + i)

            #update age of spouse
            spouse["data"]['age'] = spouse["data"]['age'] + 1
            
        #projection of children
        for id_c, child in children_proj.items():
            
            # if new child continue (treate next year)
            if child['entrance'] > i:
                continue
            
            #update age of children
            age = child["data"]['age']
            
            #probability of surviving
            survie = act.sfs_nPx(age,1, mortalityTable)
            
            #probability of dying
            death = act.sfs_nQx(age,1, mortalityTable)
            
            # the type of child is that of his related employee (but only if not widow)
            if child["type"][i-1] == "active" or child["type"][i-1] == "retired" or child["type"][i-1] == '':
                child["type"][i] = employees_proj[id_c[0]]["type"][i]
            else:
                child["type"][i] = "widow"
            
            #probability of quitting (probability that the related employee will quit)
            if child["type"][i] == "active":
                # we have to recalculate resignation because employees_proj[id[0]]['res'][i] contains res of many employees (new recrues)
                 args_ = tuple([employees_proj[id_c[0]]["data"][z] for z in cols_res])
                
                 resignation = law_resignation(*args_)
            else:
                resignation = 0
           
            #update lives
            child["lives"][i] = child["lives"][i-1] * survie * (1-resignation)
            
            #update deaths
            child["deaths"][i] = child["lives"][i-1] * death
            
            #update age of spouses
            child["data"]['age'] = child["data"]['age'] + 1 
            
        
        # replacement of departures
        if not (law_replacement_ == None):
            new_emp = law_replacement_(departures, i) # new_emp is a list of dics having keys : key, number and data (list of values corresponding to employees)
            for ne in new_emp:
                add_new_employee('new_employee_year_' + str(i) + '_key_' + str(ne['key']), i, ne['number'],ne['data']) 
        
        
    return employees_proj, spouses_proj, children_proj, new_retirees, n_new_retirees
    
    
def globalNumbers(employees_proj_, spouses_proj_, children_proj_, MAX_YEARS):
    """ 
        Assumes parameters are of the form of those returned by simulerEffectif
  
        Parameters: 
            employees_proj_ (dic): a dic containing projected employees
            spouses_proj_ (dic): a dic containing projected spouses
            children_proj_ (dic): a dic containing projected children
          
        Returns: 
            DataFrame: A DataFrame containing global numbers by year : 
                       Actives, Retirees, Wives, Widows, Children 
    """
    
    
    # number of actives per year
    effectif_actifs = [0] * MAX_YEARS
    effectif_conjoints_actifs = [0] * MAX_YEARS
    effectif_enfants_actifs = [0] * MAX_YEARS

    # number of retired per year
    effectif_retraites = [0] * MAX_YEARS
    effectif_conjoints_retraites = [0] * MAX_YEARS
    effectif_enfants_retraites = [0] * MAX_YEARS
    effectif_enfants_ayant_cause = [0] * MAX_YEARS

    # number of quitters per year
    effectif_demissions = [0] * MAX_YEARS

    # number of dying actives
    effectif_deces_actifs = [0] * MAX_YEARS
    effectif_deces_conjoints_actifs = [0] * MAX_YEARS
    effectif_deces_enfants_actifs = [0] * MAX_YEARS
    
    # number of dying retired
    effectif_deces_retraites = [0] * MAX_YEARS
    effectif_deces_conjoints_retraites = [0] * MAX_YEARS
    effectif_deces_enfants_retraites = [0] * MAX_YEARS
    effectif_deces_enfants_ayant_cause = [0] * MAX_YEARS

    # number of living widows
    effectif_ayants_cause = [0] * MAX_YEARS

    for i in range(MAX_YEARS):
        for a in employees_proj_.values():
            if a['type'][i] == 'active':
                effectif_actifs[i] = effectif_actifs[i] + a['lives'][i]
                effectif_deces_actifs[i] = effectif_deces_actifs[i] + a['deaths'][i]
            else:
                effectif_retraites[i] = effectif_retraites[i] + a['lives'][i]
                effectif_deces_retraites[i] = effectif_deces_retraites[i] + a['deaths'][i]
            
            effectif_demissions[i] = effectif_demissions[i] + a['res'][i]
        
        for a in spouses_proj_.values():
            if a['type'][i] == 'active':
                effectif_conjoints_actifs[i] = effectif_conjoints_actifs[i] + a['lives'][i]
                effectif_deces_conjoints_actifs[i] = effectif_deces_conjoints_actifs[i] + a['deaths'][i]
                
            if a['type'][i] == 'retired':
                effectif_conjoints_retraites[i] = effectif_conjoints_retraites[i] + a['lives'][i]
                effectif_deces_conjoints_retraites[i] = effectif_deces_conjoints_retraites[i] + a['deaths'][i]
                
            if a['type'][i] == 'widow':
                effectif_ayants_cause[i] = effectif_ayants_cause[i] + a['lives'][i]
                
        for a in children_proj_.values():
            if a['type'][i] == 'active':
                effectif_enfants_actifs[i] = effectif_enfants_actifs[i] + a['lives'][i]
                effectif_deces_enfants_actifs[i] = effectif_deces_enfants_actifs[i] + a['deaths'][i]
                
            if a['type'][i] == 'retired':
                effectif_enfants_retraites[i] = effectif_enfants_retraites[i] + a['lives'][i]
                effectif_deces_enfants_retraites[i] = effectif_deces_enfants_retraites[i] + a['deaths'][i]

            if a['type'][i] == 'widow':
                effectif_enfants_ayant_cause[i] = effectif_enfants_ayant_cause[i] + a['lives'][i]
                effectif_deces_enfants_ayant_cause[i] = effectif_deces_enfants_ayant_cause[i] + a['deaths'][i]
            
    # construct DataFrame of projected numbers
    totalEmployees = [sum(x) for x in zip(effectif_actifs, effectif_retraites)]
    totalSpouses = [sum(x) for x in zip(effectif_conjoints_actifs, effectif_conjoints_retraites)]
    totalChildren = [sum(x) for x in zip(effectif_enfants_actifs, effectif_enfants_retraites, effectif_enfants_ayant_cause)]

    Data = {'Year':list(range(MAX_YEARS)), 'effectif_actifs' : effectif_actifs, 'effectif_retraites' : effectif_retraites, 'Total Employees' : totalEmployees,
            'effectif_ayants_cause' : effectif_ayants_cause, 'effectif_conjoints_actifs' : effectif_conjoints_actifs,
            'effectif_conjoints_retraites' : effectif_conjoints_retraites, 'Total Spouses' : totalSpouses, 'effectif_enfants_actifs' : effectif_enfants_actifs,
            'effectif_enfants_retraites' : effectif_enfants_retraites, 'effectif_enfants_ayant_cause' : effectif_enfants_ayant_cause,'Total Children' : totalChildren}

    Effectifs = pd.DataFrame(data=Data,
                columns=['Year', 'effectif_actifs', 'effectif_retraites', 'Total Employees' , 'effectif_ayants_cause',
                         'effectif_conjoints_actifs', 'effectif_conjoints_retraites', 'Total Spouses', 'effectif_enfants_actifs', 
                         'effectif_enfants_retraites', 'effectif_enfants_ayant_cause','Total Children' ]) 
    return Effectifs
    
def individual_employees_numbers(employees_proj_): 
    """
    Returns a tuple of four data frames : projected lives, deaths, res and 
    type for employees
    
    Parameters
    ----------
    employees_proj_ : dic of the form of that returned by simulerEffectif
        
    
    """
    ids = []
    data = []
    lives = []
    deaths = []
    res = []
    types = []

    
    # Store data in lists
    for emp in employees_proj_:
        ids.append(emp)
        data.append(employees_proj_[emp]['data'])
        lives.append(employees_proj_[emp]['lives'])
        deaths.append(employees_proj_[emp]['deaths'])
        res.append(employees_proj_[emp]['res'])
        types.append(employees_proj_[emp]['type'])

    # number of employees
    n_emp = len(ids)

    #number of years
    n_years = len(lives[0])

    # create the dataframes to be returned
    df_lives = pd.DataFrame()
    df_deaths = pd.DataFrame()
    df_res = pd.DataFrame()
    df_types = pd.DataFrame()

    #add the id and the data columns
    df_lives['id'] = ids
    df_deaths['id'] = ids
    df_res['id'] = ids
    df_types['id'] = ids
    cols_data = data[0].keys()
    for c in cols_data:
        temp = []
        for d in data:
            if c in d:
                temp.append(d[c])
            else:
                temp.append('')
        
        df_lives[c] = temp
        df_deaths[c] = temp
        df_types[c] = temp
        df_res[c] = temp

        # df_lives[c] = [d[c] for d in data]
        # df_deaths[c] = [d[c] for d in data]
        # df_res[c] = [d[c] for d in data]
        # df_types[c] = [d[c] for d in data]

    for year in range(n_years):
        df_lives['year_' + str(year)] = [lives[emp][year] for emp in range(n_emp)]
        df_deaths['year_' + str(year)] = [deaths[emp][year] for emp in range(n_emp)]
        df_res['year_' + str(year)] = [res[emp][year] for emp in range(n_emp)]
        df_types['year_' + str(year)] = [types[emp][year] for emp in range(n_emp)]

    return df_lives, df_deaths, df_res, df_types


def individual_spouses_numbers(spouses_proj_): 
    """
    Returns a tuple of four data frames : projected lives, deaths and 
    type for spouses
    
    Parameters
    ----------
    spouses_proj_ : dic of the form of that returned by simulerEffectif
        
    
    """
    ids = []
    rangs = []
    data = []
    lives = []
    deaths = []
    types = []
    
    # Store data in lists
    for spouse in spouses_proj_:
        ids.append(spouse[0])
        rangs.append(spouse[1])
        data.append(spouses_proj_[spouse]['data'])
        lives.append(spouses_proj_[spouse]['lives'])
        deaths.append(spouses_proj_[spouse]['deaths'])
        types.append(spouses_proj_[spouse]['type'])

    # number of spouses
    n_spouses = len(ids)

    #number of years
    n_years = len(lives[0])

    # create the dataframes to be returned
    df_lives = pd.DataFrame()
    df_deaths = pd.DataFrame()
    df_types = pd.DataFrame()

    #add the id column
    df_lives['id'] = ids
    df_lives['rang'] = rangs
    df_deaths['id'] = ids
    df_deaths['rang'] = rangs
    df_types['id'] = ids
    df_types['rang'] = rangs

    # data columns
    cols_data = data[0].keys()
    for c in cols_data:
        temp = []
        for d in data:
            if c in d:
                temp.append(d[c])
            else:
                temp.append('')
        
        df_lives[c] = temp
        df_deaths[c] = temp
        df_types[c] = temp

        # df_lives[c] = [d[c] for d in data]
        # df_deaths[c] = [d[c] for d in data]
        # df_types[c] = [d[c] for d in data]
    
    for year in range(n_years):
        df_lives['year_' + str(year)] = [lives[spouse][year] for spouse in range(n_spouses)]
        df_deaths['year_' + str(year)] = [deaths[spouse][year] for spouse in range(n_spouses)]
        df_types['year_' + str(year)] = [types[spouse][year] for spouse in range(n_spouses)]

    return df_lives, df_deaths, df_types


def individual_children_numbers(children_proj_): 
    """
    Returns a tuple of four data frames : projected lives, deaths and 
    type for children
    
    Parameters
    ----------
    children_proj_ : dic of the form of that returned by simulerEffectif
        
    
    """
    ids = []
    rangs = []
    data = []
    lives = []
    deaths = []
    types = []
    
    # Store data in lists
    for child in children_proj_:
        ids.append(child[0])
        rangs.append(child[1])
        data.append(children_proj_[child]['data'])
        lives.append(children_proj_[child]['lives'])
        deaths.append(children_proj_[child]['deaths'])
        types.append(children_proj_[child]['type'])

    # number of children
    n_children = len(ids)

    #number of years
    n_years = len(lives[0])

    # create the dataframes to be returned
    df_lives = pd.DataFrame()
    df_deaths = pd.DataFrame()
    df_types = pd.DataFrame()

    #add the id and rang columns which are key
    df_lives['id'] = ids
    df_lives['rang'] = rangs
    df_deaths['id'] = ids
    df_deaths['rang'] = rangs
    df_types['id'] = ids
    df_types['rang'] = rangs

    # data columns
    cols_data = data[0].keys()
    for c in cols_data:
        temp = []
        for d in data:
            if c in d:
                temp.append(d[c])
            else:
                temp.append('')
        
        df_lives[c] = temp
        df_deaths[c] = temp
        df_types[c] = temp

        # df_lives[c] = [d[c] if c in d else '' for d in data]
        # df_deaths[c] = [d[c] if c in d else '' for d in data]
        # df_types[c] = [d[c] if c in d else ''for d in data]
    
    for year in range(n_years):
        df_lives['year_' + str(year)] = [lives[child][year] for child in range(n_children)]
        df_deaths['year_' + str(year)] = [deaths[child][year] for child in range(n_children)]
        df_types['year_' + str(year)] = [types[child][year] for child in range(n_children)]

    return df_lives, df_deaths, df_types


def leavingNumbers(employees_proj_, n_new_retirees_, MAX_YEARS):
    """ 
        Assumes parameter employees_proj_ is of the form of that returned by simulerEffectif
  
        Parameters: 
            employees_proj_ (dic): a dic containing projected employees
            n_new_retirees_ (list) : number of new retired per year
        Returns: 
            DataFrame: A DataFrame containing global numbers leaving population of employees by year : 
                       deaths, resignation, new retirees 
    """
    
    # number of quitters (resignations) per year
    effectif_demissions = [0] * MAX_YEARS
    
    # number of dying actives per year
    effectif_deces_actifs = [0] * MAX_YEARS
    
    for i in range(MAX_YEARS):
        for a in employees_proj_.values():
            if a['type'][i] == 'active':
                effectif_deces_actifs[i] = effectif_deces_actifs[i] + a['deaths'][i]
            
            effectif_demissions[i] = effectif_demissions[i] + a['res'][i]
    
    
    
    #construct DataFrame of projected numbers leaving the pop : deaths, resignations and new retirees
    totalLeaving = [sum(x) for x in zip(effectif_deces_actifs, effectif_demissions, n_new_retirees_ )]
    
    Data = {'Year':list(range(MAX_YEARS)),'effectif_deces_actifs' : effectif_deces_actifs, 'effectif_demissions' : effectif_demissions, 
            'new_retirees' : n_new_retirees_, 'Total Leaving' : totalLeaving}

    Leaving = pd.DataFrame(data=Data, 
            columns=['Year', 'effectif_deces_actifs', 'effectif_demissions', 'new_retirees' , 'Total Leaving'])
    
    return Leaving


def plot_pyramide_spouses(numbers_, year_, MAX_YEARS, color_males = (149/255,125/255,98/255), color_females = (0/255,128/255,0/255)):

    # Check that year is greater than 0 and smaller than MAX_YEARS
    if year_ < 1 or year_ > MAX_YEARS:
        print("year_ maust be greater than 0 and smaller than MAX_YEARS !")
        return
    
    # Setting ages boundaries
    min_age_ = 19
    max_age_ = 100

    # color_males = (149/255,125/255,98/255) 
    # color_females = (0/255,128/255,0/255)

    # Getting individual numbers of spouses
    ind_spo_numbers = individual_spouses_numbers(numbers_)

    #Getting lives numbers for spouses
    spouses_proj = ind_spo_numbers[0]
    
    # Group lives numbers at year (year_-1) by age and sex
    emp_grouped = spouses_proj.groupby(['age','sex'], as_index=False)['year_'+str((year_-1))].sum()
        
    #update colum age to be age at year (year_-1)
    emp_grouped['age'] = emp_grouped['age'] - MAX_YEARS + (year_-1)
    
    # Getting just ages between defined boudaries
    emp_grouped = emp_grouped.loc[(emp_grouped['age'] < max_age_) & (emp_grouped['age'] > min_age_)]
    
    # Pivot table : lines year_ - 1 ; columns sex
    table = pd.pivot_table(emp_grouped, values='year_'+str((year_-1)), index=['age'],  columns=['sex'], aggfunc=np.sum)
    
    # Replace nas with 0
    table = table.fillna(0)
    
    #calculate percentage
    if 'male' in list(table.columns):
        table['male'] = table['male']/np.sum(table['male'])

    if 'female' in list(table.columns):
        table['female'] = table['female']/np.sum(table['female'])
    
    if 'female' in list(table.columns):
        table['female'] = table['female'] * (-1)
    
    # plt.subplot(len(tables) , 1, plot_num)
    # plt.subplots_adjust(hspace = 0.5)
    plt.xlim(-0.05,0.05)
    # plt.title('Mortality table ' + t)
    
    if 'male' in list(table.columns):
        values = [0] * (max_age_ - min_age_ - 1)
        for i in range(len(table['male'])):
            values[table.index[i] - min_age_ - 1] = table.iloc[i]['male']
        p_male = plt.barh(list(range(min_age_ + 1, max_age_)), values, color = color_males )
    
    if 'female' in list(table.columns):
        for i in range(len(table['female'])):
            values[table.index[i] - min_age_ - 1] = table.iloc[i]['female']
        p_female = plt.barh(list(range(min_age_ + 1, max_age_)), values, color = color_females)

    

    plt.show()
    


def new_employees(employees_proj_, MAX_YEARS):
    """ 
        Assumes parameter employees_proj_ is of the form of that returned by simulerEffectif
  
        Parameters: 
            employees_proj_ (dic): a dic containing projected employees
            MAX_YEARS (int) : number of years of prjection
        Returns: 
            DataFrame: A DataFrame containing new employees entering the population
    """

    ids = []
    data = []
    entrances = []
    n_new_employees = 0

    for emp in employees_proj_:
        if employees_proj_[emp]['entrance'] > 0:
            ids.append(emp)
            entrances.append(employees_proj_[emp]['entrance'])
            data.append(employees_proj_[emp]['data'])
            n_new_employees = n_new_employees +1
    
    if n_new_employees == 0:
        return None
    
    # create the dataframes
    df_new_employees = pd.DataFrame()       
    df_new_employees['id'] = ids
    df_new_employees['entrance'] = entrances

    # data columns
    cols_data = data[0].keys()
    for c in cols_data:
        df_new_employees[c] = [d[c] for d in data]

    return df_new_employees
