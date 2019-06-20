class ActionableDict(dict):

    parent = None
    callback = None

    def __init__(self, initial_dict, callback = None, parent = None):
        self.parent = parent
        self.callback = callback
        for key, value in initial_dict.items():
            if isinstance(value, dict):
                initial_dict[key] = ActionableDict(value, self.callback, self)
        super(ActionableDict, self).__init__(initial_dict)

    def __setitem__(self, item, value):
        if isinstance(value, dict):
            _value = ActionableDict(value, self.callback, self)
        else:
            _value = value
        super(ActionableDict, self).__setitem__(item, _value)
        if self.callback != None:
            self.callback(self.__traverse_parents(item), _value)

    def __traverse_parents(self, item):
        test_item = self
        parent_keys = [ item ]
        while(hasattr(test_item, 'parent') and test_item.parent != None):
            for key, value in test_item.parent.items():
                if value == test_item:
                    parent_keys.append(key)
            test_item = test_item.parent
        return parent_keys[::-1]
