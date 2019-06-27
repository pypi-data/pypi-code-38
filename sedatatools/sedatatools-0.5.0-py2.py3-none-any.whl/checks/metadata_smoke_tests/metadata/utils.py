def getFormats(formatting):
    if formatting == '0':
        return "None"
    elif formatting == '1':
        return "custom"
    elif formatting == '2':
        return "12%"
    elif formatting == '3':
        return "12.1%"
    elif formatting == '4':
        return "12.12%"
    elif formatting == '5':
        return "12.123%"
    elif formatting == '6':
        return "12.1234%"
    elif formatting == '7':
        return "$1,234"
    elif formatting == '8':
        return "$1,234.12"
    elif formatting == '9':
        return "1,234"
    elif formatting == '10':
        return "1,234.1"
    elif formatting == '11':
        return "1,234.12"
    elif formatting == '12':
        return "1,234.123"
    elif formatting == '13':
        return "1,234.1234"
    elif formatting == '14':
        return "1,234.12345"
    elif formatting == '15':
        return "1234"
    elif formatting == '16':
        return "1234.1"
    elif formatting == '17':
        return "1234.12"
    elif formatting == '18':
        return "1234.123"
    elif formatting == '19':
        return "1234.1234"
    elif formatting == '20':
        return "1234.12345"

if __name__ == "__main__":
    getFormats()
