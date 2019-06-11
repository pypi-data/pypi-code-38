def read(file_req = './requeriments.txt'):
    requeriments=[]
    with open(file_req, 'r') as file:
        reader = file.readlines()
        for line in reader:
            requeriments.append(line.replace('\n',''))
    return requeriments
