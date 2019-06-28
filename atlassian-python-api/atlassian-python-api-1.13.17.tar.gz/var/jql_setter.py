file = open('123', 'r')

for line in file:
    print(line.split("-")[0].strip() + ",")
