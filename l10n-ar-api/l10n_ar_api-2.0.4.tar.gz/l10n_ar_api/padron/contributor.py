# -*- coding: utf-8 -*-
class Contributor:

    @classmethod
    def is_valid_cuit(cls, cuit):
        """
        :param cuit: Cuit a validar
        :return: Falso si no es valido
        """

        try:
            int(cuit)
        except ValueError:
            return False

        cuit = str(cuit)

        if len(cuit) != 11:
            return False

        numbers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

        var1 = 0
        for i in range(10):
            var1 = var1 + int(cuit[i]) * numbers[i]
        var3 = 11 - var1 % 11

        if var3 == 11:
            var3 = 0
        if var3 == 10:
            var3 = 9
        if var3 == int(cuit[10]):
            return True

        return False
