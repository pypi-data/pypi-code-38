import math


def get_magnitude(number):
    if number == 0:
        return 0

    return math.floor(math.log(abs(number), 10))


def get_name(magnitude_over_3, shorten=False):
    if magnitude_over_3 == 0:
        return ""

    filename = ""
    if shorten:
        filename = "symbols.txt"
    else:
        filename = "words.txt"

    names_file = open(filename, "r")
    names_lines = [i.split("\n")[0] for i in names_file.readlines()]

    if magnitude_over_3 == 1:
        return names_lines[0]

    small_units_names = names_lines[1].split(",")
    big_units_names = [i.split("_")[0] for i in names_lines[2].split(",")]
    tens_names = [i.split("_")[0] for i in names_lines[3].split(",")]

    if not shorten:
        big_units_flags = []
        tens_flags = []

        for big_units, tens in [
            (names_lines[2].split(",")[i], names_lines[3].split(",")[i])
            for i in range(9)
        ]:
            big_units_append = ""
            tens_append = ""

            big_units_split = big_units.split("_")
            tens_split = tens.split("_")

            if len(big_units_split) > 1:
                big_units_append = big_units_split[1]

            if len(tens_split) > 1:
                tens_append = tens_split[1]

            big_units_flags.append(big_units_append)
            tens_flags.append(tens_append)

    magnitude_units_digit = (magnitude_over_3 - 1) % 10
    magnitude_tens_digit = math.floor((magnitude_over_3-1) / 10)

    units_name = ""
    tens_name = ""
    exception_char = ""

    # Use second line of names file when magnitude is under 11
    if magnitude_over_3 < 11:
        units_name = small_units_names[magnitude_units_digit - 1]
    else:
        # Use third line for the units digits of the magnitude
        if magnitude_units_digit > 0:
            units_name = big_units_names[magnitude_units_digit - 1]

        # Use fourth line for the tens digits of the magnitude
        tens_name = tens_names[magnitude_tens_digit - 1]

        if not shorten:
            # Add exception character to join the two words if needed.
            exception_char = "".join(
                set(big_units_flags[magnitude_units_digit - 1])
                & set(tens_flags[magnitude_tens_digit - 1])
            )

            # Strange exception case:
            # "tre" has the "x" flag but uses the character "s"

            if units_name == "tre" and "x" in tens_flags[magnitude_tens_digit - 1]:
                exception_char = "s"

    names_file.close()

    return units_name + exception_char + tens_name


def format_num(number, shorten=False, precision=0):
    if abs(number) >= 1e303:
        raise ValueError("Number is bigger than or equal to 1e303.")

    negative = number < 0
    magnitude = get_magnitude(number)
    magnitude_over_3 = math.floor(magnitude / 3)

    number_string = "{:0f}".format(number)
    numbers_list = []

    min_index = 0
    max_index = (magnitude + 1) % 3

    if max_index == 0:
        max_index = 3

    last_index = 0
    if precision <= 0:
        last_index = -precision
    else:
        last_index = magnitude_over_3 - precision + 1

    last_index = min(max(last_index, 0), magnitude_over_3)

    for i in range(magnitude_over_3, last_index - 1, -1):
        sub_number_string = str(int(number_string[min_index:max_index]))

        number_name = get_name(i, shorten)

        if sub_number_string != "0":
            numbers_list.append(sub_number_string + " " * (1 - shorten) + number_name)

        min_index = max_index
        max_index += 3

    if len(numbers_list) == 1:
        return numbers_list[0]

    final_number = ""
    if shorten:
        final_number = " ".join(numbers_list)
    else:
        final_number = ", ".join(numbers_list[:-1])
        final_number += " and " + numbers_list[-1]

    return final_number
