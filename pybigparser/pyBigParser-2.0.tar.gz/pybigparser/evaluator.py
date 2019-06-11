import math
import string
import re
### Constants

special_functs = ["log", "exp", "cos", "sin",
                 "tan", "log10", "abs", "pi", "e"]
g_string = set(string.ascii_lowercase)
g_string = g_string.union(set(string.ascii_uppercase))
g_numbers = [str(i) for i in range(0, 100)]

### Tests function


##def testA():
##
##    myf = bigFunction()
##    myf.setFunction("x+y+z+log(t)+exp(s)+4")
##
##    myf.addSub("x", "t+0.24*s")
##    myf.addSub("y", "s+0.24*t")
##    myf.addSub("z", "s/log(t)")
##
##
##    print myf.evaluate({"s": "0.32", "t": "0.15"})
##    print myf.value
##    print myf.getSubValue("x")
##    print myf.getSubValue("y")
##    print myf.getSubValue("z")
##
##
##def testB():
##
##    myf = bigFunction()
##    myf.setFunction("x1+y2+z3+log(t4)+exp(s5)+4")
##
##    myf.addSub("x1", "t4+0.24*s5")
##    myf.addSub("y2", "s5+0.24*t4")
##    myf.addSub("z3", "s5/log(t4)")
##
##    print myf.evaluate({"s5": "0.32", "t4": "0.15"})
##    print myf.value
##    print myf.getSubValue("x1")
##    print myf.getSubValue("y2")
##    print myf.getSubValue("z3")
##
##def testC():
##
##    darcy = bigFunction()
##    darcy.setFunction("(1/(a*(log(d/q)+delta)))**2")
##    darcy.addSub("a", "2/log(10)")
##    darcy.addSub("b", "(er/d)/3.7")
##    darcy.addSub("d", "Re*(log(10)/5.02)")
##    darcy.addSub("q", "s**(s/(s+1))")
##    darcy.addSub("s", "b*d+log(d)")
##    darcy.addSub("delta", "z*(g/(g+1))")
##    darcy.addSub("g", "b*d+log(d/q)")
##    darcy.addSub("z", "log(q/g)")
##    data={}
##    data['Re']='126400'
##    data['er'] = 0.000007
##    data['D'] = '2.0 / 12'
##    print darcy.evaluate(data)
##
##def testD():
##
##    from magnitude import mg
##    d = mg(300, "km")
##    t = mg(1, "h")
##    f = bigFunction()
##    f.setFunction("d/t")
##    print f.evaluate({'d':d,'t':t})
##
##def testE():
##
##    from magnitude import mg
##    d = mg(300, "km")
##    t = mg(1, "h")
##    f = bigFunction()
##    f.setFunction("d/t")
##    f.addSub("d", d)
##    f.addSub("t", t)
##    print f.evaluate()
    
###


def pi():
    '''
    Returns pi constant
    '''
    return math.pi

###


def e():
    '''
    Returns e constant
    '''
    return math.e

###


def cos(x):
    '''
    Function to determinate the
    cosine value of x

    x: number

    Returns number
    '''
    return math.cos(x)

###


def sin(x):
    '''
    Function to determinate the
    sin value of x

    x: number

    Returns number
    '''
    return math.sin(x)

###


def abs(x):
    '''
    Function to determinate the
    absolute value of x

    x: number

    Returns number
    '''
    return math.fabs(x)

###


def log10(x):
    '''
    Function to determinate the decimal
    logarithm of x

    x: number

    Returns number
    '''
    return math.log10(x)

###


def log(x):
    '''
    Function to determinate the natural
    logarithm of x

    x: number

    Returns number
    '''
    return math.log(x)

###


def exp(x):
    '''
    Function to determinate the exponential
    of x

    x: number

    Returns number
    '''
    if x > 700:

        inlet = 700

        x = 700
        
    return math.exp(x)

###


def tan(x):
    '''
    Function to determinate the tangent
    of x

    x: number

    Returns number
    '''
    return math.tan(x)

###


def got_string(string):
    '''
    Function to determinate that
    a string has an alfabet character

    mystr: string

    Returns True or False
    '''

    result = False
    for i in string:
        if i in g_string:
            result = True

    return result

###


def is_expression(char):
    '''
    Function to determinate if a character is
    a valid character for a math expresion

    char: char

    Returns True or False
    '''
    return True and ((char in g_string) or (char in g_numbers))

