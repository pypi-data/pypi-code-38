class TransformNumbers:

    def number_to_letters(self, number, cents=False):
        indicator = [("", ""), ("MIL", "MIL"), ("MILLON", "MILLONES"), ("MIL", "MIL"), ("BILLON", "BILLONES")]
        integer = int(number)
        decimal = int(round((number - integer) * 100))
        counter = 0
        number_in_letters = ""
        while integer > 0:
            a = integer % 1000
            if counter == 0:
                in_letters = self.convert_figure(a, 1).strip()
            else:
                in_letters = self.convert_figure(a, 0).strip()
            if a == 0:
                number_in_letters = in_letters + " " + number_in_letters
            elif a == 1:
                if counter in (1, 3):
                    number_in_letters = indicator[counter][0] + " " + number_in_letters
                else:
                    number_in_letters = in_letters + " " + indicator[counter][0] + " " + number_in_letters
            else:
                number_in_letters = in_letters + " " + indicator[counter][1] + " " + number_in_letters

            number_in_letters = number_in_letters.strip()
            counter = counter + 1
            integer = int(integer/1000)
        if cents:
            number_in_letters = number_in_letters + " PUNTO " + self.convert_figure(decimal, 0).strip().upper()
        else:
            number_in_letters = number_in_letters
        return number_in_letters.replace("  ", " ")

    def convert_figure(self, number, sw):
        list_hundred = ["", ("CIEN", "CIENTO"), "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
                        "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]
        list_ten = ["", (
            "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE"),
                        ("VEINTE", "VEINTI"), ("TREINTA", "TREINTA Y "), ("CUARENTA", "CUARENTA Y "),
                        ("CINCUENTA", "CINCUENTA Y "), ("SESENTA", "SESENTA Y "),
                        ("SETENTA", "SETENTA Y "), ("OCHENTA", "OCHENTA Y "),
                        ("NOVENTA", "NOVENTA Y ")
                        ]
        list_unit = ["", ("UN", "UNO"), "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
        hundred = int(number / 100)
        ten = int((number - (hundred * 100)) / 10)
        unit = int(number - (hundred * 100 + ten * 10))

        text_unit = ""

        text_hundred = list_hundred[hundred]
        if hundred == 1:
            if (ten + unit) != 0:
                text_hundred = text_hundred[1]
            else:
                text_hundred = text_hundred[0]

        text_ten = list_ten[ten]
        if ten == 1:
            text_ten = text_ten[unit]
        elif ten > 1:
            if unit != 0:
                text_ten = text_ten[1]
            else:
                text_ten = text_ten[0]

        if ten != 1:
            text_unit = list_unit[unit]
            if unit == 1:
                text_unit = text_unit[sw]

        return "%s %s %s" % (text_hundred, text_ten, text_unit)
