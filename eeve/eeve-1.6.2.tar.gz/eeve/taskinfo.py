from eeve.variable import VariableGroup, Variable
from dataclasses import dataclass
from typing import List


@dataclass
class TaskInfo:
    actions: 'List[Action]'
    global_variables: VariableGroup
    task_variables: VariableGroup
    local_variables: VariableGroup
    current_action_index: int = 0
    increment_action_index: bool = True

    def get_next_actions(self):
        """Returns an enumerated list of actions starting from the task
        with index 'current_action_index + 1'
        
        Returns:
            List[Tuple[int, Action]] -- Enumerated list of next actions
        """
        return enumerate(self.actions[self.current_action_index + 1:], self.current_action_index + 1)

    def get_var(self, var_name: str):
        """Returns a variable reference if var_name starts with var
        or the variable value if it does not. In case var_name is vars
        (either var$[$[$]]vars or [$[$[$]]]vars), the returned value is a dict in the format 
        {var_name:Variable(var_name, var_value), ...} for the former or a dict in the format
        {var_name:var_value, ...} for the latter. 

        Scopes:
            $ or empty -> local scope
            $$         -> task scope
            $$$        -> global scope

        Arguments:
            var_name {str} -- the variable name with format [var][$[$[$]]]var_name
        
        Returns:
            Union[Any, dict] -- The requested variable info (read docstring above)
        """
        original_var_name = var_name
        is_var_ref = var_name.startswith('var$')

        class Scopes:
            Global = self.global_variables
            Task = self.task_variables
            Local = self.local_variables

        scope: VariableGroup = Scopes.Local

        # remove 'var' prefix if is variable reference
        if is_var_ref:
            var_name = var_name[3:]

        # define scope and remove all prefixing '$', being variable reference or just variable value
        if var_name.startswith('$$$'):
            scope = Scopes.Global
            var_name = var_name[3:]
        elif var_name.startswith('$$'):
            scope = Scopes.Task
            var_name = var_name[2:]
        elif var_name.startswith('$'):
            scope = Scopes.Local
            var_name = var_name[1:]

        # return variable ref or value
        if is_var_ref:
            if var_name == 'vars':
                return scope.vars
            else:
                return scope.get_or_create(var_name)
        else:
            if var_name == 'vars':
                return scope.to_kwargs()
            else:
                return scope.get(var_name, original_var_name)

    def has_var(self, var_name: str) -> bool:
        """Checks if a given variable exists. 
        the 'var' prefix is ignored

        Scopes:
            $ or empty -> local scope
            $$         -> task scope
            $$$        -> global scope

        
        Arguments:
            var_name {str} -- the name of the variable
        
        Returns:
            bool -- Does the variable exist?
        """
        is_var = var_name.startswith('var$')

        class Scopes:
            Global = self.global_variables
            Task = self.task_variables
            Local = self.local_variables

        scope = Scopes.Local

        if is_var:
            var_name = var_name[3:]
        if var_name.startswith('$$$'):
            scope = Scopes.Global
            var_name = var_name[3:]
        elif var_name.startswith('$$'):
            scope = Scopes.Task
            var_name = var_name[2:]
        elif var_name.startswith('$'):
            scope = Scopes.Local
            var_name = var_name[1:]

        return var_name in scope.vars
