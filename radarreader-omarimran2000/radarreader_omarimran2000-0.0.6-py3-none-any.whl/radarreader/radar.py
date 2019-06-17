
import numpy as np
import matplotlib.pyplot as plt
import csv


def dat_reader(filename):
    
    """
    Parsing binary data into a CSV file
    
    Combines 180 real and 180 complex values from a .dat file into a CSV file. 
    After combining them together, there are 180 complex values. 
    Both files have to be in the same directory 
    
    Parameters
    filename: .dat file 
    
    Returns
    CSV File: in the same directory as the .dat file 
    
    """
    csvname=input("Enter name of CSV File")

    with open(filename, "rb") as f:  # Opening .dat file
        data = np.fromfile(f, dtype=np.float32)  # Loading .dat file
        for i in range(0, len(data) // 363 - 1):
            temp = data[3 * (i + 1) + 360 * i:3 * (i + 1) + 360 * (i + 1)]
            iqdata = []
            for j in range(0, 180):
                if (temp[j + 180] > 0):
                    iqdata.append(str(round(temp[j], 4)) + "+" + str(round(temp[j + 180], 4)) + "j")
                else:
                    iqdata.append(str(round(temp[j], 4)) + str(round(temp[j + 180], 4)) + "j")

            with open(csvname+".csv", 'a', newline="") as csvFile:            # Writing into CSV with complex numbers
                writer = csv.writer(csvFile)
                writer.writerow(iqdata)

        f.close()  # Closing CSV and .dat files
        csvFile.close()

def raw_reader(filename):
    
    """
    Parsing raw data into a CSV file
      
     
    Parameters
    filename: .dat file 
     
    Returns
    CSV File: in the same directory as the .dat file 
    """
    csvname=input("Enter name of CSV File")
     
    with open(filename, "rb") as f:
                 
        data = np.fromfile(f, dtype=np.float32)
                 
                 
        for i in range(0, len(data)//1473-1):
            temp=data[3+1470*i:3+1470*(i+1)]
                     
        with open (csvname+".csv", 'a', newline="") as csvFile:
            writer=csv.writer(csvFile)
            writer.writerow(temp)
     
     
        f.close()
        csvFile.close()



