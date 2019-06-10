import time

  

def locate(row,column,clear=True):

    if (clear == True): clearscreen()

    print("\033[{};{}H".format(row,column), end="")





def clearscreen():

    print("\033[0;0H", end="")

    print("\033[0J",end="")


def read_line(fr):
    try:
        line = fr.fd.readline()
        line = line.rstrip("\r\n")
        line = line.rstrip("\r")
        line = line.rstrip("\n")
        return line
    except Exception as e:
        line = ""
        print("Error reading line ", e)
    finally:
        return line


def write_line(fw, write_string, crlf = True):
    try:
        if(crlf == False):
            line = write_string
        else:
            line = write_string + "\r"
        fw.fd.write(line)
    except Exception as e:
        print("Error writing line ", e)


def varmid(num1, rec, var, length):
    num3=int(num1) - 1
    num4 = num3 + length
    return str(rec[var])[num3:num4]


def main():

    locate(10,10,clear=True)

    for i in range(10):

        locate(12,40)

        print(i)

        time.sleep(1)

    clearscreen()



if __name__ == "__main__":

    main()