###


def remove_duplicates(l):
    '''
    Function to remove duplicates items from a
    list
    l: a list of string
    Returns a list
    '''
    return list(set(l))

###


def get_vars(str_expr):
    '''
    Function to create a list of string of
    a math expressions, every item of the list
    is a valid math variable
    strExpr: string
    Returns list
    '''

    test = [x for x in str_expr]
    result = []
    s = ''
    while len(test) != 0:
        ax = test.pop(0)
        if is_expression(ax):
            s += ax
        else:
            if s != '' and got_string(s):
                result.append(s)
            s = ''

    if got_string(s):
        result.append(s)

    result3 = remove_duplicates(result)

    final = [x for x in result3 if not x in special_functs]

    return final

###


def add_functions(indict={}):
    outdict = dict()

    if len(indict)>0:
        for key, value in indict.items():
            outdict[key] = value
    
    outdict['log'] = log
    outdict['exp'] = exp
    outdict['pi'] = pi
    outdict['e'] = e
    outdict['log10'] = log10
    outdict['e'] = e
    outdict['sin'] = sin
    outdict['cos'] = cos
    outdict['tan'] = tan
    outdict['abs'] = abs

    return outdict

###


class MathParser(object):

    def __init__(self):
        
        self.function = ""
        self.value = None
        self.data = dict()
        self.p_values = dict()

    def set_function(self, function):
        """Set the global function to evaluate

        Keyword arguments:
        function (str) -- Variable designed in the global function
        """
        bSet = True

        import ast
        try:
            ast.parse(function)

        except SyntaxError as e:
            bSet = False
            print("A syntax error was found in function: {}".format(function))

        if bSet:
            self.function = function
            
    def add_sub(self, var, function):
        """Add sub-functions to the collection

        Keyword arguments:
        var (str) -- Variable designed in the global function
        function (str) -- Sub-function
        """
        bSet = True

        import ast
        try:
            if isinstance(function, (int, float,)):
                aux = function
            else:
                if isinstance(function, (str)):
                    ast.parse(function)
                else:
                    aux = function
                    
        except SyntaxError as e:
            bSet = False
            print("A syntax error was found in function: {}".format(function))

        try:
            ast.parse(var)

        except SyntaxError as e:
            bSet = False
            print("A syntax error was found in variable: {}".format(var))

        if bSet:
            self.data[var] = function
            self.p_values[var] = None

    def get_data_vars(self):

        return self.data.keys()

    def get_sub_value(self, var):

        result = None
        
        if var in self.get_data_vars():

            result = self.p_values[var]

        return result

    def set_sub_value(self, var, value):

        if var in self.get_data_vars():

            self.p_values[var] = value
     
    def update_sub(self, var, function):
        """Update sub-functions to the collection

        Keyword arguments:
        var (str) -- Variable to update
        function (str) -- Sub-function to update
        """
        bSet = True

        import ast
        try:
            ast.parse(function)

        except SyntaxError as e:
            bSet = False
            print("A syntax error was found in function: {}".format(function))

        try:
            ast.parse(var)

        except SyntaxError as e:
            bSet = False
            print("A syntax error was found in variable: {}".format(var))

        if bSet:
            if var in self.data.keys():
                self.data[var] = function
            else:
                print("variable {} was not found".format(var))

    def __rec_evaluate(self, function, myparameters):

        myvars = list()
        bStr = False
        if isinstance(function, str):
            myvars = get_vars(function)
            bStr = True

        if len(myvars) > 0:
            new_parameters = add_functions()
            parameters = add_functions(myparameters)

            for i in myvars:
                new_parameters[i] = self.__rec_evaluate(parameters[i], parameters)
                self.set_sub_value(i, new_parameters[i])
                
            return eval(function, new_parameters)

        else:
            if isinstance(function, (int, float,)):
                return eval(str(function), myparameters)
            else:
                if bStr:
                    return eval(function, myparameters)
                else:
                    return function

    def evaluate(self, values={}):

        """Evaluates global function within values

        Keyword arguments:
        values (dict) -- Variables and Values por parsing (default {})
        """

        result = None

        if self.function != "":
            if len(values) > 0:
                for key, value in values.items():
                    self.data[key] = value

            try:
                result = self.__rec_evaluate(self.function, self.data)
                self.value = result

            except KeyError as e:

                print("the key {} was not found in collection".format(e))

        return result
