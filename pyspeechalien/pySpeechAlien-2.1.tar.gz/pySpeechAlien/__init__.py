# Based on Shahabks/my-voice-analysis

import parselmouth
from parselmouth.praat import call, run_file
import glob
import pandas as pd
import numpy as np
import scipy
from scipy.stats import binom
from scipy.stats import ks_2samp
from scipy.stats import ttest_ind
import os

# return array of all analysis results
# this is the structure of the array:
#   array[0] is gender
#   array[1] is mood
#   array[2] is number of syllables
#   array[3] is number of pauses
#   array[4] is total duration (seconds)
#   array[5] is speaking duration (seconds of actual speaking)
#   array[6] is silent duration (seconds of silence)
#   array[7] is speech rate (number of syllables / seconds of speaking duration)
#   array[8] is average pause length (seconds of silent duration / number of pauses)
#   array[9] is speaking-to-total ratio (ratio of speaking duration to total duration)
#   array[10] is syllables-per-sec (number of syllables per second of total duration)
#   array[11] is pauses-per-sec (number of pauses per second of total duration)
#   array[12] is pronunciation probability score
def analysis_array(m, p):
    sound = p + "/" + m
    sourcerun = p + "/myspsolution.praat"
    path = p + "/"

    try:
        objects= run_file(sourcerun, -20, 2, 0.3, "yes", sound,path, 80, 400, 0.01, capture_output = True)
    except:
        return ("Audio was invalid/unclear. pySpeechAlien is cringing")

    array = []

    array.append(gender(m, p, objects)) # gender
    array.append(mood(m, p, objects)) # mood

    syllables = objects[1].strip().split()[0];
    array.append(objects[1].strip().split()[0]) # number of syllables

    pauses = objects[1].strip().split()[1];
    array.append(objects[1].strip().split()[1]) # number of pauses

    total_duration = objects[1].strip().split()[5];
    array.append(total_duration) # total duration (seconds)

    speaking_duration = objects[1].strip().split()[4]
    array.append(speaking_duration) # speaking duration (seconds of silence)

    silent_duration = str(float(total_duration) - float(speaking_duration));
    array.append(silent_duration) # silent duration

    array.append(str(float(syllables) / float(speaking_duration))) # speech rate (number of syllables / seconds of speaking duration)
    array.append(str(float(silent_duration) / float(pauses))) # average pause length (seconds of silent duration / number of pauses)
    array.append(str(float(speaking_duration) / float(total_duration))) # speaking duration to total duration ratio

    array.append(str(float(syllables) / float(total_duration))) # number of syllables per second of total duration
    array.append(str(float(pauses) / float(total_duration))) # number of pauses per second of total duration

    array.append(pronunciation(m, p, objects)) # pronunciation_probability_score

    return array

# pronunciation_probability_score
def pronunciation(m, p, objects):
    sound = p + "/" + m
    sourcerun = p + "/myspsolution.praat"
    path = p + "/"
    try:
        z1 = str(objects[1]) # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2 = z1.strip().split()
        z3 = int(z2[13]) # will be the integer number 10
        z4 = float(z2[14]) # will be the floating point number 8.3
        db = binom.rvs(n=10, p=z4, size=10000)
        a = np.array(db)
        b = np.mean(a) * 100 / 10
        return (str(b))
    except:
        return ("Audio was invalid/unclear. pySpeechAlien is cringing")

