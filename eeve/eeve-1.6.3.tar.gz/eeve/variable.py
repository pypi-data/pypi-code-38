class Variable:
    def __init__(self, name: str, value):
        self.value = value
        self._name = name

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return f'<Variable {self.name}: self.value>'


class VariableGroup:
    def __init__(self):
        self.vars = dict()

    def __getitem__(self, key: str) -> Variable:
        return self.vars[key].value

    def __setitem__(self, key: str, value: 'Any') -> None:
        if type(value) is Variable:
            self.vars[key] = value
        else:
            self.vars[key] = Variable(name=key, value=value)

    def update(self, new: dict) -> None:
        for k, v in new.items():
            self.__setitem__(key=k, value=v)

    def get(self, var: str, default=None) -> 'Any':
        """Returns the variable value if it exists or
        the default value if it does not
        
        Arguments:
            var {str} -- The variable name
        
        Keyword Arguments:
            default {Any} -- The value to return in case the variable does not exists (default: {None})
        
        Returns:
            Any -- Variable value if exists or default value
        """
        if var.startswith('var'):
            var = var[3:]
        while var.startswith('$'):
            var = var[1:]

        if var in self.vars:
            return self[var]  # returns value
        else:
            return default

    def get_or_create(self, var: str, default=None) -> Variable:
        """Returns the existing variable reference if it exists. If it
        does not, the variable is created and added to the scope
        with the supplied default value
        
        Arguments:
            var {str} -- The variable name to search or create
        
        Keyword Arguments:
            default {Any} -- The value to set the variable in case it does not exists (default: {None})
        
        Returns:
            Variable -- The requested variable
        """
        if var not in self.vars:
            self.vars[var] = Variable(name=var, value=default)

        return self.vars[var]

    def to_kwargs(self) -> dict:
        """Returns all variable names and values in a dictionary

        var_name:var_value
        
        Returns:
            dict -- Dictionary with all variable names and values
        """
        result = dict()
        for k, v in self.vars.items():
            result[k] = v.value
        return result

    def __repr__(self):
        return str(self.to_kwargs())


def get_var_name(var_name):
    if var_name.startswith('var$'):
        var_name = var_name[3:]
    while var_name.startswith('$'):
        var_name = var_name[1:]

    return var_name