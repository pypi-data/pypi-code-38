import pandas as pd
import numpy as np
import pickle

def makeArray(studentCount, studentsDF, courseCount, coursesDF, bias, w1, w2, w3, w4, w5):
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

def calcChoiceCost(anAllotment, SvCarray3):
    cost1 = (np.sum(anAllotment * SvCarray3))
    return cost1

def squeezeAllotment(anAllotment, times, studentCount, courseCount):
    allotment = np.zeros((studentCount, courseCount))
    start = 0
    for i in range(courseCount):
        stop = start + times[i]
        allotment[:,i] = (np.sum(anAllotment[:,start:stop], 1)).ravel()
        start = stop
    allotment = np.array(allotment, dtype=np.int64)
    return allotment

def calculateVariance(cpiArray, allotment, courseCount):
    cpiRepeated = (np.array([cpiArray, ]*courseCount)).transpose()
    SvC_cpi = allotment * cpiRepeated
    b = np.ma.masked_where(SvC_cpi == 0, SvC_cpi)
    #a = np.array(np.ma.mean(b, 0), dtype=np.float)
    a = np.array(np.nanmean(b, 0), dtype=np.float)
    #print b
    variance = np.var(a)
    return variance

def calcGoodness(anAllotment, SvCarray, courseCount, cpiArray):
    a = anAllotment.data * SvCarray
    b = np.ma.masked_where(a == 0, a)
    choiceGoodness = np.array(np.nanmean(b, 1), dtype=np.float)
    # meanChoiceGoodness = np.mean(choiceGoodness)
    #
    cpiRepeated = (np.array([cpiArray, ]*courseCount)).transpose()
    SvC_cpi = anAllotment.data * cpiRepeated
    b = np.ma.masked_where(SvC_cpi == 0, SvC_cpi)
    cpiGoodness = np.array(np.nanmean(b, 0), dtype=np.float)
    return choiceGoodness, cpiGoodness

def allottedCourseGrade(studentCount, courseCount, studentsDF, anAllotment, SvCarray3):
    allotmentMatrix = anAllotment * SvCarray3
    temp = np.zeros((studentCount, 1))
    for i in range(studentCount):
        for j in range(courseCount):
            if(allotmentMatrix[i,j] != 0):
                if(allotmentMatrix[i,j] == 10):
                    temp[i] = 0;
                    break
                else:
                    temp[i] = studentsDF.loc[i][str("Grade"+str(allotmentMatrix[i,j]))]
                    break

    return sum(temp)

def calculateUtility(anAllotment, C1, C2, C3, SvCarray2, SvCarray3, courseCount, studentCount, studentsDF, cpiArray):
    choiceSum = calcChoiceCost(anAllotment, SvCarray3)
    cost1 = C1*choiceSum
    cost2 = C2*allottedCourseGrade(studentCount, courseCount, studentsDF, anAllotment, SvCarray3)
    var = calculateVariance(cpiArray, anAllotment, courseCount)
    cost3 = C3/var
    totalUtility = cost1 + cost2 + cost3
    return totalUtility

def swapRows(anAllotment, studentCount):
    swapId1 = np.random.randint(0,studentCount-1)
    swapId2 = np.random.randint(0,studentCount-1)
    temp2 = anAllotment.copy()
    tempVar = temp2[swapId1,:].copy()
    temp2[swapId1,:] = temp2[swapId2,:]
    temp2[swapId2,:] = tempVar
    return temp2

def runMCMC(x_0, nIters, studentCount, courseCount, C1, C2, C3, SvCarray2, SvCarray3, studentsDF, cpiArray):
    beta = 10*np.log10(1+studentCount)
    utility = np.zeros((nIters,1))
    for i in range(nIters):
        print(i)
        newAllotment = swapRows(x_0, studentCount)

        u1 = calculateUtility(newAllotment, C1, C2, C3, SvCarray2, SvCarray3, courseCount, studentCount, studentsDF, cpiArray)
        u2 = calculateUtility(x_0, C1, C2, C3, SvCarray2, SvCarray3, courseCount, studentCount, studentsDF, cpiArray)
        utility[i] = u1;
        print(u1)
        if u1 >= u2:
            x_0 = newAllotment
        else:
            beta = 10*np.log10(1+i)
            probVar = np.exp(beta*(u1 - u2))
            randNum = np.random.uniform()
            if randNum < probVar:
                x_0 = newAllotment
            else:
                x_0 = x_0
    return x_0, utility

def writePerformance(x_0, choiceGoodnessOld, cpiGoodnessOld, choiceGoodnessNew, cpiGoodnessNew, utility):
    with open('objsWithUtility.pickle', 'wb') as f:
        pickle.dump([x_0, choiceGoodnessOld, cpiGoodnessOld, choiceGoodnessNew, cpiGoodnessNew, utility], f)