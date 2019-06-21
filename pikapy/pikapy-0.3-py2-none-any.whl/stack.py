"""Provide the basic data structure and functions of the pikachu language.

Classes:
PikaStack -- The basic data structure of the pikachu language.
"""

from random import randrange


class PikaStack():
    """Encapsulate Stack specific data and methods defined in the pikachu langeuage.

    PikaStack()
    ADD() -> void
    SUB() -> void
    MULT() -> void
    DIV() -> void
    RAND() -> void
    POP() -> int, 'NaN', or None
    PUSH() -> void
    PEEK() -> int, 'NaN', or None
    EMPTY() -> bool
    """

    def __init__(self):
        """
        Construct a PikaStack object.
        """
        self.elements = []

    def ADD(self):
        """
        Add the top two elements on the stack.

        Adds the top two elements on the stack and pushes the result back onto 
        the stack.
        
        Error handling:
        If the stack is empty, nothing happens.
        If the stack only has a single element, the result pushed to the top of
        the stack is equal to the current top.
        """
        a = self.POP()
        b = self.POP()
        c = a + b
        self.PUSH(b)
        self.PUSH(a)
        self.PUSH(c)

    def SUB(self):
        """
        Subtracts the top two elements.
        
        Subtracts the first element on the stack from the second element and
        pushes the result back onto the stack.

        Error Handling:
        If the stack is empty, nothing happens.
        If the stack only has a single element, the result pushed to the top of
        the stack is -top
        """
        a = self.POP()
        b = self.POP()
        c = b - a
        self.PUSH(b)
        self.PUSH(a)
        self.PUSH(c)

    def MULT(self):
        """
        Multiplies the top two elements on the stack.

        Multiplies the top two elements on the stack and pushes the result back
        onto the stack.

        Error handling:
        If the stack is empty, nothing happens.
        If the stack only has a single element, the result pushed to the top of 
        the stack is 0
        """
        a = self.POP()
        b = self.POP()
        c = a * b
        self.PUSH(b)
        self.PUSH(a)
        self.PUSH(c)

    def DIV(self):
        """
        Divides the top two elements on the stack

        Divides the second element on the stack by the first element on the stack,
        and pushes the result back on top of the stack.
        
        Error Handling:
        If the stack is empty, nothing happens.
        If the stack only has a single element, the result pushed to the top of 
        the stack is 0
        If the divisor is '0', the result pushed to the top of the stack is 
        float("NaN")
        """
        a = self.POP()
        b = self.POP()
        if a == 0:
            self.PUSH(float('NaN'))
        else:
            c = b // a
            self.PUSH(b)
            self.PUSH(a)
            self.PUSH(c)

    def RAND(self):
        """
        Returns a random number between 1 and the top element on the stack (inclusive).

        Error Hnadling:
        If stack is empty, push 0 to the top of the stack.
        If top of the stack is negative, push 0 to the top of the stack.
        :return:
        """
        if self.PEEK() and self.PEEK() > 0:
            self.PUSH(randrange(self.PEEK()) + 1)
        else:
            self.PUSH(0)

    def POP(self):
        """
        Pops and returns the top element from the stack.

        Error Handling:
        If the stack is empty 0 is returned.
        """
        if len(self.elements):
            return self.elements.pop()
        else:
            return 0

    def PUSH(self, element):
        """
        Pushes an element to the top of the stack.

        Arguments:
        element -> The element to push on the top of the stack.
        """
        self.elements.append(element)

    def PEEK(self):
        """
        Returns the top element from the stack without removing it.

        Error Handling:
        If the stack is empty 0 is returned.
        """
        if len(self.elements):
            return self.elements[-1]
        else:
            return 0

    def EMPTY(self):
        """
        Returns True if the stack is empty, false otherwise.
        """
        return len(self.elements) == 0

    def __str__(self):
        """Defines the string representation of the PikaStack object."""
        return str(self.elements)
