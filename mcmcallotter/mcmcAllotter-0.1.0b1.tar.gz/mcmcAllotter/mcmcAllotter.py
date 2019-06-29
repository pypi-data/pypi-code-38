import pandas as pd
import numpy as np
import utils

np.random.seed(2**13 - 1)
C1 = -1.0
C2 = 1
C3 = 1
nIters = 45000

class allotment(object):
    """An allotment class"""
    def __init__(self, studentCount, courseCount, times):
        super(allotment, self).__init__()
        self.studentCount = studentCount
        self.courseCount = courseCount
        self.times = times
        self.data = np.eye(studentCount)
        self.squeezeAllotment()
    
    def squeezeAllotment(self):
        dataHolder = np.zeros((self.studentCount, self.courseCount))
        start = 0
        for i in range(self.courseCount):
            stop = start + self.times[i]
            dataHolder[:,i] = (np.sum(self.data[:,start:stop], 1)).ravel()
            start = stop
        self.data = np.array(dataHolder, dtype=np.int64)

    def calcGoodness(self, choiceWeights, cpiArray):
        a = self.data*choiceWeights
        b = np.ma.masked_where(a == 0, a)
        choiceGoodness = np.array(np.nanmean(b, 1), dtype=np.float)
        cpiRepeated = (np.array([cpiArray, ]*self.courseCount)).transpose()
        SvC_cpi = self.data * cpiRepeated
        b = np.ma.masked_where(SvC_cpi == 0, SvC_cpi)
        cpiGoodness = np.array(np.nanmean(b, 0), dtype=np.float)
        return choiceGoodness, cpiGoodness

    def makeArray(studentCount, studentsDF, courseCount, coursesDF, bias, w1, w2, w3, w4, w5):
        studentCount = len(studentsDF.index)
        courseCount = len(coursesDF.index)
        Array = np.zeros((studentCount, courseCount), dtype=np.int64) + bias
        for i in np.arange(0,courseCount):
            for j in np.arange(0,studentCount):
                if coursesDF['CourseCode'][i] == studentsDF['Choice1'][j]:
                    Array[j][i] = w1
                elif coursesDF['CourseCode'][i] == studentsDF['Choice2'][j]:
                    Array[j][i] = w2
                elif coursesDF['CourseCode'][i] == studentsDF['Choice3'][j]:
                    Array[j][i] = w3
                elif coursesDF['CourseCode'][i] == studentsDF['Choice4'][j]:
                    Array[j][i] = w4
                elif coursesDF['CourseCode'][i] == studentsDF['Choice5'][j]:
                    Array[j][i] = w5
        return Array

coursesDF = pd.read_csv('../data/courseFile3.csv')
studentsDF = pd.read_csv('../data/studentsWithCpi.csv')

courseCount = len(coursesDF.index)
studentCount = len(studentsDF.index)
cpiArray = studentsDF['CPI']
times = np.array(coursesDF['CourseNeeds'])

choiceIdx = utils.makeArray(studentCount, studentsDF, courseCount, coursesDF, 0, 1, 2, 3, 4, 5)
choiceWeights = utils.makeArray(studentCount, studentsDF, courseCount, coursesDF, 10, 1, 2, 3, 4, 5)

x_0 = allotment(studentCount, courseCount, times)

choiceGoodnessOld, cpiGoodnessOld = x_0.calcGoodness(choiceWeights, cpiArray)

finalAllottment, utility = utils.runMCMC(x_0.data, nIters, studentCount, courseCount, C1, C2, C3, choiceIdx, choiceWeights, studentsDF, cpiArray)

print(utils.calculateUtility(finalAllottment.data, C1, C2, C3, choiceIdx, choiceWeights, courseCount, studentCount, studentsDF, cpiArray))

choiceGoodnessNew, cpiGoodnessNew = utils.calcGoodness(finalAllottment, choiceWeights, courseCount, cpiArray)

utils.writePerformance(finalAllottment.data, choiceGoodnessOld, cpiGoodnessOld, choiceGoodnessNew, cpiGoodnessNew, utility)