# return gender of speaker
def gender(m, p, objects):
    sound = p + "/" + m
    sourcerun = p + "/myspsolution.praat"
    path = p + "/"
    try:
        z1 = str(objects[1]) # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2 = z1.strip().split()
        z3 = float(z2[8]) # will be the integer number 10
        z4 = float(z2[7]) # will be the floating point number 8.3
        if z4 <= 114:
            g = 101
            j = 3.4
        elif z4 > 114 and z4 <= 135:
            g = 128
            j = 4.35
        elif z4 > 135 and z4 <= 163:
            g = 142
            j = 4.85
        elif z4 > 163 and z4 <= 197:
            g = 182
            j = 2.7
        elif z4 > 197 and z4 <= 226:
            g = 213
            j = 4.5
        elif z4 > 226:
            g = 239
            j = 5.3
        else:
            return ("Voice_not_recognized")
            exit()
        def teset(a, b, c, d):
            d1 = np.random.wald(a, 1, 1000)
            d2 = np.random.wald(b,1,1000)
            d3 = ks_2samp(d1, d2)
            c1 = np.random.normal(a,c,1000)
            c2 = np.random.normal(b,d,1000)
            c3 = ttest_ind(c1,c2)
            y = ([d3[0],d3[1],abs(c3[0]),c3[1]])
            return y
        nn = 0
        mm = teset(g, j, z4, z3)
        while (mm[3] > 0.05 and mm[0] > 0.04 or nn < 5):
            mm = teset(g, j, z4, z3)
            nn = nn + 1
        nnn = nn
        if mm[3] <= 0.09:
            mmm = mm[3]
        else:
            mmm = 0.35
        if z4 > 97 and z4 <= 114:
            return ("Male")
        elif z4 > 114 and z4 <= 135:
            return ("Male")
        elif z4 > 135 and z4 <= 163:
            return ("Male")
        elif z4 > 163 and z4 <= 197:
            return ("Female")
        elif z4 > 197 and z4 <= 226:
            return ("Female")
        elif z4 > 226 and z4 <= 245:
            return ("Female")
        else:
            return ("Voice_not_recognized")
    except:
        return ("Audio was invalid/unclear. pySpeechAlien is cringing")

# return mood of speaker
def mood(m, p, objects):
    sound = p + "/" + m
    sourcerun = p + "/myspsolution.praat"
    path = p + "/"
    try:
        z1 = str(objects[1]) # This will print the info from the textgrid object, and objects[1] is a parselmouth.Data object with a TextGrid inside
        z2 = z1.strip().split()
        z3 = float(z2[8]) # will be the integer number 10
        z4 = float(z2[7]) # will be the floating point number 8.3
        if z4 <= 114:
            g = 101
            j = 3.4
        elif z4 > 114 and z4 <= 135:
            g = 128
            j = 4.35
        elif z4 > 135 and z4 <= 163:
            g = 142
            j = 4.85
        elif z4 > 163 and z4 <= 197:
            g = 182
            j = 2.7
        elif z4 > 197 and z4 <= 226:
            g = 213
            j = 4.5
        elif z4 > 226:
            g = 239
            j = 5.3
        else:
            return ("Voice_not_recognized")
            exit()
        def teset(a, b, c, d):
            d1 = np.random.wald(a, 1, 1000)
            d2 = np.random.wald(b,1,1000)
            d3 = ks_2samp(d1, d2)
            c1 = np.random.normal(a,c,1000)
            c2 = np.random.normal(b,d,1000)
            c3 = ttest_ind(c1,c2)
            y = ([d3[0],d3[1],abs(c3[0]),c3[1]])
            return y
        nn = 0
        mm = teset(g, j, z4, z3)
        while (mm[3] > 0.05 and mm[0] > 0.04 or nn < 5):
            mm = teset(g, j, z4, z3)
            nn = nn + 1
        nnn = nn
        if mm[3] <= 0.09:
            mmm = mm[3]
        else:
            mmm = 0.35
        if z4 > 97 and z4 <= 114:
            return ("No_emotion")
        elif z4 > 114 and z4 <= 135:
            return ("Reading")
        elif z4 > 135 and z4 <= 163:
            return ("Passionate")
        elif z4 > 163 and z4 <= 197:
            return ("No_emotion")
        elif z4 > 197 and z4 <= 226:
            return ("Reading")
        elif z4 > 226 and z4 <= 245:
            return ("Passionate")
        else:
            return ("Voice_not_recognized")
    except:
        return ("Audio was invalid/unclear. pySpeechAlien is cringing")
