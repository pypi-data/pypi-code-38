class Matrix:
    
    def __init__(self, m = 2, n = 2):
        """ A class to represent a mathematical (m x n) matrix using Python lists 
        
        Attributes:
            m (int): the number of rows
            n (int): the number of columns            
        """
        
        self.m = m
        self.n = n
        
        self.data = []
        
        #initialize with 0's
        for i in range(self.m):
            self.data.append([])
            for j in range(self.n):
                self.data[i].append(0)
                
                
    def insert_value_given_index(self, i, j, value):
        """ Inserts value into matrix at particular given index 
        
            Args:
                i (int): row-index
                j (int): column-index
                
            Returns:
                self.data
        """
        
        self.data[i][j] = value
        
        return self.data 
                                 
    def __add__(self, other):
        """Add two matrices only if they're the same dimensions.
           Matrix addition is element-wise.
        
        Args:
            other (Matrix): the matrix object on the right-hand side of the '+' sign
            
        Returns: 
            Matrix: Matrix object, result of the addition
        """
        try:
            assert self.m == other.m and self.n == other.n, 'Matrices are not the same dimension'
        except AssertionError as error:
            raise
            
        m = self.m
        n = self.n
        
        result = Matrix(m, n)
        
        for i in range(m):
            for j in range(n):
                res = self.data[i][j] + other.data[i][j]
                result.data[i][j] = res
        
        return result
    
    def __sub__(self, other):
        """Subtract two matrices only if they're the same dimensions.
           Matrix subtraction is element-wise.
        
        Args:
            other (Matrix): the matrix object on the right-hand side of the '-' sign
            
        Returns: 
            Matrix: Matrix object, result of the subtraction
        """
        try:
            assert self.m == other.m and self.n == other.n, 'Matrices are not the same dimension'
        except AssertionError as error:
            raise
            
        m = self.m
        n = self.n
        
        result = Matrix(m, n)
        
        for i in range(m):
            for j in range(n):
                res = self.data[i][j] - other.data[i][j]
                result.data[i][j] = res
        
        return result 
    
    
    def __mul__(self, other):
        """Straightforward brute-force matrix multiplication algorithm. Only computes if 
           self.n == other.m
        
        Args:
            other (Matrix): the matrix object on the right-hand side of the '-' sign
            
        Returns: 
            Matrix: Matrix object, result of the multiplication
        """
        try:
            assert self.n == other.m, 'Cannot multiply matrices. Incorrect dimensions (' + str(self.n) + '!=' + str(other.m) + ')'
        except AssertionError as error:
            raise
            
        inner_dimension = self.n # will be convenient in multiplication
            
        m = self.m
        n = other.n
        
        result = Matrix(m, n)
        
        # multiply
        for i in range(m): # each row in lhs matrix
            for j in range(n): # each col in rhs matrix
                
                res = 0
                for k in range(inner_dimension): # each pt
                    res += self.data[i][k] * other.data[k][j] # multiply and sum
                
                #store in result
                result.insert_value_given_index(i,j,res)
        
        return result
    
       
    def __repr__(self):
        """ Overload magic method. When object is typed, just print the matrix as a string
        
        Args: 
            none
        
        Returns: 
            string: the matrix 
        """
        return str(self.data)
    
        