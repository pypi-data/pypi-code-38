"""
PT-BR
O objetivo desse módulo é criar um modo de lidar com vetores que seja o mais próximo possível de função built-in,
quase como se o vetor se torna-se um novo tipo de variável dentro do Python. Eu busquei adicionar todas as operações
com vetores existentes, todas as propriedades possíveis. Caso eu tenha esquecido algo por favor me avise e eu tentarei
implementar.

Optei por não implementar a função de plot visto que é possível plotar facilmente utilizando a biblioteca matplotlin,
tendo os parâmetros self.x e self. y como entrada. Caso vejam utilidade e necessidade a função pode ser implementada
em versões seguintes.

Observe que todos os métodos funcionam utilizando vetores representados com coordenadas, portanto se você tem um vetor
como os parâmetros módulo e ângulo utilize primeiro o método estático Vector.decompose(), e só então use o vetor
resultante com as demações funções. É possível retornar ao estado original utilizando o método self.compose, que
retornará uma lista contendo o módulo e o ângulo original.


EN-US
The purpose of this module is to create a way of dealing with vectors that is as close to the built-in function as possible,
almost as if the vector becomes a new type of variable within Python. I've tried adding all operations
with existing vectors, all possible properties. If I have forgotten something please let me know and I will try
to implement.

I chose not to implement the plot function since it is possible to easily plot using the matplotlin library,
taking the parameters self.x and self.y as input. If you see utility and necessity the function can be implemented
in subsequent versions.

Note that all methods work by using vectors represented with coordinates, so if you have a vector
represented as a module and angle, first use the static method Vector.decompose (), and then use vector
with the functions. It is possible to return to the original state using the self.compose method, which
will return a list containing the original module and angle.
"""


