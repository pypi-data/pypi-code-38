#!/usr/bin/python
#
# This script will query the edpdb database and save the 
# output to a file. 
#
import psycopg2

print("Running database_query.py\n")

# Connect to the database 
try:
    #conn = psycopg2.connect("dbname='edpdb' user='edpdbrole' host='nlets-db-dev.cprk.ncep.noaa.gov' password='JaQy2p5z'") #Dev
    conn = psycopg2.connect("dbname='edpdb' user='edpdbrole' host='nlets-db-qa.cprk.ncep.noaa.gov' password='abcvedf2w'") #QA
    print "Connecting to the database..."
except:
    print "Unable to connect to the database."

# Define a cursor to work with
cur = conn.cursor()

# Select fields from the table
#query = """SELECT esb_timestamp, datatype_ttaaii, datatype_cccc, datatype_nnn, datatype_yygggg FROM nwwproduct WHERE (received_via != 'WEBIMG')""" #Dev
query = """SELECT DISTINCT ON (checksum) esb_timestamp, datatype_ttaaii, datatype_cccc, datatype_nnn, datatype_yygggg, received_via, checksum FROM edp.nwwproduct WHERE (received_via != 'WEBIMG') AND (esb_timestamp > '2019-03-04' AND esb_timestamp < '2019-03-05')""" #QA
print "Running query..."

# Copy the results to a new file
outputquery = "COPY ({0}) to STDOUT WITH CSV HEADER".format(query)
with open('Database_Query_QA_checksum.csv', 'w') as f:
#with open('Database_Query_QA.csv', 'w') as f: #QA
    cur.copy_expert(outputquery, f)
print "CSV file created.\n"

