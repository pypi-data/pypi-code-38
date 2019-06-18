
import numpy as np
import matplotlib.pyplot as plt
import csv


def dat_reader(filename,datasize,csvname):
    
    """
    Parsing data for a .dat file into a CSV file
    
    Combines real and imaginary values from a .dat file into a CSV file. 
    After combining them together, there are  imaginary values. 
    Both files have to be in the same directory. Data is colled from
    "XEP_X4M200_X4M300_plot_record_playback.py".
    
    Parameters
    filename: .dat file
    datasize: How many sets of data are there
    csvname= Name of CSV file
    
    Returns
    CSV File: in the same directory as the .dat file
    1 : To show file has been converted 
    
    Sample Usuage
    
    >>>dat_reader("xethru_datafloat_20190614_141837.dat",180,csv_converted)
    >>>1
    
    
    
    """
   

    with open(filename, "rb") as f:  # Opening .dat file
        data = np.fromfile(f, dtype=np.float32)  # Loading .dat file
        for i in range(0, len(data) // 363 - 1):
            temp = data[3 * (i + 1) + (datasize*2) * i:3 * (i + 1) + (datasize*2) * (i + 1)]
            iqdata = []
            for j in range(0, datasize):
                if (temp[j + datasize] > 0):
                    iqdata.append(str(round(temp[j], 4)) + "+" + str(round(temp[j + datasize], 4)) + "j")
                else:
                    iqdata.append(str(round(temp[j], 4)) + str(round(temp[j + datasize], 4)) + "j")

            with open(csvname+".csv", 'a', newline="") as csvFile:            # Writing into CSV with complex numbers
                writer = csv.writer(csvFile)
                writer.writerow(iqdata)

        f.close()  # Closing CSV and .dat files
        csvFile.close()
    return 1

def raw_reader(filename,csvname):
    
    """
    Parsing data for a .dat file into a CSV file
      
     
    Parameters
    filename: .dat file 
     
    Returns
    CSV File: in the same directory as the .dat file
    1 : To show file has been converted 
    
    Sample Usuage
    
    >>>dat_reader("xethru_datafloat_20190614_141837.dat",csv_converted)
    >>>1
    
    """
    
     
    with open(filename, "rb") as f:
                 
        data = np.fromfile(f, dtype=np.float32)
                 
                 
        for i in range(0, len(data)//1473-1):
            temp=data[3+1470*i:3+1470*(i+1)]
                     
        with open (csvname+".csv", 'a', newline="") as csvFile:
            writer=csv.writer(csvFile)
            writer.writerow(temp)
     
     
        f.close()
        csvFile.close()
    return 1



