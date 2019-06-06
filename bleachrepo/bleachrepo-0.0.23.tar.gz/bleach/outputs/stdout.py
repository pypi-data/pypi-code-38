def send(data):
    if type(data) == list:
        for d in data:
            print(d)
    else:
        print(data)
