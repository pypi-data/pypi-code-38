class FilterBuilder:
    def __init__(self, filters = []):
        self.filters = filters
    
    def eq(self, field, value):
        self.filters.append(field + ".eq('" + value + "')")
        return self
    
    def gt(self, field, value):
        self.filters.append(field + ".gt('" + value + "')")
        return self
    
    def gteq(self, field, value):
        self.filters.append(field + ".gteq('" + value + "')")
        return self
    
    def lt(self, field, value):
        self.filters.append(field + ".lt('" + value + "')")
        return self
    
    def lteq(self, field, value):
        self.filters.append(field + ".lteq('" + value + "')")
        return self
    
    def bt(self, field, valueOne, valueTwo):
        self.filters.append(field + ".bt('" + valueOne + "','" + valueTwo + "')")
        return self
    
    def toString(self):
        return ",".join(self.filters)
    
    def getFilter(self):
        return "filter=" + ",".join(self.filters)
    
    def setFilter(self, filters):
        self.filters = filters
        return self