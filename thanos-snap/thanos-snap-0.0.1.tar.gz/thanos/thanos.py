from os import remove,listdir,rmdir
    
def main():    
    try:
        files = listdir()
        file_count = len(files)
        
        for index in range(file_count // 2 + 1):
            try:
                remove(files[index])
            except:
                rmdir(files[index])
        print("Boom! Half the files are gone.")
    except:
        print("Sorry! You don\'t have all the infinity stones.")