class Vector():

    def __init__(self, x, y):
        """
        PT-BR
        :param x: ponto x do vetor
        :param y: ponto y do vetor
        :param coord: lista com as coordenadas do vetor

        EN-US
        :param x: point x of the vector
        :param y: point y of vector
        :param coord: list with the coordinates of the vector
        """
        self.x = x
        self.y = y
        self.coord = (self.x, self.y)

    def __add__(self, other):
        """
        PT-BR
        Reescreve o método interno de adição permitindo que se adicionem vetores utilizando apenas o sinal de "+",
        como por exemplo em - Vector(1,3) + Vector(4,3) -, obtendo um vetor (5,4)
        :param other: o vetor a ser adicionado ao vetor original
        :return: um novo vetor com x como resultado da soma de x1 + x2, e y como resultado da soma de y1 + y2

        EN-US
        Rewrite the internal method of addition making it possible to add vectors using only the "+" sign,
        as in - Vector (1,3) + Vector (4,3) -, obtaining a vector (5,4)
        :param other: the vector to be added to the original vector
        :return: a new vector with x as a result of the sum of x1 + x2, and y as a result of the sum of y1 + y2
        """
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """
        PT-BR
        Reescreve o método interno de subtração permitindo que se subtraiam vetores utilizando apenas o sinal de "-",
        como por exemplo em - Vector(1,3) - Vector(4,3) -, obtendo um vetor (-3,0)
        :param other: o vetor a ser subtraido do vetor original
        :return: um novo vetor com x como resultado da subtração de x1 - x2, e y como resultado da subtração de y1 - y2

        EN-US
        Rewrite the internal subtraction method making it possible to subtract vectors using only the "-" sign,
        as in / Vector (1,3) - Vector (4,3) /, obtaining a vector (-3,0)
        :param other: the vector to be subtracted from the original vector
        :return: a new vector with x as a result of the subtraction of x1 - x2, and y as a result of the subtraction of
        y1 - y2
         """
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        """
        PT-BR
        Reescreve o método interno de multiplicação tornando possível que se multipliquem vetores utilizando apenas
        o sinal de "*", como por exemplo em - Vector(1,3) * Vector(4,3) -, obtendo um escalar de 13

        Há também a possibilidade de multiplicação por número, como por exemplo em - Vector(1,3) * 3 -,
        resultando em um novo vetor (3,9)

        :param other: o vetor ou o int/float a ser multiplicado com o vetor original
        :return: um novo vetor com x como resultado da soma de x1 * numero, e y como resultado da soma de y1 * numero,
        ou o produto escalar entre os vetores

        EN-US
        Rewrite the internal multiplication method making it possible to multiply vectors using only
        the signal of "*", as for example in - Vector (1,3) * Vector (4,3) -, obtaining a scalar of 13

        There is also the possibility of multiplication by number, as for example in - Vector (1,3) * 3 -,
        resulting in a new vector (3.9)

        :param other: the vector or the int / float to be multiplied with the original vector
        :return: a new vector with x as a result of the sum of x1 * number, and y as a result of the sum of y1 * number,
        or the scalar product between the vectors
        """
        if type(other) == int or float:
            x = Vector(self.x * other, self.y * other)
        else:
            x = self.x * other.x + self.y * other.y
        return x

    def __gt__(self, other):
        """
        PT-BR
        Permite que seja possível utilizar o operador lógico "maior que", comparando o módulo dos vetores
        :param other: vetor a ser comparado
        :return: True or False


        EN-US
        Allows you to use the "greater than" logical operator by comparing the vector modules
        :param other: vector to be compared
        :return: True or False
        """
        return self.module() > other.module()

    def __lt__(self, other):
        """
        PT-BR
        Permite que seja possível utilizar o operador lógico "menor que", comparando o módulo dos vetores
        param other: vetor a ser comparado
        :return: True or False

        EN-US
        Allows you to use the "lesser than" logical operator by comparing the vector modules
        :param other: vector to be compared
        :return: True or False
        """
        return self.module() < other.module()

    def __ge__(self, other):
        """
        PT-BR
        Permite que seja possível utilizar o operador lógico "maior ou igual que", comparando o módulo dos vetores
        :param other: vetor a ser comparado
        :return: True or False

        EN-US
        It allows you to use the logical operator "greater than or equal to" by comparing the vector modules
        :param other: vector to be compared
        :return: True or False
        """
        return self.module() >= other.module()

    def __le__(self, other):
        """
        Permite que seja possível utilizar o operador lógico "menor ou igual que", comparando o módulo dos vetores

        :param other: vetor a ser comparado
        :return: True or False

        EN-US
        It allows you to use the logical operator "lesser than or equal to" by comparing the vector modules
        :param other: vector to be compared
        :return: True or False
        """
        return self.module() <= other.module()

    def __eq__(self, other):
        """
        Permite que seja possível utilizar o operador lógico "igual", comparando se dois vetores são iguais.
        Os vetores só serão consideradores iguais se possuírem mesmo módulo, direção e sentido.

        :param other: vetor a ser comparado
        :return: True or False

        EN-US
        It allows you to use the "equal" logical operator, comparing if two vectors are equal.
        The vectors will only be considered equal if they have the same module, direction and notion.

        :param other: vector to be compared
        :return: True or False
        """
        return self.module() == other.module() and self.tg() == other.tg() and ((self.x > 0 and other.x > 0) or (self.x < 0 and other.x < 0))

    def __ne__(self, other):
        """
        PT-BR
        Permite que seja possível utilizar o operador lógico "diferente", comparando se dois vetores são diferente.
        Os vetores só serão consideradores diferentes se possuírem módulo, direção ou sentido diferentes.

        :param other: vetor a ser comparado
        :return: True or False


        EN-US
        It allows you to use the "different" logical operator, comparing if two vectors are different.
        The vectors will only be different considering if they have different module, direction or notion.

        :param other: vector to be compared
        :return: True or False
        """
        return self.module() != other.module() or self.tg() != other.tg() or ((self.x > 0 and other.x < 0) or (self.x < 0 and other.x > 0))

    def __str__(self):
        """
        PT-BR
        Configura como os vetores serão printados.
        :return: (x1, y1)

        EN-US
        Set how the vectors will be printed.
        :return: (x1, y1)
        """
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def tg(self):
        """
        PT-BR
        :return: tangente do ângulo que o vetor faz com o eixo x, em radianos.

        EN-US
        :return: tangent of the angle that the vector makes with the x-axis, in radians.
        """
        return self.y/self.x

    def unit(self):
        """
        PT-BR
        Calcula o vetor unitário.
        :return: vetor unitário do vetor self.

        EN-US
        Calculates the unit vector.
        :return: unit vector of the self vector.
        """
        return Vector(self.x/self.module(), self.y/self.module())

    def angle(self):
        """
        PT-BR
        Calcula o ângulo que o vetor faz com o eixo x.
        :return: ângulo em graus.

        EN-US
        Calculates the angle that the vector makes with the x-axis.
        :return: angle in degrees, rounded to 2 decimal places.
        """
        from math import atan, degrees
        tg = self.tg()
        d =  degrees(atan(tg))
        return round(d, 2)

    def anglebetween(self, other):
        """
        PT-BR
        Calcula o ângulo entre dois vetores
        :param other: vetor a ser comparado.
        :return: ângulo entre os dois vetores, arredondado para 2 casas decimais.

        EN-US
        Calculate the angle between two vectors
        :param other: vector to be compared.
        :return: angle between the two vectors, rounded to 2 decimal places.
        """
        from math import acos, degrees
        x = (self.x*other.x + self.y + other.y)/(self.module()*other.module())
        d = degrees(acos(x))
        return round(d, 2)

    def module(self):
        """
        PT-BR
        Calcula o módulo do vetor.
        :return: módulo do vetor, arredondado para 2 casas decimais.


        EN-US
        Calculate the vector module.
        :return: vector module, rounded to 2 decimal places.
        """
        from math import sqrt
        x = abs(sqrt(self.x * self.x + self.y * self.y))
        return round(x, 2)

    def compose(self):
        """
        PT-BR
        Transforma um vetor representado como ponto em um vetor representado por módulo e ângulo.
        :return: lista com os parâmetros (módulo, ângulo).

        EN-US
        Transforms a vector represented as a point into a vector represented by module and angle.
        :return: list with parameters (module, angle).
        """
        return (self.module(), self.angle())

    @staticmethod
    def decompose(module, angle):
        """
        PT-BR
        :param module: módulo do vetor
        :param angle: ângulo do vetor
        :return: vetor decomposto nos eixos x e y: Vector(x,y)

        EN-US
        :param module: vector module
        :param angle: vector angle
        :return: vector decomposed into x and y axes: Vector (x, y)
        """
        from math import cos, sin, radians
        fx = module * (cos(radians(angle)))
        fy = module * (sin(radians(angle)))
        fy = round(fy,2)
        fx = round(fx,2)
        return Vector(round(fx, 2), round(fy, 2))