import numpy as np
import matplotlib.pyplot as plt
import csv


class X4():
    def __init__(self,filename):
        with open (filename,"rb") as self.f:
            self.data = np.fromfile(f, dtype=np.float32)

    def iq_data(self):
        for i in range(0, len(self.data) // 363 - 1):
            temp = self.data[3 * (i + 1) + 360 * i:3 * (i + 1) + 360 * (i + 1)]
            iqdata = []
            for j in range(0, 180):
                if (temp[j + 180] > 0):
                    iqdata.append(str(round(temp[j], 4)) + "+" + str(round(temp[j + 180], 4)) + "j")
                else:
                    iqdata.append(str(round(temp[j], 4)) + str(round(temp[j + 180], 4)) + "j")

            with open('nohex.csv', 'a', newline="") as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(iqdata)
        self.f.close()
        csvFile.close()

    def raw_data(self):
        for i in range(0, len(self.data) // 1473 - 1):
            temp = self.data[3 + 1470 * i:3 + 1470 * (i + 1)]
            with open('test.csv', 'a', newline="") as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(temp)
        self.f.close()
        csvFile.close()