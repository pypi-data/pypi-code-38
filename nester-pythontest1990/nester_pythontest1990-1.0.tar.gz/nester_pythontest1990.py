
def nest_list(my_list):
    for item in my_list:
        if isinstance(item,list):
            nest_list(item)
        else:
            print(item)

    
