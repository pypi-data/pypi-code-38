def to_google_num(value):
    return "{:}".format(value).replace(".", ",")


def unpack_dates(date_value):
    date = date_value.strftime("%d/%m/%Y") if date_value else "N/D"
    week = int(date_value.strftime("%U")) + 1 if date_value else "N/D"
    year = date_value.strftime("%Y") if date_value else "N/D"
    return date, week, year
