#!/usr/bin/python/
#
# This script will compare the arrival time of data to the ESB between
# the legacy system and the enterprise/new system.
#
#
import csv, psycopg2, time, collections
from datetime import datetime, timedelta
from collections import Counter
from collections import OrderedDict 

# Define empty list to store data
date1 = []
date2 = []
wmoHeader1 = [] 
wmoHeader2 = [] 

#readerLegacy = csv.reader(open("RG-merge-r3.csv"), delimiter=",")
#legacyFileSorted = sorted(readerLegacy, key=operator.itemgetter(7), reverse=True)

print "Starting comparison..."
# Open the legacy CSV file 
#with open('RG-merge-r3.csv', 'r')as csvfile:
with open('RG-merge-r3.csv', 'r')as csvfile:
    filereader = csv.reader(csvfile, delimiter=',')
    next(filereader, None) #skip header row
    print "Extracting data from legacy file..."
    for column in filereader:
        # Extract the datetime info as a datetime object to use in timedelta
        legacyDateString = datetime.strptime(column[7], '%m/%d/%Y %H:%M').strftime('%Y-%m-%d %H:%M:%S') #reformat string to use dashes
        legacyDateObject = datetime.strptime(legacyDateString, '%Y-%m-%d %H:%M:%S') #returns datetime object
        date1.append(legacyDateObject)
        # Extract WMO header info
        wmoHeaderLegacy = column[1] # TTAAii CCCC YYGGgg
        wmoHeaderNoSpace = wmoHeaderLegacy.replace(" ", "") #Remove whitespace
        # Remove datetime info (YYGGgg)
        wmoHeaderNoSpaceTrimmed = wmoHeaderNoSpace[0:10] # [0:12] if including day(YY)
        dayYY = wmoHeaderNoSpace[10:12]
        nnn = column[2][0:3]
        newColumn = wmoHeaderNoSpaceTrimmed + nnn + dayYY #merge TTAAiiCCCC, NNN, and YY
        wmoHeader1.append(newColumn)

# Open the database query results file and write to a new file, after merging columns
# containing WMO header information 
with open('Database_Query_QA_checksum.csv', 'r')as csvfile:
    filereader2 = csv.reader(csvfile, delimiter=',')
    next(filereader2, None)
    # Open new file to write to
    with open('Database_Query_merged.csv', 'w+') as mergedcsvfile:
        writer = csv.writer(mergedcsvfile)
        for row in filereader2:
            # Merge columns in database results file to form WMO header 
            new_row = ''.join([row[1], row[2]]) #merge ttaaii and cccc
            new_row_nnn = ''.join([new_row, row[3]]) #merge ttaaiicccc and nnn
            new_row_yy = ''.join([new_row_nnn, row[4][0:2]])
            awips_row = ''.join([row[3], row[2][1:4]]) #merge nnn and trimmed cccc (to function as xxx)
            writer.writerow((row[0], new_row, new_row_nnn, new_row_yy, awips_row, row[3], row[4], row[5], row[6]))

# Define module to parse dates queried from the database, having two formats - with and without milliseconds
# Takes a datetime object as an argument
def parse_dates(datetimeObject):
    for formats in ('%Y-%m-%d %H:%M:%S.%f','%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(datetimeObject, formats)
        except ValueError:
            pass
    raise ValueError('No valid date format found.') # If format does not match those defined above

# Open merged file for reading to append WMO header info to empty list defined earlier
with open('Database_Query_merged.csv', 'r')as csvfile:
    filereader3 = csv.reader(csvfile, delimiter=',')
    print "Extracting data from database file..."
    for column in filereader3: 
        wmoHeaderOther = column[1]
        wmoHeaderWithNnn = column[2]
        awipsId = column[4]
        wmoHeaderWithNnnYY = column[3] 
        wmoHeader2.append(wmoHeaderWithNnnYY) 
        # Extract datetime info
        parsedString = parse_dates(column[0]).replace(microsecond=0)
        timeString = datetime.strftime(parsedString, '%Y-%m-%d %H:%M') # string
        timeObject = datetime.strptime(timeString, '%Y-%m-%d %H:%M') # datetime object
        date2.append(timeObject)

# Zip the WMO header and datetimes into a dictionary
HeaderDates1 = dict(zip(wmoHeader1,date1))
HeaderDates2 = dict(zip(wmoHeader2,date2))


# Define dictionaries after wmo header and date lists, sort by wmo header
dict1 = collections.OrderedDict(sorted(HeaderDates1.items()))
dict2 = collections.OrderedDict(sorted(HeaderDates2.items()))

#comparison = {(dict1[x], dict2[x]): dict1[x] - dict2[x] for x in dict1 if x in dict2}
#for (time1, time2), value in comparison.iteritems():
#    print >> file1, ('%s - %s = %s' % (time1, time2, value))
#comparison = {x: dict1[x] - dict2[x] for x in dict1 if x in dict2}
#for key,value in comparison.iteritems():
#    print >> file1, ('%s: %s' % (key,value)) #format output string: string

# Perform a 1 to 1 comparison. Match the header/awips ids in each 
# dictionary and take the difference between the datetimes
file1 = open('Latency.txt', 'w')
print "Saving results..."
for k in HeaderDates1:
    if k in HeaderDates2:
        print >> file1, k, ": ", HeaderDates1[k], "-", HeaderDates2[k], "=", abs(HeaderDates1[k]-HeaderDates2[k])
file1.close()

# Count products and sort keys alphabetically
legacyProductCount = Counter(wmoHeader1) #Counter (dictionary subclass)
newProductCount = Counter(wmoHeader2)
legacyCountOrdered = OrderedDict(sorted(legacyProductCount.items(), key=lambda t: t[0])) #Ordered Dictionary 
newCountOrdered = OrderedDict(sorted(newProductCount.items(), key=lambda t: t[0]))

print("wmoHeader1: " + str(len(wmoHeader1))) #list
print("legacyProductCount: " + str(len(legacyProductCount))) #Counter class collection
print("wmoHeader2: " + str(len(wmoHeader2)))
print("newProductCount: " + str(len(newProductCount)))

# Save ouput to file
file2 = open('Legacy_Products_Count.txt', 'w')
for key, value in legacyCountOrdered.items():
    count = (key, value)
    print >> file2, count
file2.close()

file3 = open('New_Products_Count.txt', 'w')
for key, value in newCountOrdered.items():
    count = (key, value)
    print >> file3, count
file3.close()

# End of